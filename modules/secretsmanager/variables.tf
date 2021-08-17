# Variables obtained by Cumulus deployment
# Should exist in https://github.com/nasa/cumulus-template-deploy/blob/master/cumulus-tf/variables.tf
# REQUIRED
variable "aws_profile" {
  type        = string
  description = "AWS profile used to deploy the terraform application."
}

variable "prefix" {
  type        = string
  description = "Prefix used to prepend to all object names and tags."
}

variable "region" {
  type        = string
  description = "AWS region to deploy configuration to."
}


variable "tags" {
  type        = map(string)
  description = "Tags to be applied to resources that support tags."
}

## Variables unique to ORCA

variable "db_deploy_arn" {
  type        = string
  description = "AWS ARN of the db_deploy lambda used to create/modify the DB."
}

variable "db_deploy_source_code_hash" {
  type        = string
  description = "Base 64 SHA-256 hash of the db_deploy lambda used to create/modify the DB."
}

## variables related to DB and secretsmanager

variable "database_admin_name" {
  description = "Name of RDS database administrator authentication"
  type        = string
}

variable "db_admin_username" {
  description = "Username for RDS database administrator authentication"
  type        = string
}
variable "db_admin_password" {
  description = "Password for RDS database administrator authentication"
  type        = string
}
variable "database_user_name" {
  description = "Name of RDS database user authentication"
  type        = string
}

variable "db_user_username" {
  description = "Username for RDS database user authentication"
  type        = string
}
variable "db_user_password" {
  description = "Password for RDS database user authentication"
  type        = string
}
variable "database_port" {
  type        = number
  description = "Database port that PostgreSQL traffic will be allowed on."
}

variable "db_host_endpoint" {
  type        = string
  description = "Database host endpoint to connect to."
}

## OPTIONAL (DO NOT CHANGE!) - Development use only
## Default variable value is set in ../main.tf to disallow any modification.
variable "database_name" {
  type        = string
  description = "Name of the ORCA database in PostgreSQL"
}