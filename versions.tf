## Terraform Requirements
terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0.0, <=5.81.0"
    }
  }
}