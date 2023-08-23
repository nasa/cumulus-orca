output "orca_sfn_recovery_workflow_arn" {
  description = "The ARN of the recovery step function."
  value       = aws_sfn_state_machine.default.arn
}