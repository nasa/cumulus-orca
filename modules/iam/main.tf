data "aws_region" "current_region" {}
## Local Variables
# We will eventually create more specific permissions. For now, only reports buckets are separated.
# Note that all_bucket_names does not actually contain all buckets used by Orca.
locals {
  all_bucket_names  = length(var.orca_recovery_buckets) > 0 ? var.orca_recovery_buckets : [for k, v in var.buckets : v.name]
  all_bucket_arns   = [for name in local.all_bucket_names : "arn:aws:s3:::${name}"]
  all_bucket_paths  = [for name in local.all_bucket_names : "arn:aws:s3:::${name}/*"]
  orca_bucket_arns  = [for k, v in var.buckets : "arn:aws:s3:::${v.name}" if v.type == "orca"]
  orca_bucket_paths = [for k, v in var.buckets : "arn:aws:s3:::${v.name}/*" if v.type == "orca"]
}


## Data
data "aws_iam_policy_document" "assume_lambda_role" {
  statement {
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}


data "aws_iam_policy_document" "restore_object_role_policy_document" {
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
      "s3:GetObjectVersion",
      "s3:PutObject",
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


## RESOURCES
resource "aws_iam_role" "restore_object_role" {
  name                 = "${var.prefix}_restore_object_role"
  assume_role_policy   = data.aws_iam_policy_document.assume_lambda_role.json
  permissions_boundary = var.permissions_boundary_arn
  tags                 = var.tags
}


resource "aws_iam_role_policy" "restore_object_role_policy" {
  name   = "${var.prefix}_restore_object_role_policy"
  role   = aws_iam_role.restore_object_role.id
  policy = data.aws_iam_policy_document.restore_object_role_policy_document.json
}


# Step functions
# copied from (cumulus/tf-modules/ingest/iam.tf) todo: Strip back and personalize for each step-function
data "aws_iam_policy_document" "states_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["states.${data.aws_region.current_region.name}.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "step_functions" {
  name                 = "${var.prefix}-orca-steprole"
  assume_role_policy   = data.aws_iam_policy_document.states_assume_role_policy.json
  permissions_boundary = var.permissions_boundary_arn
  tags                 = var.tags
}

data "aws_iam_policy_document" "step_functions_policy" {
  statement {
    actions = [
      "lambda:InvokeFunction",
      "ecr:*",
      "cloudtrail:LookupEvents",
      "ecs:RunTask",
      "ecs:StopTask",
      "ecs:DescribeTasks",
      "autoscaling:Describe*",
      "cloudwatch:*",
      "logs:*",
      "sns:*",
      "iam:GetPolicy",
      "iam:GetPolicyVersion",
      "iam:GetRole",
    ]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "step_functions_role" {
  name   = "${var.prefix}_orca_step_policy"
  role   = aws_iam_role.step_functions.id
  policy = data.aws_iam_policy_document.step_functions_policy.json
}
