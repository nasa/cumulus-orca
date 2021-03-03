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
ORCA. The first method involves modifying files in the Cumulus `cumulus-tf`
deployment to deploy ORCA with Cumulus. The second method involves deploying ORCA
as a separate module after the Cumulus deployment.

The general steps to deploy ORCA are:

1. Configure the ORCA deployment using one of the two methods.
2. [Define the ORCA Ingest and Recovery workflows.](#define-the-orca-wokflows)
3. [Deploy ORCA using terraform.](#deploy-orca-with-terraform)
4. [Configure ORCA in the collection configuration of the running Cumulus instance.](#collection-configuration)


## Configuring the Cumulus Deployment to use ORCA

Follow the instructions for [deploying Cumulus](https://nasa.github.io/cumulus/docs/deployment/deployment-readme)
on the Cumulus website through the configuration of the Cumulus module `cumulus-tf`.

Prior to deploying the `cumulus-tf` module, the following files need to be
modified to deploy ORCA with Cumulus.
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
  postgres_user_pw               = var.postgres_user_pw
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
these variables can be found in the [variables section](#orca-variables).

- platform
- database_name
- database_port
- postgres_user_pw
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
be found in the [Cumulus variable definitions](https://github.com/nasa/cumulus/blob/master/tf-modules/cumulus/variables.tf).

- region
- prefix
- permissions_boundary_arn
- buckets

#### Required Values Retrieved from Other Modules

The following variables are set by retrieving output from other modules. This is
done so that the user does not have to lookup and set these variables after a
deployment. More information about these variables can be found in the
[Cumulus variable definitions](https://github.com/nasa/cumulus/blob/master/tf-modules/cumulus/variables.tf).

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
  default = "orca"
  type = string
  description = "Name of the ORCA database that contains state information."
}

variable "database_port" {
  default = "5432"
  type = string
  description = "Port the database listens on."
}

variable "postgres_user_pw" {
  type = string
  description = "postgres database user password."
}

variable "database_app_user" {
  default = "orca_user"
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
  description = "The location of the ddl dir that contains the sql to create the application database."
}

variable "lambda_timeout" {
  default = 300
  type = number
  description = "Lambda max time before a timeout error is thrown."
}

variable "restore_complete_filter_prefix" {
  default = ""
  type = string
  description = ""
}

variable "copy_retry_sleep_secs" {
  default = 0
  type = number
  description = "How many seconds to wait between retry calls to `copy_object`."
}

variable "default_tags" {
  type = object({ team = string, application = string })
  default = {
    team : "DR",
    application : "disaster-recovery"
  }
}
```


### Modifying `cumulus-tf/terraform.tfvars`

At the end of the `terrafor.tfvars` file, add the following code. Update the
variable values to the values for your particular environment.

:::note

The example below shows the minimum variables to set for the module and accepting
default values for the rest. The ORCA variables section provides additional
information on variables that can be set for the ORCA application. In some cases
additional variable definitions may be needed.

:::

```terraform
## ORCA Configuration
database_app_user_pw = "my-orca-application-user-password"
orca_default_bucket  = "orca-archive-primary"
postgres_user_pw     = "my-super-secret-database-owner-password"
```

Below describes the type of value expected for each variable.

* `database_app_user_pw` - the password for the application user
* `orca_default_bucket` - default S3 glacier bucket to use for ORCA data
* `postgres_user_pw` - password for the postgres user

Additional variable definitions can be found in the [ORCA variables](#orca-variables)
section of the document.

:::important

The cumulus bucket variable will have to be modified to include the
disaster recovery buckets with a *type* of **orca**. An example can be seen below.

```terraform
buckets = {
  orca_default = {
    name = "orca-archive-primary"
    type = "orca"
  },
  internal = {
    name = "orca-internal"
    type = "internal"
  },
  private = {
    name = "orca-private"
    type = "private"
  },
  protected = {
    name = "orca-protected"
    type = "protected"
  },
  public = {
    name = "orca-public"
    type = "public"
  }
}
```

:::


## Configuring ORCA as a Standalone Module with Cumulus

To deploy ORCA as a separate module, create an orca-tf folder in your Cumulus
deployment and perform the steps laid out below.


### Configure Terraform

The state of the Terraform deployment is stored in S3. In the following
examples, it will be assumed that state is being stored in a bucket called
`dr-tf-state`. You can also use an existing bucket, if desired.

#### Create the state bucket:

```shell
aws s3api create-bucket \
  --bucket dr-tf-state \
  --create-bucket-configuration LocationConstraint=us-west-2
```
:::note

The `--create-bucket-configuration` line is only necessary if you are creating your bucket outside of `us-east-1`.

:::

In order to help prevent loss of state information, it is recommended that
versioning be enabled on the state bucket:

```shell
$ aws s3api put-bucket-versioning \
    --bucket dr-tf-state \
    --versioning-configuration Status=Enabled
```


#### Create the locks table:

Terraform uses a lock stored in DynamoDB in order to prevent multiple
simultaneous updates. In the following examples, that table will be called
`dr-tf-locks`.

:::important

The `--billing-mode` option was recently added to the AWS CLI. You
may need to upgrade your version of the AWS CLI if you get an error about
provisioned throughput when creating the table.

:::

```shell
$ aws dynamodb create-table \
    --table-name dr-tf-locks \
    --attribute-definitions AttributeName=LockID,AttributeType=S \
    --key-schema AttributeName=LockID,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST
```

#### Configure and deploy the `main` root module

Create a `terraform.tf` file, substituting the appropriate values for `bucket`
and `dynamodb_table` in the `orca-tf` directory. This tells Terraform where to
store its remote state. See the example below for the information to add to the
file.

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


### Create the `terraform.tfvars` file.

Create a `terraform.tfvars` file in the `orca-tf` directory. This is where you
will place input variables to Terraform. A complete list of variables is in the
[ORCA variables](#orca-variables) section. In addition, the following Cumulus
variables must be set.

- buckets
- ecs_cluster_instance_subnet_ids
- permissions_boundary_arn
- prefix
- region
- vpc_id
- workflow_config


### Create the `variables.tf` file.

Create a `variables.tf` file in the `orca-tf` directory. Copy the code below and
add to the file.

```terraform
## Required Cumulus Variables Definitions
variable "buckets" {
  type    = map(object({ name = string, type = string }))
  default = {}
}

variable "permissions_boundary_arn" {
  type    = string
  default = null
}

variable "prefix" {
  type = string
}

variable "region" {
  type    = string
  default = "us-west-2"
}

variable "ecs_cluster_instance_subnet_ids" {
  type    = list(string)
  default = []
}

variable "vpc_id" {
  type = string
}


## ORCA Variables Definitions

variable "platform" {
  default = "AWS"
  type = string
  description = "Indicates if running locally (onprem) or in AWS (AWS)."
}

variable "database_name" {
  default = "orca"
  type = string
  description = "Name of the ORCA database that contains state information."
}

variable "database_port" {
  default = "5432"
  type = string
  description = "Port the database listens on."
}

variable "postgres_user_pw" {
  type = string
  description = "postgres database user password."
}

variable "database_app_user" {
  default = "orca_user"
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
  description = "The location of the ddl dir that contains the sql to create the application database."
}

variable "lambda_timeout" {
  default = 300
  type = number
  description = "Lambda max time before a timeout error is thrown."
}

variable "orca_default_bucket" {
  type        = string
  description = "Name of the default ORCA archive S3 Glacier bucket."
}

variable "restore_complete_filter_prefix" {
  default = ""
  type = string
  description = ""
}

variable "copy_retry_sleep_secs" {
  default = 0
  type = number
  description = "How many seconds to wait between retry calls to `copy_object`."
}

variable "default_tags" {
  type = object({ team = string, application = string })
  default = {
    team : "DR",
    application : "disaster-recovery"
  }
}
```


### Modifying `cumulus-tf/terraform.tfvars`

At the end of the `terrafor.tfvars` file, add the following code. Update the
variable values to the values for your particular environment.

:::note

The example below shows the minimum variables to set for the module and accepting
default values for the rest. The ORCA variables section provides additional


### Create the `main.tf` file.

Create the `main.tf` file in the `orca-tf` director. Copy the code block below
into the main.tf file for ORCA.


:::important Only change the value of source

Only change the value of `source` in the code example below to point to the
proper ORCA version. The ORCA version is specifed right after *download* in the
URL path to the release. In the example above the release being used is v2.0.1.

:::

```terraform
provider "aws" {
  version = "~> 2.13"
  region  = var.region
  profile = var.profile
}

# ORCA Module
module "orca" {
  source                         = "https://github.com/nasa/cumulus-orca/releases/download/v2.0.1/cumulus-orca-terraform.zip//modules/orca"
  vpc_id                         = var.vpc_id
  subnet_ids                     = var.ecs_cluster_instance_subnet_ids
  workflow_config                = var.workflow_config
  region                         = var.region
  prefix                         = var.prefix
  permissions_boundary_arn       = var.permissions_boundary_arn
  buckets                        = var.buckets
  platform                       = var.platform
  database_name                  = var.database_name
  database_port                  = var.database_port
  postgres_user_pw               = var.postgres_user_pw
  database_app_user              = var.database_app_user
  database_app_user_pw           = var.database_app_user_pw
  drop_database                  = var.drop_database
  ddl_dir                        = var.ddl_dir
  lambda_timeout                 = var.lambda_timeout
  restore_complete_filter_prefix = var.restore_complete_filter_prefix
  copy_retry_sleep_secs          = var.copy_retry_sleep_secs
  default_tags                   = var.default_tags
  orca_default_bucket            = var.orca_default_bucket
}
```


## Define the ORCA Wokflows

### Add the Copy To Glacier Step to an Ingest Workflow

Navigate to `cumulus-tf/ingest_granule_workflow.tf` then add the following step
anywhere after the MoveGranuleStep step being sure to change the MoveGranuleStep's
`"Next"` parameter equal to "CopyToGlacier".

:::important

Adjust the `"Next"` step in the example below to point to the proper step in
the ingest workflow.

:::

```
"CopyToGlacier":{
   "Parameters":{
      "cma":{
         "event.$":"$",
         "task_config":{
            "buckets":"{$.meta.buckets}",
            "provider": "{$.meta.provider}",
            "collection":"{$.meta.collection}",
            "granules": "{$.meta.processed_granules}",
            "files_config": "{$.meta.collection.files}"
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
   "Retry": [
      {
        "ErrorEquals": [
           "States.ALL"
        ],
        "IntervalSeconds": 2,
        "MaxAttempts": 3,
        "BackoffRate": 2
      }
   ],
   "Next":"WorkflowSucceeded"
},
```


### Modify the Recovery Workflow (*OPTIONAL*)

Copy the workflow from `workflows/workflows.yml.dr` into your Cumulus workflow.
Modify as needed.


## ORCA Variables

**Required:**
* `ngap_subnets` - NGAP Subnets (array)
* `vpc_id` - ID of VPC to place resources in - recommended that this be a private VPC (or at least one with restricted access).
* `glacier_bucket` - Bucket with Glacier policy
* `public_bucket` - Bucket with public permissions (Cumulus public bucket)
* `private_bucket` - Bucket with private permissions (Cumulus private bucket)
* `internal_bucket` - Analogous to the Cumulus internal bucket
* `protected_bucket` - Analogous to the Cumulus protected bucket
* `permissions_boundary_arn` - Permission Boundary Arn (Policy) for NGAP compliance
* `postgres_user_pw` - password for the postgres user
* `database_name` - orca
* `database_app_user` - orca_user
* `database_app_user_pw` - the password for the application user
* `orca_default_bucket` - default S3 glacier bucket ORCA uses

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




## Deploy ORCA with Terraform

In the proper module directory, initialize and apply changes using the commands
below.

1. Run `terraform init`.
2. Run `terraform plan` #optional, but allows you to preview the deploy.
3. Run `terraform apply`.

This commands above will create and deploy ORCA. To delete the created objects,
run `terraform destroy`.


## Collection Configuration

To configure a collection to enable ORCA, add the line
`"granuleRecoveryWorkflow": "DrRecoveryWorkflow"` to the collection configuration
as seen below. Optionally, you can exclude files by adding values to an
`"exclue_file_type"` variable. For more information, see the documentation on the
[`copy_to_glacier` task](https://github.com/nasa/cumulus-orca/tree/master/tasks/copy_to_glacier).

```json
{
  "queriedAt": "2019-11-07T22:49:46.842Z",
  "name": "L0A_HR_RAW",
  "version": "1",
  "sampleFileName": "L0A_HR_RAW_product_0001-of-0420.h5",
  "dataType": "L0A_HR_RAW",
  "granuleIdExtraction": "^(.*)((\\.cmr\\.json)|(\\.iso\\.xml)|(\\.tar\\.gz)|(\\.h5)|(\\.h5\\.mp))$",
  "reportToEms": true,
  "granuleId": "^.*$",
  "provider_path": "L0A_HR_RAW/",
  "meta": {
    "granuleRecoveryWorkflow": "DrRecoveryWorkflow",
    "exclue_file_type": [".cmr", ".xml", ".met"]
  },
  ...
}
```
## Enable `Recover Granule` Button

To enable the `Recover Granule` button on the Cumulus Dashboard (available at github.com/nasa/cumulus-dashboard), 
set the environment variable `ENABLE_RECOVERY=true`.

Here is an sample command to run the Cumulus Dashboard locally.

```bash
APIROOT=https://uttm5y1jcj.execute-api.us-west-2.amazonaws.com:8000/dev ENABLE_RECOVERY=true npm run serve
```

