variable "egress_from_port" {
  type    = number
  default = 5432
}
variable "egress_to_port" {
  type    = number
  default = 5432
}
variable "vpc_id" {
  type = string
}

variable "prefix" {
  type    = string
  default = "orca"
}

variable "tags" {}