## Variables obtained by Cumulus deployment
## Should exist in https://github.com/nasa/cumulus-template-deploy/blob/master/cumulus-tf/variables.tf
## REQUIRED
variable "prefix" {
  type        = string
  description = "Prefix used to prepend to all object names and tags."
}


variable "vpc_id" {
  type        = string
  description = "Virtual Private Cloud AWS ID"
}


variable "tags" {
  type        = map(string)
  description = "Tags to be applied to resources that support tags."
}


variable "rds_security_group_id" {
  type        = string
  description = "Cumulus' RDS Security Group's ID."
}