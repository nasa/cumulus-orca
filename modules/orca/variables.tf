variable "prefix" {
  default = "dr"
}


variable "vpc_id" {}

//
variable "restore_complete_filter_prefix" {
  default = ""
}

variable "permissions_boundary_arn" {}

variable "subnet_ids" {}


variable "profile" {
  default = "default"
}

variable "region" {
  default = "us-west-2"
}

variable "restore_expire_days" {
  default = 5
}

variable "restore_request_retries" {
  default = 3
}

variable "restore_retry_sleep_secs" {
  default = 0
}

variable "restore_retrieval_type" {
  default = "Standard"
}

variable "copy_retries" {
  default = 3
}

variable "copy_retry_sleep_secs" {
  default = 0
}

variable "database_port" {
  default = "5432"
}

variable "postgres_user_pw" {}

variable "database_name" {
  default = "disaster_recovery"
}

variable "database_app_user" {
  default = "druser"
}

variable "database_app_user_pw" {}


variable "ddl_dir" {
  default = "ddl/"
}
variable "drop_database" {
  //TODO Maybe this needs to be a boolean false?
  default = "False"
}

variable "platform" {
  default = "AWS"
}
variable "lambda_timeout" {
  default = 300
}

variable "workflow_config" {}

variable "buckets" {
  type = map(object({ name = string, type = string }))
}

variable "default_tags" {
  type = object({ team : string, application : string })
  default = {
    team : "DR",
    application : "disaster-recovery"
  }
}

## Variables unique to ORCA
## OPTIONAL
variable "sqs_delay_time" {
  description = "The time in seconds that the delivery of all messages in the queue will be delayed."
  type        = number
}

variable "sqs_maximum_message_size" {
  type        = number
  description = "The limit of how many bytes a message can contain before Amazon SQS rejects it. "
}

variable "staged_recovery_queue_message_retention_time" {
  type        = number
  description = "The number of seconds staged-recovery-queue fifo SQS retains a message in seconds. Maximum value is 14 days."
}

variable "status_update_queue_message_retention_time" {
  type        = number
  description = "The number of seconds status_update_queue SQS retains a message in seconds. Maximum value is 14 days."
}