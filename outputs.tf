## Module outputs
## =============================================================================

## RDS Module outputs
## =============================================================================
output "orca_rds_address" {
  description = "The address of the RDS instance"
  value       = module.orca.orca_rds.address
}


output "orca_rds_arn" {
  description = "The ARN of the RDS instance"
  value       = module.orca.orca_rds.arn
}


output "orca_rds_availability_zone" {
  description = "The availability zone of the RDS instance"
  value       = module.orca.orca_rds.availability_zone
}


output "orca_rds_endpoint" {
  description = "The connection endpoint in address:port format"
  value       = module.orca.orca_rds.endpoint
}


output "orca_rds_hosted_zone_id" {
  description = "The canonical hosted zone ID of the DB instance (to be used in a Route 53 Alias record)"
  value       = module.orca.orca_rds.hosted_zone_id
}


output "orca_rds_id" {
  description = "The RDS instance ID"
  value       = module.orca.orca_rds.id
}


output "orca_rds_resource_id" {
  description = "The RDS Resource ID of this instance"
  value       = module.orca.orca_rds.resource_id
}


output "orca_rds_status" {
  description = "The RDS instance status"
  value       = module.orca.orca_rds.status
}


output "orca_rds_name" {
  description = "The database name"
  value       = module.orca.orca_rds.name
}


output "orca_rds_username" {
  description = "The master username for the database"
  value       = module.orca.orca_rds.username
}


output "orca_rds_port" {
  description = "The database port"
  value       = module.orca.orca_rds.port
}


output "orca_subnet_group_id" {
  description = "The db subnet group name"
  value       = module.orca.orca_subnet_group.id
}


output "orca_subnet_group_arn" {
  description = "The ARN of the subnet group"
  value       = module.orca.orca_subnet_group.arn
}


## Lambda Module outputs
## =============================================================================
# Ingest Lambdas
# ------------------------------------------------------------------------------
output "orca_lambda_copy_to_glacier_cumulus_translator_arn" {
  description = "AWS ARN of the ORCA copy_to_glacier_cumulus_translator lambda."
  value       = module.orca.orca_lambda_copy_to_glacier_cumulus_translator_arn
}

output "orca_lambda_copy_to_glacier_arn" {
  description = "AWS ARN of the ORCA copy_to_glacier lambda."
  value       = module.orca.orca_lambda_copy_to_glacier_arn
}


# Recovery Lambdas
# ------------------------------------------------------------------------------
output "orca_lambda_extract_filepaths_for_granule_arn" {
  description = "AWS ARN of the ORCA extract_filepaths_for_granule lambda."
  value       = module.orca.orca_lambda_extract_filepaths_for_granule_arn
}


output "orca_lambda_request_files_arn" {
  description = "AWS ARN of the ORCA request_files lambda."
  value       = module.orca.orca_lambda_request_files_arn
}


output "orca_lambda_copy_files_to_archive_arn" {
  description = "AWS ARN of the ORCA copy_files_to_archive lambda."
  value       = module.orca.orca_lambda_copy_files_to_archive_arn
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
