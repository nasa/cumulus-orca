output "ec2_instance_id" {
  value = aws_instance.web.id
  description = "EC2 Instance ID"
}