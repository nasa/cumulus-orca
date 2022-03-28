## Variables obtained by Cumulus deployment
## Should exist in https://github.com/nasa/cumulus-template-deploy/blob/master/cumulus-tf/variables.tf
## REQUIRED
variable "lambda_subnet_ids" {
  type        = list(string)
  description = "List of subnets the lambda functions have access to."
}

variable "prefix" {
  type        = string
  description = "Prefix used to prepend to all object names and tags."
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
variable "restore_object_role_arn" {
  type        = string
  description = "AWS ARN of the restore_object_role."
}

variable "orca_sfn_internal_reconciliation_workflow_arn" {
  type        = string
  description = "The ARN of the internal_reconciliation step function."
}

variable "orca_sqs_s3_inventory_queue_arn" {
  type        = string
  description = "The ARN of the internal-report-queue SQS"
}

variable "orca_sqs_internal_report_queue_id" {
  type        = string
  description = "The URL of the internal-report-queue SQS"
}

variable "vpc_postgres_ingress_all_egress_id" {
  type        = string
  description = "PostgreSQL security group id"
}


## OPTIONAL - Default variable value is set in ../variables.tf to keep default values centralized.
variable "orca_reconciliation_lambda_memory_size" {
  type        = number
  description = "Amount of memory in MB the ORCA reconciliation lambda can use at runtime."
}


variable "orca_reconciliation_lambda_timeout" {
  type        = number
  description = "Timeout in number of seconds for ORCA reconciliation lambdas."
}

