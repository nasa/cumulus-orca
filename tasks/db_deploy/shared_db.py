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

    Environment Vars:
        PREFIX (str): Deployment prefix used to pull the proper AWS secret.
        DATABASE_PORT (str): The database port. The standard is 5432
        DATABASE_NAME (str): The name of the application database being created.
        APPLICATION_USER (str): The name of the database application user.
        ROOT_USER (str): The name of the database super user.
        ROOT_DATABASE (str): The name of the root database for the instance.

    Parameter Store:
        <prefix>-drdb-user-pass (string): The password for the application user (APPLICATION_USER).
        <prefix>-drdb-host (string): The database host.
        <prefix>-drdb-admin-pass: The password for the admin user

    Args:
        None

    Returns:
        Configuration (Dict): Dictionary with all of the configuration information

    Raises:
        Exception (Exception): When variables or secrets are not available.
    """
    # Get the PREFIX
    logger.debug("Getting environment variable PREFIX value.")
    prefix = os.getenv("PREFIX", None)

    if prefix is None or len(prefix) == 0:
        logger.critical("Environment variable PREFIX is not set.")
        raise Exception("Environment variable PREFIX is not set.")

    # Get the PREFIX
    logger.debug("Getting environment variable AWS_REGION value.")
    aws_region = os.getenv("AWS_REGION", None)

    if aws_region is None or len(aws_region) == 0:
        logger.critical("Environment variable AWS_REGION is not set.")
        raise Exception("Environment variable AWS_REGION is not set.")

    # Create config dictionary
    config = {}

    # Create my config map that maps a key to the environment variable name
    config_map = {
        "database": "DATABASE_NAME",
        "port": "DATABASE_PORT",
        "app_user": "APPLICATION_USER",
        "root_user": "ROOT_USER",
        "root_database": "ROOT_DATABASE",
    }

    # Get the environment variables
    for key, value in config_map.items():
        logger.debug(f"Getting environment variable {value} value.")
        env_value = os.getenv(value, None)

        if env_value is None or len(env_value) == 0:
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
        root_user_pw = secretsmanager.get_secret_value(
            SecretId=f"{prefix}-drdb-admin-pass"
        )
        config["root_user_password"] = root_user_pw["SecretString"]

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
    Base function for creating a connection

    Args:
        host (str): Database host to connect to
        port (str): Database port to connect to
        database (str): Database name to connect to
        user (str): Database user to connect as
        password (str): Database password for the user
    """
    logger.debug("Creating URL object to connect to the database.")
    connection_url = URL.create(
        drivername="postgresql",
        username=kwargs["user"],
        password=kwargs["password"],
        host=kwargs["host"],
        port=kwargs["port"],
        database=kwargs["database"],
    )
    return create_engine(connection_url, future=True)


def get_root_connection(config: Dict[str, str], database: str = None) -> Engine:
    """
    Creates a connection to the database as a superuser.

    Args:
        config (Dict): Configuration containing connection information.
        database (str): Database for the root user to connect to. Defaults to root database.

    Returns
        Connection (): Connection object
    """
    # Determine database to use
    if database is None or len(database) == 0:
        root_database = config["root_database"]
    else:
        root_database = database

    logger.debug("Creating root user connection object.")
    logger.debug(f"Database set to {root_database} for the connection.")
    connection = _create_connection(
        host=config["host"],
        port=config["port"],
        database=root_database,
        user=config["root_user"],
        password=config["root_user_password"],
    )

    return connection
