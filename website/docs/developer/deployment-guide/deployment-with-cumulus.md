---
id: deployment-with-cumulus
title: Deploying ORCA with Cumulus
description: Provides developer information for ORCA code deployment with Cumulus.
---

:::important

Prior to following this document, make sure that your [deployment environment](setting-up-deployment-environment.md)
is setup and an [ORCA archive glacier bucket](creating-orca-glacier-bucket.md) is
created.

:::

ORCA is meant to be deployed with Cumulus. There are two methods for deploying
ORCA. The first method involves modifying files in the Cumulus deployment to
deploy ORCA with Cumulus. The second method involves downloading the ORCA deployment
and deploying ORCA after the Cumulus deployment.


## Deploying ORCA using the Cumulus Deployment

Follow the instructions for [deploying Cumulus](https://nasa.github.io/cumulus/docs/deployment/deployment-readme)
on the Cumulus website up to the deployment of the Cumulus module `cumulus-tf`.

Prior to deploying the cumulus module, the following files need to be modified.
- main.tf
- variables.tf
- terraform.tfvars

### Modifying `cumulus-tf/main.tf`

At the end of the `main.tf` file, add the following code and update the source
variable.

:::important Only change the value of source

Only change the value of `source` in the code example below to point to the
proper ORCA version. The ORCA version is specifed right after *download* in the
URL path to the release. In the example above the release being used is v2.0.1.

:::

```terraform
# ORCA Module
module "orca" {
  source                         = "https://github.com/nasa/cumulus-orca/releases/download/v2.0.1/cumulus-orca-terraform.zip//modules/orca"
  vpc_id                         = module.ngap.ngap_vpc.id
  subnet_ids                     = module.ngap.ngap_subnets_ids
  workflow_config                = module.cumulus.workflow_config
  region                         = var.region
  prefix                         = var.prefix
  permissions_boundary_arn       = var.permissions_boundary_arn
  buckets                        = var.buckets
  platform                       = var.platform
  database_name                  = var.database_name
  database_port                  = var.database_port
  database_user_pw               = var.database_user_pw
  database_app_user              = var.database_app_user
  database_app_user_pw           = var.database_app_user_pw
  drop_database                  = var.drop_database
  ddl_dir                        = var.ddl_dir
  lambda_timeout                 = var.lambda_timeout
  restore_complete_filter_prefix = var.restore_complete_filter_prefix
  copy_retry_sleep_secs          = var.copy_retry_sleep_secs
  default_tags                   = var.default_tags
}
```

#### Required Values Unique to the ORCA Module

The following variables are unique to the ORCA module. More information about
these variables can be found in the variables section.

- platform
- database_name
- database_port
- database_user_pw
- database_app_user
- database_app_user_pw
- drop_database
- ddl_dir
- lambda_timeout
- restore_complete_filter_prefix
- copy_retry_sleep_secs
- default_tags

#### Required Values Retrieved from Cumulus Variables

The following variables are set as part of your Cumulus deployment. ORCA utilizes
these same variables for the build. More information about these variables can
be found in the variables section.

- region
- prefix
- permissions_boundary_arn
- buckets

#### Required Values Retrieved from Other Modules

The following variables are set by retrieving output from other modules. This is
done so that the user does not have to lookup and set these variables after a
deployment. More information about these variables can be found in the variables
section.

- vpc_id
- subnet_ids
- workflow_config


### Modifying `cumulus-tf/variables.tf`

At the end of the `variables.tf` file, add the following code.

```terraform
## ORCA Variables Definitions

variable "platform" {
  default = "AWS"
  type = string
  description = "Indicates if running locally (onprem) or in AWS (AWS)."
}

variable "database_name" {
  default = "disaster_recovery"
  type = string
  description = "Name of the ORCA database that contains state information."
}

variable "database_port" {
  default = "5432"
  type = string
  description = "Port the database listens on."
}

variable "database_user_pw" {
  type = string
  description = "postgres database user password."
}

variable "database_app_user" {
  default = "druser"
  type = string
  description = "ORCA application database user name."
}

variable "database_app_user_pw" {
  type = string
  description = "ORCA application database user password."
}

variable "drop_database" {
  default = "False"
  type = string
  description = "Tells ORCA to drop the database on deployments."
}

variable "ddl_dir" {
  default = "ddl/"
  type = string
}

variable "lambda_timeout" {
  default = 300
  type = number
}

variable "restore_complete_filter_prefix" {
  default = ""
  type = string
}

variable "copy_retry_sleep_secs" {
  default = 0
  type = number
}

variable "default_tags" {
  type = object({ team = string, application = string })
  default = {
    team : "DR",
    application : "disaster-recovery"
  }
}


### NEED to ask on these


variable "ngap_sgs" {
  default = []
}

variable "profile" {
  default = "default"
}

variable "restore_expire_days" {
  default = 5
}

variable "restore_request_retries" {
  default = 3
}

variable "restore_retry_sleep_secs" {
  default = 0
}

variable "restore_retrieval_type" {
  default = "Standard"
}

variable "copy_retries" {
  default = 3
}





```
```
# Variables specific to ORCA
variable "database_user_pw" {
  type = string
}

variable "database_name" {
  type = string
}

variable "database_app_user" {
  type = string
}

variable "database_app_user_pw" {
  type = string
}
```



### Modifying `cumulus-tf/terraform.tfvars`

At the end of the `terrafor.tfvars` file, add the following code.

**terraform.tfvars Addition**
```terraform
## ORCA Configuration
subnet_ids           = ["subnet-0d3416cbfaaf3508e", "subnet-0b7acca747c16c895"] # Possibly change variable name to line up with Cumulus TF ECS_Cluster_Instance_Subnet_IDs
database_port        = "5432"
database_name        = "disaster_recovery"
database_app_user    = "druser"
database_app_user_pw = "my_app-user-pw"
database_user_pw     = "super secur3 p4ssw0rd"
postgres_user_pw     = "super secur3 p4ssw0rd"
ddl_dir              = "ddl/"
drop_database        = "False"
platform             = "AWS"

## This is needed if we deploy outside of Cumulus as a standalone.
#workflow_config = {
#  sf_event_sqs_to_db_records_sqs_queue_arn = module.cumulus.archive.sf_event_sqs_to_db_records_sqs_queue_arn
#  sf_semaphore_down_lambda_function_arn    = module.cumulus.ingest.sf_semaphore_down_lambda_function_arn
#  state_machine_role_arn                   = module.cumulus.ingest.step_role_arn
#  sqs_message_remover_lambda_function_arn  = module.cumulus.ingest.sqs_message_remover_lambda_function_arn
#}
restore_complete_filter_prefix = ""
```

Below describes the type of value expected for each variable.


## Deploying ORCA after Deploying Cumulus



- Assumptions about OU setup, access, etc.
- Setup environment
- Create Glacier S3 bucket
- Followed Cumulus directions


ORCA Deployment

Changes to files
- main.tf
- variables.tf
- variables.tfvars

Terraform deploy
- terraform init
- terraform apply

aws ssm start-session --target i-0650c326450164b73 --document-name AWS-StartPortForwardingSession --parameters portNumber=22,localPortNumber=6868 &
Ssh

ENABLE_RECOVERY=true APIROOT=https://acryfz64bj.execute-api.us-west-2.amazonaws.com/dev/ npm run serve

## Configure the Terraform backend

The state of the Terraform deployment is stored in S3. In the following
examples, it will be assumed that state is being stored in a bucket called
`dr-tf-state`. You can also use an existing bucket, if desired.

Create the state bucket:

```shell
aws s3api create-bucket --bucket dr-tf-state --create-bucket-configuration LocationConstraint=us-west-2
```
**Note:** The `--create-bucket-configuration` line is only necessary if you are creating your bucket outside of `us-east-1`.

In order to help prevent loss of state information, it is recommended that
versioning be enabled on the state bucket:

```shell
$ aws s3api put-bucket-versioning \
    --bucket dr-tf-state \
    --versioning-configuration Status=Enabled
```

Terraform uses a lock stored in DynamoDB in order to prevent multiple
simultaneous updates. In the following examples, that table will be called
`dr-tf-locks`.

Create the locks table:

⚠️ **Note:** The `--billing-mode` option was recently added to the AWS CLI. You
may need to upgrade your version of the AWS CLI if you get an error about
provisioned throughput when creating the table.

```shell
$ aws dynamodb create-table \
    --table-name dr-tf-locks \
    --attribute-definitions AttributeName=LockID,AttributeType=S \
    --key-schema AttributeName=LockID,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST
```

## Configure and deploy the `main` root module

These steps should be executed in the root directory of the repo.

Create a `terraform.tf` file, substituting the appropriate values for `bucket`
and `dynamodb_table`. This tells Terraform where to store its
remote state.

**terraform.tf**

```
terraform {
  backend "s3" {
    region         = "us-west-2"
    bucket         = "dr-tf-state"
    key            = "terraform.tfstate"
    dynamodb_table = "dr-tf-locks"
  }
}
```

## Variables
First, run a `mv terraform.tfvars.example terraform.tfvars` to get a template `terraform.tfvars` in your working directory. This is where you will place input variables to Terraform.

**Necessary:**
* `ngap_subnets` - NGAP Subnets (array)
* `vpc_id` - ID of VPC to place resources in - recommended that this be a private VPC (or at least one with restricted access).
* `glacier_bucket` - Bucket with Glacier policy
* `public_bucket` - Bucket with public permissions (Cumulus public bucket)
* `private_bucket` - Bucket with private permissions (Cumulus private bucket)
* `internal_bucket` - Analogous to the Cumulus internal bucket 
* `protected_bucket` - Analogous to the Cumulus protected bucket
* `permissions_boundary_arn` - Permission Boundary Arn (Policy) for NGAP compliance
* `postgres_user_pw` - password for the postgres user
* `database_name` - disaster_recovery
* `database_app_user` - druser 
* `database_app_user_pw` - the password for the application user

**Optional:**
* `prefix` - Prefix that will be pre-pended to resource names created by terraform. 
  Defaults to `dr`.
* `profile` - AWS CLI Profile (configured via `aws configure`) to use. 
  Defaults to `default`.
* `region` - Your AWS region. 
  Defaults to `us-west-2`.
* `restore_expire_days` - How many days to restore a file for. 
  Defaults to 5.
* `restore_request_retries` - How many times to retry a restore request to Glacier. 
  Defaults to 3.
* `restore_retry_sleep_secs` - How many seconds to wait between retry calls to `restore_object`. 
  Defaults to 3.
* `restore_retrieval_type` -  the Tier for the restore request. Valid values are 'Standard'|'Bulk'|'Expedited'. 
  Defaults to `Standard`. Understand the costs associated with the tiers before modifying.
* `copy_retries` - How many times to retry a copy request from the restore location to the archive location. 
  Defaults to 3.
* `copy_retry_sleep_secs` - How many seconds to wait between retry calls to `copy_object`. 
  Defaults to 0.
* `ddl_dir` - the location of the ddl dir that contains the sql to create the application database. 
  Defaults to 'ddl/'.
* `drop_database` - Whether to drop the database if it exists (True), or keep it (False). 
  Defaults to False.
* `database_port` - the port for the postgres database. 
  Defaults to '5432'.
* `platform` - indicates if running locally (onprem) or in AWS (AWS). 
  Defaults to 'AWS'.

## Deploying with Terraform
Run `terraform init`.
Run `terraform plan` #optional, but allows you to preview the deploy.
Run `terraform apply`.

This will deploy ORCA.

## Delete Terraform stack
If you want to remove it:
```
terraform destroy
```

## Integrating with Cumulus
Integrate ORCA with Cumulus to be able to recover a granule from the Cumulus Dashboard.

### Define the ORCA workflow (Cumulus < v1.15)

Copy the workflow from `workflows/workflows.yml.dr` into your Cumulus workflow.

Set the values of these environment variables to the ARN for the 
{prefix}-extract-filepaths-for-granule and {prefix}-request-files lambdas,
respectively:
```
DR_EXTRACT_LAMBDA_ARN=arn:aws:lambda:us-west-2:012345678912:function:dr_extract_filepaths_for_granule

DR_REQUEST_LAMBDA_ARN=arn:aws:lambda:us-west-2:012345678912:function:dr_request_files
```

Add an `aws` provider to `main.tf`:

```
provider "aws" {
  version = "~> 2.13"
  region  = var.region
  profile = var.profile
}
```

### Integrating ORCA With Cumulus >= v1.15

#### Adding a ORCA module to the Cumulus deployment

Navigate to `cumulus-tf/main.tf` within your Cumulus deployment directory and add the following module:
```
module "orca" {
  source = "https://github.com/ghrcdaac/operational-recovery-cloud-archive/releases/download/1.0.2/orca-1.0.2.zip"

  prefix = var.prefix
  subnet_ids = module.ngap.ngap_subnets_ids
  database_port = "5432"
  database_user_pw = var.database_user_pw
  database_name = var.database_name
  database_app_user = var.database_app_user
  database_app_user_pw = var.database_app_user_pw
  ddl_dir = "ddl/"
  drop_database = "False"
  platform = "AWS"
  lambda_timeout = 300
  restore_complete_filter_prefix = ""
  vpc_id = module.ngap.ngap_vpc.id
  copy_retry_sleep_secs = 2
  permissions_boundary_arn = var.permissions_boundary_arn
  buckets = var.buckets
  workflow_config = module.cumulus.workflow_config
  region = var.region
}
```

*Note*: This above snippet assumes that you've configured your Cumulus deployment. More information on that process can be found in their [documentation](https://nasa.github.io/cumulus/docs/deployment/deployment-readme#configure-and-deploy-the-cumulus-tf-root-module)

#### Add necessary variables (unique to ORCA) to the Cumulus TF configuration

To support this module, you'll have to add the following values to your `cumulus-tf/variables.tf` file:
```
# Variables specific to ORCA
variable "database_user_pw" {
  type = string
}

variable "database_name" {
  type = string
}

variable "database_app_user" {
  type = string
}

variable "database_app_user_pw" {
  type = string
}
```

The values corresponding to these variables must be set in your `cumulus-tf/terraform.tfvars` file, but note that many of these variables are actually hardcoded at the time of updating this README

#### Adding the Copy To Glacier Step to the Ingest Workflow
Navigate to `cumulus-tf/ingest_granule_workflow.tf` then add the following step after the PostToCMR step being sure to change the PostToCMR's "Next" parameter equal to "CopyToGlacier"
```
"CopyToGlacier":{
         "Parameters":{
            "cma":{
               "event.$":"$",
               "task_config":{
                  "bucket":"{$.meta.buckets.internal.name}",
                  "buckets":"{$.meta.buckets}",
                  "distribution_endpoint":"{$.meta.distribution_endpoint}",
                  "files_config":"{$.meta.collection.files}",
                  "fileStagingDir":"{$.meta.collection.url_path}",
                  "granuleIdExtraction":"{$.meta.collection.granuleIdExtraction}",
                  "collection":"{$.meta.collection}",
                  "cumulus_message":{
                     "input":"{[$.payload.granules[*].files[*].filename]}",
                     "outputs":[
                        {
                           "source":"{$}",
                           "destination":"{$.payload}"
                        }
                     ]
                  }
               }
            }
         },
         "Type":"Task",
         "Resource":"${module.orca.copy_to_glacier_lambda_arn}",
         "Catch":[
            {
               "ErrorEquals":[
                  "States.ALL"
               ],
               "ResultPath":"$.exception",
               "Next":"WorkflowFailed"
            }
         ],
         "Retry":[
            {
               "ErrorEquals":[
                  "States.ALL"
               ],
               "IntervalSeconds":2,
               "MaxAttempts":3
            }
         ],
         "Next":"WorkflowSucceeded"
      },
```

### Collection configuration
To configure a collection to enable ORCA, add the line
`"granuleRecoveryWorkflow": "DrRecoveryWorkflow"` to the collection configuration:
```
{
  "queriedAt": "2019-11-07T22:49:46.842Z",
  "name": "L0A_HR_RAW",
  "version": "1",
  "sampleFileName": "L0A_HR_RAW_product_0001-of-0420.h5",
  "dataType": "L0A_HR_RAW",
  "granuleIdExtraction": "^(.*)((\\.cmr\\.json)|(\\.iso\\.xml)|(\\.tar\\.gz)|(\\.h5)|(\\.h5\\.mp))$",
  "reportToEms": true,
  "createdAt": 1561749178492,
  "granuleId": "^.*$",
  "provider_path": "L0A_HR_RAW/",
  "meta": {
    "response-endpoint": "arn:aws:sns:us-west-2:012345678912:providerResponseSNS",
    "granuleRecoveryWorkflow": "DrRecoveryWorkflow"
  },
  "files": [
    {
```
### Enable `Recover Granule` button

To enable the `Recover Granule` button on the Cumulus Dashboard (available at github.com/nasa/cumulus-dashboard), 
set the environment variable `ENABLE_RECOVERY=true`.

Here is an example command to run the Cumulus Dashboard locally:
```
  APIROOT=https://uttm5y1jcj.execute-api.us-west-2.amazonaws.com:8000/dev ENABLE_RECOVERY=true npm run serve
```

## Release Documentation:

Information about how to create an ORCA release can be found here
