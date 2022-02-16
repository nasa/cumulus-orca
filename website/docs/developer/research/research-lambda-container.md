---
id: research-lambda-container
title: Using Lambda functions as container research Notes
description: Research Notes on 
---

## Overview

Lambda functions can now be deployed as container images using Docker instead of zip files. This research webpage discusses how lambda functions can be prototyped as container and its pros and cons.

## Elastic Container Registry (ECR)

AWS Elastic Container Registry(ECR) is used to store container images for lambdas and is fully managed by AWS. It hosts the images in a highly available and scalable architecture, allowing developers to reliably deploy containers for their applications. See this [link](https://aws.amazon.com/ecr/) for additional information on ECR. Currently, you have to use ECR to store container images for lambdas as it does not support other storage options such as Github, Dockerhub, etc.

## Pros and Cons of using container for lambdas

### Pros
- Defining runtime environment in a container image gives developers more control over their environment compared to what they get with predefined runtimes and zipping dependencies. 
- you can now package and deploy Lambda functions as container images of up to 10 GB in size compared to only 250MB in case of lambda deployment package size. 
- preferable for data-heavy or dependency-heavy applications.
- The Lambda service provides a variety of base image options with pre-installed runtimes that will be patched and maintained by AWS.
- Once deployed, containerized lambdas have no additional cost compared to zipped lambdas except the cost of using ECR repository.

### Cons
- Container support requires your Lambda function code point to an ECR Repo URI which means that repo also has to be maintained.
- need additional work to create the Dockerfile, tag and push the image to ECR repo.
- Need additional work for deleting older images under the ECR repository.

:::warning
Currently NGAP only allows `private` ECR repository which could bring possible risk and challenges in using a public repository for storing container image for lambdas. More discussion is needed with NGAP on allowing a public repository.
:::

## New configuration for lambda container
There are a few configuration that needs to be added if the lambda is deployed from docker image.
- Architecture- This  determines the type of computer processor that Lambda uses to run the function. Lambda provides a choice of instruction set architectures which is either `arm64` or `x86_64`. The `arm64` architecture offer lower cost per Gb/s compared to the other one. Check this [link](https://docs.aws.amazon.com/lambda/latest/dg/foundation-arch.html?icmpid=docs_lambda_help) for additional information.
- Image configuration- These are values that can be used to override the container image settings for `ENTRYPOINT`, `CMD`, `WORKDIR` and `ENV`.

```
  ENTRYPOINT – Specifies the absolute path of the entry point to the application.

  CMD – Specifies parameters that you want to pass in with ENTRYPOINT.

  WORKDIR – Specifies the absolute path of the working directory.

  ENV – Specifies an environment variable for the Lambda function.
```
- Image URI- The location of the container image to use for your function.


## Creating a prototype

Creating or updating the function is done by building a Docker image, uploading the new version to ECR and deploying/updating the Lambda function to point to the newly uploaded image using terraform. Docker CLI has been used to build, tag and push the container image to ECR.

The steps for prototyping lambda container are as follows:
- Create or locate an AWS ECR repository for storing the Docker images. 
- Create the Dockerfile and then build, tag and push the image to the above ECR repository.
- Update terraform configuration of the lambda function to deploy it as container.

:::warning
Currently NGAP only allows developers to create a `private` ECR repository which was used here to create the prototype. Using a `public` ECR repository will need approval from NGAP first which could bring security concerns.
:::

Details on creating the prototype are shown below:

1. Create an ECR repository from AWS CLI if needed as shown. Check [here](https://docs.aws.amazon.com/AmazonECR/latest/userguide/getting-started-cli.html#cli-create-repository) for additional details on this.

```bash
aws ecr create-repository \
    --repository-name <YOUR_REPOSITORY_NAME>
```

2. Create a project directory. Under that directory, add  your script (`test.py` in this case) and `requirements.txt`to install any dependencies. Then create a `Dockerfile` that creates the image. 

:::note
  You should use the AWS lambda base image specific to the language you are using to write the lambda function.
:::

An example of a Dockerfile used for prototying a lambda having `test.py` file is shown below.

```yaml
FROM public.ecr.aws/lambda/python:3.8

# Copy function code
COPY test.py ${LAMBDA_TASK_ROOT}

# Install the function's dependencies using file requirements.txt
# from your project folder.

COPY requirements.txt  .
RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "test.hambda_handler" ]

```

3. The next steps are to build, tag and push the image to the ECR repo. You can build a new image named `prototype-lambda-image` in this case using:

```bash
docker build -t prototype-lambda-image .
```
Once build is successful, tag the image

```bash
docker tag prototype-lambda-image:<IMAGE_TAG> <YOUR_ECR_REPO_URI>:<IMAGE_TAG>
```
Next, login to the ECR repo using:

```bash
aws ecr get-login-password --region <YOUR_REGION> | docker login --username AWS --password-stdin <YOUR_AWS_ACCOUNT_ID>.dkr.ecr.<YOUR_REGION>.amazonaws.com
```
Check this [link](https://docs.aws.amazon.com/AmazonECR/latest/userguide/docker-push-ecr-image.html) for additional information on pushing image to ECR using Docker CLI.

Finally, push the image to ECR using:

```bash
docker push <YOUR_ECR_REPO_URI>:<IMAGE_TAG>
```

4. The next step is to deploy the lambda using terraform. Use the following example code to deploy the lambda container:

```terraform

resource "aws_lambda_function" "prototype_lambda" {
  image_uri     = "<YOUR_ECR_REPO_URI>:<IMAGE_TAG>"  # repo and tag
  package_type  = "Image"
  function_name = "prototype-lambda"
  role          = "<YOUR_IAM_ROLE_ARN>"
  image_config {
    command = ["test.lambda_handler"]
  }
}
```
Using the steps above, a prototype has been created in NGAP AWS sandbox account which can be seen under the lambda function console. The lambda function is named as `prototype-lambda-container` and uses the `test:latest` private ECR repo image.


## Future directions
Currently, the only option to store the Docker image for lambda containers is AWS ECR repository. Github package could be an option to store the image but in order to deploy the lambda, the image has to be stored into an ECR.

A few possible discussion items:
- Discuss with NGAP team if the docker images can be stored in a public ECR repo.
- If github packages are supported to store and deploy the lambda, then we have to contact NASA github admins to enable this feature in our repository.

Based on this research, it looks like using lambda as containers is possible when using a private ECR to store the image which is not ideal in our case. There are some concerns which include:

- Discussing with NGAP on allowing to store container images on a public ECR repository. If that is not possible, another option is to have an ECR setup for the end user via terraform and build images. This will require additional work.
- If github package is used to store the image, deploying lambda as container will be an issue since the terraform only supports deploying the image from ECR. Moreover, this feature for the github repository has to be approved by NASA Github admins.

If the above issues are solved, then implementing lambda as container is recommended. One way to use private ECR repo is to use a script or terraform code if possible that will create the ECR repo and then build, tag and push the container image to that repo. One that is done, update the terraform lambda modules and deploy the lambda. An additional [card](https://bugs.earthdata.nasa.gov/browse/ORCA-375) has been created to look into this way.

##### References
- https://aws.amazon.com/blogs/aws/new-for-aws-lambda-container-image-support/
- https://aws.amazon.com/blogs/compute/optimizing-lambda-functions-packaged-as-container-images/
- https://dashbird.io/blog/deploying-aws-lambda-with-docker/
- https://docs.aws.amazon.com/lambda/latest/dg/images-create.html
- https://docs.aws.amazon.com/lambda/latest/dg/python-image.html
- https://acloudguru.com/blog/engineering/packaging-aws-lambda-functions-as-container-images