## REQUIRED
variable "buckets" {
  type        = map(object({ name = string, type = string }))
  description = "S3 bucket locations for all previously existing buckets."
}

variable "prefix" {
  type        = string
  description = "Prefix used to prepend to all object names and tags."
}

## OPTIONAL
variable "tags" {
  type        = map(string)
  description = "Tags to be applied to resources that support tags."
}