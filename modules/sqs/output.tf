output "orca_sqs_internal_report_queue_arn" {
  description = "The ARN of the internal-report-queue SQS"
  value       = aws_sqs_queue.status_update_queue.arn
}

output "orca_sqs_internal_report_queue_id" {
  description = "The URL of the internal-report-queue SQS"
  value       = aws_sqs_queue.internal_report_queue.id
}

output "orca_sqs_metadata_queue_arn" {
  description = "The ARN of the metadata-queue SQS"
  value       = aws_sqs_queue.metadata_queue.arn
}

output "orca_sqs_metadata_queue_id" {
  description = "The URL of the metadata-queue SQS"
  value       = aws_sqs_queue.metadata_queue.id
}

output "orca_sqs_staged_recovery_queue_arn" {
  description = "The ARN of the staged-recovery-queue SQS"
  value       = aws_sqs_queue.staged_recovery_queue.arn
}

output "orca_sqs_staged_recovery_queue_id" {
  description = "The URL of the staged-recovery-queue SQS"
  value       = aws_sqs_queue.staged_recovery_queue.id
}

output "orca_sqs_status_update_queue_arn" {
  description = "The ARN of the status-update-queue SQS"
  value       = aws_sqs_queue.status_update_queue.arn
}

output "orca_sqs_status_update_queue_id" {
  description = "The URL of the status-update-queue SQS"
  value       = aws_sqs_queue.status_update_queue.id
}