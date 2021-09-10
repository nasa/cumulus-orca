"""
Name: db_deploy.py

Description: Performs database installation and migration for the ORCA schema.
"""
# Imports
from orca_shared.shared_db import logger, get_configuration, get_admin_connection, retry_operational_error
from sqlalchemy import text
from sqlalchemy.future import Connection
from create_db import create_fresh_orca_install
from migrate_db import perform_migration
from typing import Any, Dict


# Globals
# Latest version of the ORCA schema.
LATEST_ORCA_SCHEMA_VERSION = 4
MAX_RETRIES = 3

def handler(
    event: Dict[str, Any], context: object
) -> None:  # pylint: disable-msg=unused-argument
    """
    Lambda handler for db_deploy. The handler generates the database connection
    configuration information, sets logging handler information and calls the
    Lambda task function. See the `shared_db.get_configuration()` function for
    information on the needed environment variables and parameter store names
    required by this Lambda.

    Args:
        event (Dict): Event dictionary passed by AWS.
        context (object): An object required by AWS Lambda.

    Raises:
        Exception: If environment or secrets are unavailable.
    """
    # Set the logging
    logger.setMetadata(event, context)

    # Get the configuration
    config = get_configuration()

    return task(config)

def task(config: Dict[str, str]) -> None:
    """
    Checks for the ORCA database and throws an error if it does not exist.
    Determines if a fresh install or a migration is needed for the ORCA
    schema.

    Args:
        config (Dict): Dictionary of connection information.

    Raises:
        Exception: If database does not exist.
    """
    # Create the engines
    postgres_admin_engine = get_admin_connection(config)
    user_admin_engine = get_admin_connection(config, config["user_database"])

    # Connect as admin user to the postgres database
    with postgres_admin_engine.connect() as connection:
        # Check if database exists, if not throw an error
        if not app_db_exists(connection):
            logger.critical("The ORCA database disaster_recovery does not exist.")
            # TO DO ORCA-233: Add db creation code here and remove the raise Exception error
            raise Exception("Missing application database.")

    # Connect as admin user to disaster_recovery database.
    with user_admin_engine.connect() as connection:
        # Determine if we need a fresh install or need a migration based on if
        # the orca schemas exist or not.
        if app_schema_exists(connection):
            logger.debug("ORCA schema exists. Checking for schema versions.")
            # Determine if  a migration is needed.
            current_version = get_migration_version(connection)

            # If the current version is the same as the LATEST_ORCA_SCHEMA_VERSION
            # then nothing to do we are caught up.
            if current_version == LATEST_ORCA_SCHEMA_VERSION:
                # Nothing to do. Log it and exit
                logger.info(
                    "Current ORCA schema version detected. No migration needed!"
                )
            else:
                # Run the migration
                logger.info("Performing migration of the ORCA schema.")
                perform_migration(current_version, config)

        else:
            # Run a fresh install
            logger.info("Performing full install of ORCA schema.")
            create_fresh_orca_install(config)


# def app_db_exists(config: Dict[str, str]) -> bool:
@retry_operational_error(MAX_RETRIES)
def app_db_exists(connection: Connection) -> bool:
    """
    Checks to see if the ORCA application database exists.

    Args:
        connection (sqlalchemy.future.Connection): Database connection object.

    Returns:
        True/False (bool): True if database exists.
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

    # Run the query
    results = connection.execute(check_db_sql)
    for row in results.fetchall():
        db_exists = row[0]

    return db_exists

def app_schema_exists(connection: Connection) -> bool:
    """
    Checks to see if the ORCA application schema exists.

    Args:
        connection (sqlalchemy.future.Connection): Database connection object.

    Returns:
        True/False (bool): True if ORCA schema exists.
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

    # Run the query
    results = connection.execute(check_schema_sql)
    for row in results.fetchall():
        schema_exists = row[0]

    return schema_exists

def app_version_table_exists(connection: Connection) -> bool:
    """
    Checks to see if the orca.schema_version table exists.

    Args:
        connection (sqlalchemy.future.Connection): Database connection object.

    Returns:
        True/False (bool): True if ORCA schema_version table exists.
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

    logger.debug("Checking for schema_versions table.")
    results = connection.execute(check_versions_table_sql)
    for row in results.fetchall():
        table_exists = row[0]

    logger.debug(f"schema_versions table exists {table_exists}")

    return table_exists

def get_migration_version(connection: Connection) -> int:
    """
    Queries the database version table and returns the latest version.

    Args:
        connection (sqlalchemy.future.Connection): Database connection object.

    Returns:
        Schema Version (int): Version number of the currently installed ORCA schema
    """
    # See if the schema_version table exists. If it doesn't then we are at
    # version 1 of the schema.
    schema_version = 1

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

    # If table exists get the latest version from the table
    if app_version_table_exists(connection):
        logger.debug("Getting current schema version from table.")
        results = connection.execute(orca_schema_version_sql)
        for row in results.fetchall():
            schema_version = row[0]

    return schema_version
