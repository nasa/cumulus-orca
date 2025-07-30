"""
Name: migrate.py

Description: Migrates the ORCA schema from version 7 to version 8.
"""

from orca_shared.database.entities import PostgresConnectionInfo
from orca_shared.database.shared_db import LOGGER
from orca_shared.database.use_cases import create_admin_uri
from sqlalchemy import create_engine

import migrations.migrate_versions_7_to_8.migrate_sql as sql


def migrate_versions_7_to_8(
    config: PostgresConnectionInfo, is_latest_version: bool
) -> None:
    """
    Performs the migration of the ORCA schema from version 7 to version 8 of
    the ORCA schema. This includes adding the delete_file column to files.

    Args:
        config: Connection information for the database.
        is_latest_version: Flag to determine if version 8 is the latest
                                  schema version.
    Returns:
        None
    """
    # Get the admin engine to the app database
    user_admin_engine = create_engine(
        create_admin_uri(config, LOGGER, config.user_database_name), future=True
    )

    with user_admin_engine.begin() as connection:

        # Change to DBO role and set search path
        LOGGER.debug("Changing to the dbo role to create objects ...")
        connection.execute(sql.text("SET ROLE orca_dbo;"))

        # Set the search path
        LOGGER.debug("Setting search path to the ORCA schema to create objects ...")
        connection.execute(sql.text("SET search_path TO orca, public;"))

        # Create storage_class table
        LOGGER.debug("Adding delete_file column to files table ...")
        connection.execute(
            sql.add_delete_file_to_files_table_sql()
        )
        LOGGER.info("delete_file column added to files table.")

        # If v8 is the latest version, update the schema_versions table.
        if is_latest_version:
            LOGGER.debug("Populating the schema_versions table with data ...")
            connection.execute(sql.schema_versions_data_sql())
            LOGGER.info("Data added to the schema_versions table.")
