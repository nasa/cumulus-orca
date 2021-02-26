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
}


## Resources
resource "aws_security_group" "vpc_postgres_ingress_all_egress" {
  description            = "ORCA security group to allow PostgreSQL access."
  name                   = "${var.prefix}-vpc-postgres-ingress-all-egress"
  revoke_rules_on_delete = true
  tags                   = local.tags
  vpc_id                 = var.vpc_id
}


resource "aws_security_group_rule" "rds_security_group_allow_postgres" {
  description       = "ORCA security group rule to allow PostgreSQL port traffic."
  from_port         = var.database_port
  protocol          = "tcp"
  security_group_id = aws_security_group.vpc_postgres_ingress_all_egress.id
  self              = true
  to_port           = var.database_port
  type              = "ingress"
}