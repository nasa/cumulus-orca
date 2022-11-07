# Application load balancer
resource "aws_lb" "gql_app_lb" {
  name               = "${var.prefix}-gql-app-lb"
  internal           = true
  load_balancer_type = "application"
  security_groups    = [var.vpc_postgres_ingress_all_egress_id]
  subnets            = var.lambda_subnet_ids
  idle_timeout       = 30 # API Gateway locks us to 30 seconds.
  tags               = var.tags
}

resource "aws_lb_target_group" "gql_app_lb_target_group" {
  name        = "${var.prefix}-gql-app-lb-t"
  vpc_id      = var.vpc_id
  protocol    = "HTTP"
  port        = 5000
  target_type = "ip"

  # NOTE: TF is unable to destroy a target group while a listener is attached,
  # therefore we have to create a new one before destroying the old. This also means
  # we have to let it have a random name, and then tag it with the desired name.
  # lifecycle {
  #   create_before_destroy = true
  # }

  tags = var.tags
}

resource "aws_lb_listener" "gql_app_lb_listener" {
  load_balancer_arn = aws_lb.gql_app_lb.arn
  port              = "5000"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.gql_app_lb_target_group.arn
  }
}

# Network load balancer
resource "aws_lb" "gql_nw_lb" {
  name               = "${var.prefix}-gql-nw-lb"
  internal           = true
  load_balancer_type = "network"
  subnets            = var.lambda_subnet_ids

  enable_deletion_protection = true

  tags               = var.tags
}

resource "aws_lb_target_group" "gql_nw_lb_target_group" {
  name        = "${var.prefix}-gql-nw-lb-t"
  vpc_id      = var.vpc_id
  protocol    = "TCP"
  port        = 5000
  target_type = "alb"

  # NOTE: TF is unable to destroy a target group while a listener is attached,
  # therefore we have to create a new one before destroying the old. This also means
  # we have to let it have a random name, and then tag it with the desired name.
  # lifecycle {
  #   create_before_destroy = true
  # }

  tags = var.tags
}

resource "aws_lb_listener" "gql_nw_lb_listener" {
  load_balancer_arn = aws_lb.gql_nw_lb.arn
  port              = "5000"
  protocol          = "TCP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.gql_nw_lb_target_group.arn
  }
}

resource "aws_lb_target_group_attachment" "gql_nw_app_lb_attachment" {
    target_group_arn = aws_lb_target_group.gql_nw_lb_target_group.arn
    # attach the ALB to this target group
    target_id        = aws_lb.gql_app_lb.arn
    port             = 5000
}

resource "aws_api_gateway_vpc_link" "gql_vpc_link" {
  name        = "${var.prefix}-gql-vpc-link"
  description = "Allow the API Gateway to contact the Network Load Balancer."
  target_arns = [aws_lb.gql_nw_lb.arn]

  tags = var.tags
}

# ecs service and task
data "aws_iam_policy_document" "gql_task_execution_policy_document" {
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

resource "aws_iam_role_policy" "gql_task_role_policy" {
  name   = "${var.prefix}_orca_gql_task_role_policy"
  role   = aws_iam_role.orca_ecs_task_execution_role.id
  policy = data.aws_iam_policy_document.gql_task_execution_policy_document.json
}

resource "aws_iam_role" "orca_ecs_task_execution_role" {
  name                 = "${var.prefix}_orca_ecs_task_execution_role"
  assume_role_policy   = data.aws_iam_policy_document.assume_ecs_tasks_role_policy_document.json
  permissions_boundary = var.permissions_boundary_arn
  tags                 = var.tags
}

# Defines how the image will be run.
resource "aws_ecs_task_definition" "gql_task" {
  family                   = "${var.prefix}_orca_gql_task"
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
    "name": "orca-gql",
    "image": "ghcr.io/nasa/cumulus-orca/graphql:0.0.18",
    "cpu": 512,
    "memory": 256,
    "networkMode": "awsvpc",
    "portMappings": [
      {
        "containerPort": 5000,
        "hostPort": 5000
      }
    ],
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

resource "aws_ecs_service" "gql_service" {
  depends_on = [
    aws_lb_listener.gql_app_lb_listener  # Wait for listener to associate aws_lb_target_group with aws_lb
  ]
  name            = "${var.prefix}_gql_service"
  cluster         = var.ecs_cluster_id
  task_definition = aws_ecs_task_definition.gql_task.arn
  desired_count   = 3
  launch_type     = "FARGATE"
  propagate_tags  = "TASK_DEFINITION"

  network_configuration {
    subnets         = var.lambda_subnet_ids
    security_groups = [var.vpc_postgres_ingress_all_egress_id]
  }

  load_balancer {
    container_name   = "orca-gql"
    container_port   = 5000
    target_group_arn = aws_lb_target_group.gql_app_lb_target_group.arn
  }
}