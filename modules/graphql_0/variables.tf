## Variables obtained by Cumulus deployment
## Should exist in https://github.com/nasa/cumulus-template-deploy/blob/master/cumulus-tf/variables.tf
## REQUIRED
variable "permissions_boundary_arn" {
  type        = string
  description = "AWS ARN value for the permission boundary."
}

variable "prefix" {
  type        = string
  description = "Prefix used to prepend to all object names and tags."
}

variable "vpc_id" {
  type        = string
  description = "Virtual Private Cloud AWS ID"
}

## OPTIONAL
variable "tags" {
  type        = map(string)
  description = "Tags to be applied to resources that support tags."
}

variable "db_cluster_identifier" {
  type = string
  description = "DB Cluster Identifier (Cluster Name) to associate with the IAM Role"
}

## OPTIONAL
variable "deploy_rds_cluster_role_association" {
  type        = bool
  description = "Deploys IAM role for Aurora v2 cluster if true."
}

variable "buckets" {
  type        = map(object({ name = string, type = string }))
  description = "S3 bucket locations for the various storage types being used."
}

## Variables unique to ORCA
## REQUIRED
variable "orca_reports_bucket_name" {
  type        = string
  description = "The name of the bucket to store s3 inventory reports."
}


## OPTIONAL - Default variable value is set in ../variables.tf to keep default values centralized.
variable "orca_recovery_buckets" {
  type        = list(string)
  description = "List of bucket names that ORCA has permissions to restore data to."
}