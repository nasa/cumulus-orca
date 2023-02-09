"""
Name: copy_to_archive.py
Description: Lambda function that takes a Cumulus message, extracts a list of files,
and copies those files from their current storage location into a staging/archive location.
"""
import json
import os
from typing import Any, Dict, List, Union

# Third party libraries
import boto3
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from botocore.client import Config
from run_cumulus_task import run_cumulus_task

OS_ENVIRON_COPY_TO_ARCHIVE_ARN_KEY = "COPY_TO_ARCHIVE_ARN"

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
    config = Config(read_timeout=600, retries={'max_attempts': 0})
    client = boto3.client("lambda", config=config)
    response = client.invoke(
        FunctionName=os.environ[OS_ENVIRON_COPY_TO_ARCHIVE_ARN_KEY],
        InvocationType="RequestResponse",  # Synchronous
        Payload=
        json.dumps({
            ORCA_INPUT_KEY: event["input"],
            ORCA_CONFIG_KEY: event["config"]
        }, indent=4).encode("utf-8")
    )

    if response["StatusCode"] != 200:
        raise Exception(response["FunctionError"])

    result = json.loads(response["Payload"].read())
    return result


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
        COPY_TO_ARCHIVE_ARN (string, required):
            ARN of ORCA's copy_to_archive lambda.

    Returns:
        The result of the cumulus task. See schemas/output.json for more information.
    """
    return run_cumulus_task(task, event, context)
