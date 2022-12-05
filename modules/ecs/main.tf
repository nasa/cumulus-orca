resource "aws_ecs_cluster" "orca_ecs_cluster" {
  name = "${var.prefix}_orca_ecs_cluster"
  capacity_providers = ["FARGATE"]
  default_capacity_provider_strategy {
    capacity_provider = "FARGATE"
    weight            = 100
  }
  tags                = var.tags
}