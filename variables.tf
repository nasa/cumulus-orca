variable "prefix" {
  default = "dr"
}


variable "vpc_id" {
  default = ""
}

//
variable "restore_complete_filter_prefix" {
  default = ""
}

variable "private_bucket" {
  default = ""
}

variable "protected_bucket" {
  default = ""
}

variable "internal_bucket" {
  default = ""
}

variable "public_bucket" {
  default = ""
}

variable "permissions_boundary_arn" {
  default = ""
}

variable "subnet_ids" {
  default = []
}

variable "ngap_sgs" {
  default = []
}

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

variable "database_user_pw" {}

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



variable "default_tags" {
  type = object({ team=string, application=string })
  default = {
    team: "DR",
    application: "disaster-recovery"
  }
}

variable "buckets" {
  type    = map(object({ name = string, type = string }))
}

variable "workflow_config" {
  # https://github.com/nasa/cumulus/blob/master/tf-modules/workflow/variables.tf#L23
  # Used in modules/workflows/main.tf
  description = "Configuration object with ARNs for workflow integration (Role ARN for executing workflows and Lambda ARNs to trigger on workflow execution)"
  type = object({
    sf_event_sqs_to_db_records_sqs_queue_arn = string
    sf_semaphore_down_lambda_function_arn = string
    state_machine_role_arn = string
    sqs_message_remover_lambda_function_arn = string
  })
}
