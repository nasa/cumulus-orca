import datetime
import time

import boto3
import requests


def get_state_machine_execution_results(
    execution_arn, retry_interval_seconds=5, maximum_duration_seconds=30
):
    # todo: better backoff and such
    # todo: decorator?
    start = datetime.datetime.utcnow()
    while True:
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/stepfunctions.html#SFN.Client.describe_execution
        print("Getting execution description...")
        execution_state = boto3.client("stepfunctions").describe_execution(
            executionArn=execution_arn
        )
        if execution_state["status"] != "RUNNING":
            return execution_state

        if (
            datetime.datetime.utcnow() - start
        ).total_seconds() > retry_interval_seconds:
            raise TimeoutError()

        time.sleep(retry_interval_seconds)


def post_to_api(api_invoke_url, data=...):  # todo: what?
    return requests.post(api_invoke_url, data=data)
