output "vpc_postgres_ingress_all_egress_id" {
  value       = aws_security_group.vpc_postgres_ingress_all_egress.id
  description = "PostgreSQL security group id"
}

output "vpc_all_egress_id" {
  value       = aws_security_group.vpc_all_egress.id
  description = "Egress security group id"
}
