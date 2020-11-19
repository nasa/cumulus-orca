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

