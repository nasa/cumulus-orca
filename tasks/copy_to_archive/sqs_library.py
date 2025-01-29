"""
Name: sqs_library.py
Description: library for copy_to_archive lambda function for posting to metadata SQS queue.
"""

# todo: Move to shared lib ORCA-406
# Standard libraries
import functools
import hashlib
import json
import os
import random
import time
from typing import Any, Callable, Dict, TypeVar

# Third party libraries
import boto3
import fastjsonschema
from aws_lambda_powertools import Logger

# Set AWS powertools logger
LOGGER = Logger()

MAX_RETRIES = 3  # number of times to retry.
BACKOFF_FACTOR = 2  # Value of the factor used to backoff
INITIAL_BACKOFF_IN_SECONDS = 1  # Number of seconds to sleep the first time through.
RT = TypeVar("RT")  # return type

try:
    with open("schemas/body.json", "r") as raw_schema:
        _BODY_VALIDATE = fastjsonschema.compile(json.loads(raw_schema.read()))
except Exception as ex:
    LOGGER.error(f"Could not build schema validator: {ex}")
    raise


# Retry decorator for function
# todo: Lacks unit tests. Will likely eventually be part of shared lib ORCA-148.
def retry_error(
    max_retries: int = MAX_RETRIES,
    backoff_in_seconds: int = INITIAL_BACKOFF_IN_SECONDS,
    backoff_factor: int = BACKOFF_FACTOR,
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
                try:
                    return func(*args, **kwargs)
                except fastjsonschema.JsonSchemaException:
                    raise
                except Exception:
                    if total_retries == max_retries:
                        # Log it and re-raise if we maxed our retries + initial attempt
                        LOGGER.error(
                            f"Encountered Error {total_retries} times. Reached max retry limit.",
                        )
                        raise
                    else:
                        # perform exponential delay
                        backoff_time = (
                            backoff_in_seconds * backoff_factor**total_retries
                            + random.uniform(0, 1)  # nosec
                        )
                        LOGGER.error(
                            f"Encountered Error on attempt {total_retries}. "
                            f"Sleeping {backoff_time} seconds.",
                        )
                        time.sleep(backoff_time)
                        total_retries += 1

        # Return our wrapper
        return wrapper_retry_error

    # Return our decorator
    return decorator_retry_error


def get_aws_region() -> str:
    """
    Gets AWS region variable from the runtime environment variable.
        Returns:
            The AWS region variable.
        Raises:
            Exception: Thrown if AWS region is empty or None.
    """
    LOGGER.debug("Getting environment variable AWS_REGION value.")
    aws_region = os.getenv("AWS_REGION", None)
    if aws_region is None or len(aws_region) == 0:
        message = "Runtime environment variable AWS_REGION is not set."
        LOGGER.critical(message)
        raise ValueError(message)
    LOGGER.debug(f"Got environment variable for AWS_REGION = {aws_region}")
    return aws_region


@retry_error()
def post_to_metadata_queue(
    sqs_body: Dict[str, Any],
    metadata_queue_url: str,
) -> None:
    """
    Posts metadata information to the metadata SQS queue.
    Args:
        sqs_body: A dictionary containing the metadata objects that will be sent to SQS.
        metadata_queue_url: The metadata SQS queue URL defined by AWS.
    Raises:
        None
    """
    LOGGER.debug("Validating the SQS message body with the schema.")
    _BODY_VALIDATE(sqs_body)
    body = json.dumps(sqs_body)
    LOGGER.debug(
        f"Creating SQS resource for {metadata_queue_url}",
    )
    mysqs_resource = boto3.resource("sqs", region_name=get_aws_region())
    mysqs = mysqs_resource.Queue(metadata_queue_url)
    deduplication_id = hashlib.sha256(body.encode("utf8")).hexdigest()

    md5_body = hashlib.md5(body.encode("utf8")).hexdigest()  # nosec

    LOGGER.debug(f"Sending the following data to metadata queue: {body}")
    response = mysqs.send_message(
        QueueUrl=metadata_queue_url,
        MessageDeduplicationId=deduplication_id,
        MessageGroupId="metadata_message",
        MessageBody=body,
    )  # todo: Look at changes in post_to_queue_and_trigger_step_function ORCA-406
    LOGGER.debug(f"SQS Message Response: {json.dumps(response)}")
    return_status = response["ResponseMetadata"]["HTTPStatusCode"]
    if return_status < 200 or return_status > 299:
        raise Exception(
            f"Failed to send message to Queue. HTTP Response was {return_status}"
        )

    sqs_md5 = response.get("MD5OfMessageBody")
    if md5_body != sqs_md5:
        raise Exception(
            f"Calculated MD5 of {md5_body} does not match SQS MD5 of {sqs_md5}"
        )
