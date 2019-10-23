provider "aws" {
  version = "~> 2.13"
  region  = var.region
  profile = var.profile
}

resource "aws_lambda_function" "db_deploy" {
  filename      = "tasks/db_deploy/dbdeploy.zip"
  function_name = "${var.prefix}_db_deploy"
  role          = aws_iam_role.restore_object_role.arn
  handler       = "db_deploy.handler"
  runtime       = "python3.7"
  timeout       = 300
  description   = "Deploys the Disaster Recovery database"

  vpc_config {
    subnet_ids         = var.ngap_subnets
    security_group_ids = var.ngap_sgs
  }

  environment {
    variables = {
      DATABASE_HOST  = aws_db_instance.postgresql.address
      DATABASE_PORT  = var.database_port
      DATABASE_NAME  = var.database_name
      DATABASE_USER  = var.database_app_user
      DATABASE_PW    = var.database_app_user_pw
      MASTER_USER_PW = var.postgres_user_pw
      DDL_DIR        = var.ddl_dir
      DROP_DATABASE  = var.drop_database
      PLATFORM       = var.platform
    }
  }
}

resource "aws_lambda_function" "extract_filepaths_for_granule_lambda" {
  filename      = "tasks/extract_filepaths_for_granule/extract.zip"
  function_name = "${var.prefix}_extract_filepaths_for_granule"
  role          = aws_iam_role.restore_object_role.arn
  handler       = "extract_filepaths_for_granule.handler"
  runtime       = "python3.7"
  timeout       = 300
  description   = "Extracts bucket info and granules file keys from the CMA"

  vpc_config {
    subnet_ids         = var.ngap_subnets
    security_group_ids = var.ngap_sgs
  }
}

resource "aws_lambda_function" "request_files_lambda" {
  filename      = "tasks/request_files/request.zip"
  function_name = "${var.prefix}_request_files"
  role          = aws_iam_role.restore_object_role.arn
  handler       = "request_files.handler"
  runtime       = "python3.7"
  timeout       = 300
  description   = "Submits a restore request for a file"

  vpc_config {
    subnet_ids         = var.ngap_subnets
    security_group_ids = var.ngap_sgs
  }

  environment {
    variables = {
      DATABASE_HOST            = aws_db_instance.postgresql.address
      DATABASE_PORT            = var.database_port
      DATABASE_NAME            = var.database_name
      DATABASE_PW              = var.database_app_user_pw
      DATABASE_USER            = var.database_app_user
      RESTORE_EXPIRE_DAYS      = var.restore_expire_days
      RESTORE_REQUEST_RETRIES  = var.restore_request_retries
      RESTORE_RETRY_SLEEP_SECS = var.restore_retry_sleep_secs
      RESTORE_RETRIEVAL_TYPE   = var.restore_retrieval_type
    }
  }
}

resource "aws_lambda_function" "copy_files_to_archive" {
  filename      = "tasks/copy_files_to_archive/copy.zip"
  function_name = "${var.prefix}_copy_files_to_archive"
  role          = aws_iam_role.restore_object_role.arn
  handler       = "copy_files_to_archive.handler"
  runtime       = "python3.7"
  timeout       = 300
  description   = "Copies a restored file to the archive"

  vpc_config {
    subnet_ids         = var.ngap_subnets
    security_group_ids = var.ngap_sgs
  }

  environment {
    variables = {
      COPY_RETRIES          = var.copy_retries
      COPY_RETRY_SLEEP_SECS = var.copy_retry_sleep_secs
      DATABASE_HOST         = aws_db_instance.postgresql.address
      DATABASE_PORT         = var.database_port
      DATABASE_NAME         = var.database_name
      DATABASE_PW           = var.database_app_user_pw
      DATABASE_USER         = var.database_app_user
    }
  }
}

resource "aws_lambda_function" "request_status" {
  filename      = "tasks/request_status/status.zip"
  function_name = "${var.prefix}_request_status"
  role          = aws_iam_role.restore_object_role.arn
  handler       = "request_status.handler"
  runtime       = "python3.7"
  timeout       = 300
  description   = "Queries the Disaster Recovery database for status"

  vpc_config {
    subnet_ids         = var.ngap_subnets
    security_group_ids = var.ngap_sgs
  }

  environment {
    variables = {
      DATABASE_HOST = aws_db_instance.postgresql.address
      DATABASE_PORT = var.database_port
      DATABASE_NAME = var.database_name
      DATABASE_PW   = var.database_app_user_pw
      DATABASE_USER = var.database_app_user
    }
  }
}

resource "aws_s3_bucket_notification" "copy_lambda_trigger" {
  bucket = "${var.glacier_bucket}"

  lambda_function {
    lambda_function_arn = "${aws_lambda_function.copy_files_to_archive.arn}"
    events              = ["s3:ObjectRestore:Completed"]
    filter_prefix       = "${var.restore_complete_filter_prefix}"
  }
}
