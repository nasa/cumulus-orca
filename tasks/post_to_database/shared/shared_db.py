"""
Name: shared_db.py
Description: Shared library for database objects needed by the various libraries.
"""

import os
import boto3
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.future import Engine
from cumulus_logger import CumulusLogger
from typing import Any, List, Dict, Optional, Union

# instantiate CumulusLogger
logger = CumulusLogger(name="db_deploy")


def get_configuration() -> Dict[str, str]:
    """
    Create a dictionary of configuration values based on environment variables
    parameter store information and other items needed to create the database.
    ```
    Environment Variables:
        PREFIX (str): Deployment prefix used to pull the proper AWS secret.
        AWS_REGION (str): AWS reserved runtime variable used to set boto3 client region.
        DATABASE_PORT (str): The database port. The standard is 5432
        DATABASE_NAME (str): The name of the application database.
        APPLICATION_USER (str): The name of the database application user.
        ADMIN_USER (str): *OPTIONAL* The name of the database super user (postgres).
        ADMIN_DATABASE (str): *OPTIONAL* The name of the admin database for the instance (postgres).
    Parameter Store:
        <prefix>-drdb-user-pass (string): The password for the application user (APPLICATION_USER).
        <prefix>-drdb-host (string): The database host.
        <prefix>-drdb-admin-pass: The password for the admin user
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

    # Create config dictionary
    config = {}

    # Create my config map that maps a key to the environment variable name
    config_map = {
        "database": "DATABASE_NAME",
        "port": "DATABASE_PORT",
        "app_user": "APPLICATION_USER",
        "admin_user": "ADMIN_USER",
        "admin_database": "ADMIN_DATABASE",
    }

    # Get the environment variables
    for key, value in config_map.items():
        logger.debug(f"Getting environment variable {value} value.")
        env_value = os.getenv(value, None)

        if env_value is None or len(env_value) == 0:
            # Set defaults for optional env variables
            if key in ["admin_user", "admin_database"]:
                env_value = "postgres"
                logger.info(f"Setting variable {value} value to {env_value}")
            else:
                message = f"Environment variable {value} is not set and is required"
                logger.critical(message)
                raise Exception(message)

        config[key] = env_value

    # Get the secret variables
    try:
        logger.debug("Creating secretsmanager resource.")
        secretsmanager = boto3.client("secretsmanager", region_name=aws_region)

        logger.debug("Retrieving database application user password.")
        app_user_pw = secretsmanager.get_secret_value(
            SecretId=f"{prefix}-drdb-user-pass"
        )
        config["app_user_password"] = app_user_pw["SecretString"]

        logger.debug("Retrieving database root user password.")
        admin_user_pw = secretsmanager.get_secret_value(
            SecretId=f"{prefix}-drdb-admin-pass"
        )
        config["admin_user_password"] = admin_user_pw["SecretString"]

        logger.debug("Retrieving database host information.")
        db_host = secretsmanager.get_secret_value(SecretId=f"{prefix}-drdb-host")
        config["host"] = db_host["SecretString"]

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
        username=config["admin_user"],
        password=config["admin_user_password"],
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
        database=config["database"],
        username=config["app_user"],
        password=config["app_user_password"],
    )

    return connection
