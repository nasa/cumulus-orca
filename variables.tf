variable "prefix" {
  default = "dr"
}

variable "vpc_id" {
  default = ""
}

variable "restore_complete_filter_prefix" {
  default = ""
}

variable "glacier_bucket" {
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

variable "ngap_subnets" {
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

variable "database_host" {
  default = ""
}

variable "database_port" {
  default = "5432"
}

variable "postgres_user_pw" {
  default = ""
}

variable "database_name" {
  default = "disaster_recovery"
}

variable "database_app_user" {
  default = "druser"
}

variable "database_app_user_pw" {
  default = ""
}

variable "ddl_dir" {
  default = "ddl/"
}

variable "drop_database" {
  default = "False"
}

variable "platform" {
  default = "AWS"
}

variable "default_tags" {
  type = "map"
  default = {
    team: "DR",
    application: "disaster-recovery"
  }
}
