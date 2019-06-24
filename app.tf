provider "aws" {
  version = "~> 2.13"
  region  = "us-west-2"
  profile = var.profile
}

resource "aws_lambda_function" "extract_filepaths_for_granule_lambda" {
  filename      = "tasks/extract_filepaths_for_granule/task.zip"
  function_name = "${var.prefix}_extract_filepaths_for_granule"
  role          = aws_iam_role.restore_object_role.arn
  handler       = "extract_filepaths_for_granule.handler"
  runtime       = "python3.6"

  vpc_config {
    subnet_ids = var.ngap_subnets
    security_group_ids = var.ngap_sgs
  }
}

resource "aws_lambda_function" "request_files_lambda" {
  filename      = "tasks/request_files/task.zip"
  function_name = "${var.prefix}_request_files"
  role          = aws_iam_role.restore_object_role.arn
  handler       = "request_files.handler"
  runtime       = "python3.6"

  vpc_config {
    subnet_ids         = var.ngap_subnets
    security_group_ids = var.ngap_sgs
  }

  environment {
    variables = {
      restore_expire_days      = var.restore_expire_days
      restore_request_retries  = var.restore_request_retries
      restore_retry_sleep_secs = var.restore_retry_sleep_secs
    }
  }
}

resource "aws_lambda_function" "dr_copy_files_to_archive" {
  filename      = "tasks/dr_copy_files_to_archive/task.zip"
  function_name = "${var.prefix}_dr_copy_files_to_archive"
  role          = aws_iam_role.restore_object_role.arn
  handler       = "dr_copy_files_to_archive.handler"
  runtime       = "python3.6"

  vpc_config {
    subnet_ids         = var.ngap_subnets
    security_group_ids = var.ngap_sgs
  }

  environment {
    variables = {
      BUCKET_MAP            = var.copy_bucket_map
      COPY_RETRIES          = var.copy_retries
      COPY_RETRY_SLEEP_SECS = var.copy_retry_sleep_secs
    }
  }
}
