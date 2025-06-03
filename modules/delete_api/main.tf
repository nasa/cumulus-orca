# Local Variables
locals {
  region          = data.aws_region.current_region.name
  vpc_endpoint_id = var.vpc_endpoint_id != null ? var.vpc_endpoint_id : data.aws_vpc_endpoint.vpc_endpoint_id.id
}

data "aws_region" "current_region" {}

data "aws_vpc_endpoint" "vpc_endpoint_id" {
  vpc_id       = var.vpc_id
  service_name = "com.amazonaws.${local.region}.execute-api"
}

# API Gateway- API for ORCA Delete Functionality
resource "aws_api_gateway_rest_api" "orca_delete_api" {
  name        = "${var.prefix}_orca_delete_api"
  description = "API for hard and soft delete lambda functions"
  endpoint_configuration {
    types            = ["PRIVATE"]
    vpc_endpoint_ids = [local.vpc_endpoint_id]
  }
  tags = var.tags
}

data "aws_iam_policy_document" "orca_delete_api_policy" {
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

resource "aws_api_gateway_rest_api_policy" "orca_delete_api_policy" {
  rest_api_id = aws_api_gateway_rest_api.orca_delete_api.id
  policy      = data.aws_iam_policy_document.orca_delete_api_policy.json
}

resource "aws_api_gateway_resource" "orca_soft_delete_api_resource" {
  path_part   = "catalog"
  parent_id   = aws_api_gateway_rest_api.orca_delete_api.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.orca_delete_api.id
}

resource "aws_api_gateway_method" "orca_soft_delete_api_method" {
  rest_api_id   = aws_api_gateway_rest_api.orca_delete_api.id
  resource_id   = aws_api_gateway_resource.orca_soft_delete_api_resource.id
  http_method   = "POST"
  authorization = "NONE"
  api_key_required = false
}

resource "aws_api_gateway_integration" "orca_soft_delete_api_integration" {
  rest_api_id             = aws_api_gateway_rest_api.orca_delete_api.id
  resource_id             = aws_api_gateway_resource.orca_soft_delete_api_resource.id
  http_method             = aws_api_gateway_method.orca_soft_delete_api_method.http_method
  integration_http_method = "POST"
  type                    = "AWS"
  uri                     = <PLACE_HOLDER_FOR_SOFT_DELETE_LAMBDA>
}

resource "aws_api_gateway_method_response" "orca_soft_delete_response_200" {
  rest_api_id = aws_api_gateway_rest_api.orca_delete_api.id
  resource_id = aws_api_gateway_resource.orca_soft_delete_api_resource.id
  http_method = aws_api_gateway_method.orca_soft_delete_api_method.http_method
  status_code = "200"
}

resource "aws_lambda_permission" "orca_soft_delete_api_permission" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = "<PLACE_HOLDER_FOR_SOFT_DELETE_LAMBDA>"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.orca_delete_api.execution_arn}/*/${aws_api_gateway_method.orca_soft_delete_api_method.http_method}${aws_api_gateway_resource.orca_soft_delete_api_resource.path}"
}

resource "aws_api_gateway_resource" "orca_hard_delete_api_resource" {
  path_part   = "harddelete"
  parent_id   = aws_api_gateway_rest_api.orca_delete_api.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.orca_delete_api.id
}

resource "aws_api_gateway_method" "orca_hard_delete_api_method" {
  rest_api_id   = aws_api_gateway_rest_api.orca_delete_api.id
  resource_id   = aws_api_gateway_resource.orca_hard_delete_api_resource.id
  http_method   = "POST"
  authorization = "NONE"
  api_key_required = false
}

resource "aws_api_gateway_integration" "orca_hard_delete_api_integration" {
  rest_api_id             = aws_api_gateway_rest_api.orca_delete_api.id
  resource_id             = aws_api_gateway_resource.orca_hard_delete_api_resource.id
  http_method             = aws_api_gateway_method.orca_hard_delete_api_method.http_method
  integration_http_method = "POST"
  type                    = "AWS"
  uri                     = <PLACE_HOLDER_FOR_HARD_DELETE_LAMBDA>
}

resource "aws_api_gateway_method_response" "orca_hard_delete_response_200" {
  rest_api_id = aws_api_gateway_rest_api.orca_delete_api.id
  resource_id = aws_api_gateway_resource.orca_hard_delete_api_resource.id
  http_method = aws_api_gateway_method.orca_hard_delete_api_method.http_method
  status_code = "200"
}

resource "aws_lambda_permission" "orca_hard_delete_api_permission" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = "<PLACE_HOLDER_FOR_HARD_DELETE_LAMBDA>"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.orca_delete_api.execution_arn}/*/${aws_api_gateway_method.orca_hard_delete_api_method.http_method}${aws_api_gateway_resource.orca_hard_delete_api_resource.path}"
}

#deployment for the API
resource "aws_api_gateway_deployment" "orca_delete_api_deployment" {
  rest_api_id = aws_api_gateway_rest_api.orca_delete_api.id
  depends_on = [
    aws_api_gateway_integration.orca_soft_delete_api_integration,
    aws_api_gateway_integration.orca_hard_delete_api_integration
  ]
}
resource "aws_api_gateway_stage" "orca_delete_api_stage_name" {
  deployment_id = aws_api_gateway_deployment.orca_delete_api_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.orca_delete_api.id
  stage_name    = var.api_gateway_stage_name
}






