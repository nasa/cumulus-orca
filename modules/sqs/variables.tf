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
  default     = "us-west-2"
}

variable "tags" {
  type        = map(string)
  description = "Tags to be applied to resources that support tags."
}

## Variables unique to ORCA
## OPTIONAL
variable "sqs_delay_time" {
  type        = number
  default     = 0
}

variable "maximum_message_size" {
  type        = number
  default     = 262144
  description = "The limit of how many bytes a message can contain before Amazon SQS rejects it. "
}

variable "sqs_message_retention_time" {
  type        = number
  default     = 345600 #4 days
  description = "The number of seconds Amazon SQS retains a message in seconds. Maximum value is 14 days."
}
