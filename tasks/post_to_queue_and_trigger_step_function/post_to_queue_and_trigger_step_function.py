"""
Name: post_to_queue_and_trigger_step_function.py

Description: Receives an events from an SQS queue, translates to get_current_archive_list's input format,
sends it to another queue, then triggers the internal report step function.
"""
import functools
import json
import os
import random
import time
from typing import Any, Dict, List, Callable, TypeVar

import boto3
import fastjsonschema
# noinspection PyPackageRequirements
from botocore.client import BaseClient
from cumulus_logger import CumulusLogger

OS_ENVIRON_TARGET_QUEUE_URL_KEY = "TARGET_QUEUE_URL"
OS_ENVIRON_STEP_FUNCTION_ARN_KEY = "STEP_FUNCTION_ARN"

OUTPUT_REPORT_BUCKET_REGION_KEY = "reportBucketRegion"
OUTPUT_REPORT_BUCKET_NAME_KEY = "reportBucketName"
OUTPUT_MANIFEST_KEY_KEY = "manifestKey"

RT = TypeVar("RT")  # return type

LOGGER = CumulusLogger(name="ORCA")
# Generating schema validators can take time, so do it once and reuse.
try:
    with open("schemas/input.json", "r") as raw_schema:
        _INPUT_VALIDATE = fastjsonschema.compile(json.loads(raw_schema.read()))
except Exception as ex:
    LOGGER.error(f"Could not build schema validator: {ex}")
    raise

try:
    with open("schemas/body.json", "r") as raw_schema:
        _BODY_VALIDATE = fastjsonschema.compile(json.loads(raw_schema.read()))
except Exception as ex:
    LOGGER.error(f"Could not build schema validator: {ex}")
    raise


def task(
    records: List[Dict[str, Any]],
    target_queue_url: str,
    step_function_arn: str,
) -> None:
    """
    Posts the records to the target_queue_url, triggering state machine after each one.
    Args:
        records: The records to post.
        target_queue_url: The url of the queue to post the records to.
        step_function_arn: The arn of the step function to trigger.
    Returns: See output.json for details.
    """
    aws_client_sqs = boto3.client("sqs")
    aws_client_sfn = boto3.client("stepfunctions")
    for record in records:
        # noinspection PyBroadException
        try:
            process_record(aws_client_sqs, aws_client_sfn, target_queue_url, step_function_arn, record)
        except Exception as _:
            # Do not halt on errors. Logging will be handled internally.
            pass


def process_record(
    aws_client_sqs: BaseClient,
    aws_client_sfn: BaseClient,
    target_queue_url: str,
    step_function_arn: str,
    record: Dict[str, Any],
) -> None:
    """

    Args:
        aws_client_sqs: Client for communicating with SQS.
        aws_client_sfn: Client for communicating with Step Functions.
        target_queue_url: The url of the queue to post the records to.
        step_function_arn: The arn of the step function to trigger.
        record: The record to post.
    """
    new_body = translate_record_body(record["body"])
    send_body_to_queue_and_trigger_workflow(
        aws_client_sqs,
        aws_client_sfn,
        target_queue_url,
        step_function_arn,
        new_body,
    )


def translate_record_body(body: str) -> str:
    """
    Translates the SQS body into the format expected by the get_current_archive_list queue.
    Args:
        body: The string to convert.

    Returns:
        See get_current_archive_list/schemas/input.json for details.
    """
    body = json.loads(body)
    _BODY_VALIDATE(body)

    new_body = {
        OUTPUT_REPORT_BUCKET_REGION_KEY: body["awsRegion"],
        OUTPUT_REPORT_BUCKET_NAME_KEY: body["s3"]["bucket"]["name"],
        OUTPUT_MANIFEST_KEY_KEY: body["s3"]["object"]["key"],
    }
    return json.dumps(new_body)


def send_body_to_queue_and_trigger_workflow(
    aws_client_sqs: BaseClient,
    aws_client_sfn: BaseClient,
    target_queue_url: str,
    step_function_arn: str,
    body: str,
) -> None:
    """
    Posts the records to the target_queue_url, triggering state machine after each one.
    Args:
        aws_client_sqs: Client for communicating with SQS.
        aws_client_sfn: Client for communicating with Step Functions.
        target_queue_url: The url of the queue to post the records to.
        step_function_arn: The arn of the step function to trigger.
        body: The body to post.
    Returns: See output.json for details.
    """

    with retry_error():
        aws_client_sqs.send_message(target_queue_url, body)

    with retry_error():
        aws_client_sfn.start_execution(step_function_arn)


# copied from shared_db.py
# Retry decorator for functions
def retry_error(
    max_retries: int = 3,
    backoff_in_seconds: int = 1,
    backoff_factor: int = 2,
) -> Callable[[Callable[[], RT]], Callable[[], RT]]:
    """
    Decorator takes arguments to adjust number of retries and backoff strategy.
    Args:
        max_retries (int): number of times to retry in case of failure.
        backoff_in_seconds (int): Number of seconds to sleep the first time through.
        backoff_factor (int): Value of the factor used for backoff.
    """

    def decorator_retry_error(func: Callable[[], RT]) -> Callable[[], RT]:
        """
        Main Decorator that takes our function as an argument
        """

        @functools.wraps(func)  # Use built in for decorators
        def wrapper_retry_error(*args, **kwargs) -> RT:
            """
            Wrapper that performs our extra tasks on the function
            """
            # Initialize the retry loop
            total_retries = 0

            # Enter loop
            while True:
                # Try the function and catch the expected error
                # noinspection PyBroadException
                try:
                    # noinspection PyArgumentList
                    return func(*args, **kwargs)
                except Exception:
                    if total_retries == max_retries:
                        # Log it and re-raise if we maxed our retries + initial attempt
                        LOGGER.error(
                            "Encountered Errors {total_attempts} times. Reached max retry limit.",
                            total_attempts=total_retries,
                        )
                        raise
                    else:
                        # perform exponential delay
                        backoff_time = (
                            backoff_in_seconds * backoff_factor ** total_retries
                            + random.uniform(0, 1)  # nosec
                        )
                        LOGGER.error(
                            f"Encountered Error on attempt {total_retries}. "
                            f"Sleeping {backoff_time} seconds."
                        )
                        time.sleep(backoff_time)
                        total_retries += 1

        # Return our wrapper
        return wrapper_retry_error

    # Return our decorator
    return decorator_retry_error


def handler(event: Dict[str, Any], context) -> None:
    """
    Lambda handler.
    Receives an events from an SQS queue, translates to get_current_archive_list's input format,
    sends it to another queue, then triggers the internal report step function.
    Args:
        event: See input.json for details.
        context: An object passed through by AWS. Used for tracking.
    Environment Vars:
        INTERNAL_REPORT_QUEUE_URL (string): The URL of the SQS queue the job came from.
        See shared_db.py's get_configuration for further details.
    Returns: See output.json for details.
    """
    LOGGER.setMetadata(event, context)

    _INPUT_VALIDATE(event)

    try:
        target_queue_url = str(os.environ[OS_ENVIRON_TARGET_QUEUE_URL_KEY])
    except KeyError as key_error:
        LOGGER.error(f"{OS_ENVIRON_TARGET_QUEUE_URL_KEY} environment value not found.")
        raise key_error
    try:
        state_machine_arn = str(os.environ[OS_ENVIRON_STEP_FUNCTION_ARN_KEY])
    except KeyError as key_error:
        LOGGER.error(f"{OS_ENVIRON_STEP_FUNCTION_ARN_KEY} environment value not found.")
        raise key_error

    task(event["Records"], target_queue_url, state_machine_arn)
