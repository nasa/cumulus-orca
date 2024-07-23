terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 3.14.1"
    }
  }
}

provider "aws" {
  region = var.region
}

data "aws_region" "current" {}

module "rds_cluster" {
  source                   = "https://github.com/nasa/cumulus/releases/download/v18.3.1/terraform-aws-cumulus-rds.zip"
  db_admin_username        = var.db_admin_username
  db_admin_password        = var.db_admin_password
  region                   = var.region
  vpc_id                   = var.vpc_id
  subnets                  = var.subnets
  engine_version           = var.engine_version
  deletion_protection      = var.deletion_protection
  cluster_identifier       = var.cluster_identifier
  tags                     = var.tags
  snapshot_identifier      = var.snapshot_identifier
  provision_user_database  = var.provision_user_database
  prefix                   = var.prefix
  permissions_boundary_arn = var.permissions_boundary_arn
  rds_user_password        = var.rds_user_password
}
