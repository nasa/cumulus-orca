# This would be the base of the whole thing for deploying ORCA
terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.32"
    }
    external = {
      source  = "hashicorp/external"
      version = ">= 2.3"
    }
    local = {
      source  = "hashicorp/local"
      version = ">= 2.4"
    }
    null = {
      source  = "hashicorp/null"
      version = ">= 3.2"
    }
  }
}