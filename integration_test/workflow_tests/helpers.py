import datetime
import functools
import logging
import os
import random
import time
from typing import Callable, Text, TypeVar, Union

import boto3
from requests import Session
from requests.adapters import (
    DEFAULT_POOLBLOCK,
    DEFAULT_POOLSIZE,
    DEFAULT_RETRIES,
    HTTPAdapter,
)

# Networking defaults
API_LOCAL_HOST = "127.0.0.1"
API_LOCAL_PORT = "8000"

# os.env keys
# "https://s2jmh2r60k.execute-api.us-west-2.amazonaws.com"
orca_api_deployment_invoke_url = os.environ["orca_API_DEPLOYMENT_INVOKE_URL"]
orca_copy_to_glacier_step_function_arn = os.environ[
    "orca_COPY_TO_GLACIER_STEP_FUNCTION_ARN"
]

# helpful pre-constructed values
aws_api_name = orca_api_deployment_invoke_url.replace("https://", "")
api_url = f"https://{aws_api_name}:{API_LOCAL_PORT}/orca"

MAX_RETRIES = 3  # number of times to retry.
BACKOFF_FACTOR = 2  # Value of the factor used to backoff
INITIAL_BACKOFF_IN_SECONDS = 1  # Number of seconds to sleep the first time through.
RT = TypeVar("RT")  # return type


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
                # noinspection PyBroadException
                try:
                    # noinspection PyArgumentList
                    return func(*args, **kwargs)
                except Exception:
                    if total_retries == max_retries:
                        # Log it and re-raise if we maxed our retries + initial attempt
                        logging.error(
                            f"Encountered Error {total_retries} times. Reached max retry limit."
                        )
                        raise
                    else:
                        # perform exponential delay
                        backoff_time = (
                            backoff_in_seconds * backoff_factor ** total_retries
                            + random.uniform(0, 1)  # nosec
                        )
                        logging.warning(
                            f"Encountered Error on attempt {total_retries}. "
                            f"Sleeping {backoff_time} seconds.",
                        )
                        time.sleep(backoff_time)
                        total_retries += 1

        # Return our wrapper
        return wrapper_retry_error

    # Return our decorator
    return decorator_retry_error


def create_session() -> Session:
    my_session = Session()
    my_session.mount(
        api_url,
        DNSResolverHTTPSAdapter(aws_api_name, API_LOCAL_HOST),
    )
    return my_session


def get_state_machine_execution_results(
    execution_arn, retry_interval_seconds=5, maximum_duration_seconds=60
):
    start = datetime.datetime.utcnow()
    while True:
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/stepfunctions.html#SFN.Client.describe_execution
        logging.debug("Getting execution description...")
        execution_state = boto3.client("stepfunctions").describe_execution(
            executionArn=execution_arn
        )
        if execution_state["status"] != "RUNNING":
            return execution_state

        if (
            datetime.datetime.utcnow() - start
        ).total_seconds() > maximum_duration_seconds:
            raise TimeoutError()

        time.sleep(retry_interval_seconds)


@retry_error()
def post_to_api(
    session: Session,
    api_invoke_url: Union[Text, bytes],
    data,
    headers: Union[Session.params, None] = ...,
):
    result = session.post(api_invoke_url, data=data, headers=headers)
    if result.status_code == 504:
        # Raise to allow retry logic to catch
        raise Exception(f"API Gateway '{api_invoke_url}' timed out.")
    return result


class DNSResolverHTTPSAdapter(HTTPAdapter):
    """
    client-side code to support application-specific DNS for the purpose of checking certificates
    CommonName and SubjectAltName.
    """

    def __init__(
        self,
        common_name,
        host,
        pool_connections=DEFAULT_POOLSIZE,
        pool_maxsize=DEFAULT_POOLSIZE,
        max_retries=DEFAULT_RETRIES,
        pool_block=DEFAULT_POOLBLOCK,
    ):
        self.__common_name = common_name
        self.__host = host
        super(DNSResolverHTTPSAdapter, self).__init__(
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            max_retries=max_retries,
            pool_block=pool_block,
        )

    def get_connection(self, url, proxies=None):
        redirected_url = url.replace(self.__common_name, self.__host)
        return super(DNSResolverHTTPSAdapter, self).get_connection(
            redirected_url, proxies=proxies
        )

    def init_poolmanager(
        self, connections, maxsize, block=DEFAULT_POOLBLOCK, **pool_kwargs
    ):
        pool_kwargs["assert_hostname"] = self.__common_name
        super(DNSResolverHTTPSAdapter, self).init_poolmanager(
            connections, maxsize, block=block, **pool_kwargs
        )
