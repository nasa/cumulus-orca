output "get_message_queue_arn" {
  value = aws_sqs_queue.copy_files_to_archive_get_message_queue.arn
}

output "get_message_queue_id" {
  value = aws_sqs_queue.copy_files_to_archive_get_message_queue.id
}

output "status_update_queue_arn" {
  value = aws_sqs_queue.copy_files_to_archive_send_status_update_queue.arn
}

output "status_update_queue_id" {
  value = aws_sqs_queue.copy_files_to_archive_send_status_update_queue.id
}