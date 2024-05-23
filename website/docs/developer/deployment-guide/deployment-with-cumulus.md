---
id: deployment-with-cumulus
title: Deploying ORCA with Cumulus
description: Provides developer information for ORCA code deployment with Cumulus.
---

:::important

Prior to following this document, make sure that your [deployment environment](setting-up-deployment-environment.mdx)
is setup and an [ORCA archive bucket](creating-orca-archive-bucket.md) is
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
  source = "https://github.com/nasa/cumulus-orca/releases/download/v9.0.0/cumulus-orca-terraform.zip"
  ## --------------------------
  ## Cumulus Variables
  ## --------------------------
  ## REQUIRED
  aws_region               = var.region
  buckets                  = var.buckets
  lambda_subnet_ids        = var.lambda_subnet_ids
  permissions_boundary_arn = var.permissions_boundary_arn
  prefix                   = var.prefix
  system_bucket            = var.system_bucket
  vpc_id                   = var.vpc_id

  ## OPTIONAL
  tags        = var.tags

  ## --------------------------
  ## ORCA Variables
  ## --------------------------
  ## REQUIRED
  db_admin_password        = var.db_admin_password
  db_host_endpoint         = var.db_host_endpoint
  db_user_password         = var.db_user_password
  dlq_subscription_email   = var.dlq_subscription_email
  orca_default_bucket      = var.orca_default_bucket
  orca_reports_bucket_name = var.orca_reports_bucket_name
  rds_security_group_id    = var.rds_security_group_id

  ## OPTIONAL
  # archive_recovery_queue_message_retention_time_seconds = 777600
  # db_admin_username                                     = "postgres"
  # default_multipart_chunksize_mb                        = 250
  # log_level                                             = "INFO"
  # metadata_queue_message_retention_time                 = 777600
  # orca_default_recovery_type                            = "Standard"
  # orca_default_storage_class                            = "GLACIER"
  # orca_delete_old_reconcile_jobs_frequency_cron         = "cron(0 0 ? * SUN *)"
  # orca_ingest_lambda_memory_size                        = 2240
  # orca_ingest_lambda_timeout                            = 600
  # orca_internal_reconciliation_expiration_days          = 30
  # orca_reconciliation_lambda_memory_size                = 128
  # orca_reconciliation_lambda_timeout                    = 720
  # orca_recovery_buckets                                 = []
  # orca_recovery_complete_filter_prefix                  = ""
  # orca_recovery_expiration_days                         = 5
  # orca_recovery_lambda_memory_size                      = 128
  # orca_recovery_lambda_timeout                          = 720
  # orca_recovery_retry_limit                             = 3
  # orca_recovery_retry_interval                          = 1
  # orca_recovery_retry_backoff                           = 2
  # s3_inventory_queue_message_retention_time_seconds     = 432000
  # s3_report_frequency                                   = "Daily"
  # sqs_delay_time_seconds                                = 0
  # sqs_maximum_message_size                              = 262144
  # staged_recovery_queue_message_retention_time_seconds  = 432000
  # status_update_queue_message_retention_time_seconds    = 777600


}
```

#### Required Values Unique to the ORCA Module

The following variables are unique to the ORCA module and required to be set by
the user. More information about these required variables, as well as the
optional variables can be found in the [variables section](#orca-variables).

- db_admin_password
- orca_default_bucket
- orca_reports_bucket_name
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

variable "dlq_subscription_email" {
  type        = string
  description = "The email to notify users when messages are received in dead letter SQS queue due to restore failure. Sends one email until the dead letter queue is emptied."
}

variable "orca_default_bucket" {
  type        = string
  description = "Default archive bucket to use."
}

variable "orca_reports_bucket_name" {
  type        = string
  description = "The name of the bucket to store s3 inventory reports."
}

variable "rds_security_group_id" {
  type        = string
  description = "Cumulus' RDS Security Group's ID."
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

## Default archive bucket to use
orca_default_bucket = "orca-archive-primary"

## The name of the bucket to store s3 inventory reports.
orca_reports_bucket_name = "PREFIX-orca-reports"

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
* `orca_default_bucket` (string) - default S3 archive bucket to use for ORCA data.
* `db_admin_password` (string) - password for the admin user.
* `db_host_endpoint`(string) - Database host endpoint to connect to.
* `db_user_password` (string) - the password for the application user.
* `dlq_subscription_email`(string) - "The email to notify users when messages are received in dead letter SQS queue due to restore failure. Sends one email until the dead letter queue is emptied."
* `orca_default_bucket` (string) - Default S3 archive bucket to use for ORCA data.
* `orca_reports_bucket_name` (string) - The name of the bucket to store s3 inventory reports.
* `rds_security_group_id`(string) - Cumulus' RDS Security Group's ID. Output as `security_group_id` from the rds-cluster deployment.

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

## Define the ORCA Workflows

The ORCA Ingest Workflows follows each step listed below. Adding the 
MoveGranuleStep and the CopyToArchive Step are detailed in their respective
sections.

**ORCA Ingest Workflow**
  SyncGranule
  FilesToGranuleStep
  MoveGranuleStep
  CopyToArchive

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


### Add the CopyToArchive Step to an Ingest Workflow

Navigate to `cumulus-tf/ingest_granule_workflow.tf` then add the following step
anywhere after the MoveGranuleStep step being sure to change the MoveGranuleStep's
`"Next"` parameter equal to "CopyToArchive".

:::important

Adjust the `"Next"` step in the example below to point to the proper step in
the ingest workflow.

:::

Since ORCA is decoupling from Cumulus starting in ORCA v8.0, users will now run the same [ORCA `copy_to_archive` workflow](https://github.com/nasa/cumulus-orca/tree/master/modules/workflows/OrcaCopyToArchiveWorkflow) but must need to update the existing workflow configuration to point to [copy_to_archive_adapter lambda](https://github.com/nasa/cumulus/tree/master/tasks/orca-copy-to-archive-adapter) (owned by Cumulus) which then runs our existing `copy_to_archive` lambda.

:::note
Make sure to replace `<CUMULUS_COPY_TO_ARCHIVE_ADAPTER_ARN>` under `Resource` property below. See [cumulus terraform modules](https://github.com/nasa/cumulus/blob/master/tf-modules/cumulus/outputs.tf#L86) for additional details on how to add this.
:::

```json
"CopyToArchive":{
  "Parameters":{
    "cma":{
      "event.$":"$",
      "task_config": {
        "excludedFileExtensions": "{$.meta.collection.meta.orca.excludedFileExtensions}",
        "s3MultipartChunksizeMb": "{$.meta.collection.meta.s3MultipartChunksizeMb}",
        "providerId": "{$.meta.provider.id}",
        "providerName": "{$.meta.provider.name}",
        "executionId": "{$.cumulus_meta.execution_name}",
        "collectionShortname": "{$.meta.collection.name}",
        "collectionVersion": "{$.meta.collection.version}",
        "defaultBucketOverride": "{$.meta.collection.meta.orca.defaultBucketOverride}"
      }
    }
  }
},
  "Type":"Task",
  "Resource":"<CUMULUS_COPY_TO_ARCHIVE_ADAPTER_ARN>",
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

As part of the [Cumulus Message Adapter configuration](https://nasa.github.io/cumulus/docs/workflows/input_output#cma-configuration) 
for `copy_to_archive`, the `excludedFileExtensions`, `s3MultipartChunksizeMb`, `providerId`, `executionId`, `collectionShortname`, `collectionVersion`, `defaultBucketOverride`, and `defaultStorageClassOverride` keys must be present under the 
`task_config` object as seen above. 
Per the [config schema](https://github.com/nasa/cumulus/blob/master/tasks/orca-copy-to-archive-adapter/schemas/config.json), 
the values of the keys are used the following ways. 
The `provider` key should contain an `id` key that returns the provider id from Cumulus. 
The `cumulus_meta` key should contain an `execution_name` key that returns the step function execution ID from AWS. 
The `collection` key value should contain a `name` key and a `version` key that return the required collection shortname and collection version from Cumulus respectively.
The `collection` key value should also contain a `meta` key that includes an `orca` key having an optional `excludedFileExtensions` key that is used to determine file patterns that should not be 
sent to ORCA. In addition, the `orca` key also contains optional `defaultBucketOverride` key that overrides the `ORCA_DEFAULT_BUCKET` set on deployment and optional `defaultStorageClassOverride` key that overrides the storage class to use when storing files in Orca. 
The optional `s3MultipartChunksizeMb` is used to override the default setting for the lambda s3 copy maximum multipart chunk size value when copying large files to ORCA.
These settings can often be derived from the collection configuration in Cumulus.
See the copy_to_archive_adapter json schema [configuration file](https://github.com/nasa/cumulus/blob/master/tasks/orca-copy-to-archive-adapter/schemas/config.json), [input file](https://github.com/nasa/cumulus/blob/master/tasks/orca-copy-to-archive-adapter/schemas/input.json)  and [output file](https://github.com/nasa/cumulus/blob/master/tasks/orca-copy-to-archive-adapter/schemas/output.json) for more information.

### Modify the Recovery Workflow

Since ORCA is decoupling from Cumulus starting in ORCA v8.0, users will now need to deploy a `recovery_workflow_adapter` workflow that triggers [the recovery_adapter lambda](https://github.com/nasa/cumulus/tree/master/tasks/orca-recovery-adapter) (owned by Cumulus) which then runs our existing orca recovery workflow.
As part of the [Cumulus Message Adapter configuration](https://nasa.github.io/cumulus/docs/workflows/input_output/#cma-configuration), several properties must be passed into the adapter lambda. See [input and config schemas](https://github.com/nasa/cumulus/tree/master/tasks/orca-recovery-adapter/schemas) for more information.

Here is an example of a [recovery adapter workflow step function definition](https://github.com/nasa/cumulus/blob/master/example/cumulus-tf/orca_recovery_adapter_workflow.asl.json) and the [terraform code](https://github.com/nasa/cumulus/blob/master/example/cumulus-tf/orca_recovery_adapter_workflow.tf) provided by Cumulus that can be used to deploy the step function workflow in AWS. Once deployed, you can run that workflow to test ORCA recovery.

:::note
Users should reach out to Cumulus team if they want to automate this adapter workflow in Cumulus deployment since Cumulus owns the adapter lambdas.
:::

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
| `buckets`                  | Mapping of all S3 buckets used by Cumulus and ORCA that contains a S3 `name` and `type`. A bucket with a `type` of **orca** is required.     | `buckets = { orca_default = { name = "PREFIX-orca-primary", type = "orca", ...}}` |
| `lambda_subnet_ids`        | A list of subnets that the Lambda's and the database have access to for working with Cumulus.                                                | ["subnet-12345", "subnet-abc123"] |
| `permissions_boundary_arn` | AWS ARN value of the permission boundary for the VPC account.                                                                                | "arn:aws:iam::1234567890:policy/NGAPShRoleBoundary" |
| `prefix`                   | Prefix that will be pre-pended to resource names created by terraform.                                                                       | "daac-sndbx" |
| `system_bucket`            | Cumulus system bucket used to store internal files and configurations for deployments.                                                       | "PREFIX-internal" |
| `vpc_id`                   | ID of VPC to place resources in - recommended that this be a private VPC (or at least one with restricted access).                           | "vpc-abc123456789" |

#### ORCA Required Variables

The following variables should be present in the `cumulus-tf/orca_variables.tf`
file. The variables must be set with proper values for your environment in the
`cumulus-tf/terraform.tfvars` file.

| Variable                   | Definition                                               |              Example Value                                  |
| -------------------------- | -------------------------------------------------------- | ------------------------------------------------------------|
| `aws_region`               | AWS Region to create resources in.                       | "us-west-2"                                                 |
| `db_admin_password`        | Password for RDS database administrator authentication   | "My_Sup3rS3cr3t_admin_Passw0rd"                             |
| `db_host_endpoint`         | Database host endpoint to connect to.                    | "aws.postgresrds.host"                                      |
| `db_user_password`         | Password for RDS database user authentication            | "My_Sup3rS3cr3tuserPassw0rd"                                |
| `dlq_subscription_email`   | The email to notify users when messages are received in dead letter SQS queue | "test@email.com"                       |
| `orca_default_bucket`      | Default archive bucket to use.                           | "PREFIX-orca-primary"                                       |
| `orca_reports_bucket_name` | The Name of the bucket to store s3 inventory reports.    | "PREFIX-orca-reports"                                       |
| `rds_security_group_id`    | Cumulus' RDS Security Group's ID.                        | "sg-01234567890123456"                                      |

### Optional Variables

The following variables are optional for the ORCA module and can be set by the
end user to better adjust ORCA for their specific environment.

#### Cumulus Optional Variables

The following variables should be present already in the `cumulus-tf/terraform.tfvars`
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

| Variable                                              | Type          | Definition                                                                                                                     | Default
| ----------------------------------------------------- | ------------- | ------------------------------------------------------------------------------------------------------------------------------ | ---------- |
| `archive_recovery_queue_message_retention_time_seconds`| string       | The number of seconds archive-recovery-queue SQS retains a message in seconds.                                                 | 777600     |
| `db_admin_username`                                    | string       | Username for RDS database administrator authentication.                                                                        | "postgres" |
| `default_multipart_chunksize_mb`                       | number       | The default maximum size of chunks to use when copying. Can be overridden by collection config.                                | 250 |
| `internal_report_queue_message_retention_time_seconds` | number       | Number of seconds the internal-report-queue SQS retains a message.                                                             | 432000 |
| `metadata_queue_message_retention_time_seconds`        | number       | Number of seconds the metadata-queue fifo SQS retains a message.                                                               | 777600 |
| `db_name`                                              | string       | The name of the Orca database within the RDS cluster. Any `-` in `prefix` will be replaced with `_`.                           | PREFIX_orca |
| `db_user_name`                                         | string       | The name of the application user for the Orca database. Any `-` in `prefix` will be replaced with `_`.                         | PREFIX_orcauser |
| `log_level`                                            | string       | sets the verbose of PowerTools logger. Must be one of 'INFO', 'DEBUG', 'WARN', 'ERROR'. Defaults to 'INFO'.                    | "INFO" |
| `orca_default_recovery_type`                           | string       | The Tier for the restore request. Valid values are 'Standard', 'Bulk', 'Expedited'                                               | "Standard" |
| `orca_default_storage_class`                           | string       | The [class of storage](../../operator/storage-classes.md) to use when ingesting files. Can be overridden by collection config. | "GLACIER" |
| `orca_delete_old_reconcile_jobs_frequency_cron`        | string       | Frequency cron for running the delete_old_reconcile_jobs lambda.                                                               | "cron(0 0 ? * SUN *)" |
| `orca_ingest_lambda_memory_size`                       | number       | Amount of memory in MB the ORCA copy_to_archive lambda can use at runtime.                                                     | 2240 |
| `orca_ingest_lambda_timeout`                           | number       | Timeout in number of seconds for ORCA copy_to_archive lambda.                                                                  | 600 |
| `orca_internal_reconciliation_expiration_days`         | number       | Only reports updated before this many days ago will be deleted.                                                                | 30 |
| `orca_reconciliation_lambda_memory_size`               | number       | Amount of memory in MB the ORCA reconciliation lambda can use at runtime.                                                      | 128 |
| `orca_reconciliation_lambda_timeout`                   | number       | Timeout in number of seconds for ORCA reconciliation lambdas.                                                                  | 720 |
| `orca_recovery_buckets`                                | List (string)| List of bucket names that ORCA has permissions to restore data to. Default is all in the `buckets` map.                        | [] |
| `orca_recovery_complete_filter_prefix`                 | string       | Specifies object key name prefix by the archive Bucket trigger.                                                                | "" |
| `orca_recovery_expiration_days`                        | number       | Number of days a recovered file will remain available for copy.                                                                | 5 |
| `orca_recovery_lambda_memory_size`                     | number       | Amount of memory in MB the ORCA recovery lambda can use at runtime.                                                            | 128 |
| `orca_recovery_lambda_timeout`                         | number       | Timeout in number of seconds for ORCA recovery lambdas.                                                                        | 720 |
| `orca_recovery_retry_limit`                            | number       | Maximum number of retries of a recovery failure before giving up.                                                              | 3 |
| `orca_recovery_retry_interval`                         | number       | Number of seconds to wait between recovery failure retries.                                                                    | 1 |
| `orca_recovery_retry_backoff`                          | number       | The multiplier by which the retry interval increases during each attempt.                                                      | 2 |
| `s3_inventory_queue_message_retention_time_seconds`    | number       | The number of seconds s3-inventory-queue fifo SQS retains a message in seconds. Maximum value is 14 days.                      | 432000 |
| `s3_report_frequency`                                  | string       | How often to generate s3 reports for internal reconciliation. `Daily` or `Weekly`                                              | Daily |
| `sqs_delay_time_seconds`                               | number       | Number of seconds that the delivery of all messages in the queue will be delayed.                                              | 0 |
| `sqs_maximum_message_size`                             | number       | The limit of how many bytes a message can contain before Amazon SQS rejects it.                                                | 262144 |
| `staged_recovery_queue_message_retention_time_seconds` | number       | Number of seconds the staged-recovery-queue fifo SQS retains a message.                                                        | 432000 |
| `status_update_queue_message_retention_time_seconds`   | number       | Number of seconds the status_update_queue fifo SQS retains a message.                                                          | 777600 |


## ORCA Module Outputs

The orca module provides the outputs seen below in the table. Outputs are
accessed using terraform dot syntax in the format of `module.orca.variable_name`.

| Output Variable                                         | Description                                             |
| --------------------------------------------------------|---------------------------------------------------------|
| `orca_api_deployment_invoke_url`                        | The URL to invoke the ORCA Cumulus reconciliation API gateway. Excludes the resource path |
| `orca_graphql_load_balancer_dns_name`                   | The DNS Name of the Application Load Balancer that handles access to ORCA GraphQL. |
| `orca_lambda_copy_to_archive_arn`                       | AWS ARN of the ORCA copy_to_archive lambda. |
| `orca_lambda_extract_filepaths_for_granule_arn`         | AWS ARN of the ORCA extract_filepaths_for_granule lambda. |
| `orca_lambda_orca_catalog_reporting_arn`                | AWS ARN of the ORCA orca_catalog_reporting lambda. |
| `orca_lambda_request_from_archive_arn`                  | AWS ARN of the ORCA request_from_archive lambda. |
| `orca_lambda_copy_from_archive_arn`                     | AWS ARN of the ORCA copy_from_archive lambda. |
| `orca_lambda_request_status_for_granule_arn`            | AWS ARN of the ORCA request_status_for_granule lambda. |
| `orca_lambda_request_status_for_job_arn`                | AWS ARN of the ORCA request_status_for_job lambda. |
| `orca_lambda_post_copy_request_to_queue_arn`            | AWS ARN of the ORCA post_copy_request_to_queue lambda. |
| `orca_lambda_orca_catalog_reporting_arn`                | AWS ARN of the ORCA orca_catalog_reporting lambda. |
| `orca_secretsmanager_arn`                               | The Amazon Resource Name (ARN) of the AWS secretsmanager |
| `orca_sfn_recovery_workflow_arn`                        | The ARN of the recovery step function. |
| `orca_sqs_archive_recovery_queue_arn`                   | The ARN of the archive-recovery-queue SQS |
| `orca_sqs_archive_recovery_queue_id`                    | The URL of the archive-recovery-queue SQS |
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
as seen below.

Optionally, you can exclude files by adding values to an
`excludedFileExtensions` variable as seen below.
In addition, when dealing with large files, the `s3MultipartChunksizeMb` variable can also be set to override the
default setting set during ORCA installation.
If the file should be stored in a [storage class](../../operator/storage-classes.md) other than the default set in `orca_default_storage_class` during installation, specify it using `defaultStorageClassOverride`.
For more information, see the documentation on the
[`copy_to_archive` task](https://github.com/nasa/cumulus-orca/tree/master/tasks/copy_to_archive).

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
    "s3MultipartChunksizeMb": 400,
    "granuleRecoveryWorkflow": "OrcaRecoveryWorkflow",
    "orca": {
      "excludedFileExtensions": [".cmr", ".xml", ".met"],
      "defaultBucketOverride": "prod_orca_worm",
      "defaultRecoveryTypeOverride": "Standard",
      "defaultStorageClassOverride": "DEEP_ARCHIVE"
    }
  },
}
```
## Enable `Recover Granule` Button

To enable the `Recover Granule` button on the Cumulus Dashboard (available at github.com/nasa/cumulus-dashboard), 
set the environment variable `ENABLE_RECOVERY=true`.

Here is an sample command to run the Cumulus Dashboard locally.

```bash
APIROOT=https://uttm5y1jcj.execute-api.us-west-2.amazonaws.com:8000/dev ENABLE_RECOVERY=true npm run serve
```
