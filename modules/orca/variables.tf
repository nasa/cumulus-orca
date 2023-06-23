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


variable "permissions_boundary_arn" {
  type        = string
  description = "AWS ARN value for the permission boundary."
}


variable "prefix" {
  type        = string
  description = "Prefix used to prepend to all object names and tags."
}


variable "system_bucket" {
  type        = string
  description = "Cumulus system bucket used to store internal files."
}


variable "vpc_id" {
  type        = string
  description = "Virtual Private Cloud AWS ID"
}


## OPTIONAL - Default variable value is set in ../variables.tf to keep default values centralized.
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
  description = "Default archive bucket to use if no overrides exist."
}

variable "orca_reports_bucket_name" {
  type        = string
  description = "The name of the bucket to store s3 inventory reports."
}


variable "rds_security_group_id" {
  type        = string
  description = "Cumulus' RDS Security Group's ID."
}

variable "dlq_subscription_email" {
  type        = string
  description = "The email to notify users when messages are received in dead letter SQS queue due to restore failure. Sends one email until the dead letter queue is emptied."
}

## OPTIONAL - Default variable value is set in ../variables.tf to keep default values centralized.
variable "archive_recovery_queue_message_retention_time_seconds" {
  type        = number
  description = "The number of seconds archive-recovery-queue SQS retains a message in seconds. Maximum value is 14 days."
}


variable "db_admin_username" {
  description = "Username for RDS database administrator authentication"
  type        = string
}


variable "db_name" {
  description = "The name of the Orca database within the RDS cluster."
  type        = string
}


variable "db_user_name" {
  description = "Username for RDS database user authentication"
  type        = string
}


variable "internal_report_queue_message_retention_time_seconds" {
  type        = number
  description = "The number of seconds internal-report-queue SQS retains a message in seconds. Maximum value is 14 days."
}


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


variable "s3_access_key" {
  type        = string
  description = "Access key for communicating with Orca S3 buckets."
}


variable "s3_inventory_queue_message_retention_time_seconds" {
  type        = number
  description = "The number of seconds s3-inventory-queue fifo SQS retains a message in seconds. Maximum value is 14 days."
}


variable "s3_report_frequency" {
  type        = string
  description = "How often to generate s3 reports for internal reconciliation."
}


variable "s3_secret_key" {
  type        = string
  description = "Secret key for communicating with Orca S3 buckets."
}


variable "sqs_delay_time_seconds" {
  type        = number
  description = "The time in seconds that the delivery of all messages in the queue will be delayed."
}


variable "sqs_maximum_message_size" {
  type        = number
  description = "The limit of how many bytes a message can contain before Amazon SQS rejects it."
}


variable "metadata_queue_message_retention_time_seconds" {
  type        = number
  description = "The number of seconds metadata-queue fifo SQS retains a message in seconds. Maximum value is 14 days."
}


variable "staged_recovery_queue_message_retention_time_seconds" {
  type        = number
  description = "The number of seconds staged-recovery-queue fifo SQS retains a message in seconds. Maximum value is 14 days."
}


variable "status_update_queue_message_retention_time_seconds" {
  type        = number
  description = "The number of seconds status_update_queue SQS retains a message in seconds. Maximum value is 14 days."
}


variable "vpc_endpoint_id" {
  type        = string
  description = "NGAP vpc endpoint id needed to access the api. Defaults to null"
}


variable "log_level" {
  type        = string
  description = "Sets the verbose of powertools logger. Must be one of 'INFO', 'DEBUG', 'WARN', 'ERROR'. Defaults to 'INFO'."
}