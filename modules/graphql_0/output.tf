output "gql_tasks_role_arn" {
  value       = aws_iam_role.gql_tasks_role.arn
  description = "The ARN of the role used by the code within the Graphql ECS Task."
}

output "gql_ecs_task_execution_role_arn" {
  value       = aws_iam_role.orca_ecs_task_execution_role.arn
  description = "The ARN of the role used by the ECS Task runnger."
}
