variable "archive_bucket" {
  default = ""
}

variable "private_bucket" {
  default = ""
}

variable "protected_bucket" {
  default = ""
}

variable "internal_bucket" {
  default = ""
}

variable "public_bucket" {
  default = ""
}

variable "permissions_boundary_arn" {
  default = ""
}

variable "ngap_subnet" {
  default = []
}

variable "ngap_sgs" {
  default = []
}

variable "profile" {
  default = "default"
}

variable "region" {
  default = "us-west-2"
}

variable "restore_expire_days" {
  default = 5
}

variable "restore_request_retries" {
  default = 2
}