output "this_db_instance_address" {
  description = "The address of the RDS instance"
  value       = aws_db_instance.postgresql.address
}

output "this_db_instance_arn" {
  description = "The ARN of the RDS instance"
  value       = aws_db_instance.postgresql.arn
}

output "this_db_instance_availability_zone" {
  description = "The availability zone of the RDS instance"
  value       = aws_db_instance.postgresql.availability_zone
}

output "this_db_instance_endpoint" {
  description = "The connection endpoint in address:port format"
  value       = aws_db_instance.postgresql.endpoint
}

output "this_db_instance_hosted_zone_id" {
  description = "The canonical hosted zone ID of the DB instance (to be used in a Route 53 Alias record)"
  value       = aws_db_instance.postgresql.hosted_zone_id
}

output "this_db_instance_id" {
  description = "The RDS instance ID"
  value       = aws_db_instance.postgresql.id
}

output "this_db_instance_resource_id" {
  description = "The RDS Resource ID of this instance"
  value       = aws_db_instance.postgresql.resource_id
}

output "this_db_instance_status" {
  description = "The RDS instance status"
  value       = aws_db_instance.postgresql.status
}

output "this_db_instance_name" {
  description = "The database name"
  value       = aws_db_instance.postgresql.name
}

output "this_db_instance_username" {
  description = "The master username for the database"
  value       = aws_db_instance.postgresql.username
}

# output "this_db_instance_password" {
#   description = "The database password (this password may be old, because Terraform doesn't track it after initial creation)"
#   value       = aws_db_instance.postgresql.password
# }

output "this_db_instance_port" {
  description = "The database port"
  value       = aws_db_instance.postgresql.port
}

output "this_db_subnet_group_id" {
  description = "The db subnet group name"
  value       = aws_db_subnet_group.postgres_subnet_group.id
}

output "this_db_subnet_group_arn" {
  description = "The ARN of the db subnet group"
  value       = aws_db_subnet_group.postgres_subnet_group.arn
}

output "extract_filepaths_lambda_arn" {
  description = "ARN identifying extract_filepaths lambda"
  value       = aws_lambda_function.extract_filepaths_for_granule_lambda.arn
}

output "request_files_lambda_arn" {
  description = "ARN identifying request_files lambda"
  value       = aws_lambda_function.request_files_lambda.arn
}

# Can re-enable if we want. Don't have this information if we're using the default.
# output "this_db_parameter_group_id" {
#   description = "The db parameter group id"
#   value       = "${module.db.this_db_parameter_group_id}"
# }

# output "this_db_parameter_group_arn" {
#   description = "The ARN of the db parameter group"
#   value       = "${module.db.this_db_parameter_group_arn}"
# }
