variable "ngap_subnet" {
  default = []
}

variable "ngap_sgs" {
  default = []
}

variable "lambda_processing_role" {
  default = ""
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