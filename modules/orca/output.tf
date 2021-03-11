## Lambda Module Outputs (orca_lambda)
## =============================================================================
# Ingest Lambdas
# ------------------------------------------------------------------------------
output "orca_lambda_copy_to_glacier_arn" {
  description = "AWS ARN of the ORCA copy_to_glacier lambda."
  value       = module.orca_lambdas.copy_to_glacier_arn
}


# Recovery Lambdas
# ------------------------------------------------------------------------------
output "orca_lambda_extract_filepaths_for_granule_arn" {
  description = "AWS ARN of the ORCA extract_filepaths_for_granule lambda."
  value       = module.orca_lambdas.extract_filepaths_for_granule_arn
}


output "orca_lambda_request_files_arn" {
  description = "AWS ARN of the ORCA request_files lambda."
  value       = module.orca_lambdas.request_files_arn
}


output "orca_lambda_copy_files_to_archive_arn" {
  description = "AWS ARN of the ORCA copy_files_to_archive lambda."
  value       = module.orca_lambdas.copy_files_to_archive_arn
}


output "orca_lambda_request_status_arn" {
  description = "AWS ARN of the ORCA request_status lambda."
  value       = module.orca_lambdas.request_status_arn
}


output "orca_lambda_request_status_for_granule_arn" {
  description = "AWS ARN of the ORCA request_status_for_granule lambda."
  value       = module.orca_lambdas.request_status_for_granule_arn
}


output "orca_lambda_request_status_for_job_arn" {
  description = "AWS ARN of the ORCA request_status_for_job lambda."
  value       = module.orca_lambdas.request_status_for_job_arn
}


## Workflow Module Outputs (orca_workflows)
## =============================================================================
## No workflow outputs currently requested/needed


## RDS Module Outputs (orca_rds)
## =============================================================================
output "orca_rds" {
  description = "PostgreSQL database object. Used only for development validation."
  value       = module.orca_rds.rds
}

output "orca_subnet_group" {
  description = "PostgreSQL subnet group object. Used only for development validation."
  value       = module.orca_rds.rds_subnet_group
}

