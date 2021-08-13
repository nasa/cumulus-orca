## Variables obtained by Cumulus deployment
## Should exist in https://github.com/nasa/cumulus-template-deploy/blob/master/cumulus-tf/variables.tf
## REQUIRED
variable "buckets" {
  type        = map(object({ name = string, type = string }))
  description = "S3 bucket locations for the various storage types being used."
}


variable "permissions_boundary_arn" {
  type        = string
  description = "AWS ARN value for the permission boundary."
}


variable "prefix" {
  type        = string
  description = "Prefix used to prepend to all object names and tags."
}


variable "tags" {
  type        = map(string)
  description = "Tags to be applied to resources that support tags."
}


## Variables unique to ORCA
## REQUIRED


## OPTIONAL - Default variable value is set in ../main.tf to disallow any modification.
variable "orca_recovery_buckets" {
  type        = list(string)
  description = "List of bucket names that ORCA has permissions to restore data to."
}