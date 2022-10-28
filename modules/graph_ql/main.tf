
data "aws_iam_policy_document" "graphql_task_policy_document" {
  statement {
    actions   = ["sts:AssumeRole"]
    resources = ["*"]
  }
}

data "aws_iam_policy_document" "assume_ecs_tasks_role_policy_document" {
  statement {
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

# IAM role that tasks can use to make API requests to authorized AWS services.
resource "aws_iam_role" "orca_ecs_tasks_role" {
  name                 = "${var.prefix}_orca_ecs_tasks_role"
  assume_role_policy   = data.aws_iam_policy_document.assume_ecs_tasks_role_policy_document.json
  permissions_boundary = var.permissions_boundary_arn
  tags                 = var.tags
}

resource "aws_iam_role_policy" "graphql_task_role_policy" {
  name   = "${var.prefix}_orca_graphql_task_role_policy"
  role   = aws_iam_role.orca_ecs_tasks_role.id
  policy = data.aws_iam_policy_document.graphql_task_policy_document.json
}

# This role is required by tasks to pull container images and publish container logs to Amazon CloudWatch on your behalf.
resource "aws_iam_role" "orca_ecs_task_execution_role" {
  name                 = "${var.prefix}_orca_ecs_task_execution_role"
  assume_role_policy   = data.aws_iam_policy_document.assume_ecs_tasks_role_policy_document.json
  permissions_boundary = var.permissions_boundary_arn
  tags                 = var.tags
}

# Defines how the image will be run. container_definitions can be replaced by data element.
resource "aws_ecs_task_definition" "task" {
  family                   = "${var.prefix}_orca_graphql_task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "4096"
  memory                   = "8192"
  task_role_arn            = aws_iam_role.orca_ecs_tasks_role.arn
  execution_role_arn       = aws_iam_role.orca_ecs_task_execution_role.arn
  container_definitions    = <<DEFINITION
[
  {
    "name": "orca-graphql",
    "image": "ghcr.io/nasa/orca-graphql:0.0.16",
    "cpu": 4096,
    "memory": 256,
    "networkMode": "awsvpc",
    "environment": [
    ],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-create-group": "true",
        "awslogs-region": "us-west-2",
        "awslogs-group": "${var.prefix}_orca_graph_ql",
        "awslogs-stream-prefix": "ecs"
      }
    }
  }
]
DEFINITION
}