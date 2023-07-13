## Referenced Modules - Workflows
resource "aws_sfn_state_machine" "default" {
  name       = "${var.prefix}-OrcaInternalReconciliationWorkflow"
  role_arn   = var.orca_step_function_role_arn
  definition = templatefile(
    "${path.module}/orca_internal_reconciliation_workflow.asl.json",
    {
      orca_lambda_get_current_archive_list_arn : var.orca_lambda_get_current_archive_list_arn,
      orca_lambda_perform_orca_reconcile_arn : var.orca_lambda_perform_orca_reconcile_arn
    }
  )
  tags       = var.tags
}