provider "aws" {
  version = "~> 2.13"
  region  = "us-west-2"
  profile = var.profile
}

resource "aws_lambda_function" "extract_filepaths_for_granule_lambda" {
  filename      = "tasks/extract_filepaths_for_granule/task.zip"
  function_name = "extract_filepaths_for_granule_tf"
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
  function_name = "request_files_tf"
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
  function_name = "dr_copy_files_to_archive_tf"
  role          = aws_iam_role.restore_object_role.arn
  handler       = "request-files.handler"
  runtime       = "python3.6"

  vpc_config {
    subnet_ids         = var.ngap_subnets
    security_group_ids = var.ngap_sgs
  }

  environment {
    variables = {
      BUCKET_MAP            = var.copy_bucket_map
      COPY_RETRIES          = var.copy_request_retries
      COPY_RETRY_SLEEP_SECS = var.copy_retry_sleep_secs
    }
  }
}
