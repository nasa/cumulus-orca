variable "prefix" {}

variable "workflow_config" {}
variable "system_bucket" {}

variable "tags" {}
variable "extract_filepaths_lambda_arn" {}
variable "request_files_lambda_arn" {}
variable "name" {
  type = string
  default = "DrRecoveryWorkflow"
}