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
  profile = var.aws_profile
  region  = var.region
}


## Local Variables
locals {
  tags = merge(var.tags, { Deployment = var.prefix })
}


## Referenced Modules

## orca_sqs - SQS module
## =============================================================================
module "orca_sqs" {
  source = "../sqs"
  ## --------------------------
  ## Cumulus Variables
  ## --------------------------
  ## REQUIRED
  aws_profile = var.aws_profile
  prefix      = var.prefix

  ## OPTIONAL
  region = var.region
  tags   = local.tags

  ## --------------------------
  ## ORCA Variables
  ## --------------------------
  ## OPTIONAL
  sqs_delay_time                               = var.sqs_delay_time
  sqs_maximum_message_size                     = var.sqs_maximum_message_size
  staged_recovery_queue_message_retention_time = var.staged_recovery_queue_message_retention_time
  status_update_queue_message_retention_time   = var.status_update_queue_message_retention_time
}


## orca_lambdas - lambdas module that calls iam and security_groups module
## =============================================================================
module "orca_lambdas" {
  source = "../lambdas"
  ## --------------------------
  ## Cumulus Variables
  ## --------------------------
  ## REQUIRED
  aws_profile              = var.aws_profile
  buckets                  = var.buckets
  lambda_subnet_ids        = var.lambda_subnet_ids
  permissions_boundary_arn = var.permissions_boundary_arn
  prefix                   = var.prefix
  vpc_id                   = var.vpc_id

  ## OPTIONAL
  region = var.region
  tags   = local.tags

  ## --------------------------
  ## ORCA Variables
  ## --------------------------
  ## REQUIRED
  orca_default_bucket = var.orca_default_bucket

  ## OPTIONAL
  database_port                        = var.database_port
  orca_ingest_lambda_memory_size       = var.orca_ingest_lambda_memory_size
  orca_ingest_lambda_timeout           = var.orca_ingest_lambda_timeout
  orca_recovery_buckets                = var.orca_recovery_buckets
  orca_recovery_complete_filter_prefix = var.orca_recovery_complete_filter_prefix
  orca_recovery_expiration_days        = var.orca_recovery_expiration_days
  orca_recovery_lambda_memory_size     = var.orca_recovery_lambda_memory_size
  orca_recovery_lambda_timeout         = var.orca_recovery_lambda_timeout
  orca_recovery_retry_limit            = var.orca_recovery_retry_limit
  orca_recovery_retry_interval         = var.orca_recovery_retry_interval

  ## OPTIONAL (DO NOT CHANGE DEFAULT VALUES!)
  database_app_user            = var.database_app_user
  database_name                = var.database_name
  ddl_dir                      = var.ddl_dir
  drop_database                = var.drop_database
  orca_recovery_retrieval_type = var.orca_recovery_retrieval_type
  platform                     = var.platform
}


## orca_workflows - workflows module
## =============================================================================
module "orca_workflows" {
  source = "../workflows"
  ## --------------------------
  ## Cumulus Variables
  ## --------------------------
  ## REQUIRED
  aws_profile     = var.aws_profile
  prefix          = var.prefix
  system_bucket   = var.system_bucket
  workflow_config = var.workflow_config

  ## OPTIONAL
  region = var.region
  tags   = local.tags

  ## --------------------------
  ## ORCA Variables
  ## --------------------------
  ## REQUIRED
  orca_default_bucket                           = var.orca_default_bucket
  orca_lambda_extract_filepaths_for_granule_arn = module.orca_lambdas.extract_filepaths_for_granule_arn
  orca_lambda_request_files_arn                 = module.orca_lambdas.request_files_arn
  orca_sqs_status_update_queue_id               = module.sqs.orca_sqs_status_update_queue_id
}


## orca_rds - rds module
## =============================================================================
module "orca_rds" {
  source = "../rds"
  ## --------------------------
  ## Cumulus Variables
  ## --------------------------
  ## REQUIRED
  aws_profile       = var.aws_profile
  lambda_subnet_ids = var.lambda_subnet_ids
  prefix            = var.prefix

  ## OPTIONAL
  region = var.region
  tags   = local.tags

  ## --------------------------
  ## ORCA Variables
  ## --------------------------
  ## REQUIRED
  database_app_user_pw               = var.database_app_user_pw
  db_deploy_arn                      = module.orca_lambdas.db_deploy_arn
  db_deploy_source_code_hash         = module.orca_lambdas.db_deploy_source_code_hash
  postgres_user_pw                   = var.postgres_user_pw
  vpc_postgres_ingress_all_egress_id = module.orca_lambdas.vpc_postgres_ingress_all_egress_id

  ## OPTIONAL
  database_port = var.database_port

  ## OPTIONAL (DO NOT CHANGE DEFAULT VALUES!)
  database_name = var.database_name
}