variable "prefix" {
    type = string
    description = "Prefix used for naming to manage multiple instances in a single VPC"
}

variable "tags" {
    type        = map(string)
    description = "Tags to be applied to resources that support tags."
    default     = {} 
}

variable "log_level" {
    type = string
    description = "Log level of application"
    default = "DEBUG"
}

variable "log_group" {
    type = string
    description = "arn of the log group to use"
}

variable "subnet_ids" {}

variable "vpc_id" {}
