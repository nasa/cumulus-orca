## Local Variables
locals {
  tags = merge(var.tags, { Deployment = var.prefix })
}


## Referenced Modules - Workflows

# orca_recovery_workflow - Default workflow that starts the recovery process.
# ===============================================================================
module "orca_recovery_workflow" {
  source = "./OrcaRecoveryWorkflow"
  ## --------------------------
  ## Cumulus Variables
  ## --------------------------
  ## REQUIRED
  prefix          = var.prefix
  system_bucket   = var.system_bucket
  tags            = local.tags
  workflow_config = var.workflow_config

  ## --------------------------
  ## ORCA Variables
  ## --------------------------
  ## REQUIRED
  orca_default_bucket = var.orca_default_bucket

  # Task ARNS needed for workflow template
  orca_lambda_extract_filepaths_for_granule_arn = var.orca_lambda_extract_filepaths_for_granule_arn
  orca_lambda_request_files_arn                 = var.orca_lambda_request_files_arn
}

# copy_to_glacier_workflow - On-Demand execution of copy_to_glacier.
# ===============================================================================
module "orca_copy_to_glacier_workflow" {
  source = "./OrcaCopyToGlacierWorkflow"
  ## --------------------------
  ## Cumulus Variables
  ## --------------------------
  ## REQUIRED
  prefix          = var.prefix
  system_bucket   = var.system_bucket
  tags            = local.tags
  workflow_config = var.workflow_config

  ## --------------------------
  ## ORCA Variables
  ## --------------------------
  ## REQUIRED
  # Task ARNS needed for workflow template
  orca_lambda_copy_to_glacier_cumulus_translator_arn = var.orca_lambda_copy_to_glacier_cumulus_translator_arn
  orca_lambda_copy_to_glacier_arn                    = var.orca_lambda_copy_to_glacier_arn
}