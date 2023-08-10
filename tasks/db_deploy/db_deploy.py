"""
Name: db_deploy.py

Description: Performs database installation and migration for the ORCA schema.
"""

# Imports
import os
from typing import Any, Dict, List

from aws_lambda_powertools.utilities.typing import LambdaContext
from orca_shared.database.adapters.api import get_configuration
from orca_shared.database.entities import PostgresConnectionInfo
from orca_shared.database.shared_db import LOGGER, retry_operational_error
from orca_shared.database.use_cases import create_admin_uri
from sqlalchemy import create_engine, text
from sqlalchemy.future import Connection

from install.create_db import create_database, create_fresh_orca_install
from migrations.migrate_db import perform_migration

# Globals
# Latest version of the ORCA schema.
LATEST_ORCA_SCHEMA_VERSION = 7
MAX_RETRIES = 3


@LOGGER.inject_lambda_context
def handler(
    event: Dict[str, Any], context: LambdaContext
) -> None:  # pylint: disable-msg=unused-argument
    """
    Lambda handler for db_deploy. The handler generates the database connection
    configuration information, sets logging handler information and calls the
    Lambda task function. See the `shared_db.get_configuration(db_connect_info_secret_arn)`
    function for information on the needed environment variables and parameter store names
    required by this Lambda.

    Args:
        event (Dict): Event dictionary passed by AWS.
        context: This object provides information about the lambda invocation, function,
            and execution env.
    Environment Vars:
        DB_CONNECT_INFO_SECRET_ARN (string):
            Secret ARN of the AWS secretsmanager secret
        for connecting to the database.
        See shared_db.py's get_configuration for further details.

    Raises:
        Exception: If environment or secrets are unavailable.
    """
    # get the secret ARN from the env variable
    try:
        db_connect_info_secret_arn = os.environ["DB_CONNECT_INFO_SECRET_ARN"]
    except KeyError:
        LOGGER.error("DB_CONNECT_INFO_SECRET_ARN environment value not found.")
        raise

    # Get the secrets needed for database connections
    config = get_configuration(db_connect_info_secret_arn, LOGGER)

    # Get the ORCA bucket list
    orca_buckets = event.get("orcaBuckets", None)
    if type(orca_buckets) != list or len(orca_buckets) == 0:
        raise ValueError("orcaBuckets must be a valid list of ORCA S3 bucket names.")

    return task(config, orca_buckets)


def task(config: PostgresConnectionInfo, orca_buckets: List[str]) -> None:
    """
    Checks for the ORCA database and throws an error if it does not exist.
    Determines if a fresh install or a migration is needed for the ORCA
    schema.

    Args:
        config: Dictionary of connection information.
        orca_buckets: List of ORCA buckets needed to create partitioned tables.

    Raises:
        Exception: If database does not exist.
    """
    # Create the engine
    postgres_admin_engine = create_engine(create_admin_uri(config, LOGGER), future=True)

    # Connect as admin user to the postgres database
    with postgres_admin_engine.connect() as connection:
        # Check if database exists. If not, start from scratch.
        if not app_db_exists(connection, config.user_database_name):
            LOGGER.info(
                f"The ORCA database {config.user_database_name} does not exist, "
                "or the server could not be connected to."
            )
            create_database(config)
            create_fresh_orca_install(config, orca_buckets)

            return

    # Create the engine
    user_admin_engine = \
        create_engine(create_admin_uri(config, LOGGER, config.user_database_name), future=True)

    # Connect as admin user to config["user_database"] database.
    with user_admin_engine.connect() as connection:
        # reset user password
        reset_user_password(connection, config, config.user_username)
        # Determine if we need a fresh install or need a migration based on if
        # the orca schemas exist or not.
        if app_schema_exists(connection):
            LOGGER.debug("ORCA schema exists. Checking for schema versions.")
            # Determine if  a migration is needed.
            current_version = get_migration_version(connection)

            # If the current version is the same as the LATEST_ORCA_SCHEMA_VERSION
            # then nothing to do we are caught up.
            if current_version == LATEST_ORCA_SCHEMA_VERSION:
                # Nothing to do. Log it and exit
                LOGGER.info(
                    "Current ORCA schema version detected. No migration needed!"
                )
            else:
                # Run the migration
                LOGGER.info("Performing migration of the ORCA schema.")
                perform_migration(current_version, config, orca_buckets)

        else:
            # If we got here, the DB existed, but was not correctly populated for whatever reason.
            # Run a fresh install
            LOGGER.info("Performing full install of ORCA schema.")
            create_fresh_orca_install(config, orca_buckets)


# def app_db_exists(config: Dict[str, str]) -> bool:
@retry_operational_error(MAX_RETRIES)
def app_db_exists(connection: Connection, db_name: str) -> bool:
    """
    Checks to see if the ORCA application database exists.

    Args:
        connection (sqlalchemy.future.Connection): Database connection object.
        db_name: The name of the Orca database within the RDS cluster.

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
                datname = :db_name
        );
    """
    )

    # Run the query
    results = connection.execute(check_db_sql, {"db_name": db_name})
    for row in results.fetchall():
        db_exists = row[0]

    return db_exists


@retry_operational_error(MAX_RETRIES)
def reset_user_password(connection: Connection, config: PostgresConnectionInfo,
                        user_name: str):
    """
    Resets the ORCA user password.

    Args:
        connection (sqlalchemy.future.Connection): Database connection object.
        config: Dictionary of connection information.
        user_name: Username for the application user
    """
    # SQL for checking user exists
    check_user_sql = text(
        f"""
        SELECT EXISTS(
            SELECT
                usename
            FROM
                pg_user
            WHERE
                usename = '{user_name}'
        );
        """
    )

    # SQL for resetting user password
    reset_user_password_sql = text(
        f"""
        ALTER ROLE {user_name} 
            WITH ENCRYPTED PASSWORD :user_password ;
        """
    )

    # Run the query
    results = connection.execute(check_user_sql)
    for row in results.fetchall():
        user_exists = row[0]

    if user_exists:
        # Run the update
        connection.execute(
            reset_user_password_sql, {"user_password": config.user_password}
        )
        connection.commit()
        LOGGER.info(f"Password for {config.user_username} has been reset")

    else:
        LOGGER.warn(f"User {config.user_username} does not exist! No password reset performed.")


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

    LOGGER.debug("Checking for schema_versions table.")
    results = connection.execute(check_versions_table_sql)
    for row in results.fetchall():
        table_exists = row[0]

    LOGGER.debug(f"schema_versions table exists {table_exists}")

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
        LOGGER.debug("Getting current schema version from table.")
        results = connection.execute(orca_schema_version_sql)
        for row in results.fetchall():
            schema_version = row[0]

    return schema_version
