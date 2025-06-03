output "orca_delete_api_deployment_invoke_url" {
  value       = aws_api_gateway_deployment.orca_delete_api_deployment.invoke_url
  description = "The URL to invoke the ORCA Delete API gateway. Excludes the resource path"
}
