import logging
from typing import Any

from sqlalchemy.engine import URL

from orca_shared.database.entities.postgres_connection_info import (
    PostgresConnectionInfo,
)


def create_user_uri(db_connect_info: PostgresConnectionInfo, logger: logging.Logger) -> str:
    """
    Creates a connection URI for application database as the application
    database user.

    Args:
        db_connect_info: Configuration containing connection information.
        logger: The logger to use.

    Returns:
        URI for connecting to the database.
    """

    logger.debug("Creating application user connection object.")
    return _create_connection_uri(
        logger=logger,
        host=db_connect_info.host,
        port=db_connect_info.port,
        database=db_connect_info.user_database_name,
        username=db_connect_info.user_username,
        password=db_connect_info.user_password,
    )


def create_admin_uri(db_connect_info: PostgresConnectionInfo, logger: logging.Logger,
                     database_name_overwrite: str = None) -> str:
    """
    Creates a connection URI for a database as a superuser.

    Args:
        db_connect_info: Configuration containing connection information.
        logger: The logger to use.
        database_name_overwrite: Database to connect to. Defaults to admin_database.

    Returns:
        URI for connecting to the database.
    """
    # Determine database to use
    if database_name_overwrite is None or len(database_name_overwrite) == 0:
        admin_database = db_connect_info.admin_database_name
    else:
        admin_database = database_name_overwrite

    logger.debug("Creating admin user connection object.")
    logger.debug(f"Database set to {admin_database} for the connection.")
    return _create_connection_uri(
        logger=logger,
        host=db_connect_info.host,
        port=db_connect_info.port,
        database=admin_database,
        username=db_connect_info.admin_username,
        password=db_connect_info.admin_password,
    )


def _create_connection_uri(logger: logging.Logger, **kwargs: Any) -> str:
    """
    Base function for creating a connection URI for a database.

    Args:
        logger: The logger to use.
        host (str): Database host to connect to
        port (str): Database port to connect to
        database (str): Database name to connect to
        username (str): Database user to connect as
        password (str): Database password for the user

    Returns:
        URI for connecting to the database.
    """
    logger.debug("Creating URL object to connect to the database.")
    return URL.create(drivername="postgresql", **kwargs).render_as_string(hide_password=False)
