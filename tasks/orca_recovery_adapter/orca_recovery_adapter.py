"""
Name: orca_recovery_adapter.py
Description: Lambda function that takes a Cumulus message, extracts a list of files,
and requests that those files be restored from ORCA.
"""
import datetime
import time
import json
import os
from typing import Any, Dict, List, Union

# Third party libraries
import boto3
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

# noinspection PyPackageRequirements
from botocore.client import Config
from run_cumulus_task import run_cumulus_task

OS_ENVIRON_ORCA_RECOVERY_STEP_FUNCTION_ARN_KEY = "ORCA_RECOVERY_STEP_FUNCTION_ARN"

ORCA_INPUT_KEY = "input"
ORCA_CONFIG_KEY = "config"

# Set AWS powertools logger
LOGGER = Logger()


# noinspection PyUnusedLocal
def task(event: Dict[str, Union[List[str], Dict]], context: object) -> Dict[str, Any]:
    """
    Converts event to a format accepted by ORCA's copy_to_archive lambda,
    then calls copy_to_archive and returns the result.

    Args:
        event: Passed through from {handler}
        context: An object required by AWS Lambda. Unused.

    Environment Variables:
        COPY_TO_ARCHIVE_ARN (string, required):
            ARN of ORCA's copy_to_archive lambda.

    Returns:
        A dict representing input and copied files. See schemas/output.json for more information.
    """
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda.html
    # 600s for copy_to_archive operation
    # todo: is read_timeout a thing for step functions?
    # todo: Make timeout configurable in both adapters. Tie to TF vars?
    config = Config(read_timeout=600, retries={'total_max_attempts': 1})
    client = boto3.client("stepfunctions", config=config)
    execution_info = client.start_execution(
        stateMachineArn=os.environ[OS_ENVIRON_ORCA_RECOVERY_STEP_FUNCTION_ARN_KEY],
        # name=,
        input=json.dumps({
            ORCA_INPUT_KEY: event["input"],
            ORCA_CONFIG_KEY: event["config"]
        }, indent=4)
    )
    step_function_results = get_state_machine_execution_results(
        execution_info["executionArn"]
    )

    if step_function_results["status"] != "SUCCEEDED":
        raise Exception(f"Step function did not succeed: {step_function_results}")

    return json.loads(step_function_results["output"])


def get_state_machine_execution_results(
    execution_arn, retry_interval_seconds=5, maximum_duration_seconds=600
):
    start = datetime.datetime.utcnow()
    while True:
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/stepfunctions.html#SFN.Client.describe_execution
        LOGGER.debug("Getting execution description...")
        execution_state = boto3.client("stepfunctions").describe_execution(
            executionArn=execution_arn
        )
        if execution_state["status"] != "RUNNING":
            return execution_state

        if (
            datetime.datetime.utcnow() - start
        ).total_seconds() > maximum_duration_seconds:
            return execution_state

        time.sleep(retry_interval_seconds)


@LOGGER.inject_lambda_context
def handler(event: Dict[str, Union[List[str], Dict]], context: LambdaContext) -> Any:
    """Lambda handler. Runs a cumulus task that
    Formats the input from the Cumulus format
    to the format required by ORCA's copy_to_archive Lambda,
    then calls copy_to_archive and returns the result.

    Args:
        event: Event passed into the step from the aws workflow.
            See schemas/input.json and schemas/config.json for more information.

        context: This object provides information about the lambda invocation, function,
            and execution env.

    Environment Variables:
        ORCA_RECOVERY_WORKFLOW_ARN (string, required):
            ARN of ORCA's recovery step function.

    Returns:
        The result of the cumulus task. See schemas/output.json for more information.
    """
    return run_cumulus_task(task, event, context)
