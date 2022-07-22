"""
Name: migrate.py

Description: Migrates the ORCA schema from version 5 to version 6.
"""
from typing import Dict

from orca_shared.database.shared_db import get_admin_connection, logger

import migrations.migrate_versions_5_to_6.migrate_sql as sql


def migrate_versions_5_to_6(config: Dict[str, str], is_latest_version: bool) -> None:
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
    admin_app_connection = get_admin_connection(config, config["user_database"])

    with admin_app_connection.connect() as connection:

        # Change to DBO role and set search path
        logger.debug("Changing to the dbo role to create objects ...")
        connection.execute(sql.text("SET ROLE orca_dbo;"))

        # Set the search path
        logger.debug("Setting search path to the ORCA schema to create objects ...")
        connection.execute(sql.text("SET search_path TO orca, public;"))

        # Create storage_class table
        logger.debug("Creating storage_class table ...")
        connection.execute(sql.storage_class_table_sql())
        logger.info("Populating storage_class table ...")
        connection.execute(sql.storage_class_data_sql())
        logger.info("storage_class table created.")

        # Add storage_class_id column to files table
        logger.debug("Adding storage_class_id column to files table ...")
        connection.execute(sql.add_files_storage_class_id_column_sql())
        logger.info("storage_class_id column added.")

        # Add storage_class columns to mismatches table
        logger.debug("Adding storage_class column to mismatches table ...")
        connection.execute(sql.add_mismatch_storage_class_columns_sql())
        logger.info("storage_class columns added.")

        # Add storage_class columns to phantoms table
        logger.debug("Adding storage_class column to phantoms table ...")
        connection.execute(sql.add_phantom_storage_class_column_sql())
        logger.info("storage_class column added.")

        # If v6 is the latest version, update the schema_versions table.
        if is_latest_version:
            logger.debug("Populating the schema_versions table with data ...")
            connection.execute(sql.schema_versions_data_sql())
            logger.info("Data added to the schema_versions table.")

        # Commit if there are no issues
        connection.commit()
