data "aws_iam_policy_document" "assume_lambda_role" {
  statement {
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "restore_object_role" {
  name                 = "${var.prefix}_restore_object_role"
  assume_role_policy   = data.aws_iam_policy_document.assume_lambda_role.json
  permissions_boundary = var.permissions_boundary_arn
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
    resources = [
      "arn:aws:s3:::${var.glacier_bucket}",
      "arn:aws:s3:::${var.public_bucket}",
      "arn:aws:s3:::${var.private_bucket}",
      "arn:aws:s3:::${var.internal_bucket}",
      "arn:aws:s3:::${var.protected_bucket}"
    ]
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
    resources = [
      "arn:aws:s3:::${var.glacier_bucket}/*",
      "arn:aws:s3:::${var.public_bucket}/*",
      "arn:aws:s3:::${var.private_bucket}/*",
      "arn:aws:s3:::${var.internal_bucket}/*",
      "arn:aws:s3:::${var.protected_bucket}/*"
    ]
  }
  statement {
    actions   = [
      "s3:RestoreObject",
      "s3:GetObject"
    ]
    resources = [
      "arn:aws:s3:::${var.glacier_bucket}",
      "arn:aws:s3:::${var.glacier_bucket}/*"
    ]
  }
}

resource "aws_iam_role_policy" "restore_object_role_policy" {
  name   = "${var.prefix}_restore_object_role_policy"
  role   = aws_iam_role.restore_object_role.id
  policy = data.aws_iam_policy_document.restore_object_role_policy_document.json
}
