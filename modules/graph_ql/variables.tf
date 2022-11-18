## Variables obtained by Cumulus deployment
## Should exist in https://github.com/nasa/cumulus-template-deploy/blob/master/cumulus-tf/variables.tf
## REQUIRED
variable "lambda_subnet_ids" {
  type        = list(string)
  description = "List of subnets the lambda functions have access to."
}

variable "permissions_boundary_arn" {
  type        = string
  description = "AWS ARN value for the permission boundary."
}

variable "prefix" {
  type        = string
  description = "Prefix used to prepend to all object names and tags."
}

variable "vpc_id" {
  type        = string
  description = "Virtual Private Cloud AWS ID"
}

## OPTIONAL
variable "tags" {
  type        = map(string)
  description = "Tags to be applied to resources that support tags."
}

## Variables unique to ORCA
## REQUIRED
variable "db_connect_info_secret_arn" {
  type        = string
  description = "Secret ARN of the AWS secretsmanager secret for connecting to the database."
}

variable "ecs_cluster_id" {
  type        = string
  description = "ID of the ECS cluster in AWS."
}