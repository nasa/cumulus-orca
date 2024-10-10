data "aws_caller_identity" "current_account" {}

data "aws_region" "current_region" {}

# Local Variables
locals {
  account_id   = data.aws_caller_identity.current_account.account_id
  region       = data.aws_region.current_region.name
  # Used for Load Balancer, EC2 Service, and Container ports. Specifies how GQL will be hosted.
  graphql_port = 5000
}

data "aws_ssm_parameter" "private_ca" {
  name = "ngap_private_ca_arn"
}
 
resource "aws_acm_certificate" "orca_lb_cert" {
  domain_name       = "*.us-west-2.elb.amazonaws.com"
 
  certificate_authority_arn = data.aws_ssm_parameter.private_ca.value
 
  lifecycle {
    create_before_destroy = true
  }
}
resource "random_id" "lb_name" {
  keepers = {
    # gql_app_lb change requirements
    "graphql_port" = local.graphql_port
    "vpc_id"       = var.vpc_id
  }

  byte_length = 4
}

data "aws_vpc" "primary" {
  id = var.vpc_id
}

# Final IAM setup
data "aws_iam_policy_document" "gql_task_execution_policy_document" {
  statement {
    actions   = ["sts:AssumeRole"]
    resources = [var.gql_tasks_role_arn]
  }
  statement {
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:DescribeLogStreams",
      "logs:PutLogEvents"
    ]
    resources = [
      "arn:aws:logs:${local.region}:${local.account_id}:log-group:${var.prefix}_orca_graph_ql:*",
      "arn:aws:logs:${local.region}:${local.account_id}:log-group:${var.prefix}_orca_graph_ql:log-stream:ecs/orca-gql*"
    ]
  }
  statement {
    actions = [
      "secretsmanager:GetSecretValue"
    ]
    resources = [
      var.db_connect_info_secret_arn,
    ]
  }
}

resource "aws_iam_role_policy" "gql_task_role_policy" {
  name   = "${var.prefix}_orca_gql_task_role_policy"
  role   = var.gql_ecs_task_execution_role_id
  policy = data.aws_iam_policy_document.gql_task_execution_policy_document.json
}

resource "aws_security_group" "gql_lb_security_group" {
  name        = "${var.prefix}-lb-gql"
  description = "Allow inbound communication on container port."
  vpc_id      = var.vpc_id

  ingress {
    description      = "Container port communication."
    from_port        = local.graphql_port
    to_port          = local.graphql_port
    protocol         = "tcp"
    cidr_blocks      = [data.aws_vpc.primary.cidr_block]
  }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = [data.aws_vpc.primary.cidr_block]
  }

  tags = var.tags
}

# Application load balancer
resource "aws_lb" "gql_app_lb" {
  name               = "${var.prefix}-gql-a" # Max 32 characters. Some prefixes are 25 characters long.
  internal           = true
  load_balancer_type = "application"
  access_logs {
    bucket  = var.system_bucket
    prefix  = "${var.prefix}-lb-gql-a-logs"
    enabled = true
  }
  drop_invalid_header_fields = true
  security_groups    = [aws_security_group.gql_lb_security_group.id]
  subnets            = var.lambda_subnet_ids
  idle_timeout       = 30 # API Gateway locks us to 30 seconds.
  tags               = var.tags
}

data "aws_lb" "gql_app_lb_data" {
  arn = aws_lb.gql_app_lb.arn
}

resource "aws_lb_target_group" "gql_app_lb_target_group" {
  name        = "${random_id.lb_name.hex}-gql-a" # name must be randomized. Max 32 characters. Some prefixes are 25 characters long.
  vpc_id      = var.vpc_id
  protocol    = "HTTPS"
  port        = local.graphql_port
  target_type = "ip"

  # NOTE: TF is unable to destroy a target group while a listener is attached,
  # therefore we have to create a new one before destroying the old. This also means
  # we have to let it have a random name.
  lifecycle {
    create_before_destroy = true
  }

  health_check {
    path = "/healthz"
  }

  tags = var.tags
}

resource "aws_lb_listener" "gql_app_lb_listener" {
  load_balancer_arn = aws_lb.gql_app_lb.arn
  port              = local.graphql_port
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = aws_acm_certificate.orca_lb_cert.arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.gql_app_lb_target_group.arn
  }

  tags               = var.tags
}

# Network Load Balacner
resource "aws_lb_target_group" "network_lb_tg" {
  name        = "${random_id.lb_name.hex}-gql-n"
  target_type = "alb"
  port        = local.graphql_port
  protocol    = "TCP"
  vpc_id      = var.vpc_id
  lifecycle {
    create_before_destroy = true
  }
}

data "aws_lb" "gql_net_lb_data" {
  arn = aws_lb.gql_net_lb.arn
}

resource "aws_lb" "gql_net_lb" {
  name               = "${var.prefix}-gql-n"
  internal           = true
  load_balancer_type = "network"
  access_logs {
    bucket  = var.system_bucket
    prefix  = "${var.prefix}-lb-gql-n-logs"
    enabled = true
  }
  drop_invalid_header_fields = true
  security_groups    = [aws_security_group.gql_lb_security_group.id]
  subnets            = var.lambda_subnet_ids
  idle_timeout       = 30 # API Gateway locks us to 30 seconds.
  tags = var.tags
}

resource "aws_lb_listener" "gql_net_lb_listener" {
  load_balancer_arn = aws_lb.gql_net_lb.arn
  port              = local.graphql_port
  protocol          = "TCP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.network_lb_tg.arn
  }

  tags               = var.tags
}

resource "aws_lb_target_group_attachment" "network-tg-attachment" {
  target_group_arn = aws_lb_target_group.network_lb_tg.arn
  target_id        = aws_lb.gql_app_lb.arn
  port             = local.graphql_port
}

# Pending further research on VPC Link. VPC Link -> NW LB -> App LB -> Service is recommended path, but NGAP requires NGAP involvement for VPC creation. https://eosdis.slack.com/archives/C6KK42ZJP/p1668106098892689
# # Network load balancer
# resource "aws_lb" "gql_nw_lb" {
#   name               = "${var.prefix}-gql-nw" # Max 32 characters. Some prefixes are 25 characters long.
#   internal           = true
#   load_balancer_type = "network"
#   subnets            = var.lambda_subnet_ids
# 
#   tags               = var.tags
# }
# 
# resource "aws_lb_target_group" "gql_nw_lb_target_group" {
#   name        = "${random_id.lb_name.hex}-gql-nw" # name must be randomized. Max 32 characters. Some prefixes are 25 characters long.
#   vpc_id      = var.vpc_id
#   protocol    = "TCP"
#   port        = local.graphql_port
#   target_type = "alb"
# 
#   # NOTE: TF is unable to destroy a target group while a listener is attached,
#   # therefore we have to create a new one before destroying the old. This also means
#   # we have to let it have a random name.
#   lifecycle {
#     create_before_destroy = true
#   }
# 
#   tags = var.tags
# }
# 
# resource "aws_lb_listener" "gql_nw_lb_listener" {
#   load_balancer_arn = aws_lb.gql_nw_lb.arn
#   port              = local.graphql_port
#   protocol          = "TCP"
# 
#   default_action {
#     type             = "forward"
#     target_group_arn = aws_lb_target_group.gql_nw_lb_target_group.arn
#   }
# }
# 
# resource "aws_lb_target_group_attachment" "gql_nw_app_lb_attachment" {
#     target_group_arn = aws_lb_target_group.gql_nw_lb_target_group.arn
#     # attach the ALB to this target group
#     target_id        = aws_lb.gql_app_lb.arn
#     port             = local.graphql_port
# }

# ecs service and task
# Defines how the image will be run.
resource "aws_ecs_task_definition" "gql_task" {
  depends_on = [
    aws_iam_role_policy.gql_task_role_policy # wait for the iam role to be finalized
  ]
  family                   = "${var.prefix}_orca_gql_task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "1024"
  memory                   = "2048"
  task_role_arn            = var.gql_tasks_role_arn
  execution_role_arn       = var.gql_ecs_task_execution_role_arn
  tags                     = var.tags
  container_definitions    = <<DEFINITION
[
  {
    "name": "orca-gql",
    "image": "ghcr.io/nasa/orca/graphql:0.33",
    "cpu": 512,
    "memory": 256,
    "networkMode": "awsvpc",
    "portMappings": [
      {
        "containerPort": ${local.graphql_port},
        "hostPort": ${local.graphql_port}
      }
    ],
    "environment": [
      {
        "name": "PORT",
        "value": "${local.graphql_port}"
      },
      {
        "name": "ORCA_ENV",
        "value": "production"
      }
    ],
    "secrets": [
      {
        "name": "DB_CONNECT_INFO",
        "valueFrom": "${var.db_connect_info_secret_arn}"
      }
    ],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-create-group": "true",
        "awslogs-region": "us-west-2",
        "awslogs-group": "${var.prefix}_orca_graph_ql",
        "awslogs-stream-prefix": "ecs"
      }
    },
    "HealthCheck": {
      "Command": [
        "CMD-SHELL",
	      "curl --fail http://localhost:${local.graphql_port}/healthz || exit 1"
      ],
      "StartPeriod": 30,
      "Interval": 60,
      "Timeout": 5,
      "Retries": 3
    }
  }
]
DEFINITION
}

resource "aws_security_group" "gql_task_security_group" {
  name        = "${var.prefix}-gql-task"
  description = "Allow inbound communication from LB on container port. Allow outbound communication to get image."
  vpc_id      = var.vpc_id

  ingress {
    description      = "Container port communication."
    from_port        = local.graphql_port
    to_port          = local.graphql_port
    protocol         = "tcp"
    security_groups  = [aws_security_group.gql_lb_security_group.id]
  }

  egress {
    description      = "Allow task to get the image from ghcr."
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
  }

  tags = var.tags
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
    security_groups = [aws_security_group.gql_task_security_group.id]
  }

  load_balancer {
    container_name   = "orca-gql"
    container_port   = local.graphql_port
    target_group_arn = aws_lb_target_group.gql_app_lb_target_group.arn
  }

  deployment_circuit_breaker {
    enable   = true
    rollback = false # Rolling back to previous versions can prevent proper updating and hide errors.
  }

  tags = var.tags
}
