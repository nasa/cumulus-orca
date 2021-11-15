output "orca_cumulus_reconciliation_api_deployment_invoke_url" {
  value       = aws_api_gateway_deployment.orca_cumulus_reconciliation_api_deployment.invoke_url
  description = "The URL to invoke the ORCA Cumulus reconciliation API gateway. Excludes the resource path"
}