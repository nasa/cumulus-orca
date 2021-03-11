## Variables obtained by Cumulus deployment
## Should exist in https://github.com/nasa/cumulus-template-deploy/blob/master/cumulus-tf/variables.tf
## REQUIRED
variable "aws_profile" {
  type        = string
  description = "AWS profile used to deploy the terraform application."
  default     = null
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


## OPTIONAL
variable "region" {
  type        = string
  description = "AWS region to deploy configuration to."
  default     = "us-west-2"
}


variable "tags" {
  type        = map(string)
  description = "Tags to be applied to resources that support tags."
  default     = {}
}


## Variables unique to ORCA
## REQUIRED
variable "orca_default_bucket" {
  type        = string
  description = "Default ORCA S3 Glacier bucket to use if no overrides exist."
}


## OPTIONAL
variable "database_port" {
  type        = number
  description = "Database port that PostgreSQL traffic will be allowed on."
  default     = 5432
}


variable "orca_ingest_lambda_memory_size" {
  type        = number
  description = "Amount of memory in MB the ORCA copy_to_glacier lambda can use at runtime."
  default     = 2240
}


variable "orca_ingest_lambda_timeout" {
  type        = number
  description = "Timeout in number of seconds for ORCA copy_to_glacier lambda."
  default     = 600
}


variable "orca_recovery_buckets" {
  type        = list(string)
  description = "List of bucket names that ORCA has permissions to restore data to."
  default     = []
}


variable "orca_recovery_complete_filter_prefix" {
  type        = string
  description = "Specifies object key name prefix by the Glacier Bucket trigger."
  default     = ""
}


variable "orca_recovery_expiration_days" {
  type        = number
  description = "Number of days a recovered file will remain available for copy."
  default     = 5
}


variable "orca_recovery_lambda_memory_size" {
  type        = number
  description = "Amount of memory in MB the ORCA recovery lambda can use at runtime."
  default     = 128
}


variable "orca_recovery_lambda_timeout" {
  type        = number
  description = "Timeout in number of seconds for ORCA recovery lambdas."
  default     = 300
}


variable "orca_recovery_retry_limit" {
  type        = number
  description = "Maximum number of retries of a recovery failure before giving up."
  default     = 3
}


variable "orca_recovery_retry_interval" {
  type        = number
  description = "Number of seconds to wait between recovery failure retries."
  default     = 1
}


## OPTIONAL (DO NOT CHANGE!) - Development use only
variable "database_app_user" {
  type        = string
  description = "Name of the database application user."
  default     = "druser"
}


variable "database_name" {
  type        = string
  description = "Name of the ORCA database in PostgreSQL"
  default     = "disaster_recovery"
}


variable "ddl_dir" {
  type        = string
  description = "Location of database DDL SQL files. Must have trailing /."
  default     = "ddl/"
}


variable "drop_database" {
  ##TODO: Maybe this needs to be a boolean false?
  type        = string
  description = "Boolean True/False that indicates the ORCA databse should be dropped."
  default     = "False"
}


variable "orca_recovery_retrieval_type" {
  type        = string
  description = "AWS glacier recovery type to use. One of Bulk, Standard, Express."
  default     = "Standard"
}


variable "platform" {
  type        = string
  description = "String that determines deployment platform. AWS or local."
  default     = "AWS"
}