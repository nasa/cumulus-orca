## =============================================================================
## Reconciliation Lambdas Definitions and Resources
## =============================================================================

# post_to_queue_and_trigger_step_function - Receives an events from an SQS queue, translates to get_current_archive_list's input format, sends it to another queue, then triggers the internal report step function.
# ==============================================================================
resource "aws_lambda_function" "post_to_queue_and_trigger_step_function" {
  ## REQUIRED
  function_name = "${var.prefix}_post_to_queue_and_trigger_step_function"
  role          = var.restore_object_role_arn # todo: Specialized roles. ORCA-316

  ## OPTIONAL
  description      = "Receives an events from an SQS queue, translates to get_current_archive_list's input format, sends it to another queue, then triggers the internal report step function."
  filename         = "${path.module}/../../tasks/post_to_queue_and_trigger_step_function/post_to_queue_and_trigger_step_function.zip"
  handler          = "post_to_queue_and_trigger_step_function.handler"
  memory_size      = var.orca_reconciliation_lambda_memory_size
  runtime          = var.lambda_runtime
  source_code_hash = filebase64sha256("${path.module}/../../tasks/post_to_queue_and_trigger_step_function/post_to_queue_and_trigger_step_function.zip")
  tags             = var.tags
  timeout          = var.orca_reconciliation_lambda_timeout

  vpc_config {
    subnet_ids         = var.lambda_subnet_ids
    security_group_ids = [var.vpc_postgres_ingress_all_egress_id]
  }

  environment {
    variables = {
      PREFIX                  = var.prefix
      STEP_FUNCTION_ARN       = var.orca_sfn_internal_reconciliation_workflow_arn,
      TARGET_QUEUE_URL        = var.orca_sqs_internal_report_queue_id,
      POWERTOOLS_SERVICE_NAME = "orca.internal_reconciliation"
      LOG_LEVEL               = var.log_level
    }
  }
}


# todo: Populate queue with s3 events ORCA-372 https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_notification
# Additional resources needed by post_to_queue_and_trigger_step_function
# ------------------------------------------------------------------------------
resource "aws_lambda_event_source_mapping" "post_to_queue_and_trigger_step_function_event_source_mapping" {
  event_source_arn = var.orca_sqs_s3_inventory_queue_arn
  function_name    = aws_lambda_function.post_to_queue_and_trigger_step_function.arn
}

# Permissions to allow SQS trigger to invoke lambda
resource "aws_lambda_permission" "post_to_queue_and_trigger_step_function_allow_sqs_trigger" {
  ## REQUIRED
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.post_to_queue_and_trigger_step_function.function_name
  principal     = "sqs.amazonaws.com"

  ## OPTIONAL
  statement_id = "AllowExecutionFromSQS"
  source_arn   = var.orca_sqs_s3_inventory_queue_arn
}

## Local Variables
locals {
  orca_bucket_names = [for k, v in var.buckets : v.name if v.type == "orca"]
}

resource "aws_s3_bucket_inventory" "inventory_report" {
  for_each = toset(local.orca_bucket_names)

  bucket = each.key
  name   = "${each.key}-inventory"

  included_object_versions = "All"
  optional_fields          = ["Size", "LastModifiedDate", "StorageClass", "ETag"]

  schedule {
    frequency = var.s3_report_frequency
  }

  destination {
    bucket {
      format     = "CSV"
      bucket_arn = "arn:aws:s3:::${var.orca_reports_bucket_name}"
    }
  }
}