output "orca_rds" {
  value = module.orca_rds.rds
}

output "orca_subnet_group" {
  value = module.orca_rds.rds_subnet_group
}

output "orca_lambda_extract_filepath_arn" {
  value = module.orca_lambdas.extract_filepath_arn
}

output "orca_lambda_request_files_arn" {
  value = module.orca_lambdas.request_files_arn
}

output "orca_lambda_copy_to_glacier_arn" {
  value = module.orca_lambdas.copy_to_glacier_arn
}

output "orca_sqs_staged_recovery_queue_arn" {
  description = "The ARN of the staged-recovery-queue SQS"
  value       = module.orca_sqs.staged_recovery_queue_arn
}

output "orca_sqs_staged_recovery_queue_id" {
  description = "The URL ID of the staged-recovery-queue SQS"
  value       = module.orca_sqs.staged_recovery_queue_id
}

output "orca_sqs_status_update_queue_arn" {
  description = "The ARN of the status-update-queue SQS"
  value       = module.orca_sqs.status_update_queue_arn
}

output "orca_sqs_status_update_queue_id" {
  description = "The URL ID of the status-update-queue SQS"
  value       = module.orca_sqs.status_update_queue_id
}
