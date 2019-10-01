# https://blog.faraday.io/how-to-create-an-rds-instance-with-terraform/ 
resource "aws_db_instance" "postgresql" {
  allocated_storage          = 20
  max_allocated_storage      = 21
  engine                     = "postgres"
  engine_version             = "11.4"
  identifier                 = "postgres-sndbx-r"
  instance_class             = "db.t2.micro"
  name                       = "postgres"
  password                   = "${var.postgres_user_pw}"
  username                   = "postgres"
  iam_database_authentication_enabled = "true"
  # disable backups to create DB faster
  backup_retention_period = 0
  #backup_retention_period    = 7
  backup_window              = "03:00-06:00"
  maintenance_window         = "Mon:00:00-Mon:03:00"
  #auto_minor_version_upgrade = "${var.auto_minor_version_upgrade}"
  port                       = "${var.database_port}"
  vpc_security_group_ids     = "${var.ngap_sgs}"
  db_subnet_group_name       = "${var.ngap_subnet_group}"
  parameter_group_name = "default.postgres11"
  storage_encrypted          = false
  deletion_protection        = false
  skip_final_snapshot        = true
  final_snapshot_identifier  = "daacx"
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
}
