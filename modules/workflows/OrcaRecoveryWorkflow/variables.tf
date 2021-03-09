## Variables obtained by Cumulus deployment
## Should exist in https://github.com/nasa/cumulus-template-deploy/blob/master/cumulus-tf/variables.tf
## REQUIRED
variable "aws_profile" {
  type        = string
  description = "AWS profile used to deploy the terraform application."
  default     = null
}


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
## REQUIRED
variable "cumulus_version" {
  type        = string
  description = "Cumulus workflow version to use with ORCA. In the form vX.Y.Z"
}


variable "orca_default_bucket" {
  type        = string
  description = "Default ORCA S3 Glacier bucket to use if no overrides exist."
}


variable "orca_lambda_extract_filepaths_for_granule_arn" {
  type        = string
  description = "AWS ARN of the ORCA extract_filepaths_for_granule lambda"
}


variable "orca_lambda_request_files_arn" {
  type        = string
  description = "AWS ARN of the ORCA request_files lambda."
}