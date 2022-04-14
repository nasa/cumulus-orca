# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and includes an additional section for migration notes.

- *Migration Notes* - Notes for end users to migrate to the version.
- *Added* - New features.
- *Changed* - Changes in existing functionality.
- *Deprecated* - Soon-to-be removed features.
- *Removed* - Now removed features.
- *Fixed* - Any bug fixes.
- *Security* - Vulnerabilities fixes and changes.


## [Unreleased]

### Added
- *ORCA-300* Added `OrcaInternalReconciliation` workflow allong with an accompanying input queue and dead-letter queue.
    Retention time can be changed by setting `internal_report_queue_message_retention_time_seconds` in your `variables.tf` or `orca_variables.tf` file. Defaults to 432000.
- *ORCA-161* Added dead letter queue and cloudwatch alarm terraform code to recovery SQS queue.
- *ORCA-307* Added lambda get_current_archive_list to pull S3 Inventory reports into Postgres. 
    Adds `orca_reconciliation_lambda_memory_size` and `orca_reconciliation_lambda_timeout` to Terraform variables.
- *ORCA-308* Added lambda perform_orca_reconcile to find differences between S3 Inventory reports and Orca catalog.
- *ORCA-403* Added lambda post_to_queue_and_trigger_step_function to trigger step function for internal reconciliation.
- *ORCA-373* Added input variable for `orca_reports_bucket_arn`. Set in your `variables.tf` or `orca_variables.tf` file as shown below.
    Report frequency defaults to `Daily`, but can be set to `Weekly` through variable `s3_report_frequency`.
- *ORCA-309* Added lambda internal_reconcile_report_phantom to report entries present in the catalog, but not s3.

### Changed
- *ORCA-299* `db_deploy` task has been updated to deploy ORCA internal reconciliation tables and objects.
- *ORCA-161* Changed staged recovery SQS queue type from FIFO to standard queue.
- SQS Queue names adjusted to include Orca. For example: `"${var.prefix}-orca-status-update-queue.fifo"`. Queues will be automatically recreated by Terraform.
- *ORCA-404* Updated shared_db and relevant lambdas to use secrets manager ARN instead of magic strings.

### Migration Notes

- Create a new bucket `PREFIX-orca-reports` in the same account and region as your primary orca bucket.
  - Give the bucket a [lifecycle configuration](https://docs.aws.amazon.com/AmazonS3/latest/userguide/how-to-set-lifecycle-configuration-intro.html) with an expiration period of 30 days.
  - Follow instructions in https://nasa.github.io/cumulus-orca/docs/developer/deployment-guide/deployment-s3-bucket/ to set up permission policy.
  - Modify the permissions for your primary Orca bucket.
    - Under the `Cross Account Access` policy, add `s3:GetInventoryConfiguration` and `s3:PutInventoryConfiguration` to Actions.
  - Update the `buckets` variable in your `tfvars` file by adding the bucket.
    ```
    buckets = {
      ...
      orca_reports = {
        name = "PREFIX-orca-reports"
        type = "orca-reports"
      },
      ...
    }
    ```
- The user should update their `orca.tf`, `variables.tf` and `terraform.tfvars` files with new variables. The following required variables have been added:
  - dlq_subscription_email
  - orca_reports_bucket_arn
  - s3_access_key
  - s3_secret_key
  
- Add the following ORCA required variable definition to your `variables.tf` or `orca_variables.tf` file.

```terraform
variable "dlq_subscription_email" {
  type        = string
  description = "The email to notify users when messages are received in dead letter SQS queue due to restore failure. Sends one email until the dead letter queue is emptied."
}

variable "orca_reports_bucket_arn" {
  type        = string
  description = "The ARN of the bucket to store s3 inventory reports."
}

variable "s3_access_key" {
  type        = string
  description = "Access key for communicating with Orca S3 buckets."
}

variable "s3_secret_key" {
  type        = string
  description = "Secret key for communicating with Orca S3 buckets."
}
```
- Update the `orca.tf` file to include all of the updated and new variables as seen below. Note the change to source and the commented out optional variables.
  ```terraform
  ## ORCA Module
  ## =============================================================================
  module "orca" {
    source = "https://github.com/nasa/cumulus-orca/releases/download/v3.0.1/cumulus-orca-terraform.zip//modules"
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
  tags        = local.tags

  ## --------------------------
  ## ORCA Variables
  ## --------------------------
  ## REQUIRED
  db_admin_password       = var.db_admin_password
  db_user_password        = var.db_user_password
  db_host_endpoint        = var.db_host_endpoint
  dlq_subscription_email  = var.dlq_subscription_email
  orca_default_bucket     = var.orca_default_bucket
  orca_reports_bucket_arn = var.orca_reports_bucket_arn
  rds_security_group_id   = var.rds_security_group_id
  s3_access_key           = var.s3_access_key
  s3_secret_key           = var.s3_secret_key

  ## OPTIONAL
  db_admin_username                                    = "postgres"
  default_multipart_chunksize_mb                       = 250
  internal_report_queue_message_retention_time_seconds = 432000
  orca_ingest_lambda_memory_size                       = 2240
  orca_ingest_lambda_timeout                           = 720
  orca_recovery_buckets                                = []
  orca_recovery_complete_filter_prefix                 = ""
  orca_recovery_expiration_days                        = 5
  orca_recovery_lambda_memory_size                     = 128
  orca_recovery_lambda_timeout                         = 720
  orca_recovery_retry_limit                            = 3
  orca_recovery_retry_interval                         = 1
  orca_recovery_retry_backoff                          = 2
  s3_inventory_queue_message_retention_time_seconds    = 432000
  s3_report_frequency                                  = "Daily"
  sqs_delay_time_seconds                               = 0
  sqs_maximum_message_size                             = 262144
  staged_recovery_queue_message_retention_time_seconds = 432000
  status_update_queue_message_retention_time_seconds   = 777600
  vpc_endpoint_id                                      = null
  }
  ```


## [4.0.1]

### Fixed
- Updated release build script to perform cleanup sooner.
- Updated terraform deployment with additional depends_on parameters and fixes
  to prevent db_deploy lambda from firing prematurely.


## [4.0.0]

### Removed
- The `modules/rds` directory is removed since ORCA will utilize the Cumulus DB.
- *ORCA-233* The `disaster_recovery` database, now renamed `PREFIX_orca`, will now be created by db_deploy instead of Terraform.
- *ORCA-288* Removed copy_to_glacier_cumulus_translator due to better consistency in Cumulus's [file dictionary](https://github.com/nasa/cumulus/blob/master/packages/schemas/files.schema.json).
- *ORCA-311* `copy_to_glacier` no longer accepts/returns file properties other than `bucket` and `key`.
  `copied_to_glacier` is similarly no longer passed through, but generated.

### Added
- *ORCA-256* Added AWS API Gateway in modules/api_gateway/main.tf for the catalog reporting lambda.
- *ORCA-227* Added modules/secretsmanager directory that contains terraform code for deploying AWS secretsmanager.
- *ORCA-177* Added AWS API Gateway in modules/api_gateway/main.tf for the request_status_for_granule and request_status_for_job lambdas.
- *ORCA-257* orca_catalog_reporting lambda now returns data from actual catalog.
- *ORCA-151* copy_to_glacier and request_files now accept "orcaDefaultBucketOverride" which can be used on a per-collection basis. If desired, add "orcaDefaultBucketOverride": "{$.meta.collection.meta.orcaDefaultBucketOverride}" to the workflow's task's task_config.
- *ORCA-335* request_files now recognizes when a file is already recovered, and posts an error message to status tables.
- *ORCA-230* copy_to_glacier now writes metadata to an ORCA catalog for comparisons to cumulus holdings.

### Changed
- *ORCA-217* Lambda inputs now conform to the Cumulus camel case standard.
- *ORCA-297* Default database name is now PREFIX_orca
- *ORCA-287* Updated copy_to_glacier and extract_filepaths_for_granule to [new Cumulus file format](https://github.com/nasa/cumulus/blob/master/packages/schemas/files.schema.json). 
- *ORCA-245* Updated resource policies related to KMS keys to provide better security.
- *ORCA-318* Updated post_to_catalog lambda to match new Cumulus schema changes.
- *ORCA-317* Updated the db_deploy task, unit tests, manual tests, research pages and SQL to reflect new inventory layout to better align with Cumulus.
- *ORCA-249* Changed `mutipart_chunksize_mb` in lambda configs to `s3MultipartChunksizeMb`. Standard workflows now pull from `$.meta.collection.meta.s3MultipartChunksizeMb`
- *ORCA-230* Updated lambdas to use Cumulus Message Adapter Python v2.0.0.
- *ORCA-132* Updated workflows to use latest Cumulus v10.0.0 workflow code.

### Migration Notes

- Orca is only compatible with versions of Cumulus that use the [new Cumulus file format](https://github.com/nasa/cumulus/blob/master/packages/schemas/files.schema.json). Any calls to extract_filepaths_for_granule or copy_to_glacier should switch to the new format.
- Ensure that anything calling `copy_to_glacier` only relies on properties currently present in `copy_to_glacier/schemas/output.json`
- Remove any added references in your setup to copy_to_glacier_cumulus_translator. It is no longer necesarry as a Cumulus intermediary.
- The user should update their `orca.tf`, `variables.tf` and `terraform.tfvars` files with new variables. The following two variable names have changed:
  - postgres_user_pw-> db_admin_password (*new*)
  - database_app_user_pw-> db_user_password (*new*)
- These are the new variables added:
  - db_admin_username (defaults to "postgres")
  - db_host_endpoint (Requires a value. Set in terraform.tfvars to your RDS Database's endpoint, similar to "PREFIX-cumulus-db.cluster-000000000000.us-west-2.rds.amazonaws.com")
  - db_name (Defaults to PREFIX_orca.)
    - Any `-` in `prefix` are replaced with `_` to follow [SQL Naming Conventions](https://www.postgresql.org/docs/7.0/syntax525.htm#:~:text=Names%20in%20SQL%20must%20begin,but%20they%20will%20be%20truncated.)
    - If preserving a database from a previous version of Orca, set to disaster_recovery.
  - db_user_name (Defaults to PREFIX_orcauser.)
    - Any `-` in `prefix` are replaced with `_` to follow [SQL Naming Conventions](https://www.postgresql.org/docs/7.0/syntax525.htm#:~:text=Names%20in%20SQL%20must%20begin,but%20they%20will%20be%20truncated.)
    - If preserving a database from a previous version of Orca, set to orcauser.
  - rds_security_group_id (Requires a value. Set in terraform.tfvars to the Security Group ID of your RDS Database's Security Group. Output from Cumulus' RDS module as `security_group_id`)
  - vpc_endpoint_id
- Adjust workflows/step functions for `extract_filepaths`.
  - `file-buckets` argument in `task_config` is now `fileBucketsMaps`.
- Adjust workflows/step functions for `copy_to_glacier`. 
  - `multipart_chunksize_mb` argument in `task_config` is now the Cumulus standard of `s3MultipartChunksizeMb`. See example below.
  - `copy_to_glacier` has new requirements for writing to the orca catalog. See example below. Required properties are `providerId`, `executionId`, `collectionShortname`, and `collectionVersion`. See example below.
- 
```
"task_config": {
  "s3MultipartChunksizeMb": "{$.meta.collection.meta.s3MultipartChunksizeMb}",
  "excludeFileTypes": "{$.meta.collection.meta.excludeFileTypes}",
  "providerId": "{$.meta.provider.id}",
  "providerName": "{$.meta.provider.name}",
  "executionId": "{$.cumulus_meta.execution_name}",
  "collectionShortname": "{$.meta.collection.name}",
  "collectionVersion": "{$.meta.collection.version}",
  "orcaDefaultBucketOverride": "{$.meta.collection.meta.orcaDefaultBucketOverride}"
}
```
- `request_status_for_granule` [input](https://github.com/nasa/cumulus-orca/blob/master/tasks/request_status_for_granule/schemas/input.json)/[output](https://github.com/nasa/cumulus-orca/blob/master/tasks/request_status_for_granule/schemas/output.json) and `request_status_for_job` [input](https://github.com/nasa/cumulus-orca/blob/master/tasks/request_status_for_job/schemas/input.json)/[output](https://github.com/nasa/cumulus-orca/blob/master/tasks/request_status_for_job/schemas/output.json) are now fully camel case.
- Add the following ORCA required variables definition to your `variables.tf` or `orca_variables.tf` file.

```terraform
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

variable "rds_security_group_id" {
  type        = string
  description = "Cumulus' RDS Security Group's ID."
}
```
- Update the `orca.tf` file to include all of the updated and new variables as seen below. Note the change to source and the commented out optional variables.
  ```terraform
  ## ORCA Module
  ## =============================================================================
  module "orca" {
    source = "https://github.com/nasa/cumulus-orca/releases/download/v3.0.1/cumulus-orca-terraform.zip//modules"
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
  tags        = local.tags

  ## --------------------------
  ## ORCA Variables
  ## --------------------------
  ## REQUIRED
  orca_default_bucket = var.orca_default_bucket
  db_admin_password   = var.db_admin_password
  db_user_password    = var.db_user_password
  db_host_endpoint    = var.db_host_endpoint
  rds_security_group_id    = var.rds_security_group_id
  ## OPTIONAL
  db_admin_username                                    = "postgres"
  default_multipart_chunksize_mb                       = 250
  orca_ingest_lambda_memory_size                       = 2240
  orca_ingest_lambda_timeout                           = 720
  orca_recovery_buckets                                = []
  orca_recovery_complete_filter_prefix                 = ""
  orca_recovery_expiration_days                        = 5
  orca_recovery_lambda_memory_size                     = 128
  orca_recovery_lambda_timeout                         = 720
  orca_recovery_retry_limit                            = 3
  orca_recovery_retry_interval                         = 1
  orca_recovery_retry_backoff                          = 2
  sqs_delay_time_seconds                               = 0
  sqs_maximum_message_size                             = 262144
  staged_recovery_queue_message_retention_time_seconds = 432000
  status_update_queue_message_retention_time_seconds   = 777600
  vpc_endpoint_id                                      = null
  }
  ```


## [3.0.2]

### Migration Notes
The configuration schema for `copy_to_glacier` has changed. See the updated schema
definition [here](https://github.com/nasa/cumulus-orca/blob/develop/tasks/copy_to_glacier/schemas/config.json).
Additional optional configuration settings like `multipart_chunksize_mb` can be
found for `copy_to_glacier` and ORCA recovery in the ORCA documentation
[here](https://nasa.github.io/cumulus-orca/docs/developer/deployment-guide/deployment-with-cumulus).

### Added
- *ORCA-244* Added schema files for copy_to_glacier. Errors for improperly formatted requests will look different.
- *ORCA-246* Added TF variable `default_multipart_chunksize_mb` which adjusts the maximum chunksize when copying files. Defaults to 250. Can be overridden by `multipart_chunksize_mb` within `config['collection']`. `default_multipart_chunksize_mb` can be overridden in your `orca.tf` with the line `default_multipart_chunksize_mb = 500`

### Fixed
- *ORCA-248* `excludeFileTypes` is no longer required, as intended.
- *ORCA-205* Fixed installation and usage of orca_shared libraries.


## [v3.0.1] 2021-08-31

### Migration Notes
- `database_app_user`, `database_name`, and `orca_recovery_retrieval_type` are no longer variables. If you have set these values, remove them.

### Removed
- *ORCA-240* Removed development-only variables from variables.tf
- *ORCA-243* Removed aws_profile and region variables from variables.tf

### Fixed
- ORCA-199 Standardized build and test scripts for remaining ORCA lambdas
- ORCA-236 Removed aws_profile and region variables as requirements for ORCA deployment.
- ORCA-238 Moved all terraform requirements to a single versions.tf file as part of the deployments.
- ORCA-239 Removed terraform provider block from all ORCA files and consolidated to main.tf file.
- Removed technical debt and fixed recovery bug where bucket keys that were not the standard (internal, public, private, etc.) were being ignored.

### Changed
- *ORCA-237* Updated node requirement versions to fix known security vulnerabilities.


## [v3.0.0] 2021-07-12


### Migration Notes
See the documentation for specifics on the various files and changes specified below.

- Update the buckets variable in `terraform.tfvars`. The ORCA bucket previously defined should now have a type of orca.
  ```terraform
  # OLD Setting
  buckets = {
    internal = {
      name = "my-internal-bucket",
      type = "internal"
    },
    ...
    glacier = {
      name = "my-orca-bucket",
      type = "glacier"
    }
  }

  # NEW Setting
  buckets = {
    internal = {
      name = "my-internal-bucket",
      type = "internal"
    },
    ...
    glacier = {
      name = "my-orca-bucket",
      type = "orca"
    }
  }

  ```
- Add the following ORCA required variable definition to your `variables.tf` or `orca_variables.tf` file.
  ```terraform
  variable "orca_default_bucket" {
    type        = string
    description = "Default ORCA S3 Glacier bucket to use."
  }
  ```
- Update the `terraform.tfvars` file with the value for `orca_default_bucket`.
  ```terraform
  orca_default_bucket = "my-orca-bucket"
  ```
- Update the `orca.tf` file to include all of the updated and new variables as seen below. Note the change to source and the commented out optional variables.
  ```terraform
  ## ORCA Module
  ## =============================================================================
  module "orca" {
    source = "https://github.com/nasa/cumulus-orca/releases/download/v3.0.0/cumulus-orca-terraform.zip//modules"
    ## --------------------------
    ## Cumulus Variables
    ## --------------------------
    ## REQUIRED
    aws_profile              = var.aws_profile
    buckets                  = var.buckets
    lambda_subnet_ids        = var.lambda_subnet_ids
    permissions_boundary_arn = var.permissions_boundary_arn
    prefix                   = var.prefix
    system_bucket            = var.system_bucket
    vpc_id                   = var.vpc_id
    workflow_config          = module.cumulus.workflow_config
  
    ## OPTIONAL
    region = var.region
    tags   = var.tags
  
    ## --------------------------
    ## ORCA Variables
    ## --------------------------
    ## REQUIRED
    database_app_user_pw = var.database_app_user_pw
    orca_default_bucket  = var.orca_default_bucket
    postgres_user_pw     = var.database_app_user_pw
  
    ## OPTIONAL
    # database_port                        = 5432
    # orca_ingest_lambda_memory_size       = 2240
    # orca_ingest_lambda_timeout           = 600
    # orca_recovery_buckets                = []
    # orca_recovery_complete_filter_prefix = ""
    # orca_recovery_expiration_days        = 5
    # orca_recovery_lambda_memory_size     = 128
    # orca_recovery_lambda_timeout         = 300
    # orca_recovery_retry_limit            = 3
    # orca_recovery_retry_interval         = 1
  }
  ```

### Added
- *ORCA-149* Added a new workflow, OrcaCopyToGlacierWorkflow, for ingest on-demand.
- *ORCA-175* Added copy_to_glacier_cumulus_translator for transforming CumulusDashboard input to the proper format.
- *ORCA-181* Added orca_catalog_reporting_dummy lambda for integration testing.
- *ORCA-165* Added new lambda function *post_copy_request_to_queue.py* under *tasks/post_copy_request_to_queue/ for querying the DB 
  and  posting to two queues.
  Added unit tests *test_post_copy_request_to_queue.py* under *tasks/post_copy_request_to_queue/test/unit_tests/* to test the new lambda.
  Added new scripts *run_tests.sh* and *build.sh* under */tasks/post_copy_request_to_queue/bin* to run the unit tests.
- *ORCA-163* Added shared library *shared_recovery.py* under *tasks/shared_libraries/recovery/* for posting to status SQS queue.
  This include *post_status_for_job_to_queue()* function that posts status of jobs to SQS queue,
  *post_status_for_job_to_queue()* function that posts status of files to SQS queue,
  and *post_entry_to_queue()* function that is used by the above two functions for sending the message to the queue.
  Added unit tests *test_shared_recovery.py* under *tasks/shared_libraries/recovery/test/unit_tests/* to test shared library.
  Added new script *run_tests.sh* under *tasks/shared_libraries/recovery/bin* to run the unit tests.
- *ORCA-92* Added two lambdas (request_status_for_file and request_status_for_job)
  for use with the Cumulus dashboard. request_status_for_file will retrieve status
  for an individual file, with the optional parameter of which job you want the
  file's recovery status for. request_status_for_job will retrieve a summary of
  the job along with status totals. See the task's 'schemas' folder and the
  README.md files for more information and examples.
- *ORCA-157* Modified terraform module to add two SQS queues required by
  *copy_files_to_archive* lambda function. The first queue will be used by
  *copy_files_to_archive* lambda to get necessary information needed for copying
  next files. The second queue will be used by *copy_files_to_archive* lambda to
  write database status updates.
- Deployment and development documentation has been created for ORCA.
- *ORCA-119* Added new script *bin/create_release_documentation.sh* to deploy the
  documentation when the **RELEASE_FLAG** is set to `true` in Bamboo pipeline.

### Changed
- Glacier buckets meant for the ORCA archive now should be a type of orca instead of glacier. `{ my-orca-bucket = { name = "orca-primary-bucket", type = "orca" } }`.
- The `copy_to_glacier` lambda now requires a `ORCA_DEFAULT_BUCKET` variable to be set.
- Terraform variables have been renamed and updated to better match Cumulus and identify optional and required ORCA variables. The table below shows the changes and mappings to the new names.
  | Old Variable Name              | New Variable Name                                        | Notes                           |
  | ------------------------------ | -------------------------------------------------------- | ------------------------------- |
  | copy_retry_sleep_secs          | orca_recovery_retry_interval                             | Updated to better reflect back off and retry logic |
  | database_app_user              | REMOVED                                                  | This variable is actually a static value and has been removed. |
  | database_name                  | REMOVED                                                  | This variable is actually a static value and has been removed. |
  | ddl_dir                        | REMOVED                                                  | This variable is actually a static value and has been removed. |
  | default_tags                   | tags                                                     | Renamed to match the Cumulus `tags` variable. |
  | drop_database                  | REMOVED                                                  | This has been removed and should only be used for development work. |
  | lambda_timeout                 | orca_ingest_lambda_timeout, orca_recovery_lambda_timeout | Timeout variables have been broken out per usages. |
  | platform                       | REMOVED                                                  | This was used for development and debugging. The variable is no longer needed and has been removed. |
  | profile                        | aws_profile                                              | Updated to better reflect the variable value comes from the Cumulus variable. |
  | restore_complete_filter_prefix | orca_recovery_complete_filter_prefix                     | Updated to show ORCA branding. |
  | subnet_ids                     | lambda_subnet_ids                                        | Updated to better reflect the variable value comes from the Cumulus variable. |
- The following new variables have been added to the terraform deploy. More information is available in the deployment documentation.
  | Variable Name                    | Notes                           |
  | -------------------------------- | ------------------------------- |
  | system_bucket                    | *REQUIRED*: This variable manages where configuration files are managed in AWS for the deployment. |
  | orca_default_bucket              | *REQUIRED*: This variable has the user set the default ORCA glacier bucket backups should go to. |
  | orca_ingest_lambda_memory_size   | *OPTIONAL*: Allows a user to change the max memory allocation for the `copy_to_glacier` lambda. |
  | orca_ingest_lambda_timeout       | *OPTIONAL*: Allows a user to change the timeout for the `copy_to_glacier` lambda. |
  | orca_recovery_buckets            | *OPTIONAL*: Allows users to narrowly define which buckets ORCA can restore back to. |
  | orca_recovery_expiration_days    | *OPTIONAL*: Allows a user to change the number of days a recovered file remains in S3 before being put back in glacier. |
  | orca_recovery_lambda_memory_size | *OPTIONAL*: Allows a user to change the max memory allocation for the `copy_to_archive` lambda. |
  | orca_recovery_lambda_timeout     | *OPTIONAL*: Allows a user to change the timeout for the `copy_to_archive` lambda. |
  | orca_recovery_retry_limit        | *OPTIONAL*: Allows a user to change the recovery workflow and lambdas retry limit. |
  | orca_recovery_retry_interval     | *OPTIONAL*: Allows a user to change the recovery workflow and lambdas interval to sleep between retries. |
- Task and module build scripts have been updated to better display error information and documented to the actual steps being performed.
- Documentation has been updated to better provide end users with information on ORCA.
- *ORCA-109* request_files now uses SQS queue for recovery status updates, and receives input from a separate SQS queue.
- *ORCA-91* copy_files_to_archive now uses SQS queue for recovery status updates. Will generate a job_id if none is given, and return it in the output.
- request_files now uses the same default glacier bucket as copy_to_glacier.
- *ORCA-172* db_deploy lambda now will migrate the database or create a new orca database based off of the presence of certain objects in the database. This has led to the addition/removal of environment variables and updates to the task documentation (README.md) and ORCA website documentation for architecture and ORCA schema information. The lambda has been modified to add future migrations.

### Deprecated
- None

### Removed
- The `request_status` lambda under */tasks* is removed since it is replaced by the `requests_status_for_job` 
  and `request_status_for_granule` lambdas. The terraform modules, shell scripts and variables related to the lambda are also removed.

### Fixed
- Updated IAM policies to better include all buckets by type instead of looking at the bucket variable key name.

### Security
- None


## [v2.0.1] 2021-2-5

### Changed
* *ORCA-125* BucketOwnerFullControl ACL is now set on for storage PUT requests in the copy_to_glacier lambda. This prevents errors during cross account (OU) copying of data.

## [v2.0.0] 2021-1-15

### Migration Notes
* *ORCA-67* The expected input/output of the copy_to_glacier lambda has been changed. See how to adopt these changes in
your Cumulus workflow [here](https://github.com/nasa/cumulus-orca/tree/master/tasks/copy_to_glacier).
* *ORCA-61* We now support collection-level configuration to exclude specific file-types from your glacier archive (when using
the copy_to_glacier lambda). See how to configure this for your collections [here](https://github.com/nasa/cumulus-orca/tree/master/tasks/copy_to_glacier#exclude-files-by-extension).

### Added
* *ORCA-58* ORCA user facing documentation
  * Docusaurus documentation website framework initialized and created
  * Initial content migrated off of wiki and into markdown pages for end users to view ORCA documentation with no wiki access.
  * Updates to README with starting the documentation server.
* *ORCA-61* Support dynamic configuration of files to exclude from glacier archive
  * Configured in a collection.meta configuration
* *ORCA-67* Generalize input/output scheme of copy_to_glacier lambda so it can be used more easily
in a Cumulus workflow.

### Changed
* *ORCA-68* Update DB tests to use mocking instead of real Postgres DB.
* *ORCA-70* As a DAAC we would like to be able to deploy multiple instances in our sandbox account.
  * Moves secret storage from SSM parameter store to secrets manager and adds a prefix to the keys.
* *ORCA-74* Move integration tests into their own files.


## [v1.0.0] 2020-12-4

### Migration Notes
None - this is the baseline release.

### Added
* *Misc*
  * Unit test upgrades - mocking unnecessary dependencies.
  * Code formatting and styling
* *ORCA-65* Copy Lambda
  * We're including a copy lambda in the v1.0.0 release. The use of this lambda function is optional and explained in the task readme/documentation.
* *ORCA-33* Automated Building/Testing Updates
  * Created some bash scripts for use in the Bamboo build.
  * Updated requirements-dev.txt files for each task and moved the testing framework from nosetest (no longer supported) to coverage and pytest. 
  * Support in GitHub for automated build/test/release via Bamboo
  * Use `coverage` and `pytest` for coverage/testing

### Changed
