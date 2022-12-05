## Referenced Modules - Workflows
module "orca_copy_to_archive_workflow" {
  source = "https://github.com/nasa/cumulus/releases/download/v10.0.0/terraform-aws-cumulus-workflow.zip"
  ## --------------------------
  ## Cumulus Variables
  ## --------------------------
  ## REQUIRED
  prefix          = var.prefix
  name            = "OrcaCopyToArchiveWorkflow"
  workflow_config = var.workflow_config
  system_bucket   = var.system_bucket
  tags            = var.tags

  state_machine_definition = templatefile(
    "${path.module}/orca_copy_to_archive_workflow.asl.json",
    {
      orca_lambda_copy_to_archive_arn : var.orca_lambda_copy_to_archive_arn
    }
  )
}