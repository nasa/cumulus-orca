## Variables obtained by Cumulus deployment
## Should exist in https://github.com/nasa/cumulus-template-deploy/blob/master/cumulus-tf/variables.tf
## REQUIRED
variable "aws_profile" {
  type    = string
  description = "AWS profile used to deploy the terraform application."
  default = null
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
## OPTIONAL
variable "database_port" {
  type        = number
  description = "Database port that PostgreSQL traffic will be allowed on."
  default     = 5432
}