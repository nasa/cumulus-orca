output "graphql_load_balancer_dns_name" {
  value       = data.aws_lb.gql_app_lb_data.dns_name
  description = "The DNS Name of the Application Load Balancer that handles access to ORCA GraphQL."
}