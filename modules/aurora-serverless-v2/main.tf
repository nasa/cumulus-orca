terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0.0"
    }
  }
}

locals {
  timestamp = "${timestamp()}"
  timestamp_sanitized = "${replace("${local.timestamp}", "/[-| |T|Z|:]/", "")}"

}

data "aws_caller_identity" "current" {}

resource "aws_db_subnet_group" "default" {
  name_prefix = "${var.prefix}-rds-tf-subnet"
  subnet_ids  = var.subnets
  tags        = var.tags
}

resource "aws_rds_cluster_parameter_group" "rds_cluster_group_v13" {
  name   = "${var.prefix}-v2-cluster-parameter-group-v13"
  family = var.parameter_group_family_v13

  dynamic "parameter" {
    for_each = var.db_parameters
    content {
      apply_method = parameter.value["apply_method"]
      name         = parameter.value["name"]
      value        = parameter.value["value"]
    }
  }
}

# Creates Serverless V2 Cluster
resource "aws_rds_cluster" "example" {
  cluster_identifier              = "${var.prefix}-v2-cluster"
  engine                          = "aurora-postgresql"
  engine_mode                     = "provisioned"
  engine_version                  = var.engine_version
  database_name                   = var.database_name
  master_username                 = var.master_username
  master_password                 = var.master_password
  storage_encrypted               = true
  backup_retention_period         = var.backup_retention_period
  preferred_backup_window         = var.backup_window
  db_subnet_group_name            = aws_db_subnet_group.default.id
  apply_immediately               = var.apply_immediately
  vpc_security_group_ids          = [aws_security_group.rds_security_group.id]
  deletion_protection             = var.deletion_protection
  enable_http_endpoint            = true
  tags                            = var.tags
  skip_final_snapshot             = var.skip_final_snapshot
  final_snapshot_identifier       = "${var.prefix}-v2-cluster-final-snapshot-${local.timestamp_sanitized}"
  snapshot_identifier             = var.snapshot_identifier
  db_cluster_parameter_group_name = aws_rds_cluster_parameter_group.rds_cluster_group_v13.id
  enabled_cloudwatch_logs_exports = var.aurora_cloudwatch_logs
  serverlessv2_scaling_configuration {
    max_capacity = var.max_capacity
    min_capacity = var.min_capacity
  }
}

# Instance for the Serverless V2 Cluster
resource "aws_rds_cluster_instance" "example" {
  count              = 1
  identifier         = "${var.prefix}-v2-instance-${count.index}"
  cluster_identifier = aws_rds_cluster.example.id
  instance_class     = "db.serverless"
  engine             = aws_rds_cluster.example.engine
  engine_version     = aws_rds_cluster.example.engine_version
}

# Associates the S3 Import role with the serverless cluster
resource "aws_rds_cluster_role_association" "example" {
  db_cluster_identifier = aws_rds_cluster.example.id
  feature_name          = "s3Import"
  role_arn              = aws_iam_role.rds_s3_import_role.arn
}

# Assume role for the S3 Import role
data "aws_iam_policy_document" "assume_rds_role" {
  statement {
    principals {
      type        = "Service"
      identifiers = ["rds.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
    condition {
      test = "StringEquals"
      variable = "aws:SourceAccount"
      values = [
        "${data.aws_caller_identity.current.account_id}"
      ]
    }
  }
}

# Policy document for S3 import
data "aws_iam_policy_document" "rds_s3_import_role_policy_document" {
  statement {
    actions = [
      "s3:GetObject",
      "s3:ListBucket"
    ]
    resources = [
        "arn:aws:s3:::${var.orca_reports_bucket}",
        "arn:aws:s3:::${var.orca_reports_bucket}/*"
    ]
  }
}

# Role to be associated with the Serverless Cluster for S3 Import
resource "aws_iam_role" "rds_s3_import_role" {
  name                 = "${var.prefix}_rds_s3_import_role"
  assume_role_policy   = data.aws_iam_policy_document.assume_rds_role.json
  permissions_boundary = var.permissions_boundary_arn
  tags                 = var.tags
}

# Policy for the RDS S3 Import Role
resource "aws_iam_role_policy" "rds_s3_import_role_policy" {
  name   = "${var.prefix}_rds_s3_import_role_policy"
  role   = aws_iam_role.rds_s3_import_role.id
  policy = data.aws_iam_policy_document.rds_s3_import_role_policy_document.json
}

# Security Group for the Serverless database
resource "aws_security_group" "rds_security_group" {
  name        = "${var.prefix}_rds_security_group"
  description = "Allow TLS inbound traffic and all outbound traffic"
  vpc_id      = var.vpc_id

  tags = var.tags
}

# Allows for Postgres connections to the database. For now just using an EC2 for connections
resource "aws_vpc_security_group_ingress_rule" "allow_tls_ipv4" {
  security_group_id = aws_security_group.rds_security_group.id
  cidr_ipv4         = var.ec2_ip_address
  from_port         = 5432
  ip_protocol       = "tcp"
  to_port           = 5432
}

# Allows RDS to reach the ORCA S3 Reports bucket for S3 Import
resource "aws_vpc_security_group_egress_rule" "allow_all_traffic_ipv4" {
  security_group_id = aws_security_group.rds_security_group.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 443
  ip_protocol       = "tcp"
  to_port           = 443
}
