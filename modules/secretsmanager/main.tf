## Local Variables
locals {
  tags = merge(var.tags, { Deployment = var.prefix })
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
  tags                    = local.tags
}

#Reference to Cumulus secretsmanager: https://github.com/nasa/cumulus/blob/master/tf-modules/cumulus-rds-tf/main.tf#L33
resource "aws_secretsmanager_secret_version" "db_login" {
  secret_id  = aws_secretsmanager_secret.db_login.id
  depends_on = [aws_secretsmanager_secret.db_login]
  secret_string = jsonencode({
    admin_username = "var.db_admin_username"
    admin_password = var.db_admin_password
    admin_database = "postgres"
    user_username  = "orcauser"
    user_password  = var.db_user_password
    user_database  = "disaster_recovery"
    host           = var.db_host_endpoint
    port           = "5432"
  })
}
## KMS key policy
## ====================================================================================================
data "aws_iam_policy_document" "orca_kms_key_policy" {
  statement {
    sid = "orca_kms_policy"
    # work with NGAP to restrict actions
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