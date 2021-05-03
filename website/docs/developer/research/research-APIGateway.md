---
id: research-APIGateway
title: API Gateway Research Notes
description: Research Notes on API Gateway.
---

## Overview

[AWS API Gateways](https://aws.amazon.com/api-gateway/) are used to define access to a service.

### Implementation Details
- Requires several components in Terraform.
  - aws_api_gateway_rest_api
    ```
    resource "aws_api_gateway_rest_api" "[name]_api" {
      name = "[name]_api"
    }
    ```
  - aws_api_gateway_resource
    ```
    resource "aws_api_gateway_resource" "[name]_api_resource" {
      path_part   = "resource"
      parent_id   = aws_api_gateway_rest_api.[name]_api.root_resource_id
      rest_api_id = aws_api_gateway_rest_api.[name]_api.id
    }
    ```
  - aws_api_gateway_method
    ```
    resource "aws_api_gateway_method" "[name]_api_method" {
      rest_api_id   = aws_api_gateway_rest_api.[name]_api.id
      resource_id   = aws_api_gateway_resource.[name]_api_resource.id
      http_method   = "GET"
      # todo: Make sure this is locked down against external access.
      authorization = "NONE"
    }
    ```
  - aws_api_gateway_integration
    ```
    resource "aws_api_gateway_integration" "integration" {
      rest_api_id             = aws_api_gateway_rest_api.[name]_api.id
      resource_id             = aws_api_gateway_resource.[name]_api_resource.id
      http_method             = aws_api_gateway_method.[name]_api_method.http_method
      integration_http_method = "POST"
      type                    = "AWS_PROXY"
      uri                     = aws_lambda_function.[name].invoke_arn
    }
    ```
  - aws_lambda_permission
    ```
    resource "aws_lambda_permission" "[name]_api_permission" {
      statement_id  = "AllowExecutionFromAPIGateway"
      action        = "lambda:InvokeFunction"
      function_name = aws_lambda_function.lambda.function_name  # todo: Pass this in
      # todo: Could make this the accountID. https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_permission
      principal     = "apigateway.amazonaws.com"
    
      # More: http://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-control-access-using-iam-policies-to-invoke-api.html
      source_arn = "arn:aws:execute-api:${var.region}:${var.accountId}:${aws_api_gateway_rest_api.[name]_api.id}/*/$    {aws_api_gateway_method.[name]_api_method.http_method}${aws_api_gateway_resource.[name]_api_resource.path}"
    }
    ```  
- Proper HTTP error codes can be returned from a Lambda to the gateway via a dictionary, as shown in [Handle Lambda errors in API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/handle-errors-in-lambda-integration.html)
  - For more potential patterns, see https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-integration-settings-integration-response.html and https://aws.amazon.com/blogs/compute/error-handling-patterns-in-amazon-api-gateway-and-aws-lambda/

### Future Direction
- None of this code has been successfully deployed, and needs to be tested before usage.
- Research/testing on error handling and codes is limited.
- Examples show 'source_arn' as a rather complex value. Test if it can be evaluated as aws_api_gateway_resource.[name].arn

#### Sources
- [Terraform aws_api_gateway_integration](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/api_gateway_integration)
- [Terraform aws_lambda_permission](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_permission)
- [Handle Lambda errors in API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/handle-errors-in-lambda-integration.html)
- [Handling Errors in API Gateway](https://docs.aws.amazon.com/apigateway/api-reference/handling-errors/)