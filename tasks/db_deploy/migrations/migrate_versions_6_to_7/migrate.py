"""
Name: migrate.py

Description: Migrates the ORCA schema from version 5 to version 6.
"""

from orca_shared.database.entities import PostgresConnectionInfo
from orca_shared.database.shared_db import LOGGER
from orca_shared.database.use_cases import create_admin_uri
from sqlalchemy import create_engine

import migrations.migrate_versions_6_to_7.migrate_sql as sql


def migrate_versions_6_to_7(config: PostgresConnectionInfo, is_latest_version: bool) -> None:
    """
    Performs the migration of the ORCA schema from version 6 to version 7 of
    the ORCA schema. This includes adding the collection_id column to recovery_jobs and
    recovery_files and updating the relevant keys and relations.

    Args:
        config: Connection information for the database.
        is_latest_version: Flag to determine if version 7 is the latest
                                  schema version.
    Returns:
        None
    """
    # Get the admin engine to the app database
    user_admin_engine = \
        create_engine(create_admin_uri(config, LOGGER, config.user_database_name), future=True)

    with user_admin_engine.connect() as connection:

        # Change to DBO role and set search path
        LOGGER.debug("Changing to the dbo role to create objects ...")
        connection.execute(sql.text("SET ROLE orca_dbo;"))

        # Set the search path
        LOGGER.debug("Setting search path to the ORCA schema to create objects ...")
        connection.execute(sql.text("SET search_path TO orca, public;"))

        # Create storage_class table
        LOGGER.debug("Adding collection_id to recovery status tables ...")
        connection.execute(sql.add_collection_id_to_recovery_job_and_recovery_file_sql())
        LOGGER.info("collection_id added.")

        # If v7 is the latest version, update the schema_versions table.
        if is_latest_version:
            LOGGER.debug("Populating the schema_versions table with data ...")
            connection.execute(sql.schema_versions_data_sql())
            LOGGER.info("Data added to the schema_versions table.")

        # Commit if there are no issues
        connection.commit()
