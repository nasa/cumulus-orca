## Referenced Modules - Workflows
resource "aws_sfn_state_machine" "default" {
  name       = "${var.prefix}-OrcaRecoveryWorkflow"
  role_arn   = var.orca_step_function_role_arn
  definition = templatefile(
    "${path.module}/orca_recover_workflow.asl.json",
    {
      orca_default_bucket : var.orca_default_bucket,
      orca_lambda_extract_filepaths_for_granule_arn : var.orca_lambda_extract_filepaths_for_granule_arn,
      orca_lambda_request_from_archive_arn : var.orca_lambda_request_from_archive_arn
    }
  )
  tags       = var.tags
}