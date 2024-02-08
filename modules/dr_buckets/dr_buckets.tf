variable "prefix" {
  type        = string
  description = "Prefix used to prepend to all object names and tags."
}

variable "tags" {
  type        = map(string)
  description = "Tags to be applied to resources that support tags."
  default     = {}
}

variable "cumulus_account_id" {
  type = number
  description = "Account ID of the Cumulus Account"
}

## Terraform Configuration
terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0.0"
    }
  }
}

# Get DR Account ID
data "aws_caller_identity" "current" {}

# ORCA Archive Bucket
resource "aws_s3_bucket" "orca_archive_bucket" {
  bucket = "${var.prefix}-orca-archive"
  tags = var.tags
}

resource "aws_s3_bucket_ownership_controls" "orca_archive_bucket_ownership" {
  bucket = aws_s3_bucket.orca_archive_bucket.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

# ORCA Archive Bucket Versioning
resource "aws_s3_bucket_versioning" "orca_archive_versioning" {
  bucket = aws_s3_bucket.orca_archive_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

# ORCA Archive Policy
resource "aws_s3_bucket_policy" "orca_archive_cross_account_access" {
  bucket = aws_s3_bucket.orca_archive_bucket.id
  policy = data.aws_iam_policy_document.orca_archive_cross_account_access_policy.json
}

data "aws_iam_policy_document" "orca_archive_cross_account_access_policy" {
  statement {
    sid = "CrossAccPolicyDoc"
    principals {
      type        = "AWS"
      identifiers = [var.cumulus_account_id]
    }

    actions = [
      "s3:GetObject",
      "s3:GetObjectVersion",
      "s3:RestoreObject",
      "s3:GetBucketVersioning",
      "s3:GetBucketNotification",
      "s3:ListBucket",
      "s3:PutBucketNotification",
      "s3:GetInventoryConfiguration",
      "s3:PutInventoryConfiguration",
      "s3:ListBucketVersions"
    ]

    resources = [
      aws_s3_bucket.orca_archive_bucket.arn,
      "${aws_s3_bucket.orca_archive_bucket.arn}/*",
    ]
  }
  statement {
    sid = "Cross Account Write Access"
    principals {
      type        = "AWS"
      identifiers = [var.cumulus_account_id]
    }

    actions = [
      "s3:PutObject"
    ]

    resources = [
      "${aws_s3_bucket.orca_archive_bucket.arn}/*"
    ]

    condition {
      test = "StringEquals"
      variable = "s3:x-amz-storage-class"
      values = [
        "GLACIER",
        "DEEP_ARCHIVE"
      ]
    }
  }
}

# ORCA Archive Worm Bucket
resource "aws_s3_bucket" "orca_archive_worm_bucket" {
  bucket = "${var.prefix}-orca-archive-worm"
  tags = var.tags
}

resource "aws_s3_bucket_ownership_controls" "orca_archive_worm_bucket_ownership" {
  bucket = aws_s3_bucket.orca_archive_worm_bucket.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

# ORCA Archive Worm Bucket Versioning
resource "aws_s3_bucket_versioning" "orca_archive_worm_versioning" {
  bucket = aws_s3_bucket.orca_archive_worm_bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}

# ORCA Archive Worm Bucket Object Lock
resource "aws_s3_bucket_object_lock_configuration" "orca_achive_worm_object_lock" {
  bucket = aws_s3_bucket.orca_archive_worm_bucket.id
  depends_on = [aws_s3_bucket_versioning.orca_archive_worm_versioning]

  rule {
    default_retention {
      mode = "GOVERNANCE"
      days = 5
    }
  }
}

# ORCA Archive Worm Bucket Policy
resource "aws_s3_bucket_policy" "orca_archive_worm_cross_account_access" {
  bucket = aws_s3_bucket.orca_archive_worm_bucket.id
  policy = data.aws_iam_policy_document.orca_archive_worm_cross_account_access_policy.json
}

data "aws_iam_policy_document" "orca_archive_worm_cross_account_access_policy" {
  statement {
    sid = "Cross Account Access"
    principals {
      type        = "AWS"
      identifiers = [var.cumulus_account_id]
    }

    actions = [
      "s3:PutObject"
    ]

    resources = [
      "${aws_s3_bucket.orca_archive_worm_bucket.arn}/*"
    ]
    condition {
      test = "StringEquals"
      variable = "s3:x-amz-storage-class"
      values = [
        "GLACIER",
        "DEEP_ARCHIVE"
      ]
    }
  }
}

# ORCA Reports Bucket
resource "aws_s3_bucket" "orca_reports_bucket" {
  bucket = "${var.prefix}-orca-reports"
  tags = var.tags
}

# ORCA Reports Bucket Lifecycle Rule
resource "aws_s3_bucket_lifecycle_configuration" "orca_reports_bucket_lifecycle" {
  bucket = aws_s3_bucket.orca_reports_bucket.id

  rule {
    id = "30-day-lifecycle-reports"
    expiration {
      days = 30
    }
    status = "Enabled"
  }
}

# ORCA Reports Bucket Policy
resource "aws_s3_bucket_policy" "orca_reports_cross_account_access" {
  bucket = aws_s3_bucket.orca_reports_bucket.id
  policy = data.aws_iam_policy_document.orca_reports_cross_account_access_policy.json
}

resource "aws_s3_bucket_ownership_controls" "orca_reports_bucket_ownership" {
  bucket = aws_s3_bucket.orca_reports_bucket.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

data "aws_iam_policy_document" "orca_reports_cross_account_access_policy" {
  statement {
    sid = "Reports Cross Account Access"
    principals {
      type        = "AWS"
      identifiers = [var.cumulus_account_id]
    }

    actions = [
      "s3:GetObject",
      "s3:GetBucketNotification",
      "s3:ListBucket",
      "s3:PutObject",
      "s3:PutBucketNotification"
    ]

    resources = [
      aws_s3_bucket.orca_reports_bucket.arn,
      "${aws_s3_bucket.orca_reports_bucket.arn}/*",
    ]
  }
  statement {
    sid = "Inventory ORCA Reports"
    principals {
      type        = "Service"
      identifiers = ["s3.amazonaws.com"]
    }

    actions = [
      "s3:PutObject"
    ]

    resources = [
      "${aws_s3_bucket.orca_reports_bucket.arn}/*"
    ]
    condition {
      test = "StringEquals"
      variable = "aws:SourceAccount"
      values = [
        "${data.aws_caller_identity.current.account_id}"
      ]
    }
    condition {
      test = "ArnLike"
      variable = "aws:SourceArn"
      values = [aws_s3_bucket.orca_reports_bucket.arn]
    }
  }
 
}

# DR Bucket Outputs
output "orca_achive_bucket_arn" {
  value = aws_s3_bucket.orca_archive_bucket.arn
}

output "orca_reports_bucket_arn" {
  value = aws_s3_bucket.orca_reports_bucket.arn
}

output "orca_achive_worm_bucket_arn" {
  value = aws_s3_bucket.orca_archive_worm_bucket.arn
}