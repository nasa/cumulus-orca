import datetime
import json
import re
import time
import uuid
from typing import Dict, List
from unittest import TestCase, mock

import boto3

import helpers
from custom_logger import CustomLoggerAdapter

logger = CustomLoggerAdapter.set_logger(__name__)

class TestInternalReconciliationHappyPath(TestCase):
    def test_internal_reconciliation_happy_path(self):
        """
        - Internal Report SQS queue recieves inventory report.
        - Job ID is verified in the API results.
        """
        self.maxDiff = None
        try:
            # Set up Orca API resources
            # ---
            my_session = helpers.create_session()
            boto3_session = boto3.Session()
            sqs = boto3.client("sqs")
            recovery_bucket_name = helpers.recovery_bucket_name
            reports_bucket_name = helpers.reports_bucket_name
            queue_url = helpers.orca_internal_report_sqs_url

            # Formats date for previous day's report, current date may not have ran and can cause errors.
            today_date = datetime.date.today()
            yesterday_date = today_date - datetime.timedelta(days=1)
            yesterday_date_formatted = yesterday_date.strftime("%Y-%m-%d")

            # Generates inventory report to send to the SQS queue
            inventory_report = {"reportBucketRegion": "us-west-2", "reportBucketName": f"{reports_bucket_name}", "manifestKey": f"{recovery_bucket_name}/{recovery_bucket_name}-inventory/{yesterday_date_formatted}T01-00Z/manifest.json"}
            message = json.dumps(inventory_report)
            group_id = uuid.uuid4().__str__()

            # Sends report to SQS queue
            sqs.send_message(
                QueueUrl=queue_url,
                MessageBody=message,
                MessageGroupId=group_id
            )

            # Allows time for the report to get to the SQS queue
            time.sleep(30)

            internal_reconciliation_input = {}

            # Invokes Internal Reconciliation Workflow
            execution_info = boto3_session.client("stepfunctions").start_execution(
                stateMachineArn=helpers.orca_internal_reconciliation_step_function_arn,
                input=json.dumps(internal_reconciliation_input),
            )

            step_function_results = helpers.get_state_machine_execution_results(
                boto3_session ,execution_info["executionArn"]
            )

            self.assertEqual(
                "SUCCEEDED",
                step_function_results["status"],
                "Error occurred while starting step function.",
            )

            # Allows time for the API to get step function results
            time.sleep(30)

            # Formats Step Function Output
            step_function_output = json.dumps(step_function_results, indent=4, sort_keys=True, default=str)

            # Finds job ID of the step function output
            pattern = r'"\{\\"jobId\\":\s*([^"]+)\}"'
            match = re.search(pattern, step_function_output)
            if match:
                results = match.group(1)
            else:
                print("Job ID not found in step function output")
                raise Exception


            reconciliation_input = {
                "pageIndex": 0,
            }

            reconciliation_output = helpers.post_to_api(
                my_session,
                helpers.api_url + "/orca/datamanagement/reconciliation/internal/jobs/",
                data=json.dumps(reconciliation_input),
                headers={"Host": helpers.aws_api_name},
            )

            self.assertEqual(
                200,
                reconciliation_output.status_code,
                f"Error occurred while contacting API: " f"{reconciliation_output.content}",
            )

            # Formats API results
            api_return_results = json.dumps(reconciliation_output.content, indent=4, sort_keys=True, default=str)

            api_pattern = fr'\\"id\\":({results})'
            api_match = re.search(api_pattern, api_return_results)

            # Verifies Job ID is found in the API results
            if api_match:
                api_match.group(1)
            else:
                print("Internal Reconciliation Job ID not found in API")
                raise Exception
            
        except Exception as ex:
            logger.error(ex)
            raise
