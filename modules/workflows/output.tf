output "orca_sfn_internal_reconciliation_workflow_arn" {
  description = "The ARN of the internal_reconciliation step function."
  value       = module.orca_internal_reconciliation_workflow.orca_sfn_internal_reconciliation_workflow_arn
}