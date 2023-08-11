"""
Name: migrate_db_v3.py

Description: Migrates the ORCA schema from version 2 to version 3.
"""
from orca_shared.database.entities import PostgresConnectionInfo
from orca_shared.database.shared_db import LOGGER
from orca_shared.database.use_cases import create_admin_uri
from sqlalchemy import create_engine

import migrations.migrate_versions_2_to_3.migrate_sql as sql


def migrate_versions_2_to_3(
    config: PostgresConnectionInfo, is_latest_version: bool
) -> None:
    """
    Performs the migration of the ORCA schema from version 2 to version 3 of
    the ORCA schema.
    Args:
        config: Connection information for the database.
        is_latest_version: Flag to determine if version 3 is the latest schema version.
    """
    # Get the admin engine to the app database
    user_admin_engine = create_engine(
        create_admin_uri(config, LOGGER, config.user_database_name), future=True
    )

    # Create new objects, users, roles, etc.
    with user_admin_engine.connect() as connection:
        # Change to DBO role and set search path
        LOGGER.debug("Changing to the dbo role to modify objects ...")
        connection.execute(sql.text("SET ROLE orca_dbo;"))
        LOGGER.debug("Setting search path to the ORCA schema to modify objects ...")
        connection.execute(sql.text("SET search_path TO orca, public;"))

        # Add column multipart_chunksize_mb to orca_files
        LOGGER.debug("Adding multipart_chunksize_mb column...")
        connection.execute(sql.add_multipart_chunksize_sql())
        LOGGER.info("multipart_chunksize_mb column added.")

        # If v3 is the latest version, update the schema_versions table.
        if is_latest_version:
            LOGGER.debug("Populating the schema_versions table with data ...")
            connection.execute(sql.schema_versions_data_sql())
            LOGGER.info("Data added to the schema_versions table.")

        # Commit if there are no issues
        connection.commit()
