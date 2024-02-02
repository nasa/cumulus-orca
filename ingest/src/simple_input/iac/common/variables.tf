variable "prefix" {
    type = string
    description = "Prefix used for naming to manage multiple instances in a single VPC"
}

variable "tags" {
    type        = map(string)
    description = "Tags to be applied to resources that support tags."
    default     = {} 
}

variable "simple_input_invoke_arn" {
    type = string
    description = "Invocation ARN for the simple_input lambda"
}

variable "simple_input_function_name" {
    type = string
    description = "Name of the simple_input lambda"
}