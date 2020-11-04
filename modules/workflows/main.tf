module "dr_recovery_workflow" {
  source = "https://github.com/nasa/cumulus/releases/download/v1.21.0/terraform-aws-cumulus-workflow.zip"

  prefix          = var.prefix
  name            = var.name
  workflow_config = var.workflow_config
  system_bucket   = var.system_bucket
  tags            = var.tags

  state_machine_definition = <<JSON
{
  "Comment": "Recover files belonging to a granule",
  "StartAt": "ExtractFilepaths",
  "TimeoutSeconds": 18000,
  "States": {
    "ExtractFilepaths": {
      "Parameters": {
        "cma": {
          "event.$": "$",
          "ReplaceConfig": {
            "FullMessage": true
          },
          "task_config": {
            "glacier-bucket": "{$.meta.buckets.glacier.name}",
            "public-bucket": "{$.meta.buckets.public.name}",
            "protected-bucket": "{$.meta.buckets.protected.name}",
            "private-bucket": "{$.meta.buckets.private.name}",
            "internal-bucket": "{$.meta.buckets.internal.name}",
            "file-buckets": "{$.meta.collection.files}"
          }
        }
      },
      "Type": "Task",
      "Resource": "${var.extract_filepaths_lambda_arn}",
      "Retry": [
        {
          "ErrorEquals": [
            "Lambda.ServiceException",
            "Lambda.AWSLambdaException",
            "Lambda.SdkClientException"
          ],
          "IntervalSeconds": 2,
          "MaxAttempts": 6,
          "BackoffRate": 2
        }
      ],
      "Catch": [
        {
          "ErrorEquals": [
            "States.ALL"
          ],
          "ResultPath": "$.exception",
          "Next": "WorkflowFailed"
        }
      ],
      "Next": "RequestFiles"
    },
    "RequestFiles": {
      "Parameters": {
        "cma": {
          "event.$": "$",
          "ReplaceConfig": {
            "FullMessage": true
          },
          "task_config": {
            "glacier-bucket": "{$.meta.buckets.glacier.name}"
          }
        }
      },
      "Type": "Task",
      "Resource": "${var.request_files_lambda_arn}",
      "Retry": [
        {
          "ErrorEquals": [
            "Lambda.ServiceException",
            "Lambda.AWSLambdaException",
            "Lambda.SdkClientException"
          ],
          "IntervalSeconds": 2,
          "MaxAttempts": 6,
          "BackoffRate": 2
        }
      ],
      "Catch": [
        {
          "ErrorEquals": [
            "States.ALL"
          ],
          "ResultPath": "$.exception",
          "Next": "WorkflowFailed"
        }
      ],
      "End": true
    },
    "WorkflowFailed": {
      "Type": "Fail",
      "Cause": "Workflow failed"
    }
  }
}
JSON
}