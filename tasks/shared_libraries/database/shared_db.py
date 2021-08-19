"""
Name: shared_db.py

Description: Shared library for database objects needed by the various libraries.
"""

import os
import boto3
import json
import time
import random
from sqlalchemy import create_engine, exc
from sqlalchemy.engine import URL
from sqlalchemy.future import Engine
from cumulus_logger import CumulusLogger
from typing import Any, List, Dict, Optional, Union

# instantiate CumulusLogger
logger = CumulusLogger(name="orca")
RETRIES = 3  # number of times to retry.
BACKOFF_FACTOR = 2  # Value of the factor used to backoff


def get_configuration() -> Dict[str, str]:
    """
    Create a dictionary of configuration values based on environment variables
    parameter store information and other items needed to create the database.

    ```
    Environment Variables:
        PREFIX (str): Deployment prefix used to pull the proper AWS secret.
        AWS_REGION (str): AWS reserved runtime variable used to set boto3 client region.

    Parameter Store:
        <prefix>-orca-db-login-secret (string): The json string containing all the admin and user db login info.
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
    except Exception as e:
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


def execute_connection_with_error_handling(engine, sql: str, parameters: Dict):
    """
    Executes an SQL query from the database using the connection engine.

    Args:
        engine: The sqlalchemy engine to use for contacting the database.
        sql: SQL query to execute
        parameters: A dictionary

    Returns
        A ResultProxy?? Reference: https://docs.sqlalchemy.org/en/13/core/connections.html
    """
    INITIAL_BACKOFF_IN_SECONDS = 1  # Number of seconds to sleep the first time through.
    for retry in range(RETRIES + 1):
        try:
            with engine.begin() as connection:
                connection.execute(sql, parameters)
            break
        except exc.OperationalError as err:
            message = (
                "Failed to execute the query due to {err}. Retrying {retry} time(s)"
            )
            logger.error(message, err=err, retry=retry + 1)
            INITIAL_BACKOFF_IN_SECONDS = exponential_delay(
                INITIAL_BACKOFF_IN_SECONDS, BACKOFF_FACTOR
            )
            continue
    else:
        message = f"Failed to execute the query after {RETRIES} retries."
        logger.error(message)
        raise Exception(message)


# Define our exponential delay function
def exponential_delay(base_delay: int, exponential_backoff: int = 2) -> int:
    """
    Exponential delay function. This function is used for retries during failure.
    Args:
        base_delay: Number of seconds to wait between recovery failure retries.
        exponential_backoff: The multiplier by which the retry interval increases during each attempt.
    Returns:
        An integer which is multiplication of base_delay and exponential_backoff.
    Raises:
        None
    """
    try:
        _base_delay = int(base_delay)
        _exponential_backoff = int(exponential_backoff)
        delay = _base_delay + (random.randint(0, 1000) / 1000.0)  # nosec
        logger.debug(f"Performing back off retry sleeping {delay} seconds")
        time.sleep(delay)
        return _base_delay * _exponential_backoff
    except ValueError as ve:
        # Can't use f"" because of '{}' bug in CumulusLogger.
        logger.error("arguments are not integer. Raised ValueError: {ve}", ve=ve)
        raise ve
