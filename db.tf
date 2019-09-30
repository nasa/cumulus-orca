##############################################################
# Data sources to get VPC, subnets and security group details
##############################################################
#data "aws_vpc" "default" {
#  default = true
#}

#data "aws_subnet_ids" "all" {
#  vpc_id = data.aws_vpc.default.id
#}

#data "aws_security_group" "default" {
#  vpc_id = data.aws_vpc.default.id
#  name   = "default"
#}

#####
# DB
#####
module "db" {
  source = "../terraform-aws-rds-dr"

  identifier = "postgres-sndbx"

  engine            = "postgres"
  engine_version    = "11.4"
  instance_class    = "db.t2.micro"
  allocated_storage = 20
  max_allocated_storage = 21
  storage_encrypted = false

  # kms_key_id        = "arm:aws:kms:<region>:<account id>:key/<kms key id>"
  name = "postgres"

  # NOTE: Do NOT use 'user' as the value for 'username' as it throws:
  # "Error creating DB Instance: InvalidParameterValue: MasterUsername
  # user cannot be used as it is a reserved word used by the engine"
  username = "postgres"

  password = "${var.postgres_user_pw}"
  port     = "${var.database_port}"

  vpc_security_group_ids = "${var.ngap_sgs}"

  maintenance_window = "Mon:00:00-Mon:03:00"
  backup_window      = "03:00-06:00"

  # disable backups to create DB faster
  backup_retention_period = 0
  iam_database_authentication_enabled = "true"
  tags = {
    Owner       = "dr"
    Environment = "sandbox"
  }

  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]

  # DB subnet group
  #db_subnet_group_name = "${var.ngap_subnet_group}"
  subnet_ids = "${var.ngap_subnets}"

  db_subnet_group_name = "default-vpc-3a0f3643"
  parameter_group_name = "default.postgres11"
  # DB parameter group
  family = "postgres11"

  # DB option group
  major_engine_version = "11.4"

  # Snapshot name upon DB deletion
  final_snapshot_identifier = "daac"

  # Database Deletion Protection
  deletion_protection = false
}
