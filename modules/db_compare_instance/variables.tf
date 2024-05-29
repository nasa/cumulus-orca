variable "prefix" {
    type = string
    description = "Prefix used to prepend to all object names and tags."
}

variable "permissions_boundary_arn" {
  type        = string
  description = "AWS ARN value for the permission boundary."
}

variable "subnet_id" {
    type = string
    description = "Subnet ID where to deploy the EC2"
}

variable "vpc_id" {
  type        = string
  description = "Virtual Private Cloud AWS ID"
}

variable "v1_security_group_id" {
  type        = string
  description = "Cumulus' V1 RDS Security Group's ID."
}

variable "v2_security_group_id" {
  type        = string
  description = "Cumulus' V2 RDS Security Group's ID."
}