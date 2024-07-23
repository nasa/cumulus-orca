# Local Variables
locals {
  region          = data.aws_region.current_region.name
  # vpc_endpoint_id = var.vpc_endpoint_id != null ? var.vpc_endpoint_id : data.aws_vpc_endpoint.vpc_endpoint_id.id
}

data "aws_region" "current_region" {}

# TODO: Work with NGAP to create VPC endpoint ID
# for api gateway in DR account ORCA-892
# data "aws_vpc_endpoint" "vpc_endpoint_id" {
#   vpc_id       = var.vpc_id
#   service_name = "com.amazonaws.${local.region}.execute-api"
# }

# API Gateway- API for ORCA cumulus reconciliation
resource "aws_api_gateway_rest_api" "orca_api" {
  name        = "${var.prefix}_orca_api"
  description = "API for internal reconciliation, catalog reporting, request_status_for_job and request_status_for_file lambda functions"
  endpoint_configuration {
    types            = ["PRIVATE"]
    # vpc_endpoint_ids = [local.vpc_endpoint_id]
  }
  tags = var.tags
}
data "aws_iam_policy_document" "orca_api_policy" {
  statement {
    resources = ["*"]
    actions   = ["execute-api:Invoke"]
    effect = "Allow"

    principals {
      type        = "*"
      identifiers = ["*"]
    }

  }
}

resource "aws_api_gateway_rest_api_policy" "orca_api_policy" {
  rest_api_id = aws_api_gateway_rest_api.orca_api.id
  policy      = data.aws_iam_policy_document.orca_api_policy.json
}

##Note: Resources specific to certain lambda functions have not been created. See modules/api-gateway/main.tf.