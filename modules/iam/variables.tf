variable "prefix" {}
variable "permissions_boundary_arn" {}
variable "buckets" {
  type    = map(object({ name = string, type = string }))
  default = {}
}