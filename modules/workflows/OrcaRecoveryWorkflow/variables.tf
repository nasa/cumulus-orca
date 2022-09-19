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


variable "workflow_config" {
  # https://github.com/nasa/cumulus/blob/master/tf-modules/workflow/variables.tf#L23
  description = "Configuration object with ARNs for workflow integration (Role ARN for executing workflows and Lambda ARNs to trigger on workflow execution)"
  type = object({
    sf_event_sqs_to_db_records_sqs_queue_arn = string
    sf_semaphore_down_lambda_function_arn    = string
    state_machine_role_arn                   = string
    sqs_message_remover_lambda_function_arn  = string
  })
}


## OPTIONAL
variable "tags" {
  type        = map(string)
  description = "Tags to be applied to resources that support tags."
  default     = {}
}


## Variables unique to ORCA
## REQUIRED
variable "orca_default_bucket" {
  type        = string
  description = "Default archive bucket to use if no overrides exist."
}


variable "orca_lambda_extract_filepaths_for_granule_arn" {
  type        = string
  description = "AWS ARN of the ORCA extract_filepaths_for_granule lambda"
}


variable "orca_lambda_request_files_arn" {
  type        = string
  description = "AWS ARN of the ORCA request_files lambda."
}