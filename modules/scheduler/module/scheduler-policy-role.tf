data "aws_iam_policy_document" "aws_instance_scheduler_policydata" {
  statement {
    sid = 1
    actions = [
      "rds:StartDBCluster",
      "rds:StopDBCluster",
      "kms:Decrypt",
      "autoscaling:ResumeProcesses",
      "lambda:InvokeFunction",
      "autoscaling:SuspendProcesses",
      "rds:StopDBInstance",
      "ec2:StopInstances",
      "rds:StartDBInstance",
      "logs:CreateLogStream",
      "cloudwatch:EnableAlarmActions",
      "ec2:StartInstances",
      "cloudwatch:DisableAlarmActions",
      "kms:Encrypt",
      "autoscaling:UpdateAutoScalingGroup",
      "autoscaling:TerminateInstanceInAutoScalingGroup",
      "kms:CreateGrant",
      "rds:DescribeDBClusters"
    ]
    resources = [
      "arn:aws:autoscaling:*:${var.aws_account_id}:autoScalingGroup:*:autoScalingGroupName/*",
      "arn:aws:rds:*:${var.aws_account_id}:db:*",
      "arn:aws:rds:*:${var.aws_account_id}:cluster:*",
      "arn:aws:lambda:*:${var.aws_account_id}:function:*",
      "arn:aws:cloudwatch:*:${var.aws_account_id}:alarm:*",
      "arn:aws:logs:*:${var.aws_account_id}:log-group:*",
      "arn:aws:kms:*:${var.aws_account_id}:key/*",
      "arn:aws:ec2:*:${var.aws_account_id}:instance/*"
    ]
  }

  statement {
    sid = 2
    actions = [
      "autoscaling:DescribeAutoScalingInstances",
      "ec2:DescribeInstances",
      "tag:GetResources",
      "autoscaling:DescribeScalingProcessTypes",
      "autoscaling:DescribeAutoScalingGroups",
      "autoscaling:DescribeTags"
    ]
    resources = [
      "*"
    ]
  }

  statement {
    sid = 3
    actions = [
      "logs:PutLogEvents"
    ]
    resources = [
      "arn:aws:logs:*:${var.aws_account_id}:log-group:*:log-stream:*"
    ]
  }

  statement {
    sid = 4
    actions = [
      "redshift:PauseCluster"
    ]
    resources = [
      "arn:aws:redshift:*:${var.aws_account_id}:cluster:*"
    ]
  }
}

data "aws_iam_policy_document" "aws_instance_scheduler_rolepolicy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_policy" "aws_instance_scheduler_policy" {
  name = "aws-instance-scheduler-policy"
  path = "/"
  tags = var.tags
  description = "Terraforms InstanceScheduler actions to start and stop resources"
  policy = data.aws_iam_policy_document.aws_instance_scheduler_policydata.json
}

resource "aws_iam_role" "aws_instance_scheduler_role" {
  name                = "aws-instance-scheduler-role"
  assume_role_policy  = data.aws_iam_policy_document.aws_instance_scheduler_rolepolicy.json
  managed_policy_arns = [
      aws_iam_policy.aws_instance_scheduler_policy.arn,
  ]
  permissions_boundary = var.role_permissions_boundary_arn
}

