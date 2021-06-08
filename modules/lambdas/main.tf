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


# Local Variables
locals {
  tags         = merge(var.tags, { Deployment = var.prefix })
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
# # ------------------------------------------------------------------------------
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
  # OPTIONAL
  region = var.region
  tags   = local.tags
  # --------------------------
  # ORCA Variables
  # --------------------------
  # OPTIONAL
  orca_recovery_buckets = var.orca_recovery_buckets
}


# =============================================================================
# Ingest Lambdas Definitions and Resources
# =============================================================================

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
  function_name    = aws_lambda_function.copy_files_to_archive.arn
}

# Additional resources needed by copy_files_to_archive
# ------------------------------------------------------------------------------
# Permissions to allow SQS trigger to invoke lambda
resource "aws_lambda_permission" "copy_files_to_archive_allow_sqs_trigger" {
  ## REQUIRED
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.copy_files_to_archive.function_name
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
  role          = module.restore_object_arn.restore_object_role_arn

  ## OPTIONAL
  description      = "Posts entries from SQS queue to database."
  filename         = "${path.module}/../../tasks/post_to_database/post_to_database.zip"
  handler          = "post_to_database.handler"
  memory_size      = var.orca_recovery_lambda_memory_size
  runtime          = "python3.7"
  source_code_hash = filebase64sha256("${path.module}/../../tasks/post_to_database/post_to_database.zip")
  tags             = local.tags
  timeout          = var.orca_recovery_lambda_timeout

  vpc_config {
    subnet_ids         = var.lambda_subnet_ids
    security_group_ids = [module.lambda_security_group.vpc_postgres_ingress_all_egress_id]
  }

  environment {
    variables = {
      PREFIX           = var.prefix
      DATABASE_PORT    = var.database_port
      DATABASE_NAME    = var.database_name
      APPLICATION_USER = var.database_app_user
    }
  }
}

resource "aws_lambda_event_source_mapping" "post_to_database_event_source_mapping" {
  event_source_arn = var.orca_sqs_status_update_queue_arn
  function_name    = aws_lambda_function.post_to_database.arn
}

# Additional resources needed by post_to_database
# ------------------------------------------------------------------------------
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

# API Gateway
resource "aws_api_gateway_rest_api" "request_status_for_granule_api" {
  name = "${var.prefix}_request_status_for_granule_api"
}

resource "aws_api_gateway_resource" "request_status_for_granule_api_resource" {
  path_part   = "{proxy+}"
  parent_id   = aws_api_gateway_rest_api.request_status_for_granule_api.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.request_status_for_granule_api.id
}

resource "aws_api_gateway_method" "request_status_for_granule_api_method" {
  rest_api_id   = aws_api_gateway_rest_api.request_status_for_granule_api.id
  resource_id   = aws_api_gateway_resource.request_status_for_granule_api_resource.id
  http_method   = "ANY"
  # todo: Make sure this is locked down against external access.
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "request_status_for_granule_api_integration" {
  rest_api_id             = aws_api_gateway_rest_api.request_status_for_granule_api.id
  resource_id             = aws_api_gateway_resource.request_status_for_granule_api_resource.id
  http_method             = aws_api_gateway_method.request_status_for_granule_api_method.http_method
  integration_http_method = "POST"
  type                    = "AWS"
  uri                     = aws_lambda_function.request_status_for_granule.invoke_arn
}

resource "aws_api_gateway_method_response" "request_status_for_granule_response_200" {
  rest_api_id = aws_api_gateway_rest_api.request_status_for_granule_api.id
  resource_id = aws_api_gateway_resource.request_status_for_granule_api_resource.id
  http_method = aws_api_gateway_method.request_status_for_granule_api_method.http_method
  status_code = "200"
}

resource "aws_api_gateway_integration_response" "request_status_for_granule_api_response" {
  depends_on = [aws_api_gateway_integration.request_status_for_granule_api_integration]
  rest_api_id = aws_api_gateway_rest_api.request_status_for_granule_api.id
  resource_id = aws_api_gateway_resource.request_status_for_granule_api_resource.id
  http_method = aws_api_gateway_method.request_status_for_granule_api_method.http_method
  status_code = aws_api_gateway_method_response.request_status_for_granule_response_200.status_code

  # Transforms the backend JSON response to XML
  response_templates = {
    "application/json" = <<EOF
#set($inputRoot = $input.path('$'))
$input.json("$")

#if($input.path("stackTrace") != '')
#set($context.responseOverride.status = 500)
#elseif($input.path("httpStatus") != '')
#set($context.responseOverride.status = $input.path('httpStatus'))
#end
EOF
  }
}

# Lambda
resource "aws_lambda_permission" "request_status_for_granule_api_permission" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.request_status_for_granule.function_name
  principal     = "apigateway.amazonaws.com"

  # More: http://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-control-access-using-iam-policies-to-invoke-api.html
  # source_arn = "arn:aws:execute-api:${var.region}:${var.accountId}:${aws_api_gateway_rest_api.request_status_for_granule_api.id}/*/${aws_api_gateway_method.request_status_for_granule_api_method.http_method}${aws_api_gateway_resource.request_status_for_granule_api_resource.path}"
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

# API Gateway
resource "aws_api_gateway_rest_api" "request_status_for_job_api" {
  name = "${var.prefix}_request_status_for_job_api"
}

resource "aws_api_gateway_resource" "request_status_for_job_api_resource" {
  path_part   = "{proxy+}"
  parent_id   = aws_api_gateway_rest_api.request_status_for_job_api.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.request_status_for_job_api.id
}

resource "aws_api_gateway_method" "request_status_for_job_api_method" {
  rest_api_id   = aws_api_gateway_rest_api.request_status_for_job_api.id
  resource_id   = aws_api_gateway_resource.request_status_for_job_api_resource.id
  http_method   = "ANY"
  # todo: Make sure this is locked down against external access.
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "request_status_for_job_api_integration" {
  rest_api_id             = aws_api_gateway_rest_api.request_status_for_job_api.id
  resource_id             = aws_api_gateway_resource.request_status_for_job_api_resource.id
  http_method             = aws_api_gateway_method.request_status_for_job_api_method.http_method
  integration_http_method = "POST"
  type                    = "AWS"
  uri                     = aws_lambda_function.request_status_for_job.invoke_arn
}

resource "aws_api_gateway_method_response" "request_status_for_job_response_200" {
  rest_api_id = aws_api_gateway_rest_api.request_status_for_job_api.id
  resource_id = aws_api_gateway_resource.request_status_for_job_api_resource.id
  http_method = aws_api_gateway_method.request_status_for_job_api_method.http_method
  status_code = "200"
}

resource "aws_api_gateway_integration_response" "request_status_for_job_api_response" {
  depends_on = [aws_api_gateway_integration.request_status_for_job_api_integration]
  rest_api_id = aws_api_gateway_rest_api.request_status_for_job_api.id
  resource_id = aws_api_gateway_resource.request_status_for_job_api_resource.id
  http_method = aws_api_gateway_method.request_status_for_job_api_method.http_method
  status_code = aws_api_gateway_method_response.request_status_for_job_response_200.status_code

  # Transforms the backend JSON response to XML
  response_templates = {
    "application/json" = <<EOF
#set($inputRoot = $input.path('$'))
$input.json("$")

#if($input.path("stackTrace") != '')
#set($context.responseOverride.status = 500)
#elseif($input.path("httpStatus") != '')
#set($context.responseOverride.status = $input.path('httpStatus'))
#end
EOF
  }
}

# Lambda
resource "aws_lambda_permission" "request_status_for_job_api_permission" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.request_status_for_job.function_name
  principal     = "apigateway.amazonaws.com"

  # More: http://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-control-access-using-iam-policies-to-invoke-api.html
  # source_arn = "arn:aws:execute-api:${var.region}:${var.accountId}:${aws_api_gateway_rest_api.request_status_for_job_api.id}/*/${aws_api_gateway_method.request_status_for_job_api_method.http_method}${aws_api_gateway_resource.request_status_for_job_api_resource.path}"
}

# post_copy_request_to_queue -Posts to two queues for notifying copy_files_to_archive lambda and updating the DB."
# ==============================================================================
resource "aws_lambda_function" "post_copy_request_to_queue" {
  ## REQUIRED
  function_name = "${var.prefix}_post_copy_request_to_queue"
  role          = module.restore_object_arn.restore_object_role_arn
  ## OPTIONAL
  description      = "Posts to two queues for notifying copy_files_to_archive lambda and updating the DB."
  filename         = "${path.module}/../../tasks/post_copy_request_to_queue/post_copy_request_to_queue.zip"
  handler          = "post_copy_request_to_queue.handler"
  memory_size      = var.orca_recovery_lambda_memory_size
  runtime          = "python3.7"
  source_code_hash = filebase64sha256("${path.module}/../../tasks/post_copy_request_to_queue/post_copy_request_to_queue.zip")
  tags             = local.tags
  timeout          = var.orca_recovery_lambda_timeout
  vpc_config {
    subnet_ids         = var.lambda_subnet_ids
    security_group_ids = [module.lambda_security_group.vpc_postgres_ingress_all_egress_id]
  }
  environment {
    variables = {
      PREFIX                = var.prefix
      DATABASE_PORT         = var.database_port
      DATABASE_NAME         = var.database_name
      DATABASE_USER         = var.database_app_user
      DB_QUEUE_URL          = var.orca_sqs_status_update_queue_id
      RECOVERY_QUEUE_URL    = var.orca_sqs_staged_recovery_queue_id
      MAX_RETRIES           = var.orca_recovery_retry_limit
      RETRY_SLEEP_SECS      = var.orca_recovery_retry_interval
      RETRY_BACKOFF         = var.orca_recovery_retry_backoff
    }
  }
}

# Permissions to allow S3 trigger to invoke lambda
resource "aws_lambda_permission" "allow_s3_trigger" {
  ## REQUIRED
  for_each      = toset(local.orca_buckets)
  source_arn    = "arn:aws:s3:::${each.value}"
  function_name = aws_lambda_function.post_copy_request_to_queue.function_name
  ## OPTIONAL
  principal = "s3.amazonaws.com"
  action    = "lambda:InvokeFunction"
}

resource "aws_s3_bucket_notification" "post_copy_request_to_queue_trigger" {
  depends_on = [aws_lambda_permission.allow_s3_trigger]
  # Creating loop so we can handle multiple orca buckets
  for_each = toset(local.orca_buckets)
  ## REQUIRED
  bucket = each.value
  ## OPTIONAL
  lambda_function {
    ## REQUIRED  
    lambda_function_arn = aws_lambda_function.post_copy_request_to_queue.arn
    events              = ["s3:ObjectRestore:Completed"]
    ## OPTIONAL
    filter_prefix = var.orca_recovery_complete_filter_prefix
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
  runtime          = "python3.8"
  source_code_hash = filebase64sha256("${path.module}/../../tasks/db_deploy/db_deploy.zip")
  tags             = local.tags
  timeout          = var.orca_recovery_lambda_timeout

  vpc_config {
    subnet_ids         = var.lambda_subnet_ids
    security_group_ids = [module.lambda_security_group.vpc_postgres_ingress_all_egress_id]
  }

  environment {
    variables = {
      PREFIX           = var.prefix
      DATABASE_PORT    = var.database_port
      DATABASE_NAME    = var.database_name
      APPLICATION_USER = var.database_app_user
      ADMIN_USER       = "postgres"
      ADMIN_DATABASE   = "postgres"
    }
  }
}