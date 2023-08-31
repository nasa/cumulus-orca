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
variable "orca_lambda_get_current_archive_list_arn" {
  type        = string
  description = "AWS ARN of the ORCA get_current_archive_list lambda"
}

variable "orca_lambda_perform_orca_reconcile_arn" {
  type        = string
  description = "AWS ARN of the ORCA perform_orca_reconcile lambda."
}

variable "orca_step_function_role_arn" {
  type        = string
  description = "AWS ARN of the role for step functions."
}