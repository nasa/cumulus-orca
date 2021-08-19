## Variables obtained by Cumulus deployment
## Should exist in https://github.com/nasa/cumulus-template-deploy/blob/master/cumulus-tf/variables.tf
## REQUIRED
variable "prefix" {
  type        = string
  description = "Prefix used to prepend to all object names and tags."
}


variable "vpc_id" {
  type        = string
  description = "Virtual Private Cloud AWS ID"
}


variable "tags" {
  type        = map(string)
  description = "Tags to be applied to resources that support tags."
}


## Variables unique to ORCA
## OPTIONAL - Default variable value is set in ../variables.tf to keep default values centralized.
variable "database_port" {
  type        = number
  description = "Database port that PostgreSQL traffic will be allowed on."
  default     = "5432"
}