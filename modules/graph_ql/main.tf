data "aws_iam_policy_document" "graphql_task_execution_policy_document" {
  statement {
    actions   = ["sts:AssumeRole"]
    resources = [aws_iam_role.orca_ecs_tasks_role.arn]
  }
  statement {
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:DescribeLogStreams",
      "logs:PutLogEvents"
    ]
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
  role   = aws_iam_role.orca_ecs_task_execution_role.id
  policy = data.aws_iam_policy_document.graphql_task_execution_policy_document.json
}

resource "aws_iam_role" "orca_ecs_task_execution_role" {
  name                 = "${var.prefix}_orca_ecs_task_execution_role"
  assume_role_policy   = data.aws_iam_policy_document.assume_ecs_tasks_role_policy_document.json
  permissions_boundary = var.permissions_boundary_arn
  tags                 = var.tags
}

# Defines how the image will be run.
resource "aws_ecs_task_definition" "graphql_task" {
  family                   = "${var.prefix}_orca_graphql_task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "1024"
  memory                   = "2048"
  task_role_arn            = aws_iam_role.orca_ecs_tasks_role.arn
  execution_role_arn       = aws_iam_role.orca_ecs_task_execution_role.arn
  tags                     = var.tags
  container_definitions    = <<DEFINITION
[
  {
    "name": "orca-graphql",
    "image": "ghcr.io/nasa/cumulus-orca/graphql:0.0.18",
    "cpu": 512,
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

resource "aws_ecs_service" "graphql_service" {
  name            = "${var.prefix}_graphql_service"
  cluster         = var.ecs_cluster_id
  task_definition = aws_ecs_task_definition.graphql_task.arn
  desired_count   = 3
  launch_type     = "FARGATE"
  propagate_tags  = "TASK_DEFINITION"
  network_configuration {
    subnets         = var.lambda_subnet_ids
    security_groups = [var.vpc_postgres_ingress_all_egress_id]
  }
}