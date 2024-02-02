# Getting environment information
data "aws_caller_identity" "current_account" {}
data "aws_region" "current_region" {}
data "aws_vpc" "current" {}
data "aws_subnets" "current_account" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.current.id]
  }
  filter {
    name = "tag:Name"
    values = ["Private application*"]
  }
}
data "aws_subnet" "current_account" {
  for_each = toset(data.aws_subnets.current_account.ids)
  id       = each.value
}


# Setup locals. These would be at the top level
# not normally here
locals {
  tags       = merge({ Deployment = var.prefix }, { team = "ORCA", application = "ORCA" })
  account_id = data.aws_caller_identity.current_account.account_id
  region     = data.aws_region.current_region.name
  subnet_ids = [for subnet in data.aws_subnet.current_account : subnet.id]
}

module "common" {
    source = "./common"
    prefix = var.prefix
    simple_input_function_name = module.simple_input.simple_input_function_name
    simple_input_invoke_arn = module.simple_input.simple_input_invoke_arn
}


module "simple_input" {
    source = "./simple_input"
    prefix = var.prefix
    log_group = "ORCA/ingest"
    log_level = "DEBUG"
    subnet_ids = local.subnet_ids
    vpc_id = data.aws_vpc.current.id
}