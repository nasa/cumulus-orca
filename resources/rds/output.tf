output "rds" {
  value = aws_db_instance.postgresql
}

output "rds_subnet_group" {
  value = aws_db_subnet_group.postgres_subnet_group
}