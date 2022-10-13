import json
import logging
import os

import boto3

from orca_shared.database.entities.postgres_connection_info import (
    PostgresConnectionInfo,
)


def get_configuration(db_connect_info_secret_arn: str, logger: logging.Logger) \
        -> PostgresConnectionInfo:
    """
    Create a dictionary of configuration values based on environment variables
    and secret information items needed to create ORCA database connections.

    ```
    Environment Variables:
        AWS_REGION (str): AWS reserved runtime variable used to set boto3 client region.
    ```

    Args:
        db_connect_info_secret_arn: The secret ARN of the secret in AWS secretsmanager.
        logger: The logger to use.

    Returns:
        Configuration (Dict): Dictionary with all the configuration information.
                              The schema for the output is available [here](schemas/output.json).

    Raises:
        Exception: When variables or secrets are not available,
        or if configured values are illegal.
    """

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
        db_connect_info = json.loads(
            secretsmanager.get_secret_value(SecretId=db_connect_info_secret_arn)[
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
    result = PostgresConnectionInfo(
            admin_database_name=db_connect_info["admin_database"],
            admin_username=db_connect_info["admin_username"],
            admin_password=db_connect_info["admin_password"],
            user_username=db_connect_info["user_username"],
            user_password=db_connect_info["user_password"],
            user_database_name=db_connect_info["user_database"],
            host=db_connect_info["host"],
            port=db_connect_info["port"],
        )

    _validate_config(result, logger)
    return result

def _validate_config(config: PostgresConnectionInfo, logger: logging.Logger) -> None:
    _validate_username(config.user_username, "User", logger)
    _validate_username(config.admin_username, "Admin", logger)

    _validate_password(config.user_password, "User", logger)
    # todo: More validations? These were just pulled from db_deploy

def _validate_username(username: str, context: str, logger: logging.Logger) -> None:
    """
    Validates the given username against documented restrictions and Orca restrictions.
    https://www.postgresql.org/docs/7.0/syntax525.htm#:~:text=Names%20in%20SQL%20must%20begin,but%20they%20will%20be%20truncated.
    """
    if username is None or len(username) == 0:
        msg = f"{context} username must be non-empty."
        logger.critical(msg)
        raise Exception(msg)
    if len(username) > 63:  # todo: Postgres docs limit to 21 characters by default. Why 63?
        msg = f"{context} username must be less than 64 characters."
        logger.critical(msg)
        raise Exception(msg)

def _validate_password(password: str, context: str, logger: logging.Logger) -> None:
    if password is None or len(password) < 12:
        msg = f"{context} password must be at least 12 characters long."
        logger.critical(msg)
        raise Exception(msg)
