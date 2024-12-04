## Referenced Modules

## orca_lambdas - lambdas module that calls iam and security_groups module
## =============================
module "orca_lambdas" {
  source     = "../lambdas"
  depends_on = [module.orca_iam, module.orca_secretsmanager] ## secretsmanager sets up db connection secrets.
  ## --------------------------
  ## Cumulus Variables
  ## --------------------------
  ## REQUIRED
  buckets                  = var.buckets
  lambda_subnet_ids        = var.lambda_subnet_ids
  permissions_boundary_arn = var.permissions_boundary_arn
  prefix                   = var.prefix
  rds_security_group_id    = var.rds_security_group_id
  vpc_id                   = var.vpc_id
  ## OPTIONAL
  tags                           = var.tags
  default_multipart_chunksize_mb = var.default_multipart_chunksize_mb

  ## --------------------------
  ## ORCA Variables
  ## --------------------------
  ## REQUIRED
  db_connect_info_secret_arn                           = module.orca_secretsmanager.secretsmanager_arn
  orca_default_bucket                                  = var.orca_default_bucket
  orca_sqs_archive_recovery_queue_arn                  = module.orca_sqs.orca_sqs_archive_recovery_queue_arn
  orca_sqs_archive_recovery_queue_id                   = module.orca_sqs.orca_sqs_archive_recovery_queue_id
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
  lambda_runtime                                = var.lambda_runtime
  orca_delete_old_reconcile_jobs_frequency_cron = var.orca_delete_old_reconcile_jobs_frequency_cron
  orca_default_recovery_type                    = var.orca_default_recovery_type
  orca_default_storage_class                    = var.orca_default_storage_class
  orca_ingest_lambda_memory_size                = var.orca_ingest_lambda_memory_size
  orca_ingest_lambda_timeout                    = var.orca_ingest_lambda_timeout
  orca_internal_reconciliation_expiration_days  = var.orca_internal_reconciliation_expiration_days
  orca_reconciliation_lambda_memory_size        = var.orca_reconciliation_lambda_memory_size
  orca_reconciliation_lambda_timeout            = var.orca_reconciliation_lambda_timeout
  orca_recovery_buckets                         = var.orca_recovery_buckets
  orca_recovery_complete_filter_prefix          = var.orca_recovery_complete_filter_prefix
  orca_recovery_expiration_days                 = var.orca_recovery_expiration_days
  orca_recovery_lambda_memory_size              = var.orca_recovery_lambda_memory_size
  orca_recovery_lambda_timeout                  = var.orca_recovery_lambda_timeout
  orca_recovery_retry_limit                     = var.orca_recovery_retry_limit
  orca_recovery_retry_interval                  = var.orca_recovery_retry_interval
  orca_recovery_retry_backoff                   = var.orca_recovery_retry_backoff
  log_level                                     = var.log_level
  gql_tasks_role_arn               = module.orca_graphql_0.gql_tasks_role_arn
}

## orca_lambdas_secondary - lambdas module that is dependent on resources that presently are created after most lambdas
## ====================================================================================================================
module "orca_lambdas_secondary" {
  source     = "../lambdas_secondary"
  depends_on = [module.orca_iam, module.orca_secretsmanager, module.orca_workflows] ## secretsmanager sets up db connection secrets.
  ## --------------------------
  ## Cumulus Variables
  ## --------------------------
  ## REQUIRED
  buckets           = var.buckets
  lambda_subnet_ids = var.lambda_subnet_ids
  prefix            = var.prefix
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
  orca_reports_bucket_name                      = var.orca_reports_bucket_name
  vpc_postgres_ingress_all_egress_id            = module.orca_lambdas.vpc_postgres_ingress_all_egress_id

  ## OPTIONAL
  lambda_runtime                         = var.lambda_runtime
  orca_reconciliation_lambda_memory_size = var.orca_reconciliation_lambda_memory_size
  orca_reconciliation_lambda_timeout     = var.orca_reconciliation_lambda_timeout
  s3_report_frequency                    = var.s3_report_frequency
  log_level                              = var.log_level
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

  ## OPTIONAL
  tags = var.tags

  ## --------------------------
  ## ORCA Variables
  ## --------------------------
  ## REQUIRED
  orca_default_bucket                           = var.orca_default_bucket
  orca_lambda_copy_to_archive_arn               = module.orca_lambdas.copy_to_archive_arn
  orca_lambda_extract_filepaths_for_granule_arn = module.orca_lambdas.extract_filepaths_for_granule_arn
  orca_lambda_get_current_archive_list_arn      = module.orca_lambdas.get_current_archive_list_arn
  orca_lambda_perform_orca_reconcile_arn        = module.orca_lambdas.perform_orca_reconcile_arn
  orca_lambda_request_from_archive_arn          = module.orca_lambdas.request_from_archive_arn
  orca_step_function_role_arn                   = module.orca_iam.step_function_role_arn
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
  orca_recovery_buckets    = var.orca_recovery_buckets
  orca_reports_bucket_name = var.orca_reports_bucket_name
}

## orca_graphql_0- graphql module that sets up centralized db code
## sets up components required by other modules, such as IAM roles for secretsmanager to grant permissions to
## =============================
module "orca_graphql_0" {
  source     = "../graphql_0"
  depends_on = []
  ## --------------------------
  ## Cumulus Variables
  ## --------------------------
  ## REQUIRED
  permissions_boundary_arn = var.permissions_boundary_arn
  prefix                   = var.prefix
  vpc_id                   = var.vpc_id
  db_cluster_identifier    = var.db_cluster_identifier 

  ## OPTIONAL
  tags = var.tags
  deploy_rds_cluster_role_association = var.deploy_rds_cluster_role_association
  orca_recovery_buckets                         = var.orca_recovery_buckets
  orca_reports_bucket_name                      = var.orca_reports_bucket_name
  buckets = var.buckets
}

## orca_secretsmanager - secretsmanager module
## =============================================================================
module "orca_secretsmanager" {
  source     = "../secretsmanager"
  depends_on = [module.orca_iam, module.orca_graphql_0]
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
  db_admin_password               = var.db_admin_password
  db_user_password                = var.db_user_password
  db_host_endpoint                = var.db_host_endpoint
  gql_ecs_task_execution_role_arn = module.orca_graphql_0.gql_ecs_task_execution_role_arn
  restore_object_role_arn         = module.orca_iam.restore_object_role_arn
  gql_tasks_role_arn              = module.orca_graphql_0.gql_tasks_role_arn

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
  buckets = var.buckets
  prefix  = var.prefix

  ## OPTIONAL
  tags = var.tags

  ## --------------------------
  ## ORCA Variables
  ## --------------------------

  ## REQUIRED
  dlq_subscription_email   = var.dlq_subscription_email
  orca_reports_bucket_name = var.orca_reports_bucket_name

  ## OPTIONAL
  archive_recovery_queue_message_retention_time_seconds = var.archive_recovery_queue_message_retention_time_seconds
  internal_report_queue_message_retention_time_seconds  = var.internal_report_queue_message_retention_time_seconds
  metadata_queue_message_retention_time_seconds         = var.metadata_queue_message_retention_time_seconds
  orca_reconciliation_lambda_timeout                    = var.orca_reconciliation_lambda_timeout
  s3_inventory_queue_message_retention_time_seconds     = var.s3_inventory_queue_message_retention_time_seconds
  sqs_delay_time_seconds                                = var.sqs_delay_time_seconds
  sqs_maximum_message_size                              = var.sqs_maximum_message_size
  staged_recovery_queue_message_retention_time_seconds  = var.staged_recovery_queue_message_retention_time_seconds
  status_update_queue_message_retention_time_seconds    = var.status_update_queue_message_retention_time_seconds
}

## orca_ecs - ecs module that sets up ecs cluster
## =============================
module "orca_ecs" {
  source = "../ecs"
  ## --------------------------
  ## Cumulus Variables
  ## --------------------------
  ## REQUIRED
  prefix = var.prefix

  ## OPTIONAL
  tags = var.tags
}

## orca_graphql_1 - graphql module that sets up centralized db code
## =============================
module "orca_graphql_1" {
  source     = "../graphql_1"
  depends_on = [module.orca_ecs, module.orca_graphql_0, module.orca_secretsmanager] ## secretsmanager sets up db connection secrets.
  ## --------------------------
  ## Cumulus Variables
  ## --------------------------
  ## REQUIRED
  lambda_subnet_ids        = var.lambda_subnet_ids
  permissions_boundary_arn = var.permissions_boundary_arn
  prefix                   = var.prefix
  system_bucket            = var.system_bucket
  vpc_id                   = var.vpc_id

  ## OPTIONAL
  tags = var.tags

  ## --------------------------
  ## ORCA Variables
  ## --------------------------
  ## REQUIRED
  db_connect_info_secret_arn       = module.orca_secretsmanager.secretsmanager_arn
  ecs_cluster_id                   = module.orca_ecs.ecs_cluster_id
  gql_ecs_task_execution_role_arn  = module.orca_graphql_0.gql_ecs_task_execution_role_arn
  gql_ecs_task_execution_role_id   = module.orca_graphql_0.gql_ecs_task_execution_role_id
  gql_tasks_role_arn               = module.orca_graphql_0.gql_tasks_role_arn
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
  internal_reconcile_report_job_invoke_arn      = module.orca_lambdas.internal_reconcile_report_job_invoke_arn
  internal_reconcile_report_orphan_invoke_arn   = module.orca_lambdas.internal_reconcile_report_orphan_invoke_arn
  internal_reconcile_report_phantom_invoke_arn  = module.orca_lambdas.internal_reconcile_report_phantom_invoke_arn
  internal_reconcile_report_mismatch_invoke_arn = module.orca_lambdas.internal_reconcile_report_mismatch_invoke_arn
  orca_catalog_reporting_invoke_arn             = module.orca_lambdas.orca_catalog_reporting_invoke_arn
  request_status_for_granule_invoke_arn         = module.orca_lambdas.request_status_for_granule_invoke_arn
  request_status_for_job_invoke_arn             = module.orca_lambdas.request_status_for_job_invoke_arn
  ## OPTIONAL
  vpc_endpoint_id = var.vpc_endpoint_id
  tags = var.tags
}