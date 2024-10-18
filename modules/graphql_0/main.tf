data "aws_vpc" "primary" {
  id = var.vpc_id
}

data "aws_caller_identity" "current" {}

# IAM role that tasks can use to make API requests to authorized AWS services. If you make a boto3 call, this is what carries it out.
data "aws_iam_policy_document" "assume_gql_tasks_role_policy_document" {
  statement {
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
  statement {
    principals {
      type        = "Service"
      identifiers = ["rds.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
    condition {
      test = "StringEquals"
      variable = "aws:SourceAccount"
      values = [
        "${data.aws_caller_identity.current.account_id}"
      ]
    }
  }
}

resource "aws_iam_role" "gql_tasks_role" {
  name                 = "${var.prefix}_orca_gql_tasks_role"
  assume_role_policy   = data.aws_iam_policy_document.assume_gql_tasks_role_policy_document.json
  permissions_boundary = var.permissions_boundary_arn
  tags                 = var.tags
}

data "aws_iam_policy_document" "gql_tasks_role_policy_document" {
  statement {
    actions   = ["sts:AssumeRole"]
    resources = [aws_iam_role.gql_tasks_role.arn]
  }
}

resource "aws_iam_role_policy" "gql_tasks_role_policy" {
  name   = "${var.prefix}_orca_gql_tasks_role_policy"
  role   = aws_iam_role.gql_tasks_role.id
  policy = data.aws_iam_policy_document.gql_tasks_role_policy_document.json
}

# IAM role that runs the task, but is not used by the task.
data "aws_iam_policy_document" "assume_ecs_task_execution_role_policy_document" {
  statement {
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "orca_ecs_task_execution_role" {
  name                 = "${var.prefix}_orca_ecs_task_execution_role"
  assume_role_policy   = data.aws_iam_policy_document.assume_ecs_task_execution_role_policy_document.json
  permissions_boundary = var.permissions_boundary_arn
  tags                 = var.tags
}

# Policy document for S3 import
data "aws_iam_policy_document" "rds_s3_import_role_policy_document" {
  statement {
    actions = [
      "s3:GetObject",
      "s3:ListBucket"
    ]
    resources = [
        "arn:aws:s3:::${var.prefix}-orca-reports",
        "arn:aws:s3:::${var.prefix}-orca-reports/*"
    ]
  }
}
resource "aws_iam_role_policy" "rds_s3_import_role_policy" {
  name   = "${var.prefix}_rds_s3_import_role_policy"
  role   = aws_iam_role.gql_tasks_role.id
  policy = data.aws_iam_policy_document.rds_s3_import_role_policy_document.json
}

resource "aws_rds_cluster_role_association" "orca_iam_association" {
  db_cluster_identifier = var.db_cluster_identifier
  feature_name          = "s3Import"
  role_arn              = aws_iam_role.gql_tasks_role.arn
  count                 = var.deploy_rds_cluster_role_association ? 1 : 0
}
