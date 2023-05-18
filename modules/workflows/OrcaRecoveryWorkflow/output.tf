output "orca_sfn_recovery_workflow_arn" {
  description = "The ARN of the recovery step function."
  value       = module.orca_recovery_workflow.state_machine_arn
}