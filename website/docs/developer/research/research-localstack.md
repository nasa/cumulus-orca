---
id: research-localstack
title: Localstack Research Notes
description: Research Notes on Localstack.
---

## Overview

[Localstack](https://github.com/localstack/localstack) is a method of simulating an AWS environment locally.
This can be used to bypass the requirement of a remote sandbox environment, making testing easier.


### Implemenration Details
- Some features and not present, and smore are locked behind the [Pro Version](https://localstack.cloud/#pricing).
  - RDS is not present, but testing can be done with a local database.
- Can be run in a Docker container using Docker Compose.
- Can be run directly via a docker command.
:::tip
  ```
  docker run --rm -p 4566:4566 -p 4571:4571 localstack/localstack
  ```
:::
:::tip
Docker's localhost can be accessed on the parent machine at http://host.docker.internal
:::
- Most services are accessible on port 4566, and starting the image lists them individually.
- Data is not persisted between runs of the image.
  - S3 Bucket contents can be preserved by adding the following to [docker-compose.yaml](https://git.cr.usgs.gov/LPDA/appeears/-/blob/feature/rds-setup/deployment/localstack/docker-compose.yaml)
    ```
    DATA_DIR=/tmp/localstack/data
    volumes: localstack-col:/tmp/localstack
    ```
- There currently is no page for services running in localstack.
:::tip
[Commandeer](getcommandeer.com) could theoretically be used to provide a UI, but make sure it is approved by IT.
:::
- [AWS CLI](https://aws.amazon.com/cli/) and [botocore3](https://github.com/boto/botocore) can both contact Localstack if properly (configured)[https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html].
  - AWS credentials are not checked, and can therefore be dummy values.
  - Most commands work, including those for creating, modifying, and listing services. For example:
    - Localstack In Docker:
    ```commandline
    aws --endpoint-url=http://host.docker.internal:4566 s3 ls
    ```
    - Localstack Running Locally:
    ```commandline
    aws --endpoint-url=http://localhost:4566 s3 ls
    ```
  - Presently we are unsure if an AWS CLI profile pointing to Localstack precludes the need for '--endpoint-url'.
- [Terraform](https://www.terraform.io/) can be used to deploy to Localstack.
  - Since credentials are not checked, 'access_key' and 'secret_key' can be dummy values.
  - Since full permissions are granted be default, 'lambda-vpc-role' can also be a dummy value.
  - Terraform must be informed of Localstack's ports for services.
    ```
    provider "aws"{
      endpoints {
        s3 = "http://host.docker.internal:4566"
      }
    }
    ```
    [Full example here.](https://git.cr.usgs.gov/LPDA/appeears/-/blob/feature/rds-setup/deployment/terraform/dev/main.tf)

### Known Limitations
- While commonly used AWS services are present, some more uncommon services are not.
- Is not a total replacement for AWS Sandbox testing.
  - Security checks are not present.
  - Is, by its nature, a simulation.

#### Sources
- Meeting with Aafaque
- https://github.com/localstack/localstack
- [AppEEARS' Docker Implementation](https://git.cr.usgs.gov/LPDA/appeears/-/blob/feature/rds-setup/deployment/terraform/dev/main.tf)