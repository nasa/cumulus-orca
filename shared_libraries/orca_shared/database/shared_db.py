"""
Name: shared_db.py

Description: Shared library for database objects needed by the various libraries.
"""

import functools
import json
import os
import random
import time
from typing import Any, Callable, Dict, TypeVar

import boto3
from cumulus_logger import CumulusLogger
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.exc import OperationalError
from sqlalchemy.future import Engine

# instantiate CumulusLogger
logger = CumulusLogger(name="Orca")
MAX_RETRIES = 3  # number of times to retry.
BACKOFF_FACTOR = 2  # Value of the factor used to backoff
INITIAL_BACKOFF_IN_SECONDS = 1  # Number of seconds to sleep the first time through.
RT = TypeVar("RT")  # return type


def get_configuration() -> Dict[str, str]:
    """
    Create a dictionary of configuration values based on environment variables
    parameter store information and other items needed to create the database.

    ```
    Environment Variables:
        PREFIX (str): Deployment prefix used to pull the proper AWS secret.
        AWS_REGION (str): AWS reserved runtime variable used to set boto3 client region.

    Parameter Store:
        <prefix>-orca-db-login-secret (string): The json string containing all the db login info.
    ```

    Args:
        None

    Returns:
        Configuration (Dict): Dictionary with all of the configuration information.
                              The schema for the output is available [here](schemas/output.json).

    Raises:
        Exception (Exception): When variables or secrets are not available.
    """
    # Get the PREFIX
    logger.debug("Getting environment variable PREFIX value.")
    prefix = os.getenv("PREFIX", None)

    if prefix is None or len(prefix) == 0:
        message = "Environment variable PREFIX is not set."
        logger.critical(message)
        raise Exception(message)

    # Get the AWS_REGION defined runtime environment reserved variable
    logger.debug("Getting environment variable AWS_REGION value.")
    aws_region = os.getenv("AWS_REGION", None)

    if aws_region is None or len(aws_region) == 0:
        message = "Runtime environment variable AWS_REGION is not set."
        logger.critical(message)
        raise Exception(message)

    try:
        logger.debug("Creating secretsmanager resource.")
        secretsmanager = boto3.client("secretsmanager", region_name=aws_region)

        logger.debug(
            "Retrieving db login info for both user and admin as a dictionary."
        )
        config = json.loads(
            secretsmanager.get_secret_value(SecretId=f"{prefix}-orca-db-login-secret")[
                "SecretString"
            ]
        )
        logger.debug(
            "Successfully retrieved db login info for both user and admin as a dictionary."
        )
    except Exception:
        logger.critical("Failed to retrieve secret.", exc_info=True)
        raise Exception("Failed to retrieve secret manager value.")

    # return the config dict
    return config


def _create_connection(**kwargs: Any) -> Engine:
    """
    Base function for creating a connection engine that can connect to a database.

    Args:
        host (str): Database host to connect to
        port (str): Database port to connect to
        database (str): Database name to connect to
        username (str): Database user to connect as
        password (str): Database password for the user

    Returns
        Engine (sqlalchemy.future.Engine): engine object for creating database connections.
    """
    logger.debug("Creating URL object to connect to the database.")
    connection_url = URL.create(drivername="postgresql", **kwargs)
    return create_engine(connection_url, future=True)


def get_admin_connection(config: Dict[str, str], database: str = None) -> Engine:
    """
    Creates a connection engine to a database as a superuser.

    Args:
        config (Dict): Configuration containing connection information.
        database (str): Database for the admin user to connect to. Defaults to admin_database.

    Returns
        Engine (sqlalchemy.future.Engine): engine object for creating database connections.
    """
    # Determine database to use
    if database is None or len(database) == 0:
        admin_database = config["admin_database"]
    else:
        admin_database = database

    logger.debug("Creating admin user connection object.")
    logger.debug(f"Database set to {admin_database} for the connection.")
    connection = _create_connection(
        host=config["host"],
        port=config["port"],
        database=admin_database,
        username=config["admin_username"],
        password=config["admin_password"],
    )

    return connection


def get_user_connection(config: Dict[str, str]) -> Engine:
    """
    Creates a connection engine to the application database as the application
    database user.

    Args:
        config (Dict): Configuration containing connection information.

    Returns
        Engine (sqlalchemy.future.Engine): engine object for creating database connections.
    """

    logger.debug("Creating application user connection object.")
    connection = _create_connection(
        host=config["host"],
        port=config["port"],
        database=config["user_database"],
        username=config["user_username"],
        password=config["user_password"],
    )

    return connection


# Retry decorator for functions
def retry_operational_error(
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

    def decorator_retry_operational_error(func: Callable[[], RT]) -> Callable[[], RT]:
        """
        Main Decorator that takes our function as an argument
        """

        @functools.wraps(func)  # Use built in for decorators
        def wrapper_retry_operational_error(*args, **kwargs) -> RT:
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
                except OperationalError:
                    if total_retries == max_retries:
                        # Log it and re-raise if we maxed our retries + initial attempt
                        logger.error(
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
                        logger.error(
                            "Encountered OperationalError on attempt {total_attempts}. "
                            "Sleeping {backoff_time} seconds.",
                            total_attempts=total_retries,
                            backoff_time=backoff_time,
                        )
                        time.sleep(backoff_time)
                        total_retries += 1
                except Exception as ex:
                    logger.error("Encountered a non-retriable error: {ex}", ex=ex)
                    raise ex

        # Return our wrapper
        return wrapper_retry_operational_error

    # Return our decorator
    return decorator_retry_operational_error
