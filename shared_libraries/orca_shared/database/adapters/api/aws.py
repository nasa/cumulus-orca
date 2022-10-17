import json
import logging
import os

import boto3

from orca_shared.database.entities.postgres_connection_info import (
    PostgresConnectionInfo,
)


def get_configuration(db_connect_info_secret_arn: str, LOGGER: logging.Logger) \
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
        LOGGER: The logger to use.

    Returns:
        Configuration (Dict): Dictionary with all the configuration information.
                              The schema for the output is available [here](schemas/output.json).

    Raises:
        Exception (Exception): When variables or secrets are not available.
    """

    # Get the AWS_REGION defined runtime environment reserved variable
    LOGGER.debug("Getting environment variable AWS_REGION value.")
    aws_region = os.getenv("AWS_REGION", None)

    if aws_region is None or len(aws_region) == 0:
        message = "Runtime environment variable AWS_REGION is not set."
        LOGGER.critical(message)
        raise Exception(message)

    try:
        LOGGER.debug("Creating secretsmanager resource.")
        secretsmanager = boto3.client("secretsmanager", region_name=aws_region)

        LOGGER.debug(
            "Retrieving db login info for both user and admin as a dictionary."
        )
        db_connect_info = json.loads(
            secretsmanager.get_secret_value(SecretId=db_connect_info_secret_arn)[
                "SecretString"
            ]
        )
        LOGGER.debug(
            "Successfully retrieved db login info for both user and admin as a dictionary."
        )
    except Exception:
        LOGGER.critical("Failed to retrieve secret.")
        raise Exception("Failed to retrieve secret manager value.")

    # return the config dict
    return PostgresConnectionInfo(
            admin_database_name=db_connect_info["admin_database"],
            admin_username=db_connect_info["admin_username"],
            admin_password=db_connect_info["admin_password"],
            user_username=db_connect_info["user_username"],
            user_password=db_connect_info["user_password"],
            user_database_name=db_connect_info["user_database"],
            host=db_connect_info["host"],
            port=db_connect_info["port"],
        )
