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
  aws_profile     = var.aws_profile
  prefix          = var.prefix
  region          = var.region
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