## Terraform Requirements
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 3.5.0"
    }
  }
}

## Local Variables
locals {
  tags = merge(var.tags, { Deployment = var.prefix })
}


## SQS IAM access policy for staged-recovery-queue.fifo SQS
## ====================================================================================================
data "aws_iam_policy_document" "staged_recovery_queue_policy" {
  statement {
    actions   = ["sqs:*"] # todo: Lock down access to specific actions and resources.
    resources = ["arn:aws:sqs:*"]
    effect    = "Allow"
  }
}

## SQS IAM access policy for status-update-queue.fifo SQS
## ====================================================================================================
data "aws_iam_policy_document" "status_update_queue_policy" {
  statement {
    actions   = ["sqs:*"] # todo: Lock down access to specific actions and resources.
    resources = ["arn:aws:sqs:*"]
    effect    = "Allow"
  }
}


## staged-recovery-queue - copy_files_to_archive lambda reads from this queue to get what it needs to copy next
## ====================================================================================================
resource "aws_sqs_queue" "staged_recovery_queue" {
  ## OPTIONAL
  name                        = "${var.prefix}-staged-recovery-queue.fifo"
  fifo_queue                  = true
  content_based_deduplication = true
  delay_seconds               = var.sqs_delay_time_seconds
  max_message_size            = var.sqs_maximum_message_size
  message_retention_seconds   = var.staged_recovery_queue_message_retention_time_seconds
  tags                        = local.tags
  policy                      = data.aws_iam_policy_document.staged_recovery_queue_policy.json
  visibility_timeout_seconds  = 300
}

## status_update_queue - copy_files_to_archive lambda  writes to this database status update queue.
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
  visibility_timeout_seconds  = 300
}