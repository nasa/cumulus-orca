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
