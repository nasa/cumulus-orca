## Terraform Requirements
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 3.5.0"
    }
  }
}


## AWS Provider Settings
provider "aws" {
  region  = var.region
  profile = var.aws_profile
}


## Local Variables
locals {
  all_bucket_arns   = [for k, v in var.buckets : "arn:aws:s3:::${v.name}"]
  all_bucket_paths  = [for k, v in var.buckets : "arn:aws:s3:::${v.name}/*"]
  orca_bucket_arns  = [for k, v in var.buckets : "arn:aws:s3:::${v.name}" if v.type == "orca"]
  orca_bucket_paths = [for k, v in var.buckets : "arn:aws:s3:::${v.name}/*" if v.type == "orca"]
  tags              = merge(var.tags, { Deployment = var.prefix })
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
      "s3:PutBucket"
    ]
    resources = local.all_bucket_arns
  }
  statement {
    actions = [
      "s3:AbortMultipartUpload",
      "s3:GetObject*",
      "s3:PutObject*",
      "s3:ListMultipartUploadParts",
      "s3:DeleteObject",
      "s3:DeleteObjectVersion"
    ]
    resources = local.all_bucket_paths
  }
  statement {
    actions = [
      "s3:RestoreObject",
      "s3:GetObject"
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
      "kms:Decrypt"
    ]
    resources = [
      "arn:aws:kms:::key/CMK"
    ]
  }
}


## RESOURCES
resource "aws_iam_role" "restore_object_role" {
  name                 = "${var.prefix}_restore_object_role"
  assume_role_policy   = data.aws_iam_policy_document.assume_lambda_role.json
  permissions_boundary = var.permissions_boundary_arn
  tags                 = local.tags
}


resource "aws_iam_role_policy" "restore_object_role_policy" {
  name   = "${var.prefix}_restore_object_role_policy"
  role   = aws_iam_role.restore_object_role.id
  policy = data.aws_iam_policy_document.restore_object_role_policy_document.json
}
