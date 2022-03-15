## =============================================================================
## Reconciliation Lambdas Definitions and Resources
## =============================================================================

resource "aws_lambda_function" "post_to_queue_and_trigger_step_function" {
  ## REQUIRED
  function_name = "${var.prefix}_post_to_queue_and_trigger_step_function"
  role          = var.restore_object_role_arn

  ## OPTIONAL
  description      = "Receives an events from an SQS queue, translates to get_current_archive_list's input format, sends it to another queue, then triggers the internal report step function."
  filename         = "${path.module}/../../tasks/post_to_queue_and_trigger_step_function/post_to_queue_and_trigger_step_function.zip"
  handler          = "post_to_queue_and_trigger_step_function.handler"
  memory_size      = var.orca_reconciliation_lambda_memory_size
  runtime          = "python3.9"
  source_code_hash = filebase64sha256("${path.module}/../../tasks/post_to_queue_and_trigger_step_function/post_to_queue_and_trigger_step_function.zip")
  tags             = var.tags
  timeout          = var.orca_reconciliation_lambda_timeout

  vpc_config {
    subnet_ids         = var.lambda_subnet_ids
    security_group_ids = [var.vpc_postgres_ingress_all_egress_id]
  }

  environment {
    variables = {
      PREFIX = var.prefix
      STEP_FUNCTION_ARN = var.orca_sfn_internal_reconciliation_workflow_arn,
      TARGET_QUEUE_URL  = var.orca_sqs_internal_report_queue_id,
    }
  }
}

# todo: Add s3 triggering ORCA-372