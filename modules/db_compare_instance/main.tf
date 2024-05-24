# Create the key pair
resource "tls_private_key" "rsa" {
  algorithm = "RSA"
  rsa_bits  = 4096
}
 
resource "aws_key_pair" "user" {
    key_name_prefix = "${var.prefix}-comparison-key"
    public_key = tls_private_key.rsa.public_key_openssh
}
 
resource "local_sensitive_file" "private_key" {
    content = tls_private_key.rsa.private_key_pem
    filename = "${aws_key_pair.user.key_name}.pem"
    file_permission = "0400"
}
 
# Grabs comparison script
data "template_file" "script" {
  template = "${file("${path.module}/scripts/db_compare.sh")}"
}

# Grabs config script
data "template_file" "config" {
  template = "${file("${path.module}/scripts/db_config.sh")}"
}
 
# Grabs psql install script
data "template_file" "install" {
  template = "${file("${path.module}/scripts/psql.sh")}"
}
 
# Cloud init for the scripts to be put on the instance
data "cloudinit_config" "config" {
  gzip          = false
  base64_encode = false
 
  part {
    filename     = "db_compare.sh"
    content_type = "text/x-shellscript"
    content      = "${data.template_file.script.rendered}"
  }

  part {
    filename     = "db_config.sh"
    content_type = "text/x-shellscript"
    content      = "${data.template_file.config.rendered}"
  }
 
  part {
    filename     = "psql.sh"
    content_type = "text/x-shellscript"
    content      = "${data.template_file.install.rendered}"
  }
 
}
 
# Role for the instance
resource "aws_iam_instance_profile" "test_profile" {
  name = "${var.prefix}_comparison_profile"
  role = aws_iam_role.role.name
}
 
data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"
 
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
 
    actions = ["sts:AssumeRole"]
  }
}
 
resource "aws_iam_role" "role" {
  name               = "PREFIX_compare_role"
  path               = "/"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
  permissions_boundary = var.permissions_boundary_arn
}
 
# Attach SSM policy to EC2 role for SSM access
resource "aws_iam_role_policy_attachment" "test-attach" {
  role       = aws_iam_role.role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}
 
# AMI for the instance to use
data "aws_ami" "ami" {
  most_recent = true
 
  filter {
    name   = "name"
    values = ["edc-app-base-*-amzn-linux2-x86_64"]
  }
  owners = ["863143145967"]
}
 
resource "aws_instance" "web" {
  ami                  = data.aws_ami.ami.id
  instance_type        = "t3.medium"
  key_name             = aws_key_pair.user.id
  iam_instance_profile = aws_iam_instance_profile.test_profile.name
  security_groups      = [aws_security_group.rds_security_group.id]
  subnet_id            = var.subnet_id
  root_block_device {
    volume_size = "10"
  }
  user_data = "${data.cloudinit_config.config.rendered}"
  tags = {
    Name = "${var.prefix}-comparison-instance"
  }
}
 
resource "aws_security_group" "rds_security_group" {
  name        = "${var.prefix}-compare-group"
  description = "Allow Postgres inbound traffic"
  vpc_id      = var.vpc_id
 
}
 
resource "aws_vpc_security_group_ingress_rule" "allow_postgres_v1" {
  security_group_id = aws_security_group.rds_security_group.id
  referenced_security_group_id = var.v1_security_group_id
  from_port         = 5432
  ip_protocol       = "tcp"
  to_port           = 5432
}
 
resource "aws_vpc_security_group_ingress_rule" "allow_postgres_v2" {
  security_group_id = aws_security_group.rds_security_group.id
  referenced_security_group_id = var.v2_security_group_id
  from_port         = 5432
  ip_protocol       = "tcp"
  to_port           = 5432
}
 
resource "aws_vpc_security_group_egress_rule" "allow_all_traffic_ipv4" {
  security_group_id = aws_security_group.rds_security_group.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}