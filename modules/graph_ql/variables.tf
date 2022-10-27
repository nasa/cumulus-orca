## Variables obtained by Cumulus deployment
## Should exist in https://github.com/nasa/cumulus-template-deploy/blob/master/cumulus-tf/variables.tf
## REQUIRED
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
variable "permissions_boundary_arn" {
  type        = string
  description = "AWS ARN value for the permission boundary."
}