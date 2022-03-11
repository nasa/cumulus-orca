output "kms_key_id" {
  description = "The globally unique identifier for the KMS key."
  value       = aws_kms_key.orca_kms_key.key_id
}

output "kms_key_arn" {
  description = "The Amazon Resource Name (ARN) of the KMS key."
  value       = aws_kms_key.orca_kms_key.arn
}

output "secretsmanager_arn" {
  description = "The Amazon Resource Name (ARN) of the AWS secretsmanager"  # todo: It isn't. Just of one individual secret. What is consuming this? Can we safely change it?
  value       = aws_secretsmanager_secret.db_login.arn
}

output "s3_access_credentials_secret_arn" {
  description = "The Amazon Resource Name (ARN) of the s3 credentials secret."
  value       = aws_secretsmanager_secret.s3_access_credentials.arn
}
