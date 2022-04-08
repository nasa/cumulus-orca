## Referenced Modules

## orca_lambdas - lambdas module that calls iam and security_groups module
## =============================
module "orca_lambdas" {
  source = "../lambdas"
  depends_on = [module.orca_iam, module.orca_secretsmanager]  ## secretsmanager sets up db connection secrets.
  ## --------------------------
  ## Cumulus Variables
  ## --------------------------
  ## REQUIRED
  buckets                                              = var.buckets
  lambda_subnet_ids                                    = var.lambda_subnet_ids
  prefix                                               = var.prefix
  rds_security_group_id                                = var.rds_security_group_id
  vpc_id                                               = var.vpc_id
  ## OPTIONAL
  tags                           = var.tags
  default_multipart_chunksize_mb = var.default_multipart_chunksize_mb

  ## --------------------------
  ## ORCA Variables
  ## --------------------------
  ## REQUIRED
  db_connect_info_secret_arn                           = module.orca_secretsmanager.secretsmanager_arn
  orca_default_bucket                                  = var.orca_default_bucket
  orca_secretsmanager_s3_access_credentials_secret_arn = module.orca_secretsmanager.s3_access_credentials_secret_arn
  orca_sqs_internal_report_queue_id                    = module.orca_sqs.orca_sqs_internal_report_queue_id
  orca_sqs_metadata_queue_arn                          = module.orca_sqs.orca_sqs_metadata_queue_arn
  orca_sqs_metadata_queue_id                           = module.orca_sqs.orca_sqs_metadata_queue_id
  orca_sqs_s3_inventory_queue_id                       = module.orca_sqs.orca_sqs_s3_inventory_queue_id
  orca_sqs_staged_recovery_queue_id                    = module.orca_sqs.orca_sqs_staged_recovery_queue_id
  orca_sqs_staged_recovery_queue_arn                   = module.orca_sqs.orca_sqs_staged_recovery_queue_arn
  orca_sqs_status_update_queue_id                      = module.orca_sqs.orca_sqs_status_update_queue_id
  orca_sqs_status_update_queue_arn                     = module.orca_sqs.orca_sqs_status_update_queue_arn
  restore_object_role_arn                              = module.orca_iam.restore_object_role_arn

  ## OPTIONAL
  orca_ingest_lambda_memory_size         = var.orca_ingest_lambda_memory_size
  orca_ingest_lambda_timeout             = var.orca_ingest_lambda_timeout
  orca_reconciliation_lambda_memory_size = var.orca_reconciliation_lambda_memory_size
  orca_reconciliation_lambda_timeout     = var.orca_reconciliation_lambda_timeout
  orca_recovery_buckets                  = var.orca_recovery_buckets
  orca_recovery_complete_filter_prefix   = var.orca_recovery_complete_filter_prefix
  orca_recovery_expiration_days          = var.orca_recovery_expiration_days
  orca_recovery_lambda_memory_size       = var.orca_recovery_lambda_memory_size
  orca_recovery_lambda_timeout           = var.orca_recovery_lambda_timeout
  orca_recovery_retry_limit              = var.orca_recovery_retry_limit
  orca_recovery_retry_interval           = var.orca_recovery_retry_interval
  orca_recovery_retry_backoff            = var.orca_recovery_retry_backoff
}

## orca_lambdas_secondary - lambdas module that is dependent on resources that presently are created after most lambdas
## ====================================================================================================================
module "orca_lambdas_secondary" {
  source = "../lambdas_secondary"
  depends_on = [module.orca_iam, module.orca_secretsmanager, module.orca_workflows]  ## secretsmanager sets up db connection secrets.
  ## --------------------------
  ## Cumulus Variables
  ## --------------------------
  ## REQUIRED
  buckets                                              = var.buckets
  lambda_subnet_ids                                    = var.lambda_subnet_ids
  prefix                                               = var.prefix
  ## OPTIONAL
  tags                           = var.tags
  default_multipart_chunksize_mb = var.default_multipart_chunksize_mb

  ## --------------------------
  ## ORCA Variables
  ## --------------------------
  ## REQUIRED
  orca_sfn_internal_reconciliation_workflow_arn = module.orca_workflows.orca_sfn_internal_reconciliation_workflow_arn
  orca_sqs_internal_report_queue_id             = module.orca_sqs.orca_sqs_internal_report_queue_id
  orca_sqs_s3_inventory_queue_arn               = module.orca_sqs.orca_sqs_s3_inventory_queue_arn
  restore_object_role_arn                       = module.orca_iam.restore_object_role_arn
  orca_reports_bucket_arn                       = var.orca_reports_bucket_arn
  vpc_postgres_ingress_all_egress_id            = module.orca_lambdas.vpc_postgres_ingress_all_egress_id

  ## OPTIONAL
  orca_reconciliation_lambda_memory_size = var.orca_reconciliation_lambda_memory_size
  orca_reconciliation_lambda_timeout     = var.orca_reconciliation_lambda_timeout
  s3_report_frequency                    = var.s3_report_frequency
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
  tags = var.tags

  ## --------------------------
  ## ORCA Variables
  ## --------------------------
  ## REQUIRED
  orca_default_bucket                           = var.orca_default_bucket
  orca_lambda_copy_to_glacier_arn               = module.orca_lambdas.copy_to_glacier_arn
  orca_lambda_extract_filepaths_for_granule_arn = module.orca_lambdas.extract_filepaths_for_granule_arn
  orca_lambda_get_current_archive_list_arn      = module.orca_lambdas.get_current_archive_list_arn
  orca_lambda_perform_orca_reconcile_arn        = module.orca_lambdas.perform_orca_reconcile_arn
  orca_lambda_request_files_arn                 = module.orca_lambdas.request_files_arn
}


# restore_object_arn - IAM module reference
# # ------------------------------------------------------------------------------
module "orca_iam" {
  source = "../iam"
  ## --------------------------
  ## Cumulus Variables
  ## --------------------------
  ## REQUIRED
  buckets                  = var.buckets
  permissions_boundary_arn = var.permissions_boundary_arn
  prefix                   = var.prefix
  # OPTIONAL
  tags = var.tags
  # --------------------------
  # ORCA Variables
  # --------------------------
  # OPTIONAL
  orca_recovery_buckets = var.orca_recovery_buckets
}


## orca_secretsmanager - secretsmanager module
## =============================================================================
module "orca_secretsmanager" {
  source = "../secretsmanager"
  depends_on = [module.orca_iam]
  ## --------------------------
  ## Cumulus Variables
  ## --------------------------
  ## REQUIRED
  prefix = var.prefix

  ## OPTIONAL
  tags = var.tags
  ## --------------------------
  ## ORCA Variables
  ## --------------------------
  ## REQUIRED
  db_admin_password = var.db_admin_password
  db_user_password  = var.db_user_password
  db_host_endpoint  = var.db_host_endpoint
  restore_object_role_arn = module.orca_iam.restore_object_role_arn
  s3_access_key = var.s3_access_key
  s3_secret_key = var.s3_secret_key

  ## OPTIONAL
  db_admin_username = var.db_admin_username
  db_name           = var.db_name
  db_user_name      = var.db_user_name
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
  tags = var.tags

  ## --------------------------
  ## ORCA Variables
  ## --------------------------

  ## REQUIRED
  dlq_subscription_email = var.dlq_subscription_email

  ## OPTIONAL
  internal_report_queue_message_retention_time_seconds = var.internal_report_queue_message_retention_time_seconds
  metadata_queue_message_retention_time_seconds        = var.metadata_queue_message_retention_time_seconds
  orca_reconciliation_lambda_timeout                   = var.orca_reconciliation_lambda_timeout
  s3_inventory_queue_message_retention_time_seconds    = var.s3_inventory_queue_message_retention_time_seconds
  sqs_delay_time_seconds                               = var.sqs_delay_time_seconds
  sqs_maximum_message_size                             = var.sqs_maximum_message_size
  staged_recovery_queue_message_retention_time_seconds = var.staged_recovery_queue_message_retention_time_seconds
  status_update_queue_message_retention_time_seconds   = var.status_update_queue_message_retention_time_seconds
}


## orca_api_gateway - api gateway module
## =============================================================================
module "orca_api_gateway" {
  depends_on = [
    module.orca_lambdas
  ]
  source = "../api-gateway"
  ## --------------------------
  ## Cumulus Variables
  ## --------------------------
  ## REQUIRED
  prefix = var.prefix
  vpc_id = var.vpc_id

  ## --------------------------
  ## ORCA Variables
  ## --------------------------
  ## REQUIRED
  orca_catalog_reporting_invoke_arn     = module.orca_lambdas.orca_catalog_reporting_invoke_arn
  request_status_for_granule_invoke_arn = module.orca_lambdas.request_status_for_granule_invoke_arn
  request_status_for_job_invoke_arn     = module.orca_lambdas.request_status_for_job_invoke_arn
  ## OPTIONAL
  vpc_endpoint_id                       = var.vpc_endpoint_id
}
