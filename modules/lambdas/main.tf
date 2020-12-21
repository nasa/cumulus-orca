
locals {
  default_tags = {
    Deployment = var.prefix
  }
}

module "lambda_security_group" {
  source = "../security_groups"
  tags = var.tags
  vpc_id = var.vpc_id
  prefix = var.prefix
}

module "restore_object_arn" {
  source = "../iam"
  buckets = var.buckets
  prefix = var.prefix
  permissions_boundary_arn = var.permissions_boundary_arn
}

// You don't need to specify orca version if you used source_code_hash
resource "aws_lambda_function" "db_deploy" {
  filename      = "${path.module}/../../tasks/db_deploy/db_deploy.zip"
  function_name = "${var.prefix}_db_deploy"
  source_code_hash = filemd5("${path.module}/../../tasks/db_deploy/db_deploy.zip")
  role          = module.restore_object_arn.restore_object_role_arn
  handler       = "db_deploy.handler"
  runtime       = "python3.7"
  timeout       = var.lambda_timeout
  description   = "Deploys the Disaster Recovery database"

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = [module.lambda_security_group.vpc_postgres_ingress_all_egress_id]
  }

  environment {
    variables = {
      PREFIX        = var.prefix
      DATABASE_PORT = var.database_port
      DATABASE_NAME = var.database_name
      DATABASE_USER = var.database_app_user
      DDL_DIR       = var.ddl_dir
      DROP_DATABASE = var.drop_database
      PLATFORM      = var.platform
    }
  }
}


resource "aws_lambda_function" "extract_filepaths_for_granule_lambda" {
  filename         = "${path.module}/../../tasks/extract_filepaths_for_granule/extract_filepaths_for_granule.zip"
  source_code_hash = filemd5("${path.module}/../../tasks/extract_filepaths_for_granule/extract_filepaths_for_granule.zip")
  function_name    = "${var.prefix}_extract_filepaths_for_granule"
  role             = module.restore_object_arn.restore_object_role_arn
  handler          = "extract_filepaths_for_granule.handler"
  runtime          = "python3.7"
  timeout          = var.lambda_timeout
  description      = "Extracts bucket info and granules file keys from the CMA"

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = [module.lambda_security_group.vpc_postgres_ingress_all_egress_id]
  }
}


resource "aws_lambda_function" "request_files_lambda" {
  filename         = "${path.module}/../../tasks/request_files/request_files.zip"
  function_name    = "${var.prefix}_request_files"
  source_code_hash = filemd5("${path.module}/../../tasks/request_files/request_files.zip")
  role             = module.restore_object_arn.restore_object_role_arn
  handler          = "request_files.handler"
  runtime          = "python3.7"
  timeout          = var.lambda_timeout
  description      = "Submits a restore request for a file"

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = [module.lambda_security_group.vpc_postgres_ingress_all_egress_id]
  }

  environment {
    variables = {
      PREFIX                   = var.prefix
      DATABASE_PORT            = var.database_port
      DATABASE_NAME            = var.database_name
      DATABASE_USER            = var.database_app_user
      RESTORE_EXPIRE_DAYS      = var.restore_expire_days
      RESTORE_REQUEST_RETRIES  = var.restore_request_retries
      RESTORE_RETRY_SLEEP_SECS = var.restore_retry_sleep_secs
      RESTORE_RETRIEVAL_TYPE   = var.restore_retrieval_type
    }
  }
}


resource "aws_lambda_function" "copy_files_to_archive" {
  filename      = "${path.module}/../../tasks/copy_files_to_archive/copy_files_to_archive.zip"
  source_code_hash = filemd5("${path.module}/../../tasks/copy_files_to_archive/copy_files_to_archive.zip")
  function_name = "${var.prefix}_copy_files_to_archive"
  role          = module.restore_object_arn.restore_object_role_arn
  handler       = "copy_files_to_archive.handler"
  runtime       = "python3.7"
  timeout       = var.lambda_timeout
  description   = "Copies a restored file to the archive"

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = [module.lambda_security_group.vpc_postgres_ingress_all_egress_id]
  }

  environment {
    variables = {
      PREFIX                = var.prefix
      COPY_RETRIES          = var.copy_retries
      COPY_RETRY_SLEEP_SECS = var.copy_retry_sleep_secs
      DATABASE_PORT         = var.database_port
      DATABASE_NAME         = var.database_name
      DATABASE_USER         = var.database_app_user
    }
  }
}

resource "aws_lambda_function" "request_status" {
  filename      = "${path.module}/../../tasks/request_status/request_status.zip"
  source_code_hash = filemd5("${path.module}/../../tasks/request_status/request_status.zip")
  function_name = "${var.prefix}_request_status"
  role          = module.restore_object_arn.restore_object_role_arn
  handler       = "request_status.handler"
  runtime       = "python3.7"
  timeout       = var.lambda_timeout
  description   = "Queries the Disaster Recovery database for status"

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = [module.lambda_security_group.vpc_postgres_ingress_all_egress_id]
  }

  environment {
    variables = {
      PREFIX        = var.prefix
      DATABASE_PORT = var.database_port
      DATABASE_NAME = var.database_name
      DATABASE_USER = var.database_app_user
    }
  }
}

resource "aws_lambda_permission" "allow_s3_trigger" {
  statement_id  = "AllowExecutionFromS3"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.copy_files_to_archive.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = "arn:aws:s3:::${var.buckets["glacier"]["name"]}"
}


resource "aws_s3_bucket_notification" "copy_lambda_trigger" {
  depends_on = [aws_lambda_permission.allow_s3_trigger]
  bucket = var.buckets["glacier"]["name"]

  lambda_function {
    lambda_function_arn = aws_lambda_function.copy_files_to_archive.arn
    events              = ["s3:ObjectRestore:Completed"]
    filter_prefix       = var.restore_complete_filter_prefix
  }
}


resource "aws_lambda_function" "copy_to_glacier" {
  function_name    = "${var.prefix}_copy_to_glacier"
  filename         = "${path.module}/../../tasks/copy_to_glacier/copy_to_glacier.zip"
  source_code_hash = filemd5("${path.module}/../../tasks/copy_to_glacier/copy_to_glacier.zip")
  handler          = "handler.handler"
  role             = module.restore_object_arn.restore_object_role_arn
  runtime          = "python3.7"
  memory_size      = 2240
  timeout          = 600 # 10 minutes

  tags = local.default_tags
  environment {
    variables = {
      system_bucket               = var.buckets["internal"]["name"]
      stackName                   = var.prefix
      CUMULUS_MESSAGE_ADAPTER_DIR = "/opt/"
    }
  }

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = [module.lambda_security_group.vpc_postgres_ingress_all_egress_id]
  }
}
