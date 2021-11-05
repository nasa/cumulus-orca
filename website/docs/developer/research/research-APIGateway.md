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
      name = "${var.prefix}_[name]_api"
      }
    ```
  - aws_api_gateway_resource
    ```
    resource "aws_api_gateway_resource" "[name]_api_resource" {
      path_part   = "{proxy+}" # This acts as a "catch all"
      parent_id   = aws_api_gateway_rest_api.[name]_api.root_resource_id
      rest_api_id = aws_api_gateway_rest_api.[name]_api.id
      }
    ```
  - aws_api_gateway_method
    ```
    resource "aws_api_gateway_method" "[name]_api_method" {
      rest_api_id   = aws_api_gateway_rest_api.[name]_api.id
      resource_id   = aws_api_gateway_resource.[name]_api_resource.id
      http_method = "ANY"
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
      type                    = "AWS"
      uri                     = aws_lambda_function.[name].invoke_arn
      }
    ```
  - aws_api_gateway_method_response
    ```
    resource "aws_api_gateway_method_response" "[name]_response_200" {
      rest_api_id = aws_api_gateway_rest_api.[name]_api.id
      resource_id = aws_api_gateway_resource.[name]_api_resource.id
      http_method = aws_api_gateway_method.[name]_api_method.http_method
      status_code = "200"
      }
    ```
  - aws_api_gateway_integration_response
    ```
    resource "aws_api_gateway_integration_response" "[name]_api_response" {
    depends_on = [aws_api_gateway_integration.[name]_api_integration]
    rest_api_id = aws_api_gateway_rest_api.[name]_api.id
    resource_id = aws_api_gateway_resource.[name]_api_resource.id
    http_method = aws_api_gateway_method.[name]_api_method.http_method
    status_code = aws_api_gateway_method_response.[name]_response_200.status_code
  
    # Transforms the backend JSON response to XML
    # "stackTrace" being present in the returned dictionary will cause a return code of 500
    # This will happen automatically if your Python raises an unhandled exception.
    # You can return a dictionary with a manually set "httpStatus" key with an int value to set the return code of the HTTP request.
    response_templates = {
      "application/json" = <<EOF
      #set($inputRoot = $input.path('$'))
      $input.json("$")
      
      #if($input.path("stackTrace") != '')
      #set($context.responseOverride.status = 500)
      #elseif($input.path("httpStatus") != '')
      #set($context.responseOverride.status = $input.path('httpStatus'))
      #end
      EOF
        }
      }
    ```
  - aws_api_gateway_deployment
  ```
    resource "aws_api_gateway_deployment" "[name]_api_deployment" {
      rest_api_id = aws_api_gateway_rest_api.[name]_api.id
    }
    ```
  - aws_api_gateway_stage
  ```
    resource "aws_api_gateway_stage" "[name]_api_stage" {
      deployment_id = aws_api_gateway_deployment.[name]_api_deployment.id
      rest_api_id   = aws_api_gateway_rest_api.[name]_api.id
      stage_name    = "dev" #add your stage name
    }
    ```
  - aws_lambda_permission
    ```
    resource "aws_lambda_permission" "[name]_api_permission" {
      statement_id  = "AllowExecutionFromAPIGateway"
      action        = "lambda:InvokeFunction"
      function_name = aws_lambda_function.[name].function_name
      principal     = "apigateway.amazonaws.com"
    
      # More: http://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-control-access-using-iam-policies-to-invoke-api.html
      # Alternate potential source_arn: "${aws_api_gateway_rest_api.[name]_api.execution_arn}/*/$ {aws_api_gateway_method.request_status[name]api_method.http_method}${aws_api_gateway_resource.[name]_api_resource.path}"
      # source_arn = "${aws_api_gateway_rest_api.[name]_api.execution_arn}/*/${aws_api_gateway_method.[name]_api_method.http_method}${aws_api_gateway_resource.[name]_api_resource.path}"
    }
    ```  
  - aws_api_gateway_rest_api_policy
    ```
    resource "aws_lambda_permission" "[name]_api_resource_policy" {

        rest_api_id = aws_api_gateway_rest_api.[name]_api.id
        policy = <<EOF
      {
        "Version": "2012-10-17",
        "Statement": [
          {
            "Effect": "Allow",
            "Principal": {
              "AWS": "*"
            },
            "Action": "execute-api:Invoke",
            "Resource": "${aws_api_gateway_rest_api.[name]_api.execution_arn}"
          }
        ]
      }
      EOF
    }
    ``` 
- Proper HTTP error codes can be returned from a Lambda to the gateway via a dictionary, as shown in [Handle Lambda errors in API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/handle-errors-in-lambda-integration.html)
  - For more potential patterns, see https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-integration-settings-integration-response.html and https://aws.amazon.com/blogs/compute/error-handling-patterns-in-amazon-api-gateway-and-aws-lambda/
- In order to access a private API, a `VPC endpoint` has to be created in VPC. Secondly, a [resource policy](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-resource-policies-create-attach.html) needs to be created and attached to the API.
   - For more information, see
 https://medium.com/@ilia.lazebnik/simplifying-aws-private-api-gateway-vpc-endpoint-association-with-terraform-b379a247afbf and 
 https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-private-apis.html#apigateway-private-api-test-invoke-url

### Future Direction
- This code is not secure. See the "authorization" value in [aws_api_gateway_method](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/api_gateway_method).

#### Sources
- [Terraform aws_api_gateway_integration](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/api_gateway_integration)
- [Terraform aws_lambda_permission](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_permission)
- [Handle Lambda errors in API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/handle-errors-in-lambda-integration.html)
- [Handling Errors in API Gateway](https://docs.aws.amazon.com/apigateway/api-reference/handling-errors/)