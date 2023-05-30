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

variable "system_bucket" {
  type        = string
  description = "Cumulus system bucket used to store internal files."
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

variable "gql_ecs_task_execution_role_arn" {
  type        = string
  description = "The ARN of the role used by the ECS Task runnger."
}

variable "gql_ecs_task_execution_role_id" {
  type        = string
  description = "The ID of the role used by the ECS Task runnger."
}

variable "gql_tasks_role_arn" {
  type        = string
  description = "The ARN of the role used by the code within the Graphql ECS Task."
}

variable "s3_access_credentials_secret_arn" {
  type        = string
  description = "The Amazon Resource Name (ARN) of the s3 credentials secret."
}