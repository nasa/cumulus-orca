## Variables obtained by Cumulus deployment
## Should exist in https://github.com/nasa/cumulus-template-deploy/blob/master/cumulus-tf/variables.tf
## REQUIRED
variable "prefix" {
  type        = string
  description = "Prefix used to prepend to all object names and tags."
}

variable "system_bucket" {
  type        = string
  description = "Cumulus system bucket used to store internal files."
}


## OPTIONAL
variable "tags" {
  type        = map(string)
  description = "Tags to be applied to resources that support tags."
  default     = {}
}


## Variables unique to ORCA
## REQUIRED
variable "orca_lambda_copy_to_archive_arn" {
  type        = string
  description = "AWS ARN for the copy_to_archive lambda."
}

variable "orca_step_function_role_arn" {
  type        = string
  description = "AWS ARN of the role for step functions."
}