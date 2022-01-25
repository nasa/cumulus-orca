---
id: research-lambda-container
title: Using Lambda functions as container research Notes
description: Research Notes on 
---

## Overview

Lambda functions can now be deployed as container images using Docker instead of zip files. This research webpage discusses how lambda functions can be prototyped as container and its pros and cons.

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
Currently NGAP does not support using ECR repository to store images which could bring possible risk and challenges to using containers for lambdas.
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

AWS Elastic Container Registry(ECR) is used to store container images for lambdas and is fully managed by AWS. It hosts the images in a highly available and scalable architecture, allowing developers to reliably deploy containers for their applications. See this [link](https://aws.amazon.com/ecr/) for additional information on ECR.
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

2. Create a project directory. Under that directory, add  your script (`test.py` in this case) and `requirements.txt`to install any dependencies. Then  create a `Dockerfile` that creates the image. An example of a Dockerfile used for prototying a lambda having `test.py` file is shown  below.

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
aws ecr get-login-password --region <YOUR_REGION> | docker login --username AWS --password-stdin <YOUR_PASSWORD>
```
Password can be seen by logging in to AWS console ECR repo and clicking on the `Push commands` button. This will show details of the docker CLI commands needed to build, tag and push the image to ECR. Check this [link](https://docs.aws.amazon.com/AmazonECR/latest/userguide/docker-push-ecr-image.html) for additional information on pushing image to ECR.

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
Currently, the only option to store the Docker image for lambda containers is AWS ECR repository. If github is supported in the future, then using that approach will be a good direction to go.

A few possible discussion items:
- Discuss with NGAP team if the docker images can be stored in a public ECR repo.
- Check if github can be used to store the image (currently I have not seen any example online)

##### References
- https://aws.amazon.com/blogs/aws/new-for-aws-lambda-container-image-support/
- https://aws.amazon.com/blogs/compute/optimizing-lambda-functions-packaged-as-container-images/
- https://dashbird.io/blog/deploying-aws-lambda-with-docker/
- https://docs.aws.amazon.com/lambda/latest/dg/images-create.html
- https://docs.aws.amazon.com/lambda/latest/dg/python-image.html
- https://acloudguru.com/blog/engineering/packaging-aws-lambda-functions-as-container-images
