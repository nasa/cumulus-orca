output "database_arn" {
  value = aws_rds_cluster.example.arn
}

output "database_identifier" {
  value = aws_rds_cluster.example.cluster_identifier
}

output "role_arn" {
  value = aws_iam_role.rds_s3_import_role.arn
}
