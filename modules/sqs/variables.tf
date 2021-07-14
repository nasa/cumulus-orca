## Variables obtained by Cumulus deployment
## Should exist in https://github.com/nasa/cumulus-template-deploy/blob/master/cumulus-tf/variables.tf
## REQUIRED
variable "aws_profile" {
  type        = string
  description = "AWS profile used to deploy the terraform application."
}

variable "prefix" {
  type        = string
  description = "Prefix used to prepend to all object names and tags."
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
## OPTIONAL
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
