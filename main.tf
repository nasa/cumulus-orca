locals {
  default_tags = {
    Deployment = var.prefix
  }
}

terraform {
  required_providers {
    aws  = ">= 2.31.0"
    null = "~> 2.1"
  }
}

provider "aws" {
  region = var.region
}

module "orca" {
  source = "./modules/orca"
  database_app_user_pw = var.database_app_user_pw
  default_tags = var.default_tags
  prefix = var.prefix
  subnet_ids = var.subnet_ids
  database_port = var.database_port
  postgres_user_pw = var.database_app_user_pw
  database_name = var.database_name
  database_app_user = var.database_app_user
  ddl_dir = var.ddl_dir
  drop_database = var.drop_database
  platform = var.platform
  lambda_timeout = var.lambda_timeout
  restore_complete_filter_prefix = var.restore_complete_filter_prefix
  vpc_id = var.vpc_id
  copy_retry_sleep_secs = var.copy_retry_sleep_secs
  permissions_boundary_arn = var.permissions_boundary_arn
  buckets = var.buckets
  workflow_config = var.workflow_config
  region = var.region

}
