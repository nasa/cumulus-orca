## Variables obtained by Cumulus deployment
## Should exist in https://github.com/nasa/cumulus-template-deploy/blob/master/cumulus-tf/variables.tf
## REQUIRED
variable "aws_profile" {
  type        = string
  description = "AWS profile used to deploy the terraform application."
  default     = null
}


variable "lambda_subnet_ids" {
  type        = list(string)
  description = "List of subnets the lambda functions have access to."
}


variable "prefix" {
  type        = string
  description = "Prefix used to prepend to all object names and tags."
}


## OPTIONAL
variable "region" {
  type        = string
  description = "AWS region to deploy configuration to."
  default     = "us-west-2"
}


variable "tags" {
  type        = map(string)
  description = "Tags to be applied to resources that support tags."
  default     = {}
}


## Variables unique to ORCA
## REQUIRED
variable "database_app_user_pw" {
  type        = string
  description = "ORCA application database user password."
}


variable "db_deploy_arn" {
  type        = string
  description = "AWS ARN of the db_deploy lambda used to create/modify the DB."
}


variable "db_deploy_source_code_hash" {
  type        = string
  description = "Base 64 SHA-256 hash of the db_deploy lambda used to create/modify the DB."
}


variable "postgres_user_pw" {
  type        = string
  description = "postgres database user password."
}


variable "vpc_postgres_ingress_all_egress_id" {
  description = "The security group of postgres egress ingress"
}


## OPTIONAL
variable "database_port" {
  type        = number
  description = "Database port that PostgreSQL traffic will be allowed on."
  default     = 5432
}


## OPTIONAL (DO NOT CHANGE!) - Development use only
variable "database_name" {
  type        = string
  description = "Name of the ORCA database in PostgreSQL"
  default     = "disaster_recovery"
}