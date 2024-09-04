variable "permissions_boundary_arn" {
  type        = string
  description = "AWS ARN value for the permission boundary."
}

variable "prefix" {
  type        = string
  description = "Prefix used to prepend to all object names and tags."
}

variable "tags" {
  type        = map(string)
  description = "Tags to be applied to resources that support tags."
  default = null
}

variable "orca_reports_bucket" {
  type        = string
  description = "The name of the bucket to store s3 inventory reports."
}

variable "engine_version" {
    type = string
    description = "Version of postgres to be used for the database."
    default = "13.12"
}

variable "database_name" {
    type = string
    description = "Name of the database to be created."
}

variable "master_username" {
    type = string
    description = "Master username for the database"
}

variable "master_password" {
    type = string 
    description = "Password for the master username"
}

variable "max_capacity" {
    type = number
    description = "Max number of ACUs for the database to have the ability to scale up to."
}

variable "min_capacity" {
    type = number
    description = "Minimum number of ACUs for the database to scale down to/idle at."
}

variable "vpc_id" {
  type = string
  description = "ID value of the VPC"
}

variable "ec2_ip_address" {
    type = string
    description = "IP address for EC2 connections to the database. (This is for prototyping this will be lambdas iin the future.)"
}

variable "apply_immediately" {
  description = "If true, RDS will apply updates to cluster immediately, instead of in the maintenance window"
  type        = bool
  default     = true
}

variable "skip_final_snapshot" {
  description = "If true, a final snapshot will not be created when deleting the cluster."
  type        = bool
  default     = true
}

variable "backup_retention_period" {
  description = "Number of backup periods to retain"
  type        = number
  default     = 1
}

variable "backup_window" {
  description = "Preferred database backup window (UTC)"
  type        = string
  default     = "07:00-09:00"
}

variable "deletion_protection" {
  description = "Flag to prevent terraform from making changes that delete the database in CI"
  type        = bool
  default     = false
}

variable "snapshot_identifier" {
  description = "Snapshot identifer for restore"
  default     = null
}

variable "subnets" {
  description = "Subnets for database cluster.  Requires at least 2 across multiple AZs"
  type    = list(string)
}

variable "parameter_group_family_v13" {
  description = "Database family to use for creating database parameter group under postgres 13 upgrade conditions"
  type = string
  default = "aurora-postgresql13"
}

variable "db_parameters" {
  type = list(object({
    name = string,
    value = string,
    apply_method = string
  }))
  description = "Database parameters to apply"
  default = [
    {
      name         = "shared_preload_libraries"
      value        = "pg_stat_statements,auto_explain"
      apply_method = "pending-reboot"
    },
    {
      name         = "rds.force_ssl"
      value        = 1
      apply_method = "pending-reboot"
    }
  ]
}

variable "aurora_cloudwatch_logs" {
  description = "Type of logs to export to CloudWatch"
  type = list(string)
  default = [ "postgresql" ]
  
}
