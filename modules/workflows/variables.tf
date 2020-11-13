variable "prefix" {}

variable "workflow_config" {
  # https://github.com/nasa/cumulus/blob/master/tf-modules/workflow/variables.tf#L23
  description = "Configuration object with ARNs for workflow integration (Role ARN for executing workflows and Lambda ARNs to trigger on workflow execution)"
  type = object({
    sf_event_sqs_to_db_records_sqs_queue_arn = string
    sf_semaphore_down_lambda_function_arn = string
    state_machine_role_arn = string
    sqs_message_remover_lambda_function_arn = string
  })
}
variable "system_bucket" {}

variable "tags" {}
variable "extract_filepaths_lambda_arn" {}
variable "request_files_lambda_arn" {}
variable "name" {
  type = string
  default = "DrRecoveryWorkflow"
}