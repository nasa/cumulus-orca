## Variables obtained by Cumulus deployment
## Should exist in https://github.com/nasa/cumulus-template-deploy/blob/master/cumulus-tf/variables.tf
## REQUIRED
variable "prefix" {
  type        = string
  description = "Prefix used to prepend to all object names and tags."
}

## OPTIONAL - Default variable value is set in ../variables.tf to keep default values centralized.
variable "tags" {
  type        = map(string)
  description = "Tags to be applied to resources that support tags."
}

## Variables unique to ORCA
## OPTIONAL
variable "internal_report_queue_message_retention_time_seconds" {
  type        = number
  description = "The number of seconds internal-report-queue SQS retains a message in seconds. Maximum value is 14 days."
}

variable "metadata_queue_message_retention_time_seconds" {
  type        = number
  description = "The number of seconds metadata-queue fifo SQS retains a message in seconds. Maximum value is 14 days."
}

variable "orca_reconciliation_lambda_timeout" {
  type        = number
  description = "Timeout in number of seconds for ORCA reconciliation lambdas."
}

variable "orca_reports_bucket_name" {
  type        = string
  description = "The name of the bucket to store s3 inventory reports."
}

variable "s3_inventory_queue_message_retention_time_seconds" {
  type        = number
  description = "The number of seconds s3-inventory-queue fifo SQS retains a message in seconds. Maximum value is 14 days."
}

variable "sqs_delay_time_seconds" {
  type        = number
  description = "The time in seconds that the delivery of all messages in the queue will be delayed."
}

variable "sqs_maximum_message_size" {
  type        = number
  description = "The limit of how many bytes a message can contain before Amazon SQS rejects it. "
}

variable "staged_recovery_queue_message_retention_time_seconds" {
  type        = number
  description = "The number of seconds staged-recovery-queue fifo SQS retains a message in seconds. Maximum value is 14 days."
}

variable "status_update_queue_message_retention_time_seconds" {
  type        = number
  description = "The number of seconds status_update_queue SQS retains a message in seconds. Maximum value is 14 days."
}

variable "archive_recovery_queue_message_retention_time_seconds" {
  type        = number
  description = "The number of seconds archive-recovery-queue SQS retains a message in seconds. Maximum value is 14 days."
}

variable "dlq_subscription_email" {
  type        = string
  description = "The email to notify users when messages are received in dead letter SQS queue due to restore failure. Sends one email until the dead letter queue is emptied."
}