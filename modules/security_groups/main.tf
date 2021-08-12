## Terraform Requirements
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 3.5.0"
    }
  }
}


## Local Variables
locals {
  tags = merge(var.tags, { Deployment = var.prefix })
}


## Security Group Resources

## vpc_postgres_ingress_all_egress - PostgreSQL security Group
## ==============================================================================
resource "aws_security_group" "vpc-postgres-ingress-all-egress" {
  ## OPTIONAL
  description = "ORCA security group to allow PostgreSQL access."
  name        = "${var.prefix}-vpc-ingress-all-egress"
  tags        = local.tags
  vpc_id      = var.vpc_id

  ingress {
    from_port = var.database_port
    to_port   = var.database_port
    protocol  = "TCP"
    self      = true
  }

  ## This is added to allow all egress for lambdas. See Terraform documentation
  ## for egress everything notes.
  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

}
