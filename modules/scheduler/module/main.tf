module "start_ec2_instance" {
    source = "diodonfrost/lambda-scheduler-stop-start/aws"
    version = "3.5.0"
    count = var.create_office_hours ? 1 : 0
    name = "start_ec2_instance"
    cloudwatch_schedule_expression = "cron(0 12 ? * MON-FRI *)"
    schedule_action = "start"
    aws_regions = ["us-west-2"]
    tags = var.tags
    autoscaling_schedule = "false"
    ec2_schedule = "true"
    rds_schedule = "false"
    cloudwatch_alarm_schedule = "false"
    custom_iam_role_arn = aws_iam_role.aws_instance_scheduler_role.arn
    resources_tag = {
        key = "Schedule"
        value = "office-hours"
    }
}

module "stop_ec2_instance" {
    source = "diodonfrost/lambda-scheduler-stop-start/aws"
    version = "3.5.0"
    count = var.create_office_hours ? 1 : 0
    name = "stop_ec2_instance"
    cloudwatch_schedule_expression = "cron(59 23 ? * MON-FRI *)"
    schedule_action = "stop"
    aws_regions = ["us-west-2"]
    tags = var.tags
    autoscaling_schedule = "false"
    ec2_schedule = "true"
    rds_schedule = "false"
    cloudwatch_alarm_schedule = "false"
    custom_iam_role_arn = aws_iam_role.aws_instance_scheduler_role.arn
    resources_tag = {
        key = "Schedule"
        value = "office-hours"
    }
}

# Schedule = office-hours-8-6
module "start_ec2_instance_8am" {
    source = "diodonfrost/lambda-scheduler-stop-start/aws"
    version = "3.5.0"
    count = var.create_office_hours_8_6 ? 1 : 0
    name = "start_ec2_instance_8am"
    cloudwatch_schedule_expression = "cron(0 13 ? * MON-FRI *)"
    schedule_action = "start"
    aws_regions = ["us-west-2"]
    tags = var.tags
    autoscaling_schedule = "false"
    ec2_schedule = "true"
    rds_schedule = "false"
    cloudwatch_alarm_schedule = "false"
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
    cloudwatch_schedule_expression = "cron(59 22 ? * MON-FRI *)"
    schedule_action = "stop"
    aws_regions = ["us-west-2"]
    tags = var.tags
    autoscaling_schedule = "false"
    ec2_schedule = "true"
    rds_schedule = "false"
    cloudwatch_alarm_schedule = "false"
    custom_iam_role_arn = aws_iam_role.aws_instance_scheduler_role.arn
    resources_tag = {
        key = "Schedule"
        value = "office-hours-8-6"
    }
}

module "start_autoscaling_instance" {
    source = "diodonfrost/lambda-scheduler-stop-start/aws"
    version = "3.5.0"
    count = var.create_office_hours ? 1 : 0
    name = "start_autoscaling_instance"
    cloudwatch_schedule_expression = "cron(0 12 ? * MON-FRI *)"
    schedule_action = "start"
    aws_regions = ["us-west-2"]
    tags = var.tags
    autoscaling_schedule = "true"
    ec2_schedule = "false"
    rds_schedule = "false"
    cloudwatch_alarm_schedule = "false"
    custom_iam_role_arn = aws_iam_role.aws_instance_scheduler_role.arn
    resources_tag = {
        key = "Schedule"
        value = "autoscaling-office-hours"
    }
}

module "stop_autoscaling_instance" {
    source = "diodonfrost/lambda-scheduler-stop-start/aws"
    version = "3.5.0"
    count = var.create_office_hours ? 1 : 0
    name = "stop_autoscaling_instance"
    cloudwatch_schedule_expression = "cron(59 23 ? * MON-FRI *)"
    schedule_action = "stop"
    aws_regions = ["us-west-2"]
    tags = var.tags
    autoscaling_schedule = "true"
    ec2_schedule = "false"
    rds_schedule = "false"
    cloudwatch_alarm_schedule = "false"
    custom_iam_role_arn = aws_iam_role.aws_instance_scheduler_role.arn
    resources_tag = {
        key = "Schedule"
        value = "autoscaling-office-hours"
    }
}

# Schedule = office-hours-8-6
module "start_autoscaling_instance_8am" {
    source = "diodonfrost/lambda-scheduler-stop-start/aws"
    version = "3.5.0"
    count = var.create_office_hours_8_6 ? 1 : 0
    name = "start_autoscaling_instance_8am"
    cloudwatch_schedule_expression = "cron(0 13 ? * MON-FRI *)"
    schedule_action = "start"
    aws_regions = ["us-west-2"]
    tags = var.tags
    autoscaling_schedule = "true"
    ec2_schedule = "false"
    rds_schedule = "false"
    cloudwatch_alarm_schedule = "false"
    custom_iam_role_arn = aws_iam_role.aws_instance_scheduler_role.arn
    resources_tag = {
        key = "Schedule"
        value = "autoscaling-office-hours-8-6"
    }
}

module "stop_autoscaling_instance_6pm" {
    source = "diodonfrost/lambda-scheduler-stop-start/aws"
    version = "3.5.0"
    count = var.create_office_hours_8_6 ? 1 : 0
    name = "stop_autoscaling_instance_6pm"
    cloudwatch_schedule_expression = "cron(59 22 ? * MON-FRI *)"
    schedule_action = "stop"
    aws_regions = ["us-west-2"]
    tags = var.tags
    autoscaling_schedule = "true"
    ec2_schedule = "false"
    rds_schedule = "false"
    cloudwatch_alarm_schedule = "false"
    custom_iam_role_arn = aws_iam_role.aws_instance_scheduler_role.arn
    resources_tag = {
        key = "Schedule"
        value = "autoscaling-office-hours-8-6"
    }
}

