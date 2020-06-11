resource "aws_db_subnet_group" "postgres_subnet_group" {
  name       = "${var.prefix}-postgres-subnet-group"
  subnet_ids = var.ngap_subnets
}

# Ignore aws profile in case this was deployed with CI or
# in a machine without aws profile defined
locals {
  used_profile = contains([var.profile], "default") ? "" : "--profile ${var.profile}"
}
# https://blog.faraday.io/how-to-create-an-rds-instance-with-terraform/ 
resource "aws_db_instance" "postgresql" {
  # set apply_immediately true just for testing
  apply_immediately = false
  allocated_storage          = 20
  # max_allocated_storage      = 21
  engine                     = "postgres"
  engine_version             = "11.4"
  identifier                 = "${var.prefix}-postgres-sndbx"
  instance_class             = "db.t2.micro"
  name                       = "postgres"
  password                   = var.postgres_user_pw
  username                   = "postgres"
  iam_database_authentication_enabled = "true"
  backup_retention_period    = 7
  backup_window              = "03:00-06:00"
  maintenance_window         = "Mon:00:00-Mon:03:00"
  #auto_minor_version_upgrade = "${var.auto_minor_version_upgrade}"
  port                       = var.database_port
  vpc_security_group_ids     = [aws_security_group.vpc-postgres-ingress-all-egress.id]
  db_subnet_group_name       = aws_db_subnet_group.postgres_subnet_group.id
  # parameter_group_name       = "default.postgres11"
  storage_encrypted          = false
  deletion_protection        = false
  skip_final_snapshot        = true
  final_snapshot_identifier  = "daacx"
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
}

resource "null_resource" "bootstrap" {
  triggers = {
    bootstrap_lambda_hash = aws_lambda_function.db_deploy.source_code_hash
  }

  provisioner "local-exec" {
    command = "aws lambda invoke --function-name ${aws_lambda_function.db_deploy.arn} ${local.used_profile} --region ${var.region} 'invoke-response.out'"
  }

  depends_on = [aws_db_instance.postgresql]
}

resource "aws_ssm_parameter" "drdb-admin-pass" {
  name  = "drdb-admin-pass"
  type  = "SecureString"
  value = "${var.postgres_user_pw}"
  tags = var.default_tags
}

resource "aws_ssm_parameter" "drdb-user-pass" {
  name  = "drdb-user-pass"
  type  = "SecureString"
  value = "${var.database_app_user_pw}"
  tags = var.default_tags
}

resource "aws_ssm_parameter" "drdb-host" {
  name  = "drdb-host"
  type  = "String"
  value = "${aws_db_instance.postgresql.address}"
  tags = var.default_tags
}
