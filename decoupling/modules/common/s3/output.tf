
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