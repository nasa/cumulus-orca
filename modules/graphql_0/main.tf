data "aws_vpc" "primary" {
  id = var.vpc_id
}

data "aws_iam_policy_document" "assume_gql_tasks_role_policy_document" {
  statement {
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

data "aws_iam_policy_document" "gql_tasks_role_policy_document" {
  statement {
    actions   = ["sts:AssumeRole"] # todo: needed?
    resources = ["*"]
  }
  statement {
    actions = [
      "secretsmanager:GetSecretValue"
    ]
    resources = ["*"]
  }
}

# IAM role that tasks can use to make API requests to authorized AWS services. If you make a boto3 call, this is what carries it out.
resource "aws_iam_role" "gql_tasks_role" {
  name                 = "${var.prefix}_orca_gql_tasks_role"
  assume_role_policy   = data.aws_iam_policy_document.assume_gql_tasks_role_policy_document.json
  permissions_boundary = var.permissions_boundary_arn
  tags                 = var.tags
}

resource "aws_iam_role_policy" "gql_tasks_role_policy" {
  name   = "${var.prefix}_orca_gql_tasks_role_policy"
  role   = aws_iam_role.gql_tasks_role.id
  policy = data.aws_iam_policy_document.gql_tasks_role_policy_document.json
}
