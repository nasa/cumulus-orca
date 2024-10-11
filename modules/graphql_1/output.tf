output "graphql_load_balancer_dns_name" {
  value       = data.aws_lb.gql_app_lb_data.dns_name
  description = "The DNS Name of the Application Load Balancer that handles access to ORCA GraphQL."
}

output "network_load_balancer_dns_name" {
  value       = data.aws_lb.decoupling_orca_nlb_data.dns_name
}
