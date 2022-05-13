---
id: research-pushing-docker-image
title: Notes on pushing and deploying docker images.
description: Research notes on pushing Docker images for end users
---

## Deploying ECR

ECR repo can be deploying using terraform as shown below.

```terraform
resource "aws_ecr_repository" "prototype_repo" {
  name                 = "prototype_repo"

  image_scanning_configuration {
    scan_on_push = false
  }
}
output "ecr_repo_url" {
    value = aws_ecr_repository.prototype_repo.repository_url
}
```

## Github Packages

[Github packages](https://docs.github.com/en/packages/learn-github-packages/introduction-to-github-packages) looks like a good platform to store public or private docker images. GitHub Packages usage is free for public packages. For private packages, each account on GitHub receives a certain amount of free storage and data transfer, depending on the product used with the account. Any usage beyond the included amounts is controlled by spending limits. Currently, this github package feature is already being used by our NASA [repository](https://github.com/orgs/nasa/packages).

The steps to push a docker image to github repository are shown below. Make sure Docker CLI is installed on your machine.

- Create a DockerFile that will create the image.

```yaml
#This is a sample image
FROM alpine:3.4
RUN apk update
RUN apk add vim 
CMD [“echo”,”Sample image created”]
```
- Build the image using `docker build -t sample-image .`.
- Once the image is there, the next step is to push to github. However, the user will first need to authenticate with github using a `personal access token`. See details [here](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) on how to create the token.
:::important
Github packages might need to be approved by NASA admins for use. In addition, proper permissions need to be granted to the token such as `write_package` in order to push to github.
:::

- Once the token is created, sign in to the github container registry using:
```bash
export CR_PAT=YOUR_PERSONAL_TOKEN
echo $CR_PAT | docker login ghcr.io -u <GITHUB_USERNAME> --password-stdin
```
Replace `<USERNAME>` with your github username. It will show `Login Succeeded` upon success.

- Tag the docker image using the following format. Note that the format must be `ghcr.io/<GITHUB_USERNAME>/<image_name>:<image_tag>`. The image name must have the prefix `cumulus-orca/`. e.g. `cumulus-orca/<image_name>:<image_tag>`. Note that `<image_tag>` is the image version.
```bash
docker tag <image_name> ghcr.io/<GITHUB_USERNAME>/<image_name>:<image_tag>
# example using image name "cumulus-orca/sample-image:latest" and github username "nasa"
docker tag sample-image ghcr.io/nasa/cumulus-orca/sample-image:latest
```
- Finally push the image
```bash
docker push ghcr.io/username/sample-image
```
:::note
Make sure your username matches with your github username or else it will show error while pushing the image.
:::

Once the image is pushed, it  can be view under `Packages` section in github. However, the image will be private by default. Click on the `package settings` page to change from private to public if needed.

## Pulling from Github repo and pushing to ECR

Docker image in github repository can then be pulled by other users using

```bash
docker pull ghcr.io/<GITHUB_USERNAME>/<image_name>:<TAG>
#example
docker pull ghcr.io/username/sample-image:latest

```
Once image is pulled and ECR is deployed, login to ECR and then tag and push the image.

:::note
Make sure to properly tag the image or else it will give an error.
:::

```bash
#login to ECR
aws ecr get-login-password --region <YOUR_REGION> | docker login --username AWS --password-stdin <YOUR_AWS_ACCOUNT_ID>.dkr.ecr.<YOUR_REGION>.amazonaws.com
#example
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-west-2.amazonaws.com
```

```bash
#tag your local image with your ECR repo name
docker tag <IMAGE_NAME>:<IMAGE_TAG> <YOUR_AWS_ECR_REPO_URI>:<IMAGE_TAG>
#example
docker tag ghcr.io/username/sample-image:latest 123456789.dkr.ecr.us-west-2.amazonaws.com/prototype_repo:prototype
```


```bash
#push image to your ECR
docker push <YOUR_ECR_REPO_URI>:<IMAGE_TAG>
#example
docker push 123456789.dkr.ecr.us-west-2.amazonaws.com/prototype_repo:prototype
```
## Alternative approach to pull and push images to ECR using Packer
Another approach to pull, tag and push images from github repository to AWS ECR is to use Hashicorp [Packer](https://www.packer.io/) that can automatically build and push docker images to AWS. It uses the HashiCorp Configuration Language (HCL). A sample working script named `test.pkr.hcl` deployed to AWS sandbox is shown below:
:::note
    Make sure the file name ends with ".pkr.hcl"
:::


```bash
packer {
  # install required plugins
  required_plugins {
    docker = {
      version = ">= 1.0.1"
      source  = "github.com/hashicorp/docker"
    }
  }
}

variable  "ecr_repository_url" {
  type = string
  sensitive = true
}

variable  "image_version" {
  type = string
}

# pull the image from github repo
source "docker" "prototype_image" {
  image = "ghcr.io/rizbihassan/cumulus-orca/sample-image:latest"
  commit = true
}
# build the image
build {
  sources = ["source.docker.prototype_image"]
# tag the image
  post-processors {
    post-processor "docker-tag" {
        repository = var.ecr_repository_url
        tags = [var.image_version]
    }
    # push the image to ECR repo that was deployed using terraform previously
    post-processor "docker-push" {
        ecr_login = true
        login_server = var.ecr_repository_url
    }
  }
}
```
Run the packer file using the command below. Replace `<ECR_REPOSITORY_URL>` and `<IMAGE_VERSION>` with yours.

```bash
packer build -var 'ecr_repository_url=<ECR_REPOSITORY_URL>' -var 'image_version=<IMAGE_VERSION>' test.pkr.hcl
```
The output will show something like this if successful:
```bash
user$ packer build -var 'ecr_repository_url=123456789.dkr.ecr.us-west-2.amazonaws.com/prototype_repo' -var 'image_version=v1' test.pkr.hcl
docker.prototype_image: output will be in this color.

==> docker.prototype_image: Creating a temporary directory for sharing data...
==> docker.prototype_image: Pulling Docker image: ghcr.io/rizbihassan/cumulus-orca/sample-image:latest
    docker.prototype_image: latest: Pulling from rizbihassan/cumulus-orca/sample-image
    docker.prototype_image: Status: Image is up to date for ghcr.io/rizbihassan/cumulus-orca/sample-image:latest
    docker.prototype_image: ghcr.io/rizbihassan/cumulus-orca/sample-image:latest
==> docker.prototype_image: Starting docker container...
    docker.prototype_image: Run command: docker run -v /Users/rhassan/.config/packer/tmp867764898:/packer-files -d -i -t --entrypoint=/bin/sh -- ghcr.io/rizbihassan/cumulus-orca/sample-image:latest
    docker.prototype_image: Container ID: edbdd851c37304379f241adbec0ca4aecc601c92f7f0ea60d928b3be7ed13224
==> docker.prototype_image: Using docker communicator to connect: 172.17.0.3
==> docker.prototype_image: Committing the container
    docker.prototype_image: Image ID: sha256:a68fd0613f72473f1f11bf81a87eedd308e8e0c7cc9d6568467ddd4e4df5c2aa
==> docker.prototype_image: Killing the container: edbdd851c37304379f241adbec0ca4aecc601c92f7f0ea60d928b3be7ed13224
==> docker.prototype_image: Running post-processor:  (type docker-tag)
    docker.prototype_image (docker-tag): Tagging image: sha256:a68fd0613f72473f1f11bf81a87eedd308e8e0c7cc9d6568467ddd4e4df5c2aa
    docker.prototype_image (docker-tag): Repository: <sensitive>:v1
==> docker.prototype_image: Running post-processor:  (type docker-push)
    docker.prototype_image (docker-push): Fetching ECR credentials...
    docker.prototype_image (docker-push): Logging in...
    docker.prototype_image (docker-push): Login Succeeded
    docker.prototype_image (docker-push): Pushing: <sensitive>:v1
    docker.prototype_image (docker-push): The push refers to repository [<sensitive>]
    docker.prototype_image (docker-push): f2f1289d6a81: Preparing
    docker.prototype_image (docker-push): 4dda5747d6f4: Preparing
    docker.prototype_image (docker-push): dbb5c5e8d571: Preparing
    docker.prototype_image (docker-push): 23f7bd114e4a: Preparing
    docker.prototype_image (docker-push): f2f1289d6a81: Pushed
    docker.prototype_image (docker-push): v1: digest: sha256:29c151d20a3d1e8e525e9af4e7292f0e99d8f8cd64d7bcba289ceafc77a2ea98 size: 1156
    docker.prototype_image (docker-push): Pushing: <sensitive>:v1
    docker.prototype_image (docker-push): The push refers to repository [<sensitive>]
    docker.prototype_image (docker-push): f2f1289d6a81: Preparing
    docker.prototype_image (docker-push): 4dda5747d6f4: Preparing
    docker.prototype_image (docker-push): dbb5c5e8d571: Preparing
    docker.prototype_image (docker-push): 23f7bd114e4a: Preparing
    docker.prototype_image (docker-push): v1: digest: sha256:29c151d20a3d1e8e525e9af4e7292f0e99d8f8cd64d7bcba289ceafc77a2ea98 size: 1156
    docker.prototype_image (docker-push): Logging out...
    docker.prototype_image (docker-push): Removing login credentials for 236859827343.dkr.ecr.us-west-2.amazonaws.com
Build 'docker.prototype_image' finished after 13 seconds 305 milliseconds.

==> Wait completed after 13 seconds 305 milliseconds

==> Builds finished. The artifacts of successful builds are:
--> docker.prototype_image: Imported Docker image: sha256:a68fd0613f72473f1f11bf81a87eedd308e8e0c7cc9d6568467ddd4e4df5c2aa
--> docker.prototype_image: Imported Docker image: <sensitive>:v1 with tags <sensitive>:v1

```

## Prototyping using github package

A prototype of a github package has been created by following the steps above and can be seen [here](https://github.com/users/rizbihassan/packages/container/package/cumulus-orca/sample-image). Note that a personal github account has been used for prototyping since it requires creating a personal access token first. The github repository containing image that was pulled from github repo above and pushed to ECR using packer can be found in the ECR console and is named `prototype_repo`.

## Future directions and recommendations
Using github packages for storing docker container looks promising, easy to use and free of cost. However, the user will need to create a personal access token having proper permissions first to login to github package and push images which could cause some delay. No token is necessary to pull public images from github repository. While Docker CLI can be used to build and tag the image, it is not the ideal way to push to ECR. The better and automated approach would be using Packer as shown above. Once ECR is deployed with terraform, Packer can then be used to pull and push the image to ECR.
Some cards that  could be written are as follows:
- Create a personal access token(PAT) for github container registry with proper permissions. Work with NASA admins.
- Push Docker images to github repository as needed.

##### References
- https://docs.github.com/en/packages/learn-github-packages/introduction-to-github-packages
- https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
- https://docs.github.com/en/packages/learn-github-packages/configuring-a-packages-access-control-and-visibility#visibility-and-access-permissions-for-container-images
- https://github.com/nasa/cumulus-orca/blob/develop/website/docs/developer/research/research-lambda-container.md
- https://www.packer.io/guides/hcl/variables
- https://thoughtmechanix.com/posts/8.01.2021_packer/