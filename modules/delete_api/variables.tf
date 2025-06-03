# REQUIRED
variable "prefix" {
  type        = string
  description = "Prefix used to prepend to all object names and tags."
}

variable "tags" {
  type        = map(string)
  description = "Tags to be applied to resources that support tags."
}

variable "vpc_id" {
  type        = string
  description = "Virtual Private Cloud AWS ID"
}

variable "api_gateway_stage_name" {
  type        = string
  description = "stage name for the ORCA cumulus reconciliation api gateway"
  default     = "orca_delete_api"
}

variable "vpc_endpoint_id" {
  type        = string
  description = "NGAP vpc endpoint id needed to access the api. Defaults to null."
}
