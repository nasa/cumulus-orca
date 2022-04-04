## Terraform Requirements
terraform {
  required_version = ">= 0.13"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      # todo: Update to at least 4.0. Will require updates to several resources.
      version = ">= 3.63.0"
    }
  }
}