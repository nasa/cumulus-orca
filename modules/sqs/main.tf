## Local Variables
locals {
  tags = merge(var.tags, { Deployment = var.prefix })
}

## SQS IAM access policy for metadata-queue.fifo SQS
## ====================================================================================================
data "aws_iam_policy_document" "metadata_queue_policy" {
  statement {
    actions   = ["sqs:*"] # todo: Lock down access to specific actions and resources. https://bugs.earthdata.nasa.gov/browse/ORCA-273
    resources = ["arn:aws:sqs:*"]
    effect    = "Allow"
  }
}

## SQS IAM access policy for staged-recovery-queue SQS
## ====================================================================================================
data "aws_iam_policy_document" "staged_recovery_queue_policy" {
  statement {
    actions   = ["sqs:*"] # todo: Lock down access to specific actions and resources. https://bugs.earthdata.nasa.gov/browse/ORCA-273
    resources = ["arn:aws:sqs:*"]
    effect    = "Allow"
  }
}

## SQS IAM access policy for status-update-queue.fifo SQS
## ====================================================================================================
data "aws_iam_policy_document" "status_update_queue_policy" {
  statement {
    actions   = ["sqs:*"] # todo: Lock down access to specific actions and resources. https://bugs.earthdata.nasa.gov/browse/ORCA-273
    resources = ["arn:aws:sqs:*"]
    effect    = "Allow"
  }
}


## metadata_queue - copy_to_glacier writes to this database update queue.
## ==============================================================================
resource "aws_sqs_queue" "metadata_queue" {
  ## OPTIONAL
  name                        = "${var.prefix}-metadata-queue.fifo"
  fifo_queue                  = true
  content_based_deduplication = true
  delay_seconds               = var.sqs_delay_time_seconds
  max_message_size            = var.sqs_maximum_message_size
  message_retention_seconds   = var.metadata_queue_message_retention_time_seconds
  tags                        = local.tags
  policy                      = data.aws_iam_policy_document.metadata_queue_policy.json
  visibility_timeout_seconds  = 900 # Set to the lambda max time
}

## staged-recovery-queue - copy_files_to_archive lambda reads from this queue to get what it needs to copy next
## ====================================================================================================
resource "aws_sqs_queue" "staged_recovery_queue" {
  ## OPTIONAL
  name                       = "${var.prefix}-staged-recovery-queue"
  delay_seconds              = var.sqs_delay_time_seconds
  max_message_size           = var.sqs_maximum_message_size
  message_retention_seconds  = var.staged_recovery_queue_message_retention_time_seconds
  tags                       = local.tags
  policy                     = data.aws_iam_policy_document.staged_recovery_queue_policy.json
  visibility_timeout_seconds = 1800 # Set to double lambda max time
  depends_on = [
    aws_sqs_queue.staged_recovery_deadletter_queue
  ]
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.staged_recovery_deadletter_queue.arn,
    maxReceiveCount     = 3 #number of times a consumer tries receiving a message from the queue without deleting it before being moved to DLQ.
  })
}

resource "aws_sqs_queue" "staged_recovery_deadletter_queue" {
  name                       = "${var.prefix}-staged-recovery-deadletter-queue"
  delay_seconds              = var.sqs_delay_time_seconds
  max_message_size           = var.sqs_maximum_message_size
  message_retention_seconds  = var.staged_recovery_queue_message_retention_time_seconds
  tags                       = local.tags
  visibility_timeout_seconds = 1800 # Set to same time as the staged recovery queue.
}

resource "aws_sqs_queue_policy" "deadletter_queue_policy" {
  queue_url = aws_sqs_queue.staged_recovery_deadletter_queue.id
  policy    = data.aws_iam_policy_document.staged_recovery_deadletter_queue_policy.json
}

data "aws_iam_policy_document" "staged_recovery_deadletter_queue_policy" {
  statement {
    effect    = "Allow"
    resources = [aws_sqs_queue.staged_recovery_deadletter_queue.arn]
    actions = [
      "sqs:ChangeMessageVisibility",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes",
      "sqs:GetQueueUrl",
      "sqs:ListQueueTags",
      "sqs:ReceiveMessage",
      "sqs:SendMessage",
    ]
  }
}

resource "aws_cloudwatch_metric_alarm" "staged_recovery_deadletter_alarm" {
  alarm_name          = "${aws_sqs_queue.staged_recovery_deadletter_queue.name}-not-empty-alarm"
  alarm_description   = "Items are on the ${aws_sqs_queue.staged_recovery_deadletter_queue.name} queue"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = 300 #In seconds. Valid values for period are 1, 5, 10, 30, or any multiple of 60. 
  statistic           = "Average"
  threshold           = 1 #alarm will be triggered if number of messages in the DLQ equals to this threshold.
  treat_missing_data  = "notBreaching"
  alarm_actions       = [aws_sns_topic.staged_recovery_dlq_alarm_topic.arn]
  tags                = local.tags
  dimensions = {
    "QueueName" = aws_sqs_queue.staged_recovery_deadletter_queue.name
  }
}

# SNS topic needed for cloudwatch alarm
resource "aws_sns_topic" "staged_recovery_dlq_alarm_topic" {
  name = "staged_recovery_deadletter_queue_alarm_topic"
}

resource "aws_sns_topic_subscription" "sns_subscription_for_alarm" {
  depends_on = [aws_sns_topic.staged_recovery_dlq_alarm_topic]
  topic_arn  = aws_sns_topic.staged_recovery_dlq_alarm_topic.arn
  protocol   = "email"
  endpoint   = "rhassan@contractor.usgs.gov"
}
## status_update_queue - copy_files_to_archive lambda writes to this database status update queue.
## ===============================================================================================================================
resource "aws_sqs_queue" "status_update_queue" {
  ## OPTIONAL
  name                        = "${var.prefix}-status-update-queue.fifo"
  fifo_queue                  = true
  content_based_deduplication = true
  delay_seconds               = var.sqs_delay_time_seconds
  max_message_size            = var.sqs_maximum_message_size
  message_retention_seconds   = var.status_update_queue_message_retention_time_seconds
  tags                        = local.tags
  policy                      = data.aws_iam_policy_document.status_update_queue_policy.json
  visibility_timeout_seconds  = 900 # Set arbitrarily large.
}
