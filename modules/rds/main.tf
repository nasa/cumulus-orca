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
  tags = merge(var.tags, { Deployment = var.prefix })
  # Ignore aws profile in case this was deployed with CI or in a machine without
  # aws profile defined
  used_profile = contains([var.aws_profile], "default") ? "" : "--profile ${var.aws_profile}"
}


## Resources

## =============================================================================
## DATABASE RESOURCES
## =============================================================================

## postgres_subnet_group - Subnet Group the PostgreSQL database is associated with.
## =============================================================================
resource "aws_db_subnet_group" "postgres_subnet_group" {
  ## REQUIRED
  subnet_ids = var.lambda_subnet_ids

  ## OPTIONAL
  description = "ORCA PostgreSQL Subnet group where the ORCA database resides."
  name        = "${var.prefix}-postgres-subnet-group"
  tags        = local.tags
}


## postgresql - PostgreSQL database created for ORCA metadata/status
## =============================================================================
# https://blog.faraday.io/how-to-create-an-rds-instance-with-terraform/
# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/db_instance
# https://registry.terraform.io/modules/terraform-aws-modules/rds/aws/latest
resource "aws_db_instance" "postgresql" {
  ## REQUIRED
  allocated_storage = 20
  engine            = "postgres"
  identifier        = "${var.prefix}-postgres-sndbx"
  instance_class    = "db.t2.micro"
  password          = var.postgres_user_pw
  username          = "postgres"

  ## OPTIONAL
  # set apply_immediately true just for testing
  apply_immediately                   = false
  auto_minor_version_upgrade          = true
  backup_retention_period             = 7
  backup_window                       = "03:00-06:00"
  db_subnet_group_name                = aws_db_subnet_group.postgres_subnet_group.id
  delete_automated_backups            = true
  deletion_protection                 = false
  enabled_cloudwatch_logs_exports     = ["postgresql", "upgrade"]
  engine_version                      = "11"
  final_snapshot_identifier           = "daacx"
  iam_database_authentication_enabled = true
  maintenance_window                  = "Mon:00:00-Mon:03:00"
  name                                = "postgres"
  port                                = var.database_port
  publicly_accessible                 = false
  skip_final_snapshot                 = true
  storage_encrypted                   = false
  vpc_security_group_ids              = [var.vpc_postgres_ingress_all_egress_id]
  tags                                = local.tags
}


## =============================================================================
## NULL RESOURCES - 1x Use
## =============================================================================

## bootstrap - Bootstrap lambda that creates/modifies database objects on deploys
## =============================================================================
# https://registry.terraform.io/providers/hashicorp/null/latest/docs/resources/resource
# https://www.terraform.io/docs/language/resources/provisioners/local-exec.html
resource "null_resource" "bootstrap" {
  # Determine what has to change to trigger this resource being created/re-created.
  triggers = {
    bootstrap_lambda_hash = var.db_deploy_source_code_hash
  }

  # Execute the db_deploy lambda 1 time if the resource is created/re-created.
  provisioner "local-exec" {
    command = "aws lambda invoke --function-name ${var.db_deploy_arn} ${local.used_profile} --region ${var.region} 'db_deploy-response.out'"
  }

  depends_on = [aws_db_instance.postgresql]
}


## TODO: Should create null resource to handle password changes ORCA-145


## =============================================================================
## SECRET MANAGER RESOURCES
## =============================================================================

## drdb-admin-pass - postgres (root) user password
## =============================================================================
resource "aws_secretsmanager_secret" "drdb-admin-pass" {
  ## OPTIONAL
  description             = "Admin password to be used for the PostgreSQL DB"
  name                    = "${var.prefix}-drdb-admin-pass"
  recovery_window_in_days = 0
  tags                    = local.tags
}


resource "aws_secretsmanager_secret_version" "drdb-admin-pass" {
  ## REQUIRED
  secret_id = aws_secretsmanager_secret.drdb-admin-pass.id

  ## OPTIONAL
  secret_string = var.postgres_user_pw
}


## drdb-user-pass - Application user database password
## =============================================================================
resource "aws_secretsmanager_secret" "drdb-user-pass" {
  ## OPTIONAL
  description             = "Application user password to be used for the PostgreSQL DB"
  name                    = "${var.prefix}-drdb-user-pass"
  recovery_window_in_days = 0
  tags                    = local.tags
}


resource "aws_secretsmanager_secret_version" "drdb-user-pass" {
  ## REQUIRED
  secret_id = aws_secretsmanager_secret.drdb-user-pass.id

  ## OPTIONAL
  secret_string = var.database_app_user_pw
}


## drdb-host - PostgreSQL database address for connecting
## =============================================================================
resource "aws_secretsmanager_secret" "drdb-host" {
  ## OPTIONAL
  description             = "PostgreSQL Host Address"
  name                    = "${var.prefix}-drdb-host"
  recovery_window_in_days = 0
  tags                    = local.tags
}

resource "aws_secretsmanager_secret_version" "drdb-host" {
  ## REQUIRED
  secret_id = aws_secretsmanager_secret.drdb-host.id

  ## OPTIONAL
  secret_string = aws_db_instance.postgresql.address
}

