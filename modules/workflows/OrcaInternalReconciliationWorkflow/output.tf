output "orca_sfn_internal_reconciliation_workflow_arn" {
  description = "The ARN of the internal_reconciliation step function."
  value       = aws_sfn_state_machine.default.arn
}