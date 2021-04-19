output "orca_sqs_staged_recovery_queue_arn" {
  description = "The ARN of the staged-recovery-queue SQS"
  value       = aws_sqs_queue.staged_recovery_queue.arn
}

output "orca_sqs_staged_recovery_queue_id" {
  description = "The URL ID of the staged-recovery-queue SQS"
  value       = aws_sqs_queue.staged_recovery_queue.id
}

output "orca_sqs_status_update_queue_arn" {
  description = "The ARN of the status-update-queue SQS"
  value       = aws_sqs_queue.status_update_queue.arn
}

output "orca_sqs_status_update_queue_id" {
  description = "The URL ID of the status-update-queue SQS"
  value       = aws_sqs_queue.status_update_queue.id
}

output "orca_sqs_staged_recovery_queue_arn" {
  description = "The ARN of the staged-recovery-queue SQS"
  value       = aws_sqs_queue.staged_recovery_queue.arn
}