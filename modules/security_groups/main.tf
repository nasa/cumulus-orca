resource "aws_security_group" "vpc-postgres-ingress-all-egress" {
  name   = "${var.prefix}-vpc-ingress-all-egress"
  vpc_id = var.vpc_id

  ingress {
    from_port = var.egress_from_port
    to_port   = var.egress_to_port
    protocol  = "TCP"
    self      = true
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = var.tags
}