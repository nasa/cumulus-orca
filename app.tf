provider "aws" {
  version = "~> 2.13"
  region  = "us-west-2"
  profile = var.profile
}

resource "aws_lambda_function" "db_deploy" {
  filename      = "tasks/db_deploy/dbdeploy.zip"
  function_name = "${var.prefix}_db_deploy"
  role          = aws_iam_role.restore_object_role.arn
  handler       = "db_deploy.handler"
  runtime       = "python3.7"

  vpc_config {
    subnet_ids         = var.ngap_subnets
    security_group_ids = var.ngap_sgs
  }

  environment {
    variables = {
      DATABASE_HOST            = "${module.db.this_db_instance_address}"
      DATABASE_PORT            = var.database_port
      DATABASE_NAME            = var.database_name
      DATABASE_USER            = var.database_app_user
      DATABASE_PW              = var.database_app_user_pw
      MASTER_USER_PW           = var.postgres_user_pw
      DDL_DIR                  = var.ddl_dir
      DROP_DATABASE            = var.drop_database
      PLATFORM                 = var.platform
    }
  }
}

resource "aws_lambda_function" "extract_filepaths_for_granule_lambda" {
  filename      = "tasks/extract_filepaths_for_granule/extract.zip"
  function_name = "${var.prefix}_extract_filepaths_for_granule"
  role          = aws_iam_role.restore_object_role.arn
  handler       = "extract_filepaths_for_granule.handler"
  runtime       = "python3.7"

  vpc_config {
    subnet_ids = var.ngap_subnets
    security_group_ids = var.ngap_sgs
  }
}

resource "aws_lambda_function" "request_files_lambda" {
  filename      = "tasks/request_files/request.zip"
  function_name = "${var.prefix}_request_files"
  role          = aws_iam_role.restore_object_role.arn
  handler       = "request_files.handler"
  runtime       = "python3.7"

  vpc_config {
    subnet_ids         = var.ngap_subnets
    security_group_ids = var.ngap_sgs
  }

  environment {
    variables = {
      DATABASE_HOST            = "${module.db.this_db_instance_address}"
      DATABASE_PORT            = var.database_port
      DATABASE_NAME            = var.database_name
      DATABASE_PW              = var.database_app_user_pw
      DATABASE_USER            = var.database_app_user
      RESTORE_EXPIRE_DAYS      = var.restore_expire_days
      RESTORE_REQUEST_RETRIES  = var.restore_request_retries
      RESTORE_RETRY_SLEEP_SECS = var.restore_retry_sleep_secs
    }
  }
}

resource "aws_lambda_function" "copy_files_to_archive" {
  filename      = "tasks/request_files/copy.zip"
  function_name = "${var.prefix}_copy_files_to_archive"
  role          = aws_iam_role.restore_object_role.arn
  handler       = "copy_files_to_archive.handler"
  runtime       = "python3.7"

  vpc_config {
    subnet_ids         = var.ngap_subnets
    security_group_ids = var.ngap_sgs
  }

  environment {
    variables = {
      BUCKET_MAP            = var.copy_bucket_map
      COPY_RETRIES          = var.copy_retries
      COPY_RETRY_SLEEP_SECS = var.copy_retry_sleep_secs
      DATABASE_HOST            = "${module.db.this_db_instance_address}"
      DATABASE_PORT            = var.database_port
      DATABASE_NAME            = var.database_name
      DATABASE_PW              = var.database_app_user_pw
      DATABASE_USER            = var.database_app_user
    }
  }
}

resource "aws_lambda_function" "request_status" {
  filename      = "tasks/request_files/status.zip"
  function_name = "${var.prefix}_request_status"
  role          = aws_iam_role.restore_object_role.arn
  handler       = "request_status.handler"
  runtime       = "python3.7"

  vpc_config {
    subnet_ids         = var.ngap_subnets
    security_group_ids = var.ngap_sgs
  }

  environment {
    variables = {
      DATABASE_HOST            = "${module.db.this_db_instance_address}"
      DATABASE_PORT            = var.database_port
      DATABASE_NAME            = var.database_name
      DATABASE_PW              = var.database_app_user_pw
      DATABASE_USER            = var.database_app_user
    }
  }
}