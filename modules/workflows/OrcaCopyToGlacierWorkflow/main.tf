## Local Variables
locals {
  tags = merge(var.tags, { Deployment = var.prefix })
}


## Referenced Modules - Workflows
module "orca_copy_to_glacier_workflow" {
  source = "https://github.com/nasa/cumulus/releases/download/v9.7.0/terraform-aws-cumulus-workflow.zip"
  ## --------------------------
  ## Cumulus Variables
  ## --------------------------
  ## REQUIRED
  prefix          = var.prefix
  name            = "OrcaCopyToGlacierWorkflow"
  workflow_config = var.workflow_config
  system_bucket   = var.system_bucket
  tags            = local.tags

  state_machine_definition = templatefile(
    "${path.module}/orca_copy_to_glacier_workflow.asl.json",
    {
      orca_lambda_copy_to_glacier_cumulus_translator_arn : var.orca_lambda_copy_to_glacier_cumulus_translator_arn,
      orca_lambda_copy_to_glacier_arn : var.orca_lambda_copy_to_glacier_arn
    }
  )
}