output "rds" {
  description = "PostgreSQL database object. Used only for development validation."
  value       = aws_db_instance.postgresql
}

output "rds_subnet_group" {
  description = "PostgreSQL subnet group object. Used only for development validation."
  value       = aws_db_subnet_group.postgres_subnet_group
}

output "kms_key_id" {
  description = "The globally unique identifier for the KMS key."
  value       = aws_kms_key.orca_kms_key.key_id
}

output "kms_key_arn" {
  description = "The Amazon Resource Name (ARN) of the KMS key."
  value       = aws_kms_key.orca_kms_key.arn
}
