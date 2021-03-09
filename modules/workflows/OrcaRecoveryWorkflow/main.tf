## Terraform Requirements
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 3.5.0"
    }
  }
}


## AWS Provider Settings
provider "aws" {
  region  = var.region
  profile = var.aws_profile
}


## Local Variables
locals {
  tags            = merge(var.tags, { Deployment = var.prefix })
  workflow_source = "https://github.com/nasa/cumulus/releases/download/${var.cumulus_version}/terraform-aws-cumulus-workflow.zip"
}


## Referenced Modules - Workflows
module "orca_recovery_workflow" {
  source = local.workflow_source
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