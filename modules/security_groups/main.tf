## Security Group Resources

## vpc_postgres_ingress_all_egress - PostgreSQL Security Group
## ==============================================================================
resource "aws_security_group" "vpc_postgres_ingress_all_egress" {
  ## OPTIONAL
  description = "ORCA security group to allow PostgreSQL access."
  name        = "${var.prefix}-vpc-ingress-all-egress"
  tags        = var.tags
  vpc_id      = var.vpc_id

  ingress {
    from_port = "5432"
    to_port   = "5432"
    protocol  = "TCP"
    self      = true
    description = "Allow PostgreSQL ingress for ${var.prefix} Orca lambdas."
  }

  ## This is added to allow all egress for Orca lambdas. See Terraform documentation
  ## for egress everything notes.
  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
    description = "Allow all egress for ${var.prefix} Orca lambdas."
  }

}

## rds_allow_lambda_access - PostgreSQL Security Group Rule
## ==============================================================================
resource "aws_security_group_rule" "rds_allow_lambda_access" {
  type                     = "ingress"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "TCP"
  description              = "Allows ${var.prefix} Orca lambda access."
  source_security_group_id = aws_security_group.vpc_postgres_ingress_all_egress.id
  security_group_id        = var.rds_security_group_id
}



resource "aws_security_group" "vpc_all_egress" {
  name        = "${var.prefix}-vpc-all-egress"
  description = "Allow all outbound traffic"
  tags        = var.tags
  vpc_id      = var.vpc_id
}

resource "aws_vpc_security_group_egress_rule" "allow_all_traffic_ipv4" {
  security_group_id = aws_security_group.vpc_all_egress.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1" 
}

resource "aws_vpc_security_group_egress_rule" "allow_all_traffic_ipv6" {
  security_group_id = aws_security_group.vpc_all_egress.id
  cidr_ipv6         = "::/0"
  ip_protocol       = "-1" 
}
