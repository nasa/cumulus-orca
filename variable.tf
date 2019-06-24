variable "glacier_bucket" {
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

variable "ngap_subnets" {
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
  default = 3
}

variable "restore_retry_sleep_secs" {
  default = 0
}

variable "copy_retries" {
  default = 3
}

variable "copy_retry_sleep_secs" {
  default = 0
}

variable "bucket_map" {
  default = "{\\\".hdf\\\": \\\"my-great-protected-bucket\\\", \\\".met\\\": \\\"my-great-protected-bucket\\\", \\\".txt\\\": \\\"my-great-public-bucket\\\", \\\"other\\\": \\\"my-great-protected-bucket\\\"}"
}