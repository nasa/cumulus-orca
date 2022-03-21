"""
Name: sqs_library.py
Description: library for copy_to_glacier lambda function for posting to fifo SQS queue.
"""
# todo: Move to shared lib
# todo: Include tests from copy_to_glacier
# Standard libraries
import functools
import hashlib
import json
import random
import time
from typing import Any, Callable, Dict, TypeVar

# Third party libraries
import boto3
import fastjsonschema
from cumulus_logger import CumulusLogger

# Set Cumulus LOGGER
LOGGER = CumulusLogger(name="ORCA")
MAX_RETRIES = 3  # number of times to retry.
BACKOFF_FACTOR = 2  # Value of the factor used to backoff
INITIAL_BACKOFF_IN_SECONDS = 1  # Number of seconds to sleep the first time through.
RT = TypeVar("RT")  # return type


# Retry decorator for function
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
                # noinspection PyBroadException
                try:
                    # noinspection PyArgumentList
                    return func(*args, **kwargs)
                except fastjsonschema.JsonSchemaException:
                    raise
                except Exception:
                    if total_retries == max_retries:
                        # Log it and re-raise if we maxed our retries + initial attempt
                        LOGGER.error(
                            "Encountered Error {total_attempts} times. Reached max retry limit.",
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
                            "Encountered Error on attempt {total_attempts}. "
                            "Sleeping {backoff_time} seconds.",
                            total_attempts=total_retries,
                            backoff_time=backoff_time,
                        )
                        time.sleep(backoff_time)
                        total_retries += 1

        # Return our wrapper
        return wrapper_retry_error

    # Return our decorator
    return decorator_retry_error


@retry_error()
def post_to_fifo_queue(
    queue_url: str,
    sqs_body: Dict[str, Any],
) -> None:
    """
    Posts information to the given SQS queue.
    Args:
        sqs_body: A dictionary containing the objects that will be sent to SQS.
        queue_url: The SQS queue URL defined by AWS.
    Raises:
        None
    """
    # validate body.json schema
    with open("schemas/output_body.json", "r") as raw_schema:
        schema = json.loads(raw_schema.read())
    validate = fastjsonschema.compile(schema)
    LOGGER.debug("Validating the SQS message body with the schema.")
    validate(sqs_body)
    body = json.dumps(sqs_body)
    LOGGER.debug(
        f"Creating SQS resource for {queue_url}",
    )
    deduplication_id = hashlib.sha256(body.encode("utf8")).hexdigest()

    md5_body = hashlib.md5(body.encode("utf8")).hexdigest()  # nosec

    LOGGER.debug("Sending the following data to queue: {body}", body=body)
    response = boto3.client("sqs").send_message(  # todo: Make sure the changes I made here work.
        QueueUrl=queue_url,
        MessageDeduplicationId=deduplication_id,
        MessageGroupId="general_group",
        MessageBody=body,
    )
    LOGGER.debug("SQS Message Response: {response}", response=json.dumps(response))
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
