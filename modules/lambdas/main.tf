## Terraform Requirements
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 3.5.0"
    }
  }
}


## AWS Provider Settings
provider "aws" {
  region  = var.region
  profile = var.aws_profile
}


## Local Variables
locals {
  tags         = merge(var.tags, { Deployment = var.prefix })
  orca_buckets = [for k, v in var.buckets : v.name if v.type == "orca"]
}


## Referenced Modules
# lambda_security_group - Security Groups module reference
# ------------------------------------------------------------------------------
module "lambda_security_group" {
  source = "../security_groups"
  ## --------------------------
  ## Cumulus Variables
  ## --------------------------
  ## REQUIRED
  aws_profile = var.aws_profile
  prefix      = var.prefix
  vpc_id      = var.vpc_id
  ## OPTIONAL
  region = var.region
  tags   = local.tags
  ## --------------------------
  ## ORCA Variables
  ## --------------------------
  ## OPTIONAL
  database_port = var.database_port
}

# restore_object_arn - IAM module reference
# ------------------------------------------------------------------------------
module "restore_object_arn" {
  source = "../iam"
  ## --------------------------
  ## Cumulus Variables
  ## --------------------------
  ## REQUIRED
  aws_profile              = var.aws_profile
  buckets                  = var.buckets
  permissions_boundary_arn = var.permissions_boundary_arn
  prefix                   = var.prefix
  ## OPTIONAL
  region = var.region
  tags   = local.tags
  ## --------------------------
  ## ORCA Variables
  ## --------------------------
  ## OPTIONAL
  orca_recovery_buckets = var.orca_recovery_buckets
}


## =============================================================================
## Ingest Lambdas Definitions and Resources
## =============================================================================

# copy_to_glacier - Copies files to the ORCA S3 Glacier bucket
# ==============================================================================
resource "aws_lambda_function" "copy_to_glacier" {
  ## REQUIRED
  function_name = "${var.prefix}_copy_to_glacier"
  role          = module.restore_object_arn.restore_object_role_arn

  ## OPTIONAL
  description      = "ORCA archiving lambda used to copy data to an ORCA S3 glacier bucket."
  filename         = "${path.module}/../../tasks/copy_to_glacier/copy_to_glacier.zip"
  handler          = "copy_to_glacier.handler"
  memory_size      = var.orca_ingest_lambda_memory_size
  runtime          = "python3.7"
  source_code_hash = filebase64sha256("${path.module}/../../tasks/copy_to_glacier/copy_to_glacier.zip")
  tags             = local.tags
  timeout          = var.orca_ingest_lambda_timeout

  vpc_config {
    subnet_ids         = var.lambda_subnet_ids
    security_group_ids = [module.lambda_security_group.vpc_postgres_ingress_all_egress_id]
  }

  environment {
    variables = {
      ORCA_DEFAULT_BUCKET = var.orca_default_bucket
    }
  }
}


## =============================================================================
## Recovery Lambdas Definitions and Resources
## =============================================================================

# extract_filepaths_for_granule - Translates input for request_files lambda
# ==============================================================================
resource "aws_lambda_function" "extract_filepaths_for_granule" {
  ## REQUIRED
  function_name = "${var.prefix}_extract_filepaths_for_granule"
  role          = module.restore_object_arn.restore_object_role_arn

  ## OPTIONAL
  description      = "Extracts bucket info and granules filepath from the CMA for ORCA request_files lambda."
  filename         = "${path.module}/../../tasks/extract_filepaths_for_granule/extract_filepaths_for_granule.zip"
  handler          = "extract_filepaths_for_granule.handler"
  memory_size      = var.orca_recovery_lambda_memory_size
  runtime          = "python3.7"
  source_code_hash = filebase64sha256("${path.module}/../../tasks/extract_filepaths_for_granule/extract_filepaths_for_granule.zip")
  tags             = local.tags
  timeout          = var.orca_recovery_lambda_timeout

  vpc_config {
    subnet_ids         = var.lambda_subnet_ids
    security_group_ids = [module.lambda_security_group.vpc_postgres_ingress_all_egress_id]
  }
}


# request_files - Requests files from ORCA S3 Glacier
# ==============================================================================
resource "aws_lambda_function" "request_files" {
  ## REQUIRED
  function_name = "${var.prefix}_request_files"
  role          = module.restore_object_arn.restore_object_role_arn

  ## OPTIONAL
  description      = "Submits a restore request for all archived files in a granule to the ORCA S3 Glacier bucket."
  filename         = "${path.module}/../../tasks/request_files/request_files.zip"
  handler          = "request_files.handler"
  memory_size      = var.orca_recovery_lambda_memory_size
  runtime          = "python3.7"
  source_code_hash = filebase64sha256("${path.module}/../../tasks/request_files/request_files.zip")
  tags             = local.tags
  timeout          = var.orca_recovery_lambda_timeout

  vpc_config {
    subnet_ids         = var.lambda_subnet_ids
    security_group_ids = [module.lambda_security_group.vpc_postgres_ingress_all_egress_id]
  }

  environment {
    variables = {
      RESTORE_EXPIRE_DAYS      = var.orca_recovery_expiration_days
      RESTORE_REQUEST_RETRIES  = var.orca_recovery_retry_limit
      RESTORE_RETRY_SLEEP_SECS = var.orca_recovery_retry_interval
      RESTORE_RETRIEVAL_TYPE   = var.orca_recovery_retrieval_type
      DB_QUEUE_URL             = var.orca_sqs_status_update_queue_id
      ORCA_DEFAULT_BUCKET      = var.orca_default_bucket
    }
  }
}


# copy_files_to_archive - Copies files from ORCA S3 Glacier to destination bucket
# ==============================================================================
resource "aws_lambda_function" "copy_files_to_archive" {
  ## REQUIRED
  function_name = "${var.prefix}_copy_files_to_archive"
  role          = module.restore_object_arn.restore_object_role_arn

  ## OPTIONAL
  description      = "Copies a restored file to the archive"
  filename         = "${path.module}/../../tasks/copy_files_to_archive/copy_files_to_archive.zip"
  handler          = "copy_files_to_archive.handler"
  memory_size      = var.orca_recovery_lambda_memory_size
  runtime          = "python3.7"
  source_code_hash = filebase64sha256("${path.module}/../../tasks/copy_files_to_archive/copy_files_to_archive.zip")
  tags             = local.tags
  timeout          = var.orca_recovery_lambda_timeout

  vpc_config {
    subnet_ids         = var.lambda_subnet_ids
    security_group_ids = [module.lambda_security_group.vpc_postgres_ingress_all_egress_id]
  }

  environment {
    variables = {
      COPY_RETRIES          = var.orca_recovery_retry_limit
      COPY_RETRY_SLEEP_SECS = var.orca_recovery_retry_interval
      DB_QUEUE_URL          = var.orca_sqs_status_update_queue_id
    }
  }
}

resource "aws_lambda_event_source_mapping" "copy_files_to_archive_event_source_mapping" {
  event_source_arn = var.orca_sqs_staged_recovery_queue_arn
  function_name    = aws_lambda_function.copy_files_to_archive.handler
}

# Additional resources needed by copy_files_to_archive
# ------------------------------------------------------------------------------
# Permissions to allow SQS trigger to invoke lambda
resource "aws_lambda_permission" "allow_sqs_trigger" {
  ## REQUIRED
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.copy_files_to_archive.function_name
  principal     = "sqs.amazonaws.com"

  ## OPTIONAL
  statement_id = "AllowExecutionFromSQS"
  source_arn   = module.sqs.orca_sqs_staged_recovery_queue_arn
}

# todo: Use the below as a base for s3 triggering of new lambda
## copy_lambda_trigger - Bucket notification trigger pointed to lambda
#resource "aws_s3_bucket_notification" "copy_lambda_trigger" {
#  # Create loop so we can handle multiple orca buckets
#  for_each = toset(local.orca_buckets)
#
#  # The permissions must be defined first
#  depends_on = [aws_lambda_permission.allow_s3_trigger]
#
#  ## REQUIRED
#  bucket = each.value
#
#  ## OPTIONAL
#  lambda_function {
#    ## REQUIRED
#    events              = ["s3:ObjectRestore:Completed"]
#    lambda_function_arn = aws_lambda_function.copy_files_to_archive.arn
#
#    ## OPTIONAL
#    filter_prefix = var.orca_recovery_complete_filter_prefix
#  }
#}

# request_status - CLI to provide operator status of recovery job
# ==============================================================================
resource "aws_lambda_function" "request_status" {
  ## REQUIRED
  function_name = "${var.prefix}_request_status"
  role          = module.restore_object_arn.restore_object_role_arn

  ## OPTIONAL
  description      = "Queries the Disaster Recovery database for status"
  filename         = "${path.module}/../../tasks/request_status/request_status.zip"
  handler          = "request_status.handler"
  memory_size      = var.orca_recovery_lambda_memory_size
  runtime          = "python3.7"
  source_code_hash = filebase64sha256("${path.module}/../../tasks/request_status/request_status.zip")
  tags             = local.tags
  timeout          = var.orca_recovery_lambda_timeout

  vpc_config {
    subnet_ids         = var.lambda_subnet_ids
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


# request_status_for_granule - Provides recovery status information on a specific granule
# ==============================================================================
resource "aws_lambda_function" "request_status_for_granule" {
  ## REQUIRED
  function_name = "${var.prefix}_request_status_for_granule"
  role          = module.restore_object_arn.restore_object_role_arn

  ## OPTIONAL
  description      = "Provides ORCA recover status information on a specific granule and job."
  filename         = "${path.module}/../../tasks/request_status_for_granule/request_status_for_granule.zip"
  handler          = "request_status_for_granule.handler"
  memory_size      = var.orca_recovery_lambda_memory_size
  runtime          = "python3.7"
  source_code_hash = filebase64sha256("${path.module}/../../tasks/request_status_for_granule/request_status_for_granule.zip")
  tags             = local.tags
  timeout          = var.orca_recovery_lambda_timeout

  vpc_config {
    subnet_ids         = var.lambda_subnet_ids
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


# request_status_for_job - Provides recovery status information for a job.
# ==============================================================================
resource "aws_lambda_function" "request_status_for_job" {
  ## REQUIRED
  function_name = "${var.prefix}_request_status_for_job"
  role          = module.restore_object_arn.restore_object_role_arn

  ## OPTIONAL
  description      = "Provides ORCA recover status information on a specific job."
  filename         = "${path.module}/../../tasks/request_status_for_job/request_status_for_job.zip"
  handler          = "request_status_for_job.handler"
  memory_size      = var.orca_recovery_lambda_memory_size
  runtime          = "python3.7"
  source_code_hash = filebase64sha256("${path.module}/../../tasks/request_status_for_job/request_status_for_job.zip")
  tags             = local.tags
  timeout          = var.orca_recovery_lambda_timeout

  vpc_config {
    subnet_ids         = var.lambda_subnet_ids
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


## =============================================================================
## Utility Lambda Definitions
## =============================================================================

# db_deploy - Lambda that deploys database resources
# ==============================================================================
resource "aws_lambda_function" "db_deploy" {
  ## REQUIRED
  function_name = "${var.prefix}_db_deploy"
  role          = module.restore_object_arn.restore_object_role_arn

  ## OPTIONAL
  description      = "ORCA database deployment lambda used to create and bootstrap the ORCA database."
  filename         = "${path.module}/../../tasks/db_deploy/db_deploy.zip"
  handler          = "db_deploy.handler"
  memory_size      = var.orca_recovery_lambda_memory_size
  runtime          = "python3.7"
  source_code_hash = filebase64sha256("${path.module}/../../tasks/db_deploy/db_deploy.zip")
  tags             = local.tags
  timeout          = var.orca_recovery_lambda_timeout

  vpc_config {
    subnet_ids         = var.lambda_subnet_ids
    security_group_ids = [module.lambda_security_group.vpc_postgres_ingress_all_egress_id]
  }

  environment {
    variables = {
      PREFIX        = var.prefix
      DATABASE_PORT = var.database_port
      DATABASE_NAME = var.database_name
      DATABASE_USER = var.database_app_user
      DROP_DATABASE = var.drop_database
      DDL_DIR       = var.ddl_dir
      ## TODO: Look into removing this variable and associated logic.
      PLATFORM = var.platform
    }
  }
}

