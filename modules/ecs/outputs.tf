output "ecs_cluster_id" {
  value = aws_ecs_cluster.orca_ecs_cluster.id
  description = "ID of the ECS cluster in AWS."
}