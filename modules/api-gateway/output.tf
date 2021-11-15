output "catalog_reporting_api_invoke_url" {
  value       = aws_api_gateway_stage.orca_catalog_reporting_api_stage.invoke_url
  description = "The URL to invoke the API for catalog reporting lambda"
}

output "request_status_for_granule_api_invoke_url" {
  value       = aws_api_gateway_stage.request_status_for_granule_api_stage.invoke_url
  description = "The URL to invoke the API for request_status_for_granule lambda"
}

output "request_status_for_job_api_invoke_url" {
  value       = aws_api_gateway_stage.request_status_for_job_api_stage.invoke_url
  description = "The URL to invoke the API for request_status_for_job lambda"
}