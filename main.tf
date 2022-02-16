## Local Variables
locals {
  db_name = var.db_name != null ? var.db_name : replace("${var.prefix}_orca", "-", "_")
  db_user_name = replace("${var.prefix}_orcauser", "-", "_")
  tags    = merge(var.tags, { Deployment = var.prefix }, { team = "ORCA", application = "ORCA" })
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
  rds_security_group_id    = var.rds_security_group_id
  system_bucket            = var.system_bucket
  vpc_id                   = var.vpc_id
  workflow_config          = var.workflow_config

  ## OPTIONAL
  tags = local.tags

  ## --------------------------
  ## ORCA Variables
  ## --------------------------
  ## REQUIRED
  db_admin_password         = var.db_admin_password
  db_host_endpoint          = var.db_host_endpoint
  db_user_password          = var.db_user_password
  orca_default_bucket       = var.orca_default_bucket
  dlq_subscription_email    = var.dlq_subscription_email
  
  ## OPTIONAL
  db_admin_username                                    = var.db_admin_username
  db_name                                              = local.db_name
  db_user_name                                         = local.db_user_name
  default_multipart_chunksize_mb                       = var.default_multipart_chunksize_mb
  metadata_queue_message_retention_time_seconds        = var.metadata_queue_message_retention_time_seconds
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
  vpc_endpoint_id                                      = var.vpc_endpoint_id
}
