# Instance Scheduler
This module creates Lambda functions that turn on or off EC2 Instances, Auto Scaling Groups, RDS Instances, ECS Clusters, RedShift Clusters, and DocumentDB Instances based on the instance tags. The code is sourced from the [diodonfrost terraform-aws-lambda-scheduler-stop-start github](https://github.com/diodonfrost/terraform-aws-lambda-scheduler-stop-start), with parameters entered to configure the function, including a cron expression for the schedule.

## Example Scheduler Block for EC2
```terraform
# Schedule = office-hours-8-6
module "start_ec2_instance_8am" {
    source = "diodonfrost/lambda-scheduler-stop-start/aws"
    version = "3.5.0"
    count = var.create_office_hours_8_6 ? 1 : 0
    name = "start_ec2_instance_8am"
    cloudwatch_schedule_expression = "cron(0 14 ? * MON-FRI *)"
    schedule_action = "start"
    aws_regions = ["us-west-2"]
    tags = var.tags
    ec2_schedule = "true"
    custom_iam_role_arn = aws_iam_role.aws_instance_scheduler_role.arn
    resources_tag = {
        key = "Schedule"
        value = "office-hours-8-6"
    }
}

module "stop_ec2_instance_6pm" {
    source = "diodonfrost/lambda-scheduler-stop-start/aws"
    version = "3.5.0"
    count = var.create_office_hours_8_6 ? 1 : 0
    name = "stop_ec2_instance_6pm"
    cloudwatch_schedule_expression = "cron(59 23 ? * MON-FRI *)"
    schedule_action = "stop"
    aws_regions = ["us-west-2"]
    tags = var.tags
    ec2_schedule = "true"
    custom_iam_role_arn = aws_iam_role.aws_instance_scheduler_role.arn
    resources_tag = {
        key = "Schedule"
        value = "office-hours-8-6"
    }
}


```

## Usage
1. Ensure the instance you want scheduled for start/stop has the tags specified, e.g. Key = **Schedule** Value = **office-hours-8-6**
2. Run a deployment with all lambda functions set to false in the **variables.tf** file or the deployment will fail.

**Example:**
```terraform
variable "create_office_hours" {
    default = false
}

variable "create_stop_only_8pm_autoscaling" {
    default = false
}

variable "create_office_hours_8_6_autoscaling" {
    default = false
}

variable "create_office_hours_autoscaling" {
    default = false
}
```
