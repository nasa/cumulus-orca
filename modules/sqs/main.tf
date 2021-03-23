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
  region = var.region
}

## Local Variables
locals {
  tags = merge(var.tags, { Deployment = var.prefix })
}

## copy_files_to_archive_get_message_queue - SQS queue that copy_files_to_archive lambda writes to
## ====================================================================================================
resource "aws_sqs_queue" "copy_files_to_archive_get_message_queue" {
  ## OPTIONAL
  name                      = "${var.prefix}-get-message-queue"
  fifo_queue                = false
  delay_seconds             = var.sqs_delay_time
  max_message_size          = var.maximum_message_size
  message_retention_seconds = var.sqs_message_retention_time
  tags                      = local.tags
  policy                    = <<EOF
{
  "Version": "2012-10-17",
  "Id": "SQSAllowPolicy",
  "Statement": [
    {
      "Sid": "SQSAllowID",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "SQS:*",
      "Resource": "*"
    }
  ]
}
EOF
}

## copy_files_to_archive_send_status_update_queue - SQS queue that receives status update info from copy_files_to_archive lambda
## ===============================================================================================================================
resource "aws_sqs_queue" "copy_files_to_archive_send_status_update_queue" {
  ## OPTIONAL
  name                      = "${var.prefix}-status-update-queue"
  fifo_queue                = false
  delay_seconds             = var.sqs_delay_time
  max_message_size          = var.maximum_message_size
  message_retention_seconds = var.sqs_message_retention_time
  tags                      = local.tags
  policy                    = <<EOF
{
  "Version": "2012-10-17",
  "Id": "SQSAllowPolicy",
  "Statement": [
    {
      "Sid": "SQSAllowID",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "SQS:*",
      "Resource": "*"
    }
  ]
}
EOF
}