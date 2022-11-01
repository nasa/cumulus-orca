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
## OPTIONAL
variable "tags" {
  type        = map(string)
  description = "Tags to be applied to resources that support tags."
}

## Variables unique to ORCA
## REQUIRED
variable "ecs_cluster_id" {
  type        = string
  description = "ID of the ECS cluster in AWS."
}

variable "vpc_postgres_ingress_all_egress_id" {
  type        = string
  description = "PostgreSQL security group id"
}