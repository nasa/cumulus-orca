output "rds" {
  description = "PostgreSQL database object. Used only for development validation."
  value       = aws_db_instance.postgresql
}

output "rds_subnet_group" {
  description = "PostgreSQL subnet group object. Used only for development validation."
  value       = aws_db_subnet_group.postgres_subnet_group
}