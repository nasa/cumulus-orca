## Terraform Requirements
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 3.5.0"
    }
  }
}

# AWS Provider Settings
provider "aws" {
  region  = var.region
  profile = var.aws_profile
}

# Local Variables
locals {
  tags = merge(var.tags, { Deployment = var.prefix })
  # Ignore aws profile in case this was deployed with CI or in a machine without
  # aws profile defined
  used_profile = contains([var.aws_profile], "default") ? "" : "--profile ${var.aws_profile}"
}

## Resources

## =============================================================================
## SECRET MANAGER RESOURCES
## =============================================================================

resource "aws_secretsmanager_secret" "db_login" {
  description             = "Admin password to be used for the Aurora PostgreSQL DB"
  kms_key_id              = aws_kms_key.orca_kms_key.arn
  name                    = "${var.prefix}-orca-db-admin-pass"
  recovery_window_in_days = 0
  tags                    = local.tags
}

resource "aws_secretsmanager_secret_version" "db_login" {
  secret_id  = aws_secretsmanager_secret.db_login.id
  depends_on = [aws_secretsmanager_secret.db_login]
  secret_string = jsonencode({
    username            = var.db_admin_username
    password            = var.db_admin_password
    database            = var.database_name
    engine              = var.db_engine
    host                = var.db_host_endpoint
    port                = var.database_port
    dbClusterIdentifier = var.db_cluster_identifier
  })
}
## KMS key policy
## ====================================================================================================
data "aws_iam_policy_document" "orca_kms_key_policy" {
  statement {
    sid = "orca_kms_policy"
    actions = [
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:ReEncrypt",
      "kms:CreateGrant",
      "kms:PutKeyPolicy",
      "kms:GenerateDataKey*",
      "kms:CreateKey",
      "kms:PutKeyPolicy",
      "kms:UpdateKeyDescription",
      "kms:DisableKey",
      "kms:DisableKeyRotation",
      "kms:ScheduleKeyDeletion",
      "kms:CancelKeyDeletion",
      "kms:DescribeKey",
      "kms:Get*",
      "kms:List*"
    ]
    resources = ["*"]
    effect    = "Allow"
    principals {
      type        = "AWS"
      identifiers = ["*"]
    }
  }
}
## KMS key resource
## ====================================================================================================
resource "aws_kms_key" "orca_kms_key" {
  description             = "KMS key for secrets in order to avoid Snyk vulnerability."
  deletion_window_in_days = 7 # range is between 7 and 30 days.
  is_enabled              = true
  policy                  = data.aws_iam_policy_document.orca_kms_key_policy.json
}