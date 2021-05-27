## Variables obtained by Cumulus deployment
## Should exist in https://github.com/nasa/cumulus-template-deploy/blob/master/cumulus-tf/variables.tf
## REQUIRED
variable "aws_profile" {
  type        = string
  description = "AWS profile used to deploy the terraform application."
}


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


variable "vpc_id" {
  type        = string
  description = "Virtual Private Cloud AWS ID"
}


## OPTIONAL - Default variable value is set in ../variables.tf to keep default values centralized.
variable "region" {
  type        = string
  description = "AWS region to deploy configuration to."
}


variable "tags" {
  type        = map(string)
  description = "Tags to be applied to resources that support tags."
}


## Variables unique to ORCA
## REQUIRED
variable "orca_default_bucket" {
  type        = string
  description = "Default ORCA S3 Glacier bucket to use if no overrides exist."
}


## OPTIONAL - Default variable value is set in ../variables.tf to keep default values centralized.
variable "database_port" {
  type        = number
  description = "Database port that PostgreSQL traffic will be allowed on."
}


variable "orca_ingest_lambda_memory_size" {
  type        = number
  description = "Amount of memory in MB the ORCA copy_to_glacier lambda can use at runtime."
}


variable "orca_ingest_lambda_timeout" {
  type        = number
  description = "Timeout in number of seconds for ORCA copy_to_glacier lambda."
}


variable "orca_recovery_buckets" {
  type        = list(string)
  description = "List of bucket names that ORCA has permissions to restore data to."
}


variable "orca_recovery_complete_filter_prefix" {
  type        = string
  description = "Specifies object key name prefix by the Glacier Bucket trigger."
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

## OPTIONAL (DO NOT CHANGE!) - Development use only
variable "database_app_user" {
  type        = string
  description = "Name of the database application user."
}


variable "database_name" {
  type        = string
  description = "Name of the ORCA database in PostgreSQL"
}

variable "orca_recovery_retrieval_type" {
  type        = string
  description = "AWS glacier recovery type to use. One of Bulk, Standard, Express."
}

variable "orca_sqs_staged_recovery_queue_id" {
  type        = string
  description = "SQS URL of recovery queue."
}

variable "orca_sqs_staged_recovery_queue_arn" {
  type        = string
  description = "The ARN of the staged-recovery-queue SQS"
}

variable "orca_sqs_status_update_queue_arn" {
  type        = string
  description = "The ARN of the status-update-queue SQS"
}

variable "orca_sqs_status_update_queue_id" {
  type        = string
  description = "The URL of the SQS queue that recoery status updates are read from/posted to."
}