## Local Variables
locals {
  tags = merge(var.tags, { Deployment = var.prefix })
}


## Referenced Modules - Workflows
module "orca_recovery_workflow" {
  source = "https://github.com/nasa/cumulus/releases/download/v6.0.0/terraform-aws-cumulus-workflow.zip"
  ## --------------------------
  ## Cumulus Variables
  ## --------------------------
  ## REQUIRED
  prefix          = var.prefix
  name            = "OrcaRecoveryWorkflow"
  workflow_config = var.workflow_config
  system_bucket   = var.system_bucket
  tags            = local.tags

  state_machine_definition = templatefile(
    "${path.module}/orca_recover_workflow.asl.json",
    {
      orca_default_bucket : var.orca_default_bucket,
      orca_lambda_extract_filepaths_for_granule_arn : var.orca_lambda_extract_filepaths_for_granule_arn,
      orca_lambda_request_files_arn : var.orca_lambda_request_files_arn
    }
  )
}