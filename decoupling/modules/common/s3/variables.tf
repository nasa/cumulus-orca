variable "prefix" {
  type        = string
  description = "Prefix used to prepend to all object names and tags."
}

variable "tags" {
  type        = map(string)
  description = "Tags to be applied to resources that support tags."
  default     = {}
}

variable "cumulus_account_id" {
  type = number
  description = "Account ID of the Cumulus Account"
}