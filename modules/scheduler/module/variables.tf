variable "aws_account_id" {
    type = string
}

variable "aws_region" {
    type = string
    default = "us-west-2"
}

variable "create_office_hours" {
    default = false
}

variable "create_office_hours_8_6" {
    default = false
}

variable "create_office_hours_autoscaling" {
    default = false
}

variable "create_office_hours_8_6_autoscaling" {
    default = false
}

variable "role_permissions_boundary_arn" {
  description = "CSR developer permissions boundary"
  type = string
}

variable "tags" {
  description = "Default tags to be applied."
  type = map(string)
}
