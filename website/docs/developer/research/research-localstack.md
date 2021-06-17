---
id: research-localstack
title: Localstack Research Notes
description: Research Notes on Localstack.
---

## Overview

[Localstack](https://github.com/localstack/localstack) is a method of simulating an AWS environment locally.
This can be used to bypass the requirement of a remote sandbox environment, making testing easier.


### Implementation Details
- Some features and not present, and some are locked behind the [Pro Version](https://localstack.cloud/#pricing).
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
[Commandeer](https://www.getcommandeer.com) could theoretically be used to provide a UI, but make sure it is approved by IT.
:::
- [AWS CLI](https://aws.amazon.com/cli/) and [botocore3](https://github.com/boto/botocore) can both contact Localstack if properly [configured](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html).
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


### Setup details

-	Make sure you have Docker desktop installed in your laptop and approved by EROS helpdesk.
- There are two ways to install localstack- either directly using docker command or by running a docker-compose.yaml file. The recommended way is by using docker compose since all changes will stay in one config file that can be changed according to use cases.
#### Docker compose

A sample docker-compose.yml file is shown below: 

        version: "3.8"

        services:
          localstack:
            container_name: localstack-container
            image: localstack/localstack
            ports:
              - "53:53"
              - "443:443"
              - "4566:4566"
              - "4571:4571"
            environment:
              - DEBUG=1
              - DATA_DIR=/tmp/localstack/data # Local directory for saving persistent data
              - DEFAULT_REGION=us-east-1
              - LAMBDA_EXECUTOR=local #running lambda from local dir
              - LAMBDA_REMOTE_DOCKER=0
              - DOCKER_HOST=unix:///var/run/docker.sock
              - HOST_TMP_FOLDER=/tmp/localstack
            volumes:
              - "/var/run/docker.sock:/var/run/docker.sock"

From your windows cmd, run the following command to start localstack: `docker compose up`

        C:\Users\rhassan\localstack-test>docker compose up
        [+] Running 2/1
         - Network localstack-test_default  Created                                                                                                                                                                   0.0s
         - Container localstack-container   Created                                                                                                                                                                   0.1s
        Attaching to localstack-container
        localstack-container  | Waiting for all LocalStack services to be ready
        localstack-container  | 2021-06-16 16:40:27,632 CRIT Supervisor is running as root.  Privileges were not dropped because no user is specified in the config file.  If you intend to run as root, you can set user=root in the config file to avoid this message.
        localstack-container  | 2021-06-16 16:40:27,635 INFO supervisord started with pid 14
        localstack-container  | 2021-06-16 16:40:28,638 INFO spawned: 'dashboard' with pid 20
        localstack-container  | 2021-06-16 16:40:28,640 INFO spawned: 'infra' with pid 21
        localstack-container  | 2021-06-16 16:40:28,645 INFO success: dashboard entered RUNNING state, process has stayed up for > than 0 seconds (startsecs)
        localstack-container  | 2021-06-16 16:40:28,645 INFO exited: dashboard (exit status 0; expected)
        localstack-container  | (. .venv/bin/activate; exec bin/localstack start --host)
        localstack-container  | Starting local dev environment. CTRL-C to quit.
        localstack-container  | 2021-06-16 16:40:30,317 INFO success: infra entered RUNNING state, process has stayed up for > than 1 seconds (startsecs)
        localstack-container  |
        localstack-container  | LocalStack version: 0.12.12
        localstack-container  | LocalStack build date: 2021-06-15
        localstack-container  | LocalStack build git hash: 48ac6ea8
        localstack-container  |
        localstack-container  | 2021-06-16T16:40:33:DEBUG:bootstrap.py: Loading plugins - scope "services", module "localstack": <function register_localstack_plugins at 0x7fd684268050>
        localstack-container  | Starting edge router (https port 4566)...
        localstack-container  | Starting mock ACM service on http port 4566 ...
        localstack-container  | 2021-06-16T16:40:33:INFO:localstack.multiserver: Starting multi API server process on port 36131
        localstack-container  | [2021-06-16 16:40:33 +0000] [22] [INFO] Running on https://0.0.0.0:4566 (CTRL + C to quit)
        localstack-container  | 2021-06-16T16:40:33:INFO:hypercorn.error: Running on https://0.0.0.0:4566 (CTRL + C to quit)
        localstack-container  | [2021-06-16 16:40:33 +0000] [22] [INFO] Running on http://0.0.0.0:36131 (CTRL + C to quit)
        localstack-container  | 2021-06-16T16:40:33:INFO:hypercorn.error: Running on http://0.0.0.0:36131 (CTRL + C to quit)
        localstack-container  | Waiting for all LocalStack services to be ready
        localstack-container  | Starting mock API Gateway service on http port 4566 ...
        localstack-container  | Starting mock CloudFormation service on http port 4566 ...
        localstack-container  | Starting mock CloudWatch service on http port 4566 ...
        localstack-container  | Starting mock DynamoDB service on http port 4566 ...
        localstack-container  | Starting mock DynamoDB Streams service on http port 4566 ...
        localstack-container  | Starting mock EC2 service on http port 4566 ...
        localstack-container  | Starting mock ES service on http port 4566 ...
        localstack-container  | Starting mock Firehose service on http port 4566 ...
        localstack-container  | Starting mock IAM service on http port 4566 ...
        localstack-container  | Starting mock STS service on http port 4566 ...
        localstack-container  | Starting mock Kinesis service on http port 4566 ...
        localstack-container  | Initializing DynamoDB Local with the following configuration:
        localstack-container  | Port:   52091
        localstack-container  | InMemory:       false
        localstack-container  | DbPath: /tmp/localstack/data/dynamodb
        localstack-container  | SharedDb:       false
        localstack-container  | shouldDelayTransientStatuses:   false
        localstack-container  | CorsParams:     *
        localstack-container  | Starting mock KMS service on http port 4566 ...
        localstack-container  |
        localstack-container  | INFO[2021-06-16 16:40:34.915] Local KMS 3.9.1 (4e5eb289efb23f9059ae4b1f9896bad6c9a499f2)
        localstack-container  | INFO[2021-06-16 16:40:34.936] No file found at path /init/seed.yaml; skipping seeding.
        localstack-container  | INFO[2021-06-16 16:40:34.937] Data will be stored in /tmp/localstack/data
        localstack-container  | INFO[2021-06-16 16:40:34.937] Local KMS started on 0.0.0.0:42519
        localstack-container  | Listening at http://:::40789
        localstack-container  | 2021-06-16 16:40:34,603:API:  * Running on all addresses.
        localstack-container  |    WARNING: This is a development server. Do not use it in a production deployment.
        localstack-container  | 2021-06-16 16:40:34,603:API:  * Running on http://172.21.0.2:39023/ (Press CTRL+C to quit)
        localstack-container  | Starting mock Lambda service on http port 4566 ...
        localstack-container  | Starting mock CloudWatch Logs service on http port 4566 ...
        localstack-container  | Starting mock Redshift service on http port 4566 ...
        localstack-container  | Starting mock Route53 service on http port 4566 ...

Localstack is now running in docker. To verify that the services are running, check the link http://localhost:4566/ should show a status of "running".
Open the docker desktop and click on the container's CLI to open the container.
Install the AWS CLI to run CLI commands in the docker container.

    pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org awscli-local

This prevents the need for specifying --endpoint-url everytime aws cli command is run. The container is now ready to test AWS services locally.

### Examples of AWS services deployed using localstack
Some examples of CLI commands and their corresponding outputs are shown below.
#### API gateway
  Command: `awslocal apigateway create-rest-api --name test-api`

     Response: 
        {
            "id": "0zqyew47ie",
            "name": "test-api",
            "createdDate": 1623862127,
            "version": "V1",
            "binaryMediaTypes": [],
            "apiKeySource": "HEADER",
            "endpointConfiguration": {
                "types": [
                    "EDGE"
                ]
            },
            "tags": {},
            "disableExecuteApiEndpoint": false
        }
        
  `PARENT_RESOURCE_ID=$(awslocal apigateway get-resources --rest-api-id 0zqyew47ie --query 'items[?path==`/`].id' --output text)`
  
  `awslocal apigateway create-resource --rest-api-id 0zqyew47ie --parent-id  $PARENT_RESOURCE_ID --path-part "{test}"`

     Response: 
    {
        "id": "7z17qim7fw",
        "parentId": "d22pls3twh",
        "pathPart": "{test}",
        "path": "/{test}"
}
        
        

#### Lambda function
`awslocal lambda create-function --function-name test-function --runtime python3.7 --zip-file fileb://test.zip --handler test.lambda_handler --role test`

     Response: 
    {
        "FunctionName": "test-function",
        "FunctionArn": "arn:aws:lambda:us-east-1:000000000000:function:test-function",
        "Runtime": "python3.7",
        "Role": "test",
        "Handler": "test.lambda_handler",
        "CodeSize": 217,
        "Description": "",
        "Timeout": 3,
        "LastModified": "2021-06-16T18:32:27.753+0000",
        "CodeSha256": "TxccBpGFdCdDKjbXygowwHMdUE0yPX+1U2eu6Vd+rsk=",
        "Version": "$LATEST",
        "VpcConfig": {},
        "TracingConfig": {
            "Mode": "PassThrough"
        },
        "RevisionId": "fb286270-3b68-4cae-9237-8efac356bee3",
        "State": "Active",
        "LastUpdateStatus": "Successful",
        "PackageType": "Zip"
    }
#### SQS

`awslocal sqs create-queue --queue-name test-queue`

     Response: 
    {
        "QueueUrl": "http://localhost:4566/000000000000/test-queue"
    }
`awslocal sqs send-message --queue-url http://localhost:4566/000000000000/test-queue --message-body "test message." --delay-seconds 0`

     Response: 
    {
      "MD5OfMessageBody": "5cbd04aaf0430ff7fac38ebd11b72083",
      "MessageId": "0d4d8a75-276d-9687-6604-975cc0a84c68"
  }
`awslocal sqs receive-message --queue-url http://localhost:4566/000000000000/test-queue --attribute-names All --message-attribute-names All`

     Response: 
    {
        "Messages": [
            {
                "MessageId": "0d4d8a75-276d-9687-6604-975cc0a84c68",
                "ReceiptHandle": "ljwfjwrrlolejmrqcqbsrrxajygjsbkleesnyxtvwlffoikfstreipeutydtzhxosvjicazswakagyfhcxbrbpxxofkzsdbgjlofnpbmfxxtztrsmjkhkecfbqvdxnyotoujibxdavaiewtthscexnvplkmfrryisowurnxrymfzvyozubidbhsms",
                "MD5OfBody": "5cbd04aaf0430ff7fac38ebd11b72083",
                "Body": "test message.",
                "Attributes": {
                    "SenderId": "AIDAIT2UOQQY3AUEKVGXU",
                    "SentTimestamp": "1623871655817",
                    "ApproximateReceiveCount": "1",
                    "ApproximateFirstReceiveTimestamp": "1623871770221"
                }
            }
        ]
    }


#### Secerts manager
`awslocal secretsmanager create-secret --name localstack-secret`

      Response: 
    {
        "ARN": "arn:aws:secretsmanager:us-east-1:000000000000:secret:localstack-secret-PAnuzB",
        "Name": "localstack-secret",
        "VersionId": "8c6c77a1-6400-441a-b8f7-730abec4b9d5"
    }


### Deploying AWS resources using terraform and localstack

Terraform can also be used to deploy and test AWS resources locally using localstack. Make sure to have Terraform installed on your local machine. An example of deploying services like lambda, API gateway, SQS, S3 and SNS is shown below:

    provider "aws" {
      region = "us-east-1"
      access_key = "123"
      secret_key = "xyz"
      skip_credentials_validation = true
      skip_requesting_account_id = true
      skip_metadata_api_check = true
      s3_force_path_style = true
      endpoints {
        s3 = "http://localhost:4566"
        sqs = "http://localhost:4566"
        apigateway = "http://localhost:4566"
        lambda = "http://localhost:4566"
        sns = "http://localhost:4566"
        secretsmanager = "http://localhost:4566"
        iam = "http://localhost:4566"
      }
    }
    #-------------------------------- resources-------------------
    resource "aws_s3_bucket" "localstack-test-bucket" {
      bucket = "localstack-test-bucket"
    }
    resource "aws_sqs_queue" "localstack-test-sqs" {
      name                      = "localstack-test-sqs"
      tags = {
        Environment = "dev"
      }
    }

    resource "aws_api_gateway_rest_api" "localstack-rest-api" {
      name = "localstack-rest-api"
    }

    resource "aws_api_gateway_resource" "localstack-rest-api-resource" {
      parent_id   = aws_api_gateway_rest_api.localstack-rest-api.root_resource_id
      path_part   = "test"
      rest_api_id = aws_api_gateway_rest_api.localstack-rest-api.id
    }

    resource "aws_lambda_function" "test_lambda" {
      filename      = "test.zip"
      function_name = "localstack-lambda"
      role          = aws_iam_role.localstack-role.arn
      handler       = "test.lambda_handler"
      source_code_hash = filebase64sha256("test.zip")
      runtime = "python3.7"
    }

    resource "aws_sns_topic" "localstack-sns-topic" {
      name = "localstack-sns-topic"
    }

    resource "aws_secretsmanager_secret" "localstack-secret" {
      name                    = "localstack-secret"
      recovery_window_in_days = 0
    }

    data "aws_iam_policy_document" "localstack_policy" {
      statement {
        actions   = ["*"]
        effect    = "Allow"
      }
    }

    resource "aws_iam_role" "localstack-role" {
      name               = "localstack-role"
      assume_role_policy = data.aws_iam_policy_document.localstack_policy.json
    }

Here is the output after running `terraform apply`

    Output:
    Plan: 6 to add, 0 to change, 0 to destroy.
    Do you want to perform these actions?
      Terraform will perform the actions described above.
      Only 'yes' will be accepted to approve.

      Enter a value: yes

    aws_api_gateway_rest_api.localstack-rest-api: Creating...
    aws_secretsmanager_secret.localstack-secret: Creating...
    aws_iam_role.localstack-role: Creating...
    aws_sqs_queue.localstack-test-sqs: Creating...
    aws_sns_topic.localstack-sns-topic: Creating...
    aws_s3_bucket.localstack-test-bucket: Creating...
    aws_sns_topic.localstack-sns-topic: Creation complete after 0s [id=arn:aws:sns:us-east-1:000000000000:localstack-sns-topic]
    aws_api_gateway_rest_api.localstack-rest-api: Creation complete after 0s [id=kxg64u2jdv]
    aws_api_gateway_resource.localstack-rest-api-resource: Creating...
    aws_secretsmanager_secret.localstack-secret: Creation complete after 0s [id=arn:aws:secretsmanager:us-east-1:000000000000:secret:localstack-secret-iIRbKa]
    aws_iam_role.localstack-role: Creation complete after 0s [id=localstack-role]
    aws_sqs_queue.localstack-test-sqs: Creation complete after 0s [id=http://localhost:4566/000000000000/localstack-test-sqs]
    aws_lambda_function.test_lambda: Creating...
    aws_api_gateway_resource.localstack-rest-api-resource: Creation complete after 0s [id=b97isejc8z]
    aws_s3_bucket.localstack-test-bucket: Creation complete after 0s [id=localstack-test-bucket]
    aws_lambda_function.test_lambda: Creation complete after 6s [id=localstack-lambda]

    Apply complete! Resources: 8 added, 0 changed, 0 destroyed.


### IDE for Localstack
- Currently there is an IDE named [Commandeer](https://getcommandeer.com/) that can be used to maintain localstack environments but requires to buy a premium version to use. This could be something to look into in the future if we plan to buy a premium version.

### Known Limitations
- While commonly used AWS services are present, some more uncommon services are not.
- Is not a total replacement for AWS Sandbox testing.
  - Security checks are not present.
  - Is, by its nature, a simulation.

### Future Direction
- Localstack in a Docker container would be an excellent place to deploy ORCA for local testing.
  - Could also be used for automated large testing in Bamboo if deployment scripting can be added.

#### Sources
- Meeting with Aafaque
- https://github.com/localstack/localstack
- [AppEEARS' Docker Implementation](https://git.cr.usgs.gov/LPDA/appeears/-/blob/feature/rds-setup/deployment/terraform/dev/main.tf)