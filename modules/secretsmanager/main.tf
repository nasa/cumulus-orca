## Data Lookups

## =============================================================================
## SECRET MANAGER DATA LOOKUPS
## =============================================================================

data "aws_iam_users" "orca_users" {}

data "aws_caller_identity" "current_account" {}

data "aws_region" "current_region" {}


## Local Variables
locals {
  iam_users    = data.aws_iam_users.orca_users.arns
  account_id   = data.aws_caller_identity.current_account.account_id
  region       = data.aws_region.current_region.name
  kms_arn    = "arn:aws:kms:${local.region}:${local.account_id}:key/*"
}


## Resources

## =============================================================================
## SECRET MANAGER RESOURCES
## =============================================================================

resource "aws_secretsmanager_secret" "db_login" {
  description             = "AWS secret to be used for the Aurora PostgreSQL DB"
  kms_key_id              = aws_kms_key.orca_kms_key.arn
  name                    = "${var.prefix}-orca-db-login-secret"
  recovery_window_in_days = 0
  tags                    = var.tags
}

#Reference to Cumulus secretsmanager: https://github.com/nasa/cumulus/blob/master/tf-modules/cumulus-rds-tf/main.tf#L33
resource "aws_secretsmanager_secret_version" "db_login" {
  secret_id  = aws_secretsmanager_secret.db_login.id
  depends_on = [aws_secretsmanager_secret.db_login]
  secret_string = jsonencode({
    admin_username = var.db_admin_username
    admin_password = var.db_admin_password
    admin_database = "postgres"
    user_username  = var.db_user_name
    user_password  = var.db_user_password
    user_database  = var.db_name
    host           = var.db_host_endpoint
    port           = "5432"
  })
}

resource "aws_secretsmanager_secret" "s3_access_credentials" {
  description             = "Allows postgres to access s3"
  kms_key_id              = aws_kms_key.orca_kms_key.arn
  name                    = "${var.prefix}-orca-s3-access-credentials"
  recovery_window_in_days = 0
  tags                    = var.tags
}

#Reference to Cumulus secretsmanager: https://github.com/nasa/cumulus/blob/master/tf-modules/cumulus-rds-tf/main.tf#L33
resource "aws_secretsmanager_secret_version" "s3_access_credentials" {
  secret_id  = aws_secretsmanager_secret.s3_access_credentials.id
  depends_on = [aws_secretsmanager_secret.s3_access_credentials]
  secret_string = jsonencode({
    s3_access_key = var.s3_access_key
    s3_secret_key = var.s3_secret_key
  })
}


## KMS key policy
## ====================================================================================================
data "aws_iam_policy_document" "orca_kms_key_policy" {
  statement {
    sid = "orca_kms_policy_admin"
    # work with NGAP to restrict actions
    actions = [
      "kms:*"
    ]

    resources = ["*"]
    effect    = "Allow"

    principals {
      type        = "AWS"
      identifiers = local.iam_users 
    }
  }
  statement {
    sid = "orca_kms_policy_readonly"
    # work with NGAP to restrict actions
    actions = [
      "kms:Decrypt",
      "kms:DescribeKey"
    ]

    resources = [local.kms_arn]
    effect    = "Allow"

    principals {
      type        = "AWS"
      identifiers = [var.restore_object_role_arn]
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
