## Module outputs
## =============================================================================

## Lambda Module outputs
## =============================================================================
# Ingest Lambdas
# ------------------------------------------------------------------------------
output "orca_lambda_copy_to_archive_arn" {
  description = "AWS ARN of the ORCA copy_to_archive lambda."
  value       = module.orca.orca_lambda_copy_to_archive_arn
}


# Recovery Lambdas
# ------------------------------------------------------------------------------
output "orca_lambda_extract_filepaths_for_granule_arn" {
  description = "AWS ARN of the ORCA extract_filepaths_for_granule lambda."
  value       = module.orca.orca_lambda_extract_filepaths_for_granule_arn
}


output "orca_lambda_orca_catalog_reporting_arn" {
  description = "AWS ARN of the ORCA orca_catalog_reporting lambda."
  value       = module.orca.orca_lambda_orca_catalog_reporting_arn
}


output "orca_lambda_request_from_archive_arn" {
  description = "AWS ARN of the ORCA request_from_archive lambda."
  value       = module.orca.orca_lambda_request_from_archive_arn
}


output "orca_lambda_copy_from_archive_arn" {
  description = "AWS ARN of the ORCA copy_from_archive lambda."
  value       = module.orca.orca_lambda_copy_from_archive_arn
}

output "orca_lambda_request_status_for_granule_arn" {
  description = "AWS ARN of the ORCA request_status_for_granule lambda."
  value       = module.orca.orca_lambda_request_status_for_granule_arn
}


output "orca_lambda_request_status_for_job_arn" {
  description = "AWS ARN of the ORCA request_status_for_job lambda."
  value       = module.orca.orca_lambda_request_status_for_job_arn
}

output "orca_lambda_post_copy_request_to_queue_arn" {
  description = "AWS ARN of the ORCA post_copy_request_to_queue lambda."
  value       = module.orca.orca_lambda_post_copy_request_to_queue_arn
}

## SQS Module outputs
## =============================================================================
output "orca_sqs_metadata_queue_arn" {
  description = "The ARN of the metadata-queue SQS"
  value       = module.orca.orca_sqs_metadata_queue_arn
}

output "orca_sqs_metadata_queue_id" {
  description = "The URL ID of the metadata-queue SQS"
  value       = module.orca.orca_sqs_metadata_queue_arn
}

output "orca_sqs_staged_recovery_queue_arn" {
  description = "The ARN of the staged-recovery-queue SQS"
  value       = module.orca.orca_sqs_staged_recovery_queue_arn
}

output "orca_sqs_staged_recovery_queue_id" {
  description = "The URL ID of the staged-recovery-queue SQS"
  value       = module.orca.orca_sqs_staged_recovery_queue_id
}

output "orca_sqs_status_update_queue_arn" {
  description = "The ARN of the status-update-queue SQS"
  value       = module.orca.orca_sqs_status_update_queue_arn
}

output "orca_sqs_status_update_queue_id" {
  description = "The URL ID of the status-update-queue SQS"
  value       = module.orca.orca_sqs_status_update_queue_id
}

## Workflow Module Outputs (orca_workflows)
## =============================================================================
output "orca_sfn_recovery_workflow_arn" {
  description = "The ARN of the recovery step function."
  value       = module.orca.orca_sfn_recovery_workflow_arn
}

## Secretsmanager Module outputs
## =============================================================================
output "orca_secretsmanager_arn" {
  description = "The Amazon Resource Name (ARN) of the AWS secretsmanager"
  value       = module.orca.orca_secretsmanager_arn
}

## API gateway Module outputs
## =============================================================================
output "orca_api_deployment_invoke_url" {
  value       = module.orca.orca_api_deployment_invoke_url
  description = "The URL to invoke the ORCA Cumulus reconciliation API gateway. Excludes the resource path"
}

## GraphQL Module Outputs (graphql_0 and graphql_1)
## =============================================================================
output "orca_graphql_load_balancer_dns_name" {
  value       = module.orca.orca_graphql_load_balancer_dns_name
  description = "The DNS Name of the Application Load Balancer that handles access to ORCA GraphQL."
}

output "orca_network_load_balancer_dns_name" {
  value       = module.orca.orca_network_load_balancer_dns_name
  description = "The DNS Name of the Network Load Balancer."
}
