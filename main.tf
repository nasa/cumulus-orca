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
  buckets                  = var.buckets
  lambda_subnet_ids        = var.lambda_subnet_ids
  permissions_boundary_arn = var.permissions_boundary_arn
  prefix                   = var.prefix
  system_bucket            = var.system_bucket
  vpc_id                   = var.vpc_id
  workflow_config          = var.workflow_config

  ## OPTIONAL
  aws_profile = var.aws_profile
  region      = var.region
  tags        = local.tags

  ## --------------------------
  ## ORCA Variables
  ## --------------------------
  ## REQUIRED
  database_app_user_pw = var.database_app_user_pw
  orca_default_bucket  = var.orca_default_bucket
  postgres_user_pw     = var.postgres_user_pw

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
  database_app_user            = var.database_app_user
  database_name                = var.database_name
  orca_recovery_retrieval_type = var.orca_recovery_retrieval_type
}
