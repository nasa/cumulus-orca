# REQUIRED
variable "prefix" {
  type        = string
  description = "Prefix used to prepend to all object names and tags."
  default = "decoupling-test"
}

variable "tags" {
  type        = map(string)
  description = "Tags to be applied to resources that support tags."
  default     = {}
}

variable "vpc_id" {
  type        = string
  description = "Virtual Private Cloud AWS ID in DR account"
  default = "vpc-0c692af4affe8b7cd"
}

# variable "vpc_endpoint_id" {
#   type        = string
#   description = "NGAP vpc endpoint id needed to access the api. Defaults to null."
# }
