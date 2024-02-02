# This could probably be created once for the entire project 
# to use as a common resource
resource "aws_cloudwatch_log_group" "orca" {
  name = "${var.prefix}-ORCA"
  skip_destroy = false #Possibly set to true for dev work
  log_group_class = "STANDARD" #Possibly set to INFREQUENT_ACCESS for prod
  retention_in_days = 30 # Keep 30 days, possibly make this variable
  # kms_key_id = Kms Key ARN -> set this in production and dev/test just not setting it here for demo

  tags = var.tags 
}

# API GW this copuuld probably be common
resource "aws_api_gateway_rest_api" "orca" {
  name                     = "${var.prefix}-ORCA"
  description              = "API for ORCA test Lambda."
  tags = var.tags
}

data "aws_iam_policy_document" "orca_api_gw" {
  statement {
    effect = "Allow"

    principals {
      type        = "AWS"
      identifiers = ["*"]
    }

    actions   = ["execute-api:Invoke"]
    resources = [aws_api_gateway_rest_api.orca.execution_arn]
  }

}

resource "aws_api_gateway_rest_api_policy" "orca" {
  rest_api_id = aws_api_gateway_rest_api.orca.id
  policy = data.aws_iam_policy_document.orca_api_gw.json
}

resource "aws_api_gateway_resource" "v1" {
  rest_api_id = aws_api_gateway_rest_api.orca.id
  parent_id = aws_api_gateway_rest_api.orca.root_resource_id
  path_part = "ingest"
}

resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = aws_api_gateway_rest_api.orca.id
  parent_id   = aws_api_gateway_resource.v1.id
  path_part   = "{proxy+}"
}

### Need to figure out how to put this closer to lambda
resource "aws_api_gateway_integration" "proxy" { 
  rest_api_id             = aws_api_gateway_rest_api.orca.id
  resource_id             = aws_api_gateway_resource.v1.id
  http_method             = "ANY"
  type                    = "AWS_PROXY"
  integration_http_method = "POST"
  uri                     = var.simple_input_invoke_arn
}

resource "aws_api_gateway_method" "proxy" {
  rest_api_id             = aws_api_gateway_rest_api.orca.id
  resource_id             = aws_api_gateway_resource.v1.id
  http_method      = "ANY" 
  authorization    = "NONE"
  api_key_required = false
  request_parameters = {
    "method.request.path.proxy" = true
  }
}

resource "aws_lambda_permission" "simle_input" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = var.simple_input_function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.orca.execution_arn}/*/*"
}

resource "aws_api_gateway_deployment" "orca" {
  rest_api_id = aws_api_gateway_rest_api.orca.id
  lifecycle {
    create_before_destroy = true
  }
  depends_on = [ aws_api_gateway_integration.proxy ]
}

resource "aws_api_gateway_stage" "orca" {
  deployment_id = aws_api_gateway_deployment.orca.id
  rest_api_id   = aws_api_gateway_rest_api.orca.id
  stage_name    = "orca"
  tags = var.tags
}