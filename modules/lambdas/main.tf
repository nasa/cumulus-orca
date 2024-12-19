# Local Variables
locals {
  orca_buckets = [for k, v in var.buckets : v.name if v.type == "orca"]
}


# # Referenced Modules
# lambda_security_group - Security Groups module reference
# ------------------------------------------------------------------------------
module "lambda_security_group" {
  source = "../security_groups"
  ## --------------------------
  ## Cumulus Variables
  ## --------------------------
  ## REQUIRED
  prefix                = var.prefix
  rds_security_group_id = var.rds_security_group_id
  vpc_id                = var.vpc_id
  ## OPTIONAL
  tags = var.tags
}


# =============================================================================
# Ingest Lambdas Definitions and Resources
# =============================================================================

# copy_to_archive - Copies files to the archive bucket
resource "aws_lambda_function" "copy_to_archive" {
  ## REQUIRED
  function_name = "${var.prefix}_copy_to_orca" # Since this is currently public-facing, emphasize that this is an ORCA resource.
  role          = var.restore_object_role_arn

  ## OPTIONAL
  description      = "ORCA archiving lambda used to copy data to an archive bucket."
  filename         = "${path.module}/../../tasks/copy_to_archive/copy_to_archive.zip"
  handler          = "copy_to_archive.handler"
  memory_size      = var.orca_ingest_lambda_memory_size
  runtime          = var.lambda_runtime
  source_code_hash = filebase64sha256("${path.module}/../../tasks/copy_to_archive/copy_to_archive.zip")
  tags             = var.tags
  timeout          = var.orca_ingest_lambda_timeout

  vpc_config {
    subnet_ids         = var.lambda_subnet_ids
    security_group_ids = [module.lambda_security_group.vpc_all_egress_id]
  }

  environment {
    variables = {
      ORCA_DEFAULT_BUCKET            = var.orca_default_bucket
      DEFAULT_MULTIPART_CHUNKSIZE_MB = var.default_multipart_chunksize_mb
      DEFAULT_STORAGE_CLASS          = var.orca_default_storage_class
      METADATA_DB_QUEUE_URL          = var.orca_sqs_metadata_queue_id
      POWERTOOLS_SERVICE_NAME        = "orca.ingest"
      LOG_LEVEL                      = var.log_level
      DEFAULT_MAX_POOL_CONNECTIONS   = var.max_pool_connections
    }
  }
}

## =============================================================================
## Reconciliation Lambdas Definitions and Resources
## =============================================================================

# delete_old_reconcile_jobs - Deletes old internal reconciliation reports, reducing DB size.
# ==============================================================================
resource "aws_lambda_function" "delete_old_reconcile_jobs" {
  ## REQUIRED
  function_name = "${var.prefix}_delete_old_reconcile_jobs"
  role          = var.restore_object_role_arn

  ## OPTIONAL
  description      = "Deletes old internal reconciliation reports, reducing DB size."
  filename         = "${path.module}/../../tasks/delete_old_reconcile_jobs/delete_old_reconcile_jobs.zip"
  handler          = "delete_old_reconcile_jobs.handler"
  memory_size      = var.orca_reconciliation_lambda_memory_size
  runtime          = var.lambda_runtime
  source_code_hash = filebase64sha256("${path.module}/../../tasks/delete_old_reconcile_jobs/delete_old_reconcile_jobs.zip")
  tags             = var.tags
  timeout          = var.orca_reconciliation_lambda_timeout

  vpc_config {
    subnet_ids         = var.lambda_subnet_ids
    security_group_ids = [module.lambda_security_group.vpc_postgres_ingress_all_egress_id]
  }

  environment {
    variables = {
      DB_CONNECT_INFO_SECRET_ARN              = var.db_connect_info_secret_arn
      INTERNAL_RECONCILIATION_EXPIRATION_DAYS = var.orca_internal_reconciliation_expiration_days
      POWERTOOLS_SERVICE_NAME                 = "orca.internal_reconciliation"
      LOG_LEVEL                               = var.log_level
    }
  }
}

# rule to run the lambda periodically
resource "aws_cloudwatch_event_rule" "delete_old_reconcile_jobs_event_rule" {
  ## REQUIRED
  name                = "${var.prefix}_delete_old_reconcile_jobs_event_rule"
  schedule_expression = var.orca_delete_old_reconcile_jobs_frequency_cron

  ## OPTIONAL
  description = "Scheduled execution of the ${aws_lambda_function.delete_old_reconcile_jobs.function_name} lambda."
  tags        = var.tags
}

resource "aws_cloudwatch_event_target" "delete_old_reconcile_jobs_event_link" {
  arn  = aws_lambda_function.delete_old_reconcile_jobs.arn
  rule = aws_cloudwatch_event_rule.delete_old_reconcile_jobs_event_rule.id
}

# Permissions to allow cloudwatch rule to invoke lambda
resource "aws_lambda_permission" "delete_old_reconcile_jobs_allow_cloudwatch_event" {
  ## REQUIRED
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.delete_old_reconcile_jobs.function_name
  principal     = "events.amazonaws.com"

  ## OPTIONAL
  statement_id = "AllowExecutionFromEvent"
  source_arn   = aws_cloudwatch_event_rule.delete_old_reconcile_jobs_event_rule.arn
}

# get_current_archive_list - From an s3 event for an s3 inventory report's manifest.json, pulls inventory report into postgres.
# ==============================================================================
resource "aws_lambda_function" "get_current_archive_list" {
  ## REQUIRED
  function_name = "${var.prefix}_get_current_archive_list"
  role          = var.gql_tasks_role_arn

  ## OPTIONAL
  description      = "Receives a list of s3 events from an SQS queue, and loads the s3 inventory specified into postgres."
  filename         = "${path.module}/../../tasks/get_current_archive_list/get_current_archive_list.zip"
  handler          = "get_current_archive_list.handler"
  memory_size      = var.orca_reconciliation_lambda_memory_size
  runtime          = var.lambda_runtime
  source_code_hash = filebase64sha256("${path.module}/../../tasks/get_current_archive_list/get_current_archive_list.zip")
  tags             = var.tags
  timeout          = var.orca_reconciliation_lambda_timeout

  vpc_config {
    subnet_ids         = var.lambda_subnet_ids
    security_group_ids = [module.lambda_security_group.vpc_postgres_ingress_all_egress_id]
  }

  environment {
    variables = {
      DB_CONNECT_INFO_SECRET_ARN = var.db_connect_info_secret_arn
      INTERNAL_REPORT_QUEUE_URL  = var.orca_sqs_internal_report_queue_id,
      POWERTOOLS_SERVICE_NAME    = "orca.internal_reconciliation"
      LOG_LEVEL                  = var.log_level
    }
  }
}

resource "aws_lambda_function" "perform_orca_reconcile" {
  ## REQUIRED
  function_name = "${var.prefix}_perform_orca_reconcile"
  role          = var.restore_object_role_arn

  ## OPTIONAL
  description      = "Receives a list of s3 events from an SQS queue, and loads the s3 inventory specified into postgres."
  filename         = "${path.module}/../../tasks/perform_orca_reconcile/perform_orca_reconcile.zip"
  handler          = "perform_orca_reconcile.handler"
  memory_size      = var.orca_reconciliation_lambda_memory_size
  runtime          = var.lambda_runtime
  source_code_hash = filebase64sha256("${path.module}/../../tasks/perform_orca_reconcile/perform_orca_reconcile.zip")
  tags             = var.tags
  timeout          = var.orca_reconciliation_lambda_timeout

  vpc_config {
    subnet_ids         = var.lambda_subnet_ids
    security_group_ids = [module.lambda_security_group.vpc_postgres_ingress_all_egress_id]
  }

  environment {
    variables = {
      DB_CONNECT_INFO_SECRET_ARN = var.db_connect_info_secret_arn
      INTERNAL_REPORT_QUEUE_URL  = var.orca_sqs_internal_report_queue_id
      POWERTOOLS_SERVICE_NAME    = "orca.internal_reconciliation"
      LOG_LEVEL                  = var.log_level
    }
  }
}

# internal_reconcile_report_job - Receives page index from end user and returns available internal reconciliation jobs from the Orca database.
# ==============================================================================
resource "aws_lambda_function" "internal_reconcile_report_job" {
  ## REQUIRED
  function_name = "${var.prefix}_internal_reconcile_report_job"
  role          = var.restore_object_role_arn

  ## OPTIONAL
  description      = "Receives page index from end user and returns available internal reconciliation jobs from the Orca database."
  filename         = "${path.module}/../../tasks/internal_reconcile_report_job/internal_reconcile_report_job.zip"
  handler          = "internal_reconcile_report_job.handler"
  memory_size      = var.orca_reconciliation_lambda_memory_size
  runtime          = var.lambda_runtime
  source_code_hash = filebase64sha256("${path.module}/../../tasks/internal_reconcile_report_job/internal_reconcile_report_job.zip")
  tags             = var.tags
  timeout          = var.orca_reconciliation_lambda_timeout

  vpc_config {
    subnet_ids         = var.lambda_subnet_ids
    security_group_ids = [module.lambda_security_group.vpc_postgres_ingress_all_egress_id]
  }

  environment {
    variables = {
      DB_CONNECT_INFO_SECRET_ARN = var.db_connect_info_secret_arn
      POWERTOOLS_SERVICE_NAME    = "orca.internal_reconciliation"
      LOG_LEVEL                  = var.log_level
    }
  }
}

# internal_reconcile_report_mismatch - Receives job id and page index from end user and returns reporting information of files that have records in the S3 bucket but are missing from ORCA catalog.
# ==============================================================================
resource "aws_lambda_function" "internal_reconcile_report_mismatch" {
  ## REQUIRED
  function_name = "${var.prefix}_internal_reconcile_report_mismatch"
  role          = var.restore_object_role_arn

  ## OPTIONAL
  description      = "Receives job id and page index from end user and returns reporting information of files that have records in the S3 bucket and the ORCA catalog, but the records disagree."
  filename         = "${path.module}/../../tasks/internal_reconcile_report_mismatch/internal_reconcile_report_mismatch.zip"
  handler          = "internal_reconcile_report_mismatch.handler"
  memory_size      = var.orca_reconciliation_lambda_memory_size
  runtime          = var.lambda_runtime
  source_code_hash = filebase64sha256("${path.module}/../../tasks/internal_reconcile_report_mismatch/internal_reconcile_report_mismatch.zip")
  tags             = var.tags
  timeout          = var.orca_reconciliation_lambda_timeout

  vpc_config {
    subnet_ids         = var.lambda_subnet_ids
    security_group_ids = [module.lambda_security_group.vpc_postgres_ingress_all_egress_id]
  }

  environment {
    variables = {
      DB_CONNECT_INFO_SECRET_ARN = var.db_connect_info_secret_arn
      POWERTOOLS_SERVICE_NAME    = "orca.internal_reconciliation"
      LOG_LEVEL                  = var.log_level
    }
  }
}

# internal_reconcile_report_orphan - Receives job id and page index from end user and returns reporting information of files that have records in the S3 bucket but are missing from ORCA catalog.
# ==============================================================================
resource "aws_lambda_function" "internal_reconcile_report_orphan" {
  ## REQUIRED
  function_name = "${var.prefix}_internal_reconcile_report_orphan"
  role          = var.restore_object_role_arn

  ## OPTIONAL
  description      = "Receives job id and page index from end user and returns reporting information of files that have records in the S3 bucket but are missing from ORCA catalog."
  filename         = "${path.module}/../../tasks/internal_reconcile_report_orphan/internal_reconcile_report_orphan.zip"
  handler          = "src.adapters.api.aws.handler"
  memory_size      = var.orca_reconciliation_lambda_memory_size
  runtime          = var.lambda_runtime
  source_code_hash = filebase64sha256("${path.module}/../../tasks/internal_reconcile_report_orphan/internal_reconcile_report_orphan.zip")
  tags             = var.tags
  timeout          = var.orca_reconciliation_lambda_timeout

  vpc_config {
    subnet_ids         = var.lambda_subnet_ids
    security_group_ids = [module.lambda_security_group.vpc_postgres_ingress_all_egress_id]
  }

  environment {
    variables = {
      DB_CONNECT_INFO_SECRET_ARN = var.db_connect_info_secret_arn
      POWERTOOLS_SERVICE_NAME    = "orca.internal_reconciliation"
      LOG_LEVEL                  = var.log_level
    }
  }
}

# internal_reconcile_report_phantom - Receives job id and page index from end user and returns reporting information of files that have records in the ORCA catalog but are missing from S3 bucket.
# ==============================================================================
resource "aws_lambda_function" "internal_reconcile_report_phantom" {
  ## REQUIRED
  function_name = "${var.prefix}_internal_reconcile_report_phantom"
  role          = var.restore_object_role_arn

  ## OPTIONAL
  description      = "Receives job id and page index from end user and returns reporting information of files that have records in the ORCA catalog but are missing from S3 bucket."
  filename         = "${path.module}/../../tasks/internal_reconcile_report_phantom/internal_reconcile_report_phantom.zip"
  handler          = "internal_reconcile_report_phantom.handler"
  memory_size      = var.orca_reconciliation_lambda_memory_size
  runtime          = var.lambda_runtime
  source_code_hash = filebase64sha256("${path.module}/../../tasks/internal_reconcile_report_phantom/internal_reconcile_report_phantom.zip")
  tags             = var.tags
  timeout          = var.orca_reconciliation_lambda_timeout

  vpc_config {
    subnet_ids         = var.lambda_subnet_ids
    security_group_ids = [module.lambda_security_group.vpc_postgres_ingress_all_egress_id]
  }

  environment {
    variables = {
      DB_CONNECT_INFO_SECRET_ARN = var.db_connect_info_secret_arn
      POWERTOOLS_SERVICE_NAME    = "orca.internal_reconciliation"
      LOG_LEVEL                  = var.log_level
    }
  }
}

## =============================================================================
## Recovery Lambdas Definitions and Resources
## =============================================================================

# extract_filepaths_for_granule - Translates input for request_from_archive lambda
# ==============================================================================
resource "aws_lambda_function" "extract_filepaths_for_granule" {
  ## REQUIRED
  function_name = "${var.prefix}_extract_filepaths_for_granule"
  role          = aws_iam_role.extract_filepaths_for_granule_iam_role.arn

  ## OPTIONAL
  description      = "Extracts bucket info and granules filepath from the CMA for ORCA request_from_archive lambda."
  filename         = "${path.module}/../../tasks/extract_filepaths_for_granule/extract_filepaths_for_granule.zip"
  handler          = "extract_filepaths_for_granule.handler"
  memory_size      = var.orca_recovery_lambda_memory_size
  runtime          = var.lambda_runtime
  source_code_hash = filebase64sha256("${path.module}/../../tasks/extract_filepaths_for_granule/extract_filepaths_for_granule.zip")
  tags             = var.tags
  timeout          = var.orca_recovery_lambda_timeout

  vpc_config {
    subnet_ids         = var.lambda_subnet_ids
    security_group_ids = [module.lambda_security_group.vpc_all_egress_id]
  }
  environment {
    variables = {
      POWERTOOLS_SERVICE_NAME = "orca.recovery"
      LOG_LEVEL               = var.log_level
    }
  }
}

data "aws_iam_policy_document" "assume_lambda_role_extract" {
  statement {

    principals {
      type = "Service"
      identifiers = [
        "lambda.amazonaws.com",
        "states.amazonaws.com"
      ]
    }

    actions = ["sts:AssumeRole"]

  }
}

# Permissions needed to run the function successfully
data "aws_iam_policy_document" "extract_filepaths_for_granule_policy_document" {
  statement {
    actions = [
      "lambda:Invoke*",
      "s3:PutObject"
    ]
    resources = [
      "arn:aws:s3:::*",
      "arn:aws:lambda:*:*:*extract_filepaths_for_granule"
    ]
    effect = "Allow"
  }
  statement {
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "ec2:CreateNetworkInterface",
      "ec2:DescribeNetworkInterfaces",
      "ec2:DeleteNetworkInterface",
      "ec2:AssignPrivateIpAddresses",
      "ec2:UnassignPrivateIpAddresses"
    ]
    resources = ["*"]
    effect    = "Allow"
  }
}

resource "aws_iam_role" "extract_filepaths_for_granule_iam_role" {
  name                 = "${var.prefix}_extract_filepaths_for_granule_role"
  assume_role_policy   = data.aws_iam_policy_document.assume_lambda_role_extract.json
  permissions_boundary = var.permissions_boundary_arn
  tags                 = var.tags
}


resource "aws_iam_role_policy" "extract_filepaths_for_granule_policy" {
  name   = "${var.prefix}_extract_filepaths_for_granule_policy"
  role   = aws_iam_role.extract_filepaths_for_granule_iam_role.id
  policy = data.aws_iam_policy_document.extract_filepaths_for_granule_policy_document.json
}


# request_from_archive - Requests files from archive
# ==============================================================================
resource "aws_lambda_function" "request_from_archive" {
  ## REQUIRED
  function_name = "${var.prefix}_request_from_archive"
  role          = var.restore_object_role_arn

  ## OPTIONAL
  description      = "Submits a restore request for all archived files in a granule to the archive bucket."
  filename         = "${path.module}/../../tasks/request_from_archive/request_from_archive.zip"
  handler          = "request_from_archive.handler"
  memory_size      = var.orca_recovery_lambda_memory_size
  runtime          = var.lambda_runtime
  source_code_hash = filebase64sha256("${path.module}/../../tasks/request_from_archive/request_from_archive.zip")
  tags             = var.tags
  timeout          = var.orca_recovery_lambda_timeout

  vpc_config {
    subnet_ids         = var.lambda_subnet_ids
    security_group_ids = [module.lambda_security_group.vpc_all_egress_id]
  }

  environment {
    variables = {
      ARCHIVE_RECOVERY_QUEUE_URL = var.orca_sqs_archive_recovery_queue_id
      RESTORE_EXPIRE_DAYS        = var.orca_recovery_expiration_days
      RESTORE_REQUEST_RETRIES    = var.orca_recovery_retry_limit
      RESTORE_RETRY_SLEEP_SECS   = var.orca_recovery_retry_interval
      DEFAULT_RECOVERY_TYPE      = var.orca_default_recovery_type
      STATUS_UPDATE_QUEUE_URL    = var.orca_sqs_status_update_queue_id
      ORCA_DEFAULT_BUCKET        = var.orca_default_bucket
      POWERTOOLS_SERVICE_NAME    = "orca.recovery"
      LOG_LEVEL                  = var.log_level
    }
  }
}


# copy_from_archive - Copies files from archive to destination bucket
# ==============================================================================
resource "aws_lambda_function" "copy_from_archive" {
  ## REQUIRED
  function_name = "${var.prefix}_copy_from_archive"
  role          = var.restore_object_role_arn

  ## OPTIONAL
  description      = "Copies a restored file to the archive"
  filename         = "${path.module}/../../tasks/copy_from_archive/copy_from_archive.zip"
  handler          = "copy_from_archive.handler"
  memory_size      = var.orca_recovery_lambda_memory_size
  runtime          = var.lambda_runtime
  source_code_hash = filebase64sha256("${path.module}/../../tasks/copy_from_archive/copy_from_archive.zip")
  tags             = var.tags
  timeout          = var.orca_recovery_lambda_timeout

  vpc_config {
    subnet_ids         = var.lambda_subnet_ids
    security_group_ids = [module.lambda_security_group.vpc_all_egress_id]
  }

  environment {
    variables = {
      COPY_RETRIES                   = var.orca_recovery_retry_limit
      COPY_RETRY_SLEEP_SECS          = var.orca_recovery_retry_interval
      STATUS_UPDATE_QUEUE_URL        = var.orca_sqs_status_update_queue_id
      DEFAULT_MULTIPART_CHUNKSIZE_MB = var.default_multipart_chunksize_mb
      RECOVERY_QUEUE_URL             = var.orca_sqs_staged_recovery_queue_id
      POWERTOOLS_SERVICE_NAME        = "orca.recovery"
      LOG_LEVEL                      = var.log_level
    }
  }
}

# Additional resources needed by copy_from_archive
# ------------------------------------------------------------------------------
resource "aws_lambda_event_source_mapping" "copy_from_archive_event_source_mapping" {
  event_source_arn = var.orca_sqs_staged_recovery_queue_arn
  function_name    = aws_lambda_function.copy_from_archive.arn
}

# Permissions to allow SQS trigger to invoke lambda
resource "aws_lambda_permission" "copy_from_archive_allow_sqs_trigger" {
  ## REQUIRED
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.copy_from_archive.function_name
  principal     = "sqs.amazonaws.com"

  ## OPTIONAL
  statement_id = "AllowExecutionFromSQS"
  source_arn   = var.orca_sqs_staged_recovery_queue_arn
}

# post_to_database - Posts entries from SQS queue to database.
# ==============================================================================
resource "aws_lambda_function" "post_to_database" {
  ## REQUIRED
  function_name = "${var.prefix}_post_to_database"
  role          = var.restore_object_role_arn

  ## OPTIONAL
  description      = "Posts entries from SQS queue to database."
  filename         = "${path.module}/../../tasks/post_to_database/post_to_database.zip"
  handler          = "post_to_database.handler"
  memory_size      = var.orca_recovery_lambda_memory_size
  runtime          = var.lambda_runtime
  source_code_hash = filebase64sha256("${path.module}/../../tasks/post_to_database/post_to_database.zip")
  tags             = var.tags
  timeout          = var.orca_recovery_lambda_timeout

  vpc_config {
    subnet_ids         = var.lambda_subnet_ids
    security_group_ids = [module.lambda_security_group.vpc_postgres_ingress_all_egress_id]
  }

  environment {
    variables = {
      DB_CONNECT_INFO_SECRET_ARN = var.db_connect_info_secret_arn
      POWERTOOLS_SERVICE_NAME    = "orca.ingest"
      LOG_LEVEL                  = var.log_level
    }
  }
}

# Additional resources needed by post_to_database
# ------------------------------------------------------------------------------
resource "aws_lambda_event_source_mapping" "post_to_database_event_source_mapping" {
  event_source_arn = var.orca_sqs_status_update_queue_arn
  function_name    = aws_lambda_function.post_to_database.arn
}

# Permissions to allow SQS trigger to invoke lambda
resource "aws_lambda_permission" "post_to_database_allow_sqs_trigger" {
  ## REQUIRED
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.post_to_database.function_name
  principal     = "sqs.amazonaws.com"

  ## OPTIONAL
  statement_id = "AllowExecutionFromSQS"
  source_arn   = var.orca_sqs_status_update_queue_arn
}

# request_status_for_granule - Provides recovery status information on a specific granule
# ==============================================================================
resource "aws_lambda_function" "request_status_for_granule" {
  ## REQUIRED
  function_name = "${var.prefix}_request_status_for_granule"
  role          = var.restore_object_role_arn

  ## OPTIONAL
  description      = "Provides ORCA recover status information on a specific granule and job."
  filename         = "${path.module}/../../tasks/request_status_for_granule/request_status_for_granule.zip"
  handler          = "request_status_for_granule.handler"
  memory_size      = var.orca_recovery_lambda_memory_size
  runtime          = var.lambda_runtime
  source_code_hash = filebase64sha256("${path.module}/../../tasks/request_status_for_granule/request_status_for_granule.zip")
  tags             = var.tags
  timeout          = var.orca_recovery_lambda_timeout

  vpc_config {
    subnet_ids         = var.lambda_subnet_ids
    security_group_ids = [module.lambda_security_group.vpc_postgres_ingress_all_egress_id]
  }

  environment {
    variables = {
      DB_CONNECT_INFO_SECRET_ARN = var.db_connect_info_secret_arn
      POWERTOOLS_SERVICE_NAME    = "orca.recovery"
      LOG_LEVEL                  = var.log_level
    }
  }
}


# request_status_for_job - Provides recovery status information for a job.
# ==============================================================================
resource "aws_lambda_function" "request_status_for_job" {
  ## REQUIRED
  function_name = "${var.prefix}_request_status_for_job"
  role          = var.restore_object_role_arn

  ## OPTIONAL
  description      = "Provides ORCA recover status information on a specific job."
  filename         = "${path.module}/../../tasks/request_status_for_job/request_status_for_job.zip"
  handler          = "request_status_for_job.handler"
  memory_size      = var.orca_recovery_lambda_memory_size
  runtime          = var.lambda_runtime
  source_code_hash = filebase64sha256("${path.module}/../../tasks/request_status_for_job/request_status_for_job.zip")
  tags             = var.tags
  timeout          = var.orca_recovery_lambda_timeout

  vpc_config {
    subnet_ids         = var.lambda_subnet_ids
    security_group_ids = [module.lambda_security_group.vpc_postgres_ingress_all_egress_id]
  }

  environment {
    variables = {
      DB_CONNECT_INFO_SECRET_ARN = var.db_connect_info_secret_arn
      POWERTOOLS_SERVICE_NAME    = "orca.recovery"
      LOG_LEVEL                  = var.log_level
    }
  }
}

# post_copy_request_to_queue - Posts to two queues for notifying copy_from_archive lambda and updating the DB."
# ==============================================================================
resource "aws_lambda_function" "post_copy_request_to_queue" {
  ## REQUIRED
  function_name = "${var.prefix}_post_copy_request_to_queue"
  role          = var.restore_object_role_arn
  ## OPTIONAL
  description      = "Posts to two queues for notifying copy_from_archive lambda and updating the DB."
  filename         = "${path.module}/../../tasks/post_copy_request_to_queue/post_copy_request_to_queue.zip"
  handler          = "post_copy_request_to_queue.handler"
  memory_size      = var.orca_recovery_lambda_memory_size
  runtime          = var.lambda_runtime
  source_code_hash = filebase64sha256("${path.module}/../../tasks/post_copy_request_to_queue/post_copy_request_to_queue.zip")
  tags             = var.tags
  timeout          = var.orca_recovery_lambda_timeout
  vpc_config {
    subnet_ids         = var.lambda_subnet_ids
    security_group_ids = [module.lambda_security_group.vpc_postgres_ingress_all_egress_id]
  }
  environment {
    variables = {
      DB_CONNECT_INFO_SECRET_ARN = var.db_connect_info_secret_arn
      STATUS_UPDATE_QUEUE_URL    = var.orca_sqs_status_update_queue_id
      RECOVERY_QUEUE_URL         = var.orca_sqs_staged_recovery_queue_id
      MAX_RETRIES                = var.orca_recovery_retry_limit
      RETRY_SLEEP_SECS           = var.orca_recovery_retry_interval
      RETRY_BACKOFF              = var.orca_recovery_retry_backoff
      POWERTOOLS_SERVICE_NAME    = "orca.recovery"
      LOG_LEVEL                  = var.log_level
    }
  }
}

# Additional resources needed by post_copy_request_to_queue
# ------------------------------------------------------------------------------
resource "aws_lambda_event_source_mapping" "post_copy_request_to_queue_event_source_mapping" {
  event_source_arn = var.orca_sqs_archive_recovery_queue_arn
  function_name    = aws_lambda_function.post_copy_request_to_queue.arn
  batch_size       = 1
}

# Permissions to allow SQS trigger to invoke lambda
resource "aws_lambda_permission" "post_copy_request_to_queue_allow_sqs_trigger" {
  ## REQUIRED
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.post_copy_request_to_queue.function_name
  principal     = "sqs.amazonaws.com"

  ## OPTIONAL
  statement_id = "AllowExecutionFromSQS"
  source_arn   = var.orca_sqs_archive_recovery_queue_arn
}

# orca_catalog_reporting - Returns reconcilliation report data
# ==============================================================================
resource "aws_lambda_function" "orca_catalog_reporting" {
  ## REQUIRED
  function_name = "${var.prefix}_orca_catalog_reporting"
  role          = var.restore_object_role_arn

  ## OPTIONAL
  description      = "Returns reconcilliation report data."
  filename         = "${path.module}/../../tasks/orca_catalog_reporting/orca_catalog_reporting.zip"
  handler          = "orca_catalog_reporting.handler"
  memory_size      = var.orca_ingest_lambda_memory_size
  runtime          = var.lambda_runtime
  source_code_hash = filebase64sha256("${path.module}/../../tasks/orca_catalog_reporting/orca_catalog_reporting.zip")
  tags             = var.tags
  timeout          = var.orca_ingest_lambda_timeout

  vpc_config {
    subnet_ids         = var.lambda_subnet_ids
    security_group_ids = [module.lambda_security_group.vpc_postgres_ingress_all_egress_id]
  }

  environment {
    variables = {
      DB_CONNECT_INFO_SECRET_ARN = var.db_connect_info_secret_arn
      POWERTOOLS_SERVICE_NAME    = "orca.reconciliation"
      LOG_LEVEL                  = var.log_level
    }
  }
}


# post_to_catalog - Posts provider/collection/granule/file info from SQS queue to database.
# ===========================================================================================
resource "aws_lambda_function" "post_to_catalog" {
  ## REQUIRED
  function_name = "${var.prefix}_post_to_catalog"
  role          = var.restore_object_role_arn

  ## OPTIONAL
  description      = "Posts provider/collection/granule/file info from SQS queue to database."
  filename         = "${path.module}/../../tasks/post_to_catalog/post_to_catalog.zip"
  handler          = "post_to_catalog.handler"
  memory_size      = var.orca_recovery_lambda_memory_size
  runtime          = var.lambda_runtime
  source_code_hash = filebase64sha256("${path.module}/../../tasks/post_to_catalog/post_to_catalog.zip")
  tags             = var.tags
  timeout          = 300 # Gives plenty of time for Serverless spinup.

  vpc_config {
    subnet_ids         = var.lambda_subnet_ids
    security_group_ids = [module.lambda_security_group.vpc_postgres_ingress_all_egress_id]
  }

  environment {
    variables = {
      DB_CONNECT_INFO_SECRET_ARN = var.db_connect_info_secret_arn
      POWERTOOLS_SERVICE_NAME    = "orca.reconciliation"
      LOG_LEVEL                  = var.log_level
    }
  }
}

# Additional resources needed by post_to_catalog
# ------------------------------------------------------------------------------
resource "aws_lambda_event_source_mapping" "post_to_catalog_event_source_mapping" {
  event_source_arn = var.orca_sqs_metadata_queue_arn
  function_name    = aws_lambda_function.post_to_catalog.arn
}

# Permissions to allow SQS trigger to invoke lambda
resource "aws_lambda_permission" "post_to_catalog_allow_sqs_trigger" {
  ## REQUIRED
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.post_to_catalog.function_name
  principal     = "sqs.amazonaws.com"

  ## OPTIONAL
  statement_id = "AllowExecutionFromSQS"
  source_arn   = var.orca_sqs_metadata_queue_arn
}


## =============================================================================
## Utility Lambda Definitions
## =============================================================================

# db_deploy - Lambda that deploys database resources
# ==============================================================================
resource "aws_lambda_function" "db_deploy" {
  depends_on = [
    module.lambda_security_group,
    var.restore_object_role_arn
  ]

  ## REQUIRED
  function_name = "${var.prefix}_db_deploy"
  role          = var.restore_object_role_arn

  ## OPTIONAL
  description      = "ORCA database deployment lambda used to create and bootstrap the ORCA database."
  filename         = "${path.module}/../../tasks/db_deploy/db_deploy.zip"
  handler          = "db_deploy.handler"
  memory_size      = var.orca_recovery_lambda_memory_size
  runtime          = var.lambda_runtime
  source_code_hash = filebase64sha256("${path.module}/../../tasks/db_deploy/db_deploy.zip")
  tags             = var.tags
  timeout          = var.orca_recovery_lambda_timeout

  vpc_config {
    subnet_ids         = var.lambda_subnet_ids
    security_group_ids = [module.lambda_security_group.vpc_postgres_ingress_all_egress_id]
  }

  environment {
    variables = {
      DB_CONNECT_INFO_SECRET_ARN = var.db_connect_info_secret_arn
      POWERTOOLS_SERVICE_NAME    = "orca.recovery"
      LOG_LEVEL                  = var.log_level
    }
  }
}

# # =============================================================================
# # NULL RESOURCES - 1x Use
# # =============================================================================
# data "aws_lambda_invocation" "db_migration" {
#   depends_on    = [aws_lambda_function.db_deploy]
#   function_name = aws_lambda_function.db_deploy.function_name
#   input = jsonencode({
#     replacementTrigger = timestamp()
#     orcaBuckets        = local.orca_buckets
#   })
# }
# # TODO: Should create null resource to handle password changes ORCA-145
