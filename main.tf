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
  tags = merge(var.tags, { Deployment = var.prefix }, { team = "ORCA", application = "ORCA" })
}


## Main ORCA module - This is what is called by end users.
## =============================================================================
module "orca" {
  source = "./modules/orca"
  ## --------------------------
  ## Cumulus Variables
  ## --------------------------
  ## REQUIRED
  aws_profile              = var.aws_profile
  buckets                  = var.buckets
  lambda_subnet_ids        = var.lambda_subnet_ids
  permissions_boundary_arn = var.permissions_boundary_arn
  prefix                   = var.prefix
  system_bucket            = var.system_bucket
  vpc_id                   = var.vpc_id
  workflow_config          = var.workflow_config

  ## OPTIONAL
  region = var.region
  tags   = local.tags

  ## --------------------------
  ## ORCA Variables
  ## --------------------------
  ## REQUIRED
  orca_default_bucket = var.orca_default_bucket
  database_admin_name = var.database_admin_name
  db_admin_username   = var.db_admin_username
  db_admin_password   = var.db_admin_password
  database_user_name  = var.database_user_name
  db_user_username    = var.db_user_username
  db_user_password    = var.db_user_password
  db_host_endpoint    = var.db_host_endpoint
  ## OPTIONAL
  database_port                                        = var.database_port
  orca_ingest_lambda_memory_size                       = var.orca_ingest_lambda_memory_size
  orca_ingest_lambda_timeout                           = var.orca_ingest_lambda_timeout
  orca_recovery_buckets                                = var.orca_recovery_buckets
  orca_recovery_complete_filter_prefix                 = var.orca_recovery_complete_filter_prefix
  orca_recovery_expiration_days                        = var.orca_recovery_expiration_days
  orca_recovery_lambda_memory_size                     = var.orca_recovery_lambda_memory_size
  orca_recovery_lambda_timeout                         = var.orca_recovery_lambda_timeout
  orca_recovery_retry_limit                            = var.orca_recovery_retry_limit
  orca_recovery_retry_interval                         = var.orca_recovery_retry_interval
  orca_recovery_retry_backoff                          = var.orca_recovery_retry_backoff
  sqs_delay_time_seconds                               = var.sqs_delay_time_seconds
  sqs_maximum_message_size                             = var.sqs_maximum_message_size
  staged_recovery_queue_message_retention_time_seconds = var.staged_recovery_queue_message_retention_time_seconds
  status_update_queue_message_retention_time_seconds   = var.status_update_queue_message_retention_time_seconds

  ## OPTIONAL (DO NOT CHANGE DEFAULT VALUES!)
  database_name                = var.database_name
  orca_recovery_retrieval_type = var.orca_recovery_retrieval_type
}
