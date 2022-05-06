---
id: research-pushing-docker-image
title: Notes on pushing and deploying docker images.
description: Research notes on pushing Docker images for end users
---

## Github Packages

[Github packages](https://docs.github.com/en/packages/learn-github-packages/introduction-to-github-packages) looks like a good platform to store public or private docker images. GitHub Packages usage is free for public packages. For private packages, each account on GitHub receives a certain amount of free storage and data transfer, depending on the product used with the account. Any usage beyond the included amounts is controlled by spending limits.

The steps to push a docker image to github are shown below.

- Create a DockerFile that will create the image. 

```yaml
#This is a sample image
FROM alpine:3.4
RUN apk update
RUN apk add vim 
CMD [“echo”,”Image created”]
```
- Build the image using `docker build -t sample-image .`. 
- Once the image is there, the next step is to push to github. However, the user first will need to authenticate with github using a `personal access token`. See details [here](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) on how to create the token. 
:::important
Proper permissions need to be granted to the token such as `write_package` in order to push to github.
:::

- Once the token is created, sign in to the github container registry using:
```bash
export CR_PAT=YOUR_PERSONAL_TOKEN
echo $CR_PAT | docker login ghcr.io -u <GITHUB_USERNAME> --password-stdin
```
Replace `<USERNAME>` with your github username. It will show `Login Succeeded` upon success.

- Tag the docker image using the following format. Note that the format must be `ghcr.io/<GITHUB_USERNAME>/<image_name>`
```bash
docker tag <image_name> ghcr.io/<GITHUB_USERNAME>/<image_name>
# example 
docker tag sample-image ghcr.io/rizbihassan/sample-image
```
- Finally push the image
```bash
docker push ghcr.io/rizbihassan/sample-image
```
:::note
Make sure your username matches with your github username or else it will show error while pushing the image.
:::

Once the image is pushed, it  can be view under `Packages` section in github. However, the image will be private by default. Click on the `package settings` page to change from private to public if needed.

## Prototyping using github package

A prototype of a github package has been created by following the steps above and can be seen [here](https://github.com/users/rizbihassan/packages/container/package/sample-image). Note that a personal github account has been used for prototyping since it requires creating a personal access token first.

## Future directions and recommendations
Using github packages for storing docker container looks promising, easy to use and free of cost. However, the user will need to create a personal access token having proper permissions first to login to github package and push/pull images which could cause some delay. 
Some cards that  can be written are as follows:
- Create a personal access token(PAT) for github container registry with proper permissions.
- Push Docker images to github registry as needed.

##### References
- https://docs.github.com/en/packages/learn-github-packages/introduction-to-github-packages
- https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
- https://docs.github.com/en/packages/learn-github-packages/configuring-a-packages-access-control-and-visibility#visibility-and-access-permissions-for-container-images