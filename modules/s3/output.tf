output "buckets" {
  description = "S3 bucket locations for the various storage types being used."
  value       = merge(
    var.buckets, 
    {
      orca_reports = {
        name = aws_s3_bucket.reports_bucket.bucket
        type = "orca-reports"
      }
    },
  )
}