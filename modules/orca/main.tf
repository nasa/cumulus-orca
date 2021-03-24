module "orca_workflows" {
  source                       = "../workflows"
  prefix                       = var.prefix
  workflow_config              = var.workflow_config
  system_bucket                = var.buckets["internal"]["name"]
  tags                         = var.default_tags
  extract_filepaths_lambda_arn = module.orca_lambdas.extract_filepath_arn
  request_files_lambda_arn     = module.orca_lambdas.request_files_arn
}


module "orca_lambdas" {
  source                         = "../lambdas"
  tags                           = var.default_tags
  prefix                         = var.prefix
  subnet_ids                     = var.subnet_ids
  database_port                  = var.database_port
  database_name                  = var.database_name
  database_app_user              = var.database_app_user
  ddl_dir                        = var.ddl_dir
  drop_database                  = var.drop_database
  platform                       = var.platform
  lambda_timeout                 = var.lambda_timeout
  restore_complete_filter_prefix = var.restore_complete_filter_prefix
  vpc_id                         = var.vpc_id
  copy_retry_sleep_secs          = var.copy_retry_sleep_secs
  permissions_boundary_arn       = var.permissions_boundary_arn
  buckets                        = var.buckets
}


module "orca_rds" {
  source                             = "../rds"
  prefix                             = var.prefix
  subnet_ids                         = var.subnet_ids
  profile                            = var.profile
  postgres_user_pw                   = var.postgres_user_pw
  database_port                      = var.database_port
  vpc_postgres_ingress_all_egress_id = module.orca_lambdas.vpc_postgres_ingress_all_egress_id
  db_lambda_deploy_arn               = module.orca_lambdas.db_deploy.arn
  lambda_source_code_hash            = module.orca_lambdas.db_deploy.arn
  database_app_user_pw               = var.database_app_user_pw
  region                             = var.region
  default_tags                       = var.default_tags
}

module "orca_sqs" {
  source = "../sqs"
  ## --------------------------
  ## Cumulus Variables
  ## --------------------------
  ## REQUIRED
  prefix      = var.prefix
  aws_profile = var.aws_profile
  ## OPTIONAL
  region = var.region
  tags   = local.default_tags


  ## --------------------------
  ## ORCA SQS Variables
  ## --------------------------
  ## OPTIONAL
  sqs_delay_time                               = var.sqs_delay_time
  sqs_maximum_message_size                     = var.sqs_maximum_message_size
  staged_recovery_queue_message_retention_time = var.staged_recovery_queue_message_retention_time
  status_update_queue_message_retention_time   = var.status_update_queue_message_retention_time
}