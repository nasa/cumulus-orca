---
id: deployment-with-cumulus
title: Deploying ORCA with Cumulus
description: Provides developer information for ORCA code deployment with Cumulus.
---

:::important

Prior to following this document, make sure that your [deployment environment](setting-up-deployment-environment.mdx)
is setup and an [ORCA archive glacier bucket](creating-orca-glacier-bucket.md) is
created.

:::

ORCA is meant to be deployed with Cumulus. To deploy ORCA add and/or modify the
files in the Cumulus `cumulus-tf` deployment.

The general steps to deploy and use ORCA are:

1. [Configure the ORCA deployment.](#configuring-the-orca-deployment)
2. [Define the ORCA Ingest and Recovery workflows.](#define-the-orca-wokflows)
3. [Deploy ORCA using terraform.](#deploy-orca-with-terraform)
4. [Configure ORCA in the collection configuration of the running Cumulus instance.](#collection-configuration)


## Configuring the ORCA Deployment

Follow the instructions for [deploying Cumulus](https://nasa.github.io/cumulus/docs/deployment/deployment-readme)
on the Cumulus website through the configuration of the Cumulus module `cumulus-tf`.

Prior to deploying the `cumulus-tf` module, the following files need to be added
and/or modified to deploy ORCA with Cumulus.
- orca.tf
- orca_variables.tf
- terraform.tfvars
- main.tf


### Creating `cumulus-tf/orca.tf`

Create the `orca.tf` file in the `cumulus-tf` directory and copy the code below
into the new `orca.tf` file. Update the source variable with the preferred
ORCA version.

:::important Only change the value of source

Only change the value of `source` in the code example below to point to the
proper ORCA version. The ORCA version is specified right after *download* in the
URL path to the release. In the example below the release being used is v3.0.2.

:::

:::tip Deploying a local version

If you wish to deploy code cloned locally from [Github](https://github.com/nasa/cumulus-orca) instead of a release zip, run
`./bin/build_tasks.sh`. This will crawl the `tasks` directory and build a `.zip` file (currently by just `zipping` all python files and dependencies) in each of it's sub-directories. You may then set `source` to the root folder of your cloned Orca repository.

:::

```terraform
## ORCA Module
## =============================================================================
module "orca" {
  source = "https://github.com/nasa/cumulus-orca/releases/download/v3.0.2/cumulus-orca-terraform.zip"
  ## --------------------------
  ## Cumulus Variables
  ## --------------------------
  ## REQUIRED
  buckets                  = var.buckets
  lambda_subnet_ids        = var.lambda_subnet_ids
  permissions_boundary_arn = var.permissions_boundary_arn
  prefix                   = var.prefix
  system_bucket            = var.system_bucket
  vpc_id                   = var.vpc_id
  workflow_config          = module.cumulus.workflow_config

  ## OPTIONAL
  tags        = var.tags

  ## --------------------------
  ## ORCA Variables
  ## --------------------------
  ## REQUIRED
  db_admin_password     = var.db_admin_password
  db_host_endpoint      = var.db_host_endpoint
  db_user_password      = var.db_user_password
  orca_default_bucket   = var.orca_default_bucket
  orca_reports_bucket   = var.orca_reports_bucket
  rds_security_group_id = var.rds_security_group_id
  dlq_subscription_email = var.dlq_subscription_email

  ## OPTIONAL
  # db_admin_username                                    = "postgres"
  # default_multipart_chunksize_mb                       = 250
  # metadata_queue_message_retention_time                = 777600
  # orca_ingest_lambda_memory_size                       = 2240
  # orca_ingest_lambda_timeout                           = 600
  # orca_reconciliation_lambda_memory_size               = 128
  # orca_reconciliation_lambda_timeout                   = 720
  # orca_recovery_buckets                                = []
  # orca_recovery_complete_filter_prefix                 = ""
  # orca_recovery_expiration_days                        = 5
  # orca_recovery_lambda_memory_size                     = 128
  # orca_recovery_lambda_timeout                         = 720
  # orca_recovery_retry_limit                            = 3
  # orca_recovery_retry_interval                         = 1
  # orca_recovery_retry_backoff                          = 2
  # s3_inventory_queue_message_retention_time_seconds    = 432000
  # sqs_delay_time_seconds                               = 0
  # sqs_maximum_message_size                             = 262144
  # staged_recovery_queue_message_retention_time_seconds = 432000
  # status_update_queue_message_retention_time_seconds   = 777600

}
```

#### Required Values Unique to the ORCA Module

The following variables are unique to the ORCA module and required to be set by
the user. More information about these required variables, as well as the
optional variables can be found in the [variables section](#orca-variables).

- db_admin_password
- orca_default_bucket
- orca_reports_bucket
- db_user_password
- db_host_endpoint
- rds_security_group_id
- dlq_subscription_email

#### Required Values Retrieved from Cumulus Variables

The following variables are set as part of your Cumulus deployment and are
required by the ORCA module. More information about setting these variables can
be found in the [Cumulus variable definitions](https://github.com/nasa/cumulus/blob/master/tf-modules/cumulus/variables.tf).
The variables must be set with the proper values in the `terraform.tfvars` file.

- buckets
- lambda_subnet_ids
- permissions_boundary_arn
- prefix
- system_bucket
- vpc_id

:::note Optional Cumulus Values

The `tags` value automatically adds a *Deployment* tag like the Cumulus
deployment.

:::

#### Required Values Retrieved from Other Modules

The following variables are set by retrieving output from other modules. This is
done so that the user does not have to lookup and set these variables after a
deployment. More information about these variables can be found in the
[Cumulus variable definitions](https://github.com/nasa/cumulus/blob/master/tf-modules/cumulus/variables.tf).

- workflow_config - Retrieved from the cumulus module in `main.tf`.


### Creating `cumulus-tf/orca_variables.tf`

In the `cumulus-tf` directory create the `orca_variables.tf` file. Copy the
contents below into the file so that the ORCA unique variables are defined.
For more information on the variables, see the [variables section](#orca-variables).

```terraform
## Variables unique to ORCA
## REQUIRED
variable "db_admin_password" {
  description = "Password for RDS database administrator authentication"
  type        = string
}

variable "db_user_password" {
  description = "Password for RDS database user authentication"
  type        = string
}

variable "db_host_endpoint" {
  type        = string
  description = "Database host endpoint to connect to."
}

variable "orca_default_bucket" {
  type        = string
  description = "Default ORCA S3 Glacier bucket to use."
}

variable "orca_reports_bucket" {
  type        = string
  description = "ORCA bucket to use for storing s3 reports."
}

variable "rds_security_group_id" {
  type        = string
  description = "Cumulus' RDS Security Group's ID."
}

variable "dlq_subscription_email" {
  type        = string
  description = "The email to notify users when messages are received in dead letter SQS queue due to restore failure. Sends one email until the dead letter queue is emptied."
}
```


### Modifying `cumulus-tf/terraform.tfvars`

At the end of the `terraform.tfvars` file, add the following code. Update the
required and optional variable values to the values needed for your particular
environment.

:::note

The example below shows the minimum variables to set for the module and accepting
default values for all of the optional items. The [ORCA variables section](#orca-variables)
provides additional information on variables that can be set for the ORCA application.

:::

```terraform
## =============================================================================
## ORCA Variables
## =============================================================================

## REQUIRED TO BE SET
## -----------------------------------------------------------------------------

## ORCA application database user password.
db_user_password = "my-super-secret-orca-application-user-password"

## Default ORCA S3 Glacier bucket to use
orca_default_bucket = "orca-archive-primary"

## ORCA bucket to use for storing s3 reports
orca_reports_bucket = "orca-reports"

## PostgreSQL database (root) user password
db_admin_password = "my-super-secret-database-owner-password"

## PostgreSQL database host endpoint to connect to.
db_host_endpoint = "aws.postgresrds.host"

## Cumulus' RDS Security Group's ID.
rds_security_group_id = "sg-01234567890123456"

## Dead letter queue SNS topic subscription email.
dlq_subscription_email = "test@email.com"
```

Below describes the type of value expected for each variable.

* `db_user_password` (string) - the password for the application user.
* `orca_default_bucket` (string) - Default S3 glacier bucket to use for ORCA data.
* `orca_reports_bucket` (string) - ORCA bucket to use for storing s3 reports.
* `db_admin_password` (string) - password for the postgres user.
* `db_host_endpoint`(string) - Database host endpoint to connect to.
* `rds_security_group_id`(string) - Cumulus' RDS Security Group's ID. Output as `security_group_id` from the rds-cluster deployment.
* `dlq_subscription_email`(string) - "The email to notify users when messages are received in dead letter SQS queue due to restore failure. Sends one email until the dead letter queue is emptied."

Additional variable definitions can be found in the [ORCA variables](#orca-variables)
section of the document.


:::important

The cumulus `buckets` variable will have to be modified to include the
disaster recovery buckets with a *type* of **orca**. An example can be seen below.
This addition is required for ORCA to have the proper bucket permissions to
work with Cumulus.

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

### Modifying cumulus-tf/main.tf

To use the Orca API, add the following line within the Cumulus module:

```
module "cumulus" {

  ...

  orca_api_uri = module.orca.orca_api_deployment_invoke_url
  
  ...
  
}
```

## Define the ORCA Workflows

The ORCA Ingest Workflows follows each step listed below. Adding the Move
Granule Step and Add the Copy To Glacier Step are detailed in their respective
sections.

**ORCA Ingest Workflow**
  SyncGranule
  FilesToGranuleStep
  MoveGranuleStep
  CopyToGlacier

### Add the Move Granule Step to an Ingest Workflow

Navigate to `cumulus-tf/ingest_granule_workflow.tf` then add the following 
step anywhere after the FilesToGranuleStep step being sure to change the 
FilesToGranuleStep's `"Next"` parameter equal to "MoveGranuleStep".

:::important

Adjust the `"Next"` step in the example below to point to the proper step in
the ingest workflow.

:::

```json
"MoveGranuleStep": {
      "Parameters": {
        "cma": {
          "event.$": "$",
          "task_config": {
            "bucket": "{$.meta.buckets.internal.name}",
            "buckets": "{$.meta.buckets}",
            "distribution_endpoint": "{$.meta.distribution_endpoint}",
            "collection": "{$.meta.collection}",
            "duplicateHandling": "{$.meta.collection.duplicateHandling}",
            "s3MultipartChunksizeMb": "{$.meta.collection.meta.s3MultipartChunksizeMb}",
            "cumulus_message": {
              "outputs": [
                { "source": "{$}", "destination": "{$.payload}" },
                { "source": "{$.granules}", "destination": "{$.meta.processed_granules}" }
              ]
            }
          }
        }
      },
      "Type": "Task",
      "Resource": "${move_granules_task_arn}",
      "Retry": [
        {
          "ErrorEquals": [
            "Lambda.ServiceException",
            "Lambda.AWSLambdaException",
            "Lambda.SdkClientException"
          ],
          "IntervalSeconds": 2,
          "MaxAttempts": 6,
          "BackoffRate": 2
        }
      ],
      "Catch": [
        {
          "ErrorEquals": [
            "States.ALL"
          ],
          "ResultPath": "$.exception",
          "Next": "WorkflowFailed"
        }
      ],
```


### Add the Copy To Glacier Step to an Ingest Workflow

Navigate to `cumulus-tf/ingest_granule_workflow.tf` then add the following step
anywhere after the MoveGranuleStep step being sure to change the MoveGranuleStep's
`"Next"` parameter equal to "CopyToGlacier".

:::important

Adjust the `"Next"` step in the example below to point to the proper step in
the ingest workflow.

:::


```json
"CopyToGlacier":{
  "Parameters":{
    "cma":{
      "event.$":"$",
      "task_config": {
        "excludeFileTypes": "{$.meta.collection.meta.excludeFileTypes}",
        "s3MultipartChunksizeMb": "{$.meta.collection.meta.s3MultipartChunksizeMb}",
        "providerId": "{$.meta.provider.id}",
        "providerName": "{$.meta.provider.name}",
        "executionId": "{$.cumulus_meta.execution_name}",
        "collectionShortname": "{$.meta.collection.name}",
        "collectionVersion": "{$.meta.collection.version}",
        "orcaDefaultBucketOverride": "{$.meta.collection.meta.orcaDefaultBucketOverride}"
      }
    }
  }
},
  "Type":"Task",
  "Resource":"module.orca.orca_lambda_copy_to_glacier_arn",
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
See the copy_to_glacier json schema [configuration file](https://github.com/nasa/cumulus-orca/blob/master/tasks/copy_to_glacier/schemas/config.json), [input file](https://github.com/nasa/cumulus-orca/blob/master/tasks/copy_to_glacier/schemas/input.json)  and [output file](https://github.com/nasa/cumulus-orca/blob/master/tasks/copy_to_glacier/schemas/output.json) for more information.

### Modify the Recovery Workflow (*OPTIONAL*)

It is not recommended to modify the ORCA Recovery Workflow. The workflow JSON
file is located in the `modules/workflows/OrcaRecoveryWorkflow` of the repository.
The workflow file name is `orca_recover_workflow.asl.json`. To change the
behavior of the workflow, it is recommended to modify or replace the
`copy_files_to_archive` lambda.


### Workflow Failures

Failures within ORCA break through to the Cumulus workflow they are a part
of. More information on addressing workflow failures can be found on the
ORCA [Best Practices](developer/../../development-guide/code/best-practices.mdx) 
page.

## ORCA Variables

The following sections detail the variables used by the ORCA module.

### Required Variables

The following variables are required for the ORCA module and must be set to valid
values.

#### Cumulus Required Variables

The following variables should be present already in the `cumulus-tf/terraform.tfvars`
file. The variables must be set with proper values for your environment in the
`cumulus-tf/terraform.tfvars` file.

| Variable                   | Definition                                                                                                                                   | Example Value      |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- | ------------------ |
| `buckets`                  | Mapping of all S3 buckets used by Cumulus and ORCA that contains a S3 `name` and `type`. Buckets with `type` of **orca** and **orca-reports** are required.     | `buckets = { orca_default = { name = "PREFIX-orca-primary", type = "orca", ...}, orca_reports = "PREFIX-orca-reports", type = "orca-reports", ...}` |
| `lambda_subnet_ids`        | A list of subnets that the Lambda's and the database have access to for working with Cumulus.                                                | ["subnet-12345", "subnet-abc123"] |
| `permissions_boundary_arn` | AWS ARN value of the permission boundary for the VPC account.                                                                                | "arn:aws:iam::1234567890:policy/NGAPShRoleBoundary" |
| `prefix`                   | Prefix that will be pre-pended to resource names created by terraform.                                                                       | "daac-sndbx" |
| `system_bucket`            | Cumulus system bucket used to store internal files and configurations for deployments.                                                       | "PREFIX-internal" |
| `vpc_id`                   | ID of VPC to place resources in - recommended that this be a private VPC (or at least one with restricted access).                           | "vpc-abc123456789" |
| `workflow_config`          | Configuration object with ARNs for workflow integration (Role ARN for executing workflows and Lambda ARNs to trigger on workflow execution). | module.cumulus.workflow_config |


#### ORCA Required Variables

The following variables should be present in the `cumulus-tf/orca_variables.tf`
file. The variables must be set with proper values for your environment in the
`cumulus-tf/terraform.tfvars` file.

| Variable                 | Definition                                              |              Example Value                                  |
| ------------------------ | --------------------------------------------------------| ------------------------------------------------------------|
| `db_admin_password`      | Password for RDS database administrator authentication  | "My_Sup3rS3cr3t_admin_Passw0rd"                             |
| `db_host_endpoint`       | Database host endpoint to connect to.                   | "aws.postgresrds.host"                                      |
| `db_user_password`       | Password for RDS database user authentication           | "My_Sup3rS3cr3tuserPassw0rd"                                |
| `dlq_subscription_email` | The email to notify users when messages are received in dead letter SQS queue | "test@email.com"                      |
| `orca_default_bucket`    | Default ORCA S3 Glacier bucket to use.                  | "PREFIX-orca-primary"                                       |
| `orca_reports_bucket`    | ORCA bucket to use for storing s3 reports.              | "PREFIX-orca-reports"                                       |
| `rds_security_group_id`  | Cumulus' RDS Security Group's ID.                       | "sg-01234567890123456"                                      |
| `s3_access_key`          | Access key for communicating with Orca S3 buckets.      |                                                             |
| `s3_secret_key`          | Secret key for communicating with Orca S3 buckets.      |                                                             |

### Optional Variables

The following variables are optional for the ORCA module and can be set by the
end user to better adjust ORCA for their specific environment.

#### Cumulus Optional Variables

The following variables should be present already in the `cumulus-tf/terrafor.tfvars`
file. The variables can be set with proper values for your environment in the
`cumulus-tf/terraform.tfvars` file. It is recommended that the `region` variable
is set to the proper AWS region for deployments.

| Variable               | Definition                                         | Example Value                 |
| ---------------------- | -------------------------------------------------- | ----------------------------- |
| `tags`                 | Tags to be applied to resources that support tags. | `{ environment = "development", developer = "me" }` |


#### ORCA Optional Variables

The following variables should be present in the `cumulus-tf/orca_variables.tf`
file. The variables can be set with proper values for your environment in the
`cumulus-tf/terraform.tfvars` file. The default setting for each of the optional
variables is shown in the table below.

| Variable                                              | Type          | Definition                                                                                                | Default
| ----------------------------------------------------- | ------------- | --------------------------------------------------------------------------------------------------------- | ---------- |
| `db_admin_username`                                   | string        | Username for RDS database administrator authentication.                                                   | "postgres" |
| `default_multipart_chunksize_mb`                      | number        | The default maximum size of chunks to use when copying. Can be overridden by collection config.           | 250 |
| `internal_report_queue_message_retention_time_seconds`| number        | Number of seconds the internal-report-queue SQS retains a message.                                        | 432000 |
| `metadata_queue_message_retention_time_seconds`       | number        | Number of seconds the metadata-queue fifo SQS retains a message.                                          | 777600 |
| `db_name`                                             | string        | The name of the Orca database within the RDS cluster. Any `-` in `prefix` will be replaced with `_`.      | PREFIX_orca |
| `db_user_name`                                        | string        | The name of the application user for the Orca database. Any `-` in `prefix` will be replaced with `_`.    | PREFIX_orcauser |
| `orca_ingest_lambda_memory_size`                      | number        | Amount of memory in MB the ORCA copy_to_glacier lambda can use at runtime.                                | 2240 |
| `orca_ingest_lambda_timeout`                          | number        | Timeout in number of seconds for ORCA copy_to_glacier lambda.                                             | 600 |
| `orca_reconciliation_lambda_memory_size`              | number        | Amount of memory in MB the ORCA reconciliation lambda can use at runtime.                                 | 128 |
| `orca_reconciliation_lambda_timeout`                  | number        | Timeout in number of seconds for ORCA reconciliation lambdas.                                             | 720 |
| `orca_recovery_buckets`                               | List (string) | List of bucket names that ORCA has permissions to restore data to. Default is all in the `buckets` map.   | [] |
| `orca_recovery_complete_filter_prefix`                | string        | Specifies object key name prefix by the Glacier Bucket trigger.                                           | "" |
| `orca_recovery_expiration_days`                       | number        | Number of days a recovered file will remain available for copy.                                           | 5 |
| `orca_recovery_lambda_memory_size`                    | number        | Amount of memory in MB the ORCA recovery lambda can use at runtime.                                       | 128 |
| `orca_recovery_lambda_timeout`                        | number        | Timeout in number of seconds for ORCA recovery lambdas.                                                   | 720 |
| `orca_recovery_retry_limit`                           | number        | Maximum number of retries of a recovery failure before giving up.                                         | 3 |
| `orca_recovery_retry_interval`                        | number        | Number of seconds to wait between recovery failure retries.                                               | 1 |
| `orca_recovery_retry_backoff`                         | number        | The multiplier by which the retry interval increases during each attempt.                                 | 2 |
| `s3_inventory_queue_message_retention_time_seconds`   | number        | The number of seconds s3-inventory-queue fifo SQS retains a message in seconds. Maximum value is 14 days. | 432000 |
| `sqs_delay_time_seconds`                              | number        | Number of seconds that the delivery of all messages in the queue will be delayed.                         | 0 |
| `sqs_maximum_message_size`                            | number        | The limit of how many bytes a message can contain before Amazon SQS rejects it.                           | 262144 |
| `staged_recovery_queue_message_retention_time_seconds`| number        | Number of seconds the staged-recovery-queue fifo SQS retains a message.                                   | 432000 |
| `status_update_queue_message_retention_time_seconds`  | number        | Number of seconds the status_update_queue fifo SQS retains a message.                                     | 777600 |


## ORCA Module Outputs

The orca module provides the outputs seen below in the table. Outputs are
accessed using terraform dot syntax in the format of `module.orca.variable_name`.

| Output Variable                                         | Description                                             |
| --------------------------------------------------------|---------------------------------------------------------|
| `orca_api_deployment_invoke_url`                        | The URL to invoke the ORCA Cumulus reconciliation API gateway. Excludes the resource path |
| `orca_lambda_copy_to_glacier_arn`                       | AWS ARN of the ORCA copy_to_glacier lambda. |
| `orca_lambda_extract_filepaths_for_granule_arn`         | AWS ARN of the ORCA extract_filepaths_for_granule lambda. |
| `orca_lambda_orca_catalog_reporting_arn`                | AWS ARN of the ORCA orca_catalog_reporting lambda. |
| `orca_lambda_request_files_arn`                         | AWS ARN of the ORCA request_files lambda. |
| `orca_lambda_copy_files_to_archive_arn`                 | AWS ARN of the ORCA copy_files_to_archive lambda. |
| `orca_lambda_request_status_for_granule_arn`            | AWS ARN of the ORCA request_status_for_granule lambda. |
| `orca_lambda_request_status_for_job_arn`                | AWS ARN of the ORCA request_status_for_job lambda. |
| `orca_lambda_post_copy_request_to_queue_arn`            | AWS ARN of the ORCA post_copy_request_to_queue lambda. |
| `orca_lambda_orca_catalog_reporting_arn`                | AWS ARN of the ORCA orca_catalog_reporting lambda. |
| `orca_secretsmanager_arn`                               | The Amazon Resource Name (ARN) of the AWS secretsmanager |
| `orca_sqs_metadata_queue_arn`                           | The ARN of the metadata-queue SQS |
| `orca_sqs_metadata_queue_id`                            | The URL ID of the metadata-queue SQS |
| `orca_sqs_staged_recovery_queue_arn`                    | The ARN of the staged-recovery-queue SQS |
| `orca_sqs_staged_recovery_queue_id`                     | The URL ID of the staged-recovery-queue SQS |
| `orca_sqs_status_update_queue_arn`                      | The ARN of the status-update-queue SQS |
| `orca_sqs_status_update_queue_id`                       | The URL ID of the status-update-queue SQS |
| `orca_subnet_group_id`                                  | The ORCA database subnet group name |
| `orca_subnet_group_arn`                                 | The ARN of the ORCA database subnet group |



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
`"granuleRecoveryWorkflow": "OrcaRecoveryWorkflow"` to the collection configuration
as seen below. Optionally, you can exclude files by adding values to an
`"excludeFileTypes"` variable as seen below. In addition, when dealing with large
files, the `"s3MultipartChunksizeMb"` variable can also be set to override the
default setting set during ORCA installation. For more information, see the documentation on the
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
    "granuleRecoveryWorkflow": "OrcaRecoveryWorkflow",
    "excludeFileTypes": [".cmr", ".xml", ".met"],
    "s3MultipartChunksizeMb": 400,
    "orcaDefaultBucketOverride": "prod_orca_worm"
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

