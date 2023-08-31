resource "aws_ecs_cluster" "orca_ecs_cluster" {
  name = "${var.prefix}_orca_ecs_cluster"
  tags                = var.tags
}