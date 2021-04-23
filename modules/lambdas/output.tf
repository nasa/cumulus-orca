## Module outputs
## =============================================================================
output "vpc_postgres_ingress_all_egress_id" {
  description = "Security Group ID for PostgreSQL access."
  value       = module.lambda_security_group.vpc_postgres_ingress_all_egress_id
}


## Lambda Outputs
## =============================================================================
# Ingest Lambdas
# ------------------------------------------------------------------------------
output "copy_to_glacier_arn" {
  description = "AWS ARN for the copy_to_glacier lambda."
  value       = aws_lambda_function.copy_to_glacier.arn
}


# Recovery Lambdas
# ------------------------------------------------------------------------------
output "extract_filepaths_for_granule_arn" {
  description = "AWS ARN for the extract_filepaths_for_granule lambda."
  value       = aws_lambda_function.extract_filepaths_for_granule.arn
}


output "request_files_arn" {
  description = "AWS ARN for the request_files lambda."
  value       = aws_lambda_function.request_files.arn
}


output "copy_files_to_archive_arn" {
  description = "AWS ARN for the copy_files_to_archive lambda."
  value       = aws_lambda_function.copy_files_to_archive.arn
}

output "request_status_for_granule_arn" {
  description = "AWS ARN for the request_status_for_granule lambda."
  value       = aws_lambda_function.request_status_for_granule.arn
}


output "request_status_for_job_arn" {
  description = "AWS ARN for the request_status_for_job lambda."
  value       = aws_lambda_function.request_status_for_job.arn
}


# Utility Lambdas
# ------------------------------------------------------------------------------
output "db_deploy_arn" {
  description = "AWS ARN for the db_deploy lambda."
  value       = aws_lambda_function.db_deploy.arn
}


output "db_deploy_source_code_hash" {
  description = "Base 64 SHA-256 hash of the db_deploy lambda function. Used to trigger bootstrap in rds."
  value       = aws_lambda_function.db_deploy.source_code_hash
}