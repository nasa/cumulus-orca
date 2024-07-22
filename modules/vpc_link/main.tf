terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 3.63.0, < 4.0.0"
    }
  }
}
# Configure the AWS Provider
provider "aws" {
  region = "us-west-2"
}

#create VPC link in DR account
resource "awscc_apigatewayv2_vpc_link" "orca-vpc-link" {
  name               = "rhassan-vpc-link-demo"
  subnet_ids         = ["subnet-03141fdc343bb715d"]
  # security_group_ids = [var.securit_group_id]
  tags = {
    key   = "Team"
    value = "ORCA"
  }
}

# TODO
# Create network laod balancer for contacting with VPC link ORCA-889
# Modify/change ORCA API gateway configuration to synk with VPC link ORCA-891
# }
