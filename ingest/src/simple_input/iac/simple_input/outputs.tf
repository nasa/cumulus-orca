output "simple_input_invoke_arn" {
  description = "Invoke ARN of the Simple Input Lambda"
  value = aws_lambda_function.simple_input.invoke_arn
}

output "simple_input_function_name" {
    description = "Name of the simple_input lambda"
    value = aws_lambda_function.simple_input.function_name
}