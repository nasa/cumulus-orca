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


## OPTIONAL - Default variable value is set in ../variables.tf to keep default values centralized.
variable "tags" {
  type        = map(string)
  description = "Tags to be applied to resources that support tags."
}


## Variables unique to ORCA
## REQUIRED
variable "orca_default_bucket" {
  type        = string
  description = "Default archive bucket to use if no overrides exist."
}

variable "orca_lambda_copy_to_archive_arn" {
  type        = string
  description = "AWS ARN for the copy_to_archive lambda."
}

variable "orca_lambda_extract_filepaths_for_granule_arn" {
  type        = string
  description = "AWS ARN of the ORCA extract_filepaths_for_granule lambda"
}

variable "orca_lambda_get_current_archive_list_arn" {
  type        = string
  description = "AWS ARN of the ORCA get_current_archive_list lambda"
}

variable "orca_lambda_perform_orca_reconcile_arn" {
  type        = string
  description = "AWS ARN of the ORCA orca_perform_orca_reconcile lambda"
}

variable "orca_lambda_request_from_archive_arn" {
  type        = string
  description = "AWS ARN of the ORCA request_from_archive lambda."
}

variable "orca_step_function_role_arn" {
  type        = string
  description = "AWS ARN of the role for step functions."
}