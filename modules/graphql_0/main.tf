data "aws_vpc" "primary" {
  id = var.vpc_id
}

data "aws_region" "current_region" {}

locals {
  all_bucket_names  = length(var.orca_recovery_buckets) > 0 ? var.orca_recovery_buckets : [for k, v in var.buckets : v.name]
  all_bucket_arns   = [for name in local.all_bucket_names : "arn:aws:s3:::${name}"]
  all_bucket_paths  = [for name in local.all_bucket_names : "arn:aws:s3:::${name}/*"]
  orca_bucket_arns  = [for k, v in var.buckets : "arn:aws:s3:::${v.name}" if v.type == "orca"]
  orca_bucket_paths = [for k, v in var.buckets : "arn:aws:s3:::${v.name}/*" if v.type == "orca"]
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
      identifiers = ["lambda.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["states.${data.aws_region.current_region.name}.amazonaws.com"]
    }
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
  statement {
    actions   = ["sts:AssumeRole"]
    resources = ["*"]
  }
  statement {
    actions = [
      "ec2:CreateNetworkInterface",
      "ec2:DescribeNetworkInterfaces",
      "ec2:DeleteNetworkInterface"
    ]
    resources = ["*"]
  }
  statement {
    actions = [
      "states:SendTaskFailure",
      "states:SendTaskSuccess",
      "states:GetActivityTask",
      "states:GetExecutionHistory",
      "states:DescribeActivity",
      "states:DescribeExecution",
      "states:ListStateMachines"
    ]
    resources = ["arn:aws:states:*:*:*"]
  }
  statement {
    actions = [
      "sns:publish",
      "sns:List*"
    ]
    resources = ["*"]
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
  statement {
    actions = [
      "s3:GetBucket",
      "s3:ListBucket",
      "s3:ListBucketVersions",
      "s3:PutBucket"
    ]
    resources = local.all_bucket_arns
  }
  statement {
    actions = [
      "s3:AbortMultipartUpload",
      "s3:GetObject",
      "s3:GetObjectTagging",
      "s3:GetObjectVersion",
      "s3:PutObject",
      "s3:PutObjectTagging",
      "s3:ListMultipartUploadParts",
      "s3:DeleteObject",
      "s3:DeleteObjectVersion"
    ]
    resources = local.all_bucket_paths
  }
  statement {
    actions = [
      "s3:RestoreObject",
      "s3:GetObject",
      "s3:GetObjectTagging",
      "s3:PutObjectTagging",
      "s3:GetObjectVersion"
    ]
    resources = concat(local.orca_bucket_arns, local.orca_bucket_paths)
  }
  statement {
    actions = [
      "secretsmanager:GetSecretValue"
    ]
    resources = ["*"]
  }
  statement {
    actions = [
      "kms:Decrypt",
      "kms:DescribeKey" #requested by Cumulus
    ]
    resources = [
      "arn:aws:kms:::key/CMK"
    ]
  }
  statement {
    actions = [
      "sqs:ReceiveMessage",
      "sqs:SendMessage",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes"
    ]
    resources = ["*"]
  }
  statement {
    actions = [
      "states:StartExecution",
    ]
    resources = ["*"]
  }
  statement {
    actions = [
      "s3:GetObject",  # Get the manifest
      "s3:PutObject"  # Copy the gzip to add missing metadata
    ]
    resources = ["arn:aws:s3:::${var.orca_reports_bucket_name}/*"]
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
