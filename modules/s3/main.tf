# todo: Pull out into a separate module per https://bugs.earthdata.nasa.gov/browse/ORCA-369

## Local Variables
locals {
  orca_bucket_names  = [for k, v in var.buckets : v.name if v.type == "orca"]
}

resource "aws_s3_bucket" "reports_bucket" {
  bucket = "${var.prefix}-orca-reports"
  tags   = var.tags

  lifecycle_rule {
    id = "30 day lifecycle"
    expiration {
      days = 30
    }

    enabled = true
  }
}

resource "aws_s3_bucket_inventory" "inventory-report" {
  for_each = toset(local.orca_bucket_names)

  bucket = each.key
  name   = "${var.prefix}-${each.key}-inventory-report"

  included_object_versions = "All"
  optional_fields = ["Size", "LastModifiedDate", "StorageClass", "ETag"]

  schedule {
    frequency = var.s3_report_frequency
  }

  destination {
    bucket {
      format     = "CSV"
      bucket_arn = aws_s3_bucket.reports_bucket.arn
    }
  }
}

