## Variables obtained by Cumulus deployment
## Should exist in https://github.com/nasa/cumulus-template-deploy/blob/master/cumulus-tf/variables.tf
## REQUIRED
variable "buckets" {
  type        = map(object({ name = string, type = string }))
  description = "S3 bucket locations for the various storage types being used."
}
variable "lambda_subnet_ids" {
  type        = list(string)
  description = "List of subnets the lambda functions have access to."
}


variable "prefix" {
  type        = string
  description = "Prefix used to prepend to all object names and tags."
}


variable "rds_security_group_id" {
  type        = string
  description = "Cumulus' RDS Security Group's ID."
}


variable "vpc_id" {
  type        = string
  description = "Virtual Private Cloud AWS ID"
}


## OPTIONAL
variable "tags" {
  type        = map(string)
  description = "Tags to be applied to resources that support tags."
}


variable "default_multipart_chunksize_mb" {
  type        = number
  description = "The default maximum size of chunks to use when copying. Can be overridden by collection config."
}


## Variables unique to ORCA
## REQUIRED

variable "db_connect_info_secret_arn" {
  type        = string
  description = "Secret ARN of the AWS secretsmanager secret for connecting to the database."
}

variable "orca_default_bucket" {
  type        = string
  description = "Default archive bucket to use if no overrides exist."
}

variable "orca_sqs_archive_recovery_queue_arn" {
  type        = string
  description = "The ARN of the archive-recovery-queue SQS"
}

variable "orca_sqs_archive_recovery_queue_id" {
  type        = string
  description = "The SQS URL that triggers post_copy_request_to_queue upon successful object restore from archive bucket. Also receives input from request_from_archive for files already recovered."
}

variable "orca_sqs_internal_report_queue_id" {
  type        = string
  description = "The URL of the internal-report-queue SQS"
}

variable "orca_sqs_metadata_queue_arn" {
  type        = string
  description = "The ARN of the metadata-queue SQS"
}

variable "orca_sqs_metadata_queue_id" {
  type        = string
  description = "The URL of the metadata-queue SQS"
}

variable "orca_sqs_s3_inventory_queue_id" {
  type        = string
  description = "The URL of the s3-inventory-queue SQS"
}

variable "orca_sqs_staged_recovery_queue_arn" {
  type        = string
  description = "The ARN of the staged-recovery-queue SQS"
}

variable "orca_sqs_staged_recovery_queue_id" {
  type        = string
  description = "SQS URL of recovery queue."
}

variable "orca_sqs_status_update_queue_arn" {
  type        = string
  description = "The ARN of the SQS queue that recovery status updates are read from/posted to."
}

variable "orca_sqs_status_update_queue_id" {
  type        = string
  description = "The URL of the SQS queue that recovery status updates are read from/posted to."
}

variable "permissions_boundary_arn" {
  type        = string
  description = "AWS ARN value for the permission boundary."
}

variable "restore_object_role_arn" {
  type        = string
  description = "AWS ARN of the restore_object_role."
}

## OPTIONAL - Default variable value is set in ../variables.tf to keep default values centralized.
variable "orca_default_recovery_type" {
  type        = string
  description = "The Tier for the restore request. Valid values are 'Standard'|'Bulk'|'Expedited'."
}


variable "orca_default_storage_class" {
  type        = string
  description = "The class of storage to use when ingesting files. Can be overridden by collection config. Must match value in storage_class table."
}


variable "orca_delete_old_reconcile_jobs_frequency_cron" {
  type        = string
  description = "Frequency cron for running the delete_old_reconcile_jobs lambda."
}


variable "orca_ingest_lambda_memory_size" {
  type        = number
  description = "Amount of memory in MB the ORCA copy_to_archive lambda can use at runtime."
}


variable "orca_ingest_lambda_timeout" {
  type        = number
  description = "Timeout in number of seconds for ORCA copy_to_archive lambda."
}


variable "orca_internal_reconciliation_expiration_days" {
  type        = number
  description = "Only reports updated before this many days ago will be deleted."
}


variable "orca_reconciliation_lambda_memory_size" {
  type        = number
  description = "Amount of memory in MB the ORCA reconciliation lambda can use at runtime."
}


variable "orca_reconciliation_lambda_timeout" {
  type        = number
  description = "Timeout in number of seconds for ORCA reconciliation lambdas."
}


variable "orca_recovery_buckets" {
  type        = list(string)
  description = "List of bucket names that ORCA has permissions to restore data to."
}


variable "orca_recovery_complete_filter_prefix" {
  type        = string
  description = "Specifies object key name prefix by the archive bucket trigger."
}


variable "orca_recovery_expiration_days" {
  type        = number
  description = "Number of days a recovered file will remain available for copy."
}


variable "orca_recovery_lambda_memory_size" {
  type        = number
  description = "Amount of memory in MB the ORCA recovery lambda can use at runtime."
}


variable "orca_recovery_lambda_timeout" {
  type        = number
  description = "Timeout in number of seconds for ORCA recovery lambdas."
}


variable "orca_recovery_retry_limit" {
  type        = number
  description = "Maximum number of retries of a recovery failure before giving up."
}


variable "orca_recovery_retry_interval" {
  type        = number
  description = "Number of seconds to wait between recovery failure retries."
}


variable "orca_recovery_retry_backoff" {
  type        = number
  description = "The multiplier by which the retry interval increases during each attempt."
}


variable "log_level" {
  type        = string
  description = "sets the verbose of PowerTools logger. Must be one of 'INFO', 'DEBUG', 'WARN', 'ERROR'. Defaults to 'INFO'."
}