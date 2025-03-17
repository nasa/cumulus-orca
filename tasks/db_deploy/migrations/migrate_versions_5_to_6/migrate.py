"""
Name: migrate.py

Description: Migrates the ORCA schema from version 5 to version 6.
"""

from orca_shared.database.entities import PostgresConnectionInfo
from orca_shared.database.shared_db import LOGGER
from orca_shared.database.use_cases import create_admin_uri
from sqlalchemy import create_engine

import migrations.migrate_versions_5_to_6.migrate_sql as sql


def migrate_versions_5_to_6(
    config: PostgresConnectionInfo, is_latest_version: bool
) -> None:
    """
    Performs the migration of the ORCA schema from version 5 to version 6 of
    the ORCA schema. This includes adding the
    following tables:
    - storage_class
    and adding the following columns
    - files/storage_class_id    default 1 (GLACIER)

    Args:
        config: Connection information for the database.
        is_latest_version: Flag to determine if version 6 is the latest
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
        LOGGER.debug("Creating storage_class table ...")
        connection.execute(sql.storage_class_table_sql())
        LOGGER.info("Populating storage_class table ...")
        connection.execute(sql.storage_class_data_sql())
        LOGGER.info("storage_class table created.")

        # Add storage_class_id column to files table
        LOGGER.debug("Adding storage_class_id column to files table ...")
        connection.execute(sql.add_files_storage_class_id_column_sql())
        LOGGER.info("storage_class_id column added.")

        # Add storage_class columns to mismatches table
        LOGGER.debug("Adding storage_class column to mismatches table ...")
        connection.execute(sql.add_mismatch_storage_class_columns_sql())
        LOGGER.info("storage_class columns added.")

        # Add storage_class columns to phantoms table
        LOGGER.debug("Adding storage_class column to phantoms table ...")
        connection.execute(sql.add_phantom_storage_class_column_sql())
        LOGGER.info("storage_class column added.")

        # If v6 is the latest version, update the schema_versions table.
        if is_latest_version:
            LOGGER.debug("Populating the schema_versions table with data ...")
            connection.execute(sql.schema_versions_data_sql())
            LOGGER.info("Data added to the schema_versions table.")


