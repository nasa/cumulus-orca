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
## variables related to DB and secretsmanager

variable "database_name" {
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
variable "db_engine" {
  description = "Name of the DB engine."
  type        = string
}
variable "database_port" {
  type        = number
  description = "Database port that PostgreSQL traffic will be allowed on."
}

variable "db_cluster_identifier" {
  type        = string
  description = "DB Itentifier for the RDS cluster that will be created."
}

variable "db_host_endpoint" {
  type        = string
  description = "Database host endpoint to connect to."
}