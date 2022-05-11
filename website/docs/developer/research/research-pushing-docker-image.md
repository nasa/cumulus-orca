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

- Tag the docker image using the following format. Note that the format must be `ghcr.io/<GITHUB_USERNAME>/<image_name>:<image_tag>`
```bash
docker tag <image_name> ghcr.io/<GITHUB_USERNAME>/<image_name>:<image_tag>
# example 
docker tag sample-image ghcr.io/nasa/sample-image:latest
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

## Prototyping using github package

A prototype of a github package has been created by following the steps above and can be seen [here](https://github.com/users/rizbihassan/packages/container/package/sample-image). Note that a personal github account has been used for prototyping since it requires creating a personal access token first. The github repository containing image that was pulled from github repo above can be found in the ECR console and is named `prototype_repo`.

## Future directions and recommendations
Using github packages for storing docker container looks promising, easy to use and free of cost. However, the user will need to create a personal access token having proper permissions first to login to github package and push images which could cause some delay. No token is necessary to pull public images from github repository. Other technologies to build a docker image include packer but in this case docker CLI seems to be sufficient and simple for building the image.
Some cards that  could be written are as follows:
- Create a personal access token(PAT) for github container registry with proper permissions. Work with NASA admins.
- Push Docker images to github repository as needed.

##### References
- https://docs.github.com/en/packages/learn-github-packages/introduction-to-github-packages
- https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
- https://docs.github.com/en/packages/learn-github-packages/configuring-a-packages-access-control-and-visibility#visibility-and-access-permissions-for-container-images
- https://github.com/nasa/cumulus-orca/blob/develop/website/docs/developer/research/research-lambda-container.md