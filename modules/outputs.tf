
output "orca_rds_address" {
  description = "The address of the RDS instance"
  value       = module.orca.orca_rds.address
}

//output "orca_rds_arn" {
//  description = "The ARN of the RDS instance"
//  value       = module.orca.orca_rds.arn
//}

output "orca_rds_arn" {
  description = "The ARN of the RDS instance"
  value       = module.orca.orca_rds.arn
}


//output "orca_rds_availability_zone" {
//  description = "The availability zone of the RDS instance"
//  value       = module.orca.orca_rds.availability_zone
//}

output "orca_rds_availability_zone" {
  description = "The availability zone of the RDS instance"
  value       = module.orca.orca_rds.availability_zone
}

//output "orca_rds_endpoint" {
//  description = "The connection endpoint in address:port format"
//  value       = module.orca.orca_rds.endpoint
//}

output "orca_rds_endpoint" {
  description = "The connection endpoint in address:port format"
  value       = module.orca.orca_rds.endpoint
}


//output "orca_rds_hosted_zone_id" {
//  description = "The canonical hosted zone ID of the DB instance (to be used in a Route 53 Alias record)"
//  value       = module.orca.orca_rds.hosted_zone_id
//}

output "orca_rds_hosted_zone_id" {
  description = "The canonical hosted zone ID of the DB instance (to be used in a Route 53 Alias record)"
  value       = module.orca.orca_rds.hosted_zone_id
}

output "orca_rds_id" {
  description = "The RDS instance ID"
  value       = module.orca.orca_rds.id
}

output "orca_rds_resource_id" {
  description = "The RDS Resource ID of this instance"
  value       = module.orca.orca_rds.resource_id
}

output "orca_rds_status" {
  description = "The RDS instance status"
  value       = module.orca.orca_rds.status
}

output "orca_rds_name" {
  description = "The database name"
  value       = module.orca.orca_rds.name
}

output "orca_rds_username" {
  description = "The master username for the database"
  value       = module.orca.orca_rds.username
}

# output "orca_rds_password" {
#   description = "The database password (this password may be old, because Terraform doesn't track it after initial creation)"
#   value       = module.orca.orca_rds.password
# }

output "orca_rds_port" {
  description = "The database port"
  value       = module.orca.orca_rds.port
}

output "this_db_subnet_group_id" {
  description = "The db subnet group name"
  value       = module.orca.orca_subnet_group.id
}

output "this_db_subnet_group_arn" {
  description = "The ARN of the db subnet group"
  value       = module.orca.orca_subnet_group.arn
}

output "extract_filepaths_lambda_arn" {
  description = "ARN identifying extract_filepaths lambda"
  value       = module.orca.orca_lambda_extract_filepath_arn
}

output "request_files_lambda_arn" {
  description = "ARN identifying request_files lambda"
  value       = module.orca.orca_lambda_request_files_arn
}

output "copy_to_glacier_lambda_arn" {
  description = "ARN identifying copy_to_glacier lambda"
  value       = module.orca.orca_lambda_copy_to_glacier_arn
}

# Can re-enable if we want. Don't have this information if we're using the default.
# output "this_db_parameter_group_id" {
#   description = "The db parameter group id"
#   value       = "${module.db.this_db_parameter_group_id}"
# }

# output "this_db_parameter_group_arn" {
#   description = "The ARN of the db parameter group"
#   value       = "${module.db.this_db_parameter_group_arn}"
# }
