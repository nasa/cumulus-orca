"""
Name: db_deploy.py

Description: Performs database installation and migration for the ORCA schema.
"""
# Imports
from shared_db import logger, get_configuration, get_root_connection
from sqlalchemy import text
from create_db import create_fresh_orca_install
from migrate_db import perform_migration
from typing import Any, Dict


# Globals
# Latest version of the ORCA schema.
LATEST_ORCA_SCHEMA_VERSION = 2


def handler(
    event: Dict[str, Any], context: object
) -> None:  # pylint: disable-msg=unused-argument
    """
    Lambda handler for db_deploy. The handler generates the database connection
    configuration information, sets logging handler information and calls the
    Lambda task function. See the `get_configuration()` function for
    information on the needed environment variables and parameter store names
    required by this Lambda.

    Args:
        event (Dict): Event dictionary passed by AWS.
        context (object): An object required by AWS Lambda. Unused.

    Raises:
        (Exception): If environment or secrets are unavailable.
    """
    # Set the logging
    logger.setMetadata(event, context)

    # Get the configuration
    config = get_configuration()

    return task(config)


def task(config: Dict[str, Any]) -> None:
    """
    Checks for the ORCA database and throws an error if it does not exist.
    Determines if a fresh install or a migration is needed for the ORCA
    schema.

    Args:
        config (Dict): Dictionary of connection information.

    Raises:
        (Exception): If database does not exist.
    """
    # Check if database exists, if not throw an error
    if not app_db_exists(config):
        logger.critical("The ORCA database disaster_recovery does not exist.")
        raise Exception("Missing application database.")

    # Determine if we need a fresh install or need a migration based on if the
    # orca schemas exist or not.
    if app_schema_exists(config):
        logger.debug("ORCA schema exists. Checking for schema versions ...")
        # Determine if  a migration is needed.
        current_version = get_migration_version(config)

        # If the current version is the same as the LATEST_ORCA_SCHEMA_VERSION
        # then nothing to do we are caught up.
        if current_version == LATEST_ORCA_SCHEMA_VERSION:
            # Nothing to do. Log it and exit
            logger.info("Current ORCA schema version detected. No migration needed!")
        else:
            # Run the migration
            logger.info("Performing migration of the ORCA schema.")
            perform_migration(current_version, LATEST_ORCA_SCHEMA_VERSION, config)

    else:
        # Run a fresh install
        logger.info("Performing full install of ORCA schema.")
        create_fresh_orca_install(config)


def app_db_exists(config):
    """
    Checks to see if the ORCA application database exists.

    Args:
        config (Dict): Dictionary with database connection information.

    Returns:
        (boolean): True/False if database exists
    """

    # SQL for checking database
    check_db_sql = text(
        """
        SELECT EXISTS(
            SELECT
                datname
            FROM
                pg_catalog.pg_database
            WHERE
                datname = 'disaster_recovery'
        );
    """
    )

    root_app_connection = get_root_connection(config)

    with root_app_connection.connect() as connection:
        # Run the query
        results = connection.execute(check_db_sql)
        for row in results:
            db_exists = row[0]

    return db_exists


def app_schema_exists(config):
    """
    Checks to see if the ORCA application schema exists.

    Args:
        config (Dict): Dictionary with database connection information.

    Returns:
        (boolean): True/False if schema exists
    """
    check_schema_sql = text(
        """
        SELECT EXISTS(
            SELECT
                schema_name
            FROM
                information_schema.schemata
            WHERE
                schema_name in ('orca', 'dr')
        );
    """
    )

    root_app_connection = get_root_connection(config, config["database"])

    with root_app_connection.connect() as connection:
        # Run the query
        results = connection.execute(check_schema_sql)
        for row in results:
            schema_exists = row[0]

    return schema_exists


def get_migration_version(config):
    """
    Queries the database version table and returns the latest version.

    Args:
        config (Dict): Dictionary with database connection information.

    Returns:
        (int): Version number of the currently installed ORCA schema
    """
    check_versions_table_sql = text(
        """
        SELECT EXISTS (
            SELECT
                table_name
            FROM
                information_schema.tables
            WHERE
                table_schema = 'orca'
            AND
                table_name = 'schema_versions'
        )
    """
    )

    # See if the schema_version table exists. If it doesn't then we are at
    # version 1 of the schema.
    schema_version = 1

    root_app_connection = get_root_connection(config, config["database"])

    with root_app_connection.connect() as connection:
        logger.debug("Checking for schema_versions table.")
        results = connection.execute(check_versions_table_sql)
        for row in results:
            table_exists = row[0]

        logger.debug(f"schema_versions table exists {table_exists}")

        # If table exists get the latest version from the table
        if table_exists:
            orca_schema_version_sql = text(
                """
                SELECT
                    version_id
                FROM
                    orca.schema_versions
                WHERE
                    is_latest = True
            """
            )

            logger.debug("Getting current schema version from table.")
            results = connection.execute(orca_schema_version_sql)
            for row in results:
                schema_version = row[0]

    return schema_version
