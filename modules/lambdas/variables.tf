variable "prefix" {
  type    = string
  default = "orca"
}


variable "subnet_ids" {}



variable "database_port" {
  default = "5432"
}


variable "database_name" {
  default = "orca"
}

variable "database_app_user" {}


variable "ddl_dir" {
  default = "ddl/"
  description = "Must have trailing /"
}

variable "drop_database" {
  //TODO Maybe this needs to be a boolean false?
  default = "False"
}

variable "platform" {
  default = "AWS"
}

variable "buckets" {
  type    = map(object({ name = string, type = string }))
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


variable "vpc_id" {
  type = string
}

variable "lambda_timeout" {
  type = number
  default = 300
}
variable "restore_complete_filter_prefix" {
  default = "orca"
}
variable "profile" {
  default = "default"
}
variable "tags" {}
variable "permissions_boundary_arn" {}