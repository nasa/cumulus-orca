## ORCA IAM outputs
output "restore_object_role_arn" {
  value = aws_iam_role.restore_object_role.arn
  description = "AWS ARN of the restore_object_role."
}

output "restore_object_role_name" {
  value = aws_iam_role.restore_object_role.name
  description = "Name of the restore_object_role."
}