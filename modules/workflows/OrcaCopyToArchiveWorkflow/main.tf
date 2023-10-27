## Referenced Modules - Workflows
resource "aws_sfn_state_machine" "default" {
  name       = "${var.prefix}-OrcaCopyToArchiveWorkflow"
  role_arn   = var.orca_step_function_role_arn
  definition = templatefile(
    "${path.module}/orca_copy_to_archive_workflow.asl.json",
    {
      orca_lambda_copy_to_archive_arn : var.orca_lambda_copy_to_archive_arn
    }
  )
  tags       = var.tags
}