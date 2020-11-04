variable "subnet_ids" {}
variable "prefix" {
  type    = string
  default = "orca"
}

variable "profile" {
  default = "default"
}

variable "postgres_user_pw" {}


variable "database_port" {
  default = "5432"
}

variable "database_name" {
  default = "orca"
}

variable "vpc_postgres_ingress_all_egress_id" {
  description = "The security group of postgres egress ingress"
}

variable "db_lambda_deploy_arn" {}

variable "lambda_source_code_hash" {}
variable "region" {
  default = "us-west-2"
}
variable "default_tags" {}
variable "database_app_user_pw" {}