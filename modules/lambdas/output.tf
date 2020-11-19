output "vpc_postgres_ingress_all_egress_id" {
  value = module.lambda_security_group.vpc_postgres_ingress_all_egress_id
}

output "db_deploy" {
  value = aws_lambda_function.db_deploy
}

output "extract_filepath_arn" {
  value = aws_lambda_function.extract_filepaths_for_granule_lambda.arn
}

output "request_files_arn" {
  value = aws_lambda_function.request_files_lambda.arn
}

output "copy_to_glacier_arn" {
  value = aws_lambda_function.copy_to_glacier.arn
}