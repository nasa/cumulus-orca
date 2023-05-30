output "orca_sfn_internal_reconciliation_workflow_arn" {
  description = "The ARN of the internal_reconciliation step function."
  value       = module.orca_internal_reconciliation_workflow.orca_sfn_internal_reconciliation_workflow_arn
}

output "orca_sfn_recovery_workflow_arn" {
  description = "The ARN of the recovery step function."
  value       = module.orca_recovery_workflow.orca_sfn_recovery_workflow_arn
}