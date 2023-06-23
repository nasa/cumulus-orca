## ORCA IAM outputs
output "restore_object_role_arn" {
  value       = aws_iam_role.restore_object_role.arn
  description = "AWS ARN of the restore_object_role."
}

output "step_function_role_arn" {
  value       = aws_iam_role.step_functions.arn
  description = "AWS ARN of the role for step functions."
}