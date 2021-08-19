## Local Variables
locals {
  tags = merge(var.tags, { Deployment = var.prefix })
}


## Referenced Modules

## orca_lambdas - lambdas module that calls iam and security_groups module
## =============================================================================
module "orca_lambdas" {
  source = "../lambdas"
  ## --------------------------
  ## Cumulus Variables
  ## --------------------------
  ## REQUIRED
  buckets                           = var.buckets
  lambda_subnet_ids                 = var.lambda_subnet_ids
  permissions_boundary_arn          = var.permissions_boundary_arn
  prefix                            = var.prefix
  vpc_id                            = var.vpc_id
  orca_sqs_staged_recovery_queue_id = module.orca_sqs.orca_sqs_staged_recovery_queue_id
  ## OPTIONAL
  region                             = var.region
  aws_profile                        = var.aws_profile
  tags = local.tags

  ## --------------------------
  ## ORCA Variables
  ## --------------------------
  ## REQUIRED
  orca_default_bucket                = var.orca_default_bucket
  orca_sqs_staged_recovery_queue_arn = module.orca_sqs.orca_sqs_staged_recovery_queue_arn
  orca_sqs_status_update_queue_id    = module.orca_sqs.orca_sqs_status_update_queue_id
  orca_sqs_status_update_queue_arn   = module.orca_sqs.orca_sqs_status_update_queue_arn
  db_deploy_arn                      = module.orca_lambdas.db_deploy_arn
  db_deploy_source_code_hash         = module.orca_lambdas.db_deploy_source_code_hash

  ## OPTIONAL
  orca_ingest_lambda_memory_size       = var.orca_ingest_lambda_memory_size
  orca_ingest_lambda_timeout           = var.orca_ingest_lambda_timeout
  orca_recovery_buckets                = var.orca_recovery_buckets
  orca_recovery_complete_filter_prefix = var.orca_recovery_complete_filter_prefix
  orca_recovery_expiration_days        = var.orca_recovery_expiration_days
  orca_recovery_lambda_memory_size     = var.orca_recovery_lambda_memory_size
  orca_recovery_lambda_timeout         = var.orca_recovery_lambda_timeout
  orca_recovery_retry_limit            = var.orca_recovery_retry_limit
  orca_recovery_retry_interval         = var.orca_recovery_retry_interval
  orca_recovery_retry_backoff          = var.orca_recovery_retry_backoff
}


## orca_workflows - workflows module
## =============================================================================
module "orca_workflows" {
  source = "../workflows"
  ## --------------------------
  ## Cumulus Variables
  ## --------------------------
  ## REQUIRED
  prefix          = var.prefix
  system_bucket   = var.system_bucket
  workflow_config = var.workflow_config

  ## OPTIONAL
  tags = local.tags

  ## --------------------------
  ## ORCA Variables
  ## --------------------------
  ## REQUIRED
  orca_default_bucket                                = var.orca_default_bucket
  orca_lambda_extract_filepaths_for_granule_arn      = module.orca_lambdas.extract_filepaths_for_granule_arn
  orca_lambda_request_files_arn                      = module.orca_lambdas.request_files_arn
  orca_lambda_copy_to_glacier_arn                    = module.orca_lambdas.copy_to_glacier_arn
  orca_lambda_copy_to_glacier_cumulus_translator_arn = module.orca_lambdas.copy_to_glacier_cumulus_translator_arn
}


## orca_secretsmanager - secretsmanager module
## =============================================================================
module "orca_secretsmanager" {
  source = "../secretsmanager"
  ## --------------------------
  ## Cumulus Variables
  ## --------------------------
  ## REQUIRED
  prefix = var.prefix

  ## OPTIONAL
  tags = local.tags
  ## --------------------------
  ## ORCA Variables
  ## --------------------------
  ## REQUIRED  
  db_admin_password = var.db_admin_password
  db_user_password  = var.db_user_password
  db_host_endpoint  = var.db_host_endpoint

  ## OPTIONAL
  db_admin_username = var.db_admin_username
}
## orca_sqs - SQS module
## =============================================================================
module "orca_sqs" {
  source = "../sqs"
  ## --------------------------
  ## Cumulus Variables
  ## --------------------------
  ## REQUIRED
  prefix = var.prefix

  ## OPTIONAL
  tags = local.tags

  ## --------------------------
  ## ORCA Variables
  ## --------------------------
  ## OPTIONAL
  sqs_delay_time_seconds                               = var.sqs_delay_time_seconds
  sqs_maximum_message_size                             = var.sqs_maximum_message_size
  staged_recovery_queue_message_retention_time_seconds = var.staged_recovery_queue_message_retention_time_seconds
  status_update_queue_message_retention_time_seconds   = var.status_update_queue_message_retention_time_seconds
}