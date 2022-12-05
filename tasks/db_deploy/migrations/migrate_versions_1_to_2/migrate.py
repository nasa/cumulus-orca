"""
Name: migrate_db_v2.py

Description: Migrates the ORCA schema from version 1 to version 2.
"""
from orca_shared.database.entities import PostgresConnectionInfo
from orca_shared.database.shared_db import LOGGER
from orca_shared.database.use_cases import create_admin_uri
from sqlalchemy import create_engine

import migrations.migrate_versions_1_to_2.migrate_sql as sql


def migrate_versions_1_to_2(config: PostgresConnectionInfo, is_latest_version: bool) -> None:
    """
    Performs the migration of the ORCA schema from version 1 to version 2 of
    the ORCA schema.
    Args:
        config: Connection information for the database.
        is_latest_version: Flag to determine if version 2 is the latest schema version.

    Returns:
        None
    """
    if config.user_username is None or len(config.user_username) == 0:
        LOGGER.critical("Username must be non-empty.")
        raise Exception("Username must be non-empty.")
    if len(config.user_username) > 63:
        LOGGER.critical("Username must be less than 64 characters.")
        raise Exception("Username must be less than 64 characters.")

    if config.user_password is None or len(config.user_password) < 12:
        LOGGER.critical("User password must be at least 12 characters long.")
        raise Exception("User password must be at least 12 characters long.")

    # Get the admin engine to the app database
    user_admin_engine = \
        create_engine(create_admin_uri(config, LOGGER, config.user_database_name), future=True)

    # Create all the new objects, users, roles, etc.
    with user_admin_engine.connect() as connection:
        # Create the roles first since they are needed by schema and users
        LOGGER.debug("Creating the ORCA dbo role ...")
        connection.execute(
            sql.dbo_role_sql(config.user_database_name, config.admin_username)
        )
        LOGGER.info("ORCA dbo role created.")

        LOGGER.debug("Creating the ORCA app role ...")
        connection.execute(sql.app_role_sql(config.user_database_name))
        LOGGER.info("ORCA app role created.")

        # Create the schema next
        LOGGER.debug("Creating the ORCA schema ...")
        connection.execute(sql.orca_schema_sql())
        LOGGER.info("ORCA schema created.")

        # Create the users last
        LOGGER.debug("Creating the ORCA application user ...")
        # https://bugs.earthdata.nasa.gov/browse/ORCA-461
        connection.execute(
            sql.app_user_sql(config.user_username),
            [
                {
                    "user_name": config.user_username,
                    "user_password": config.user_password,
                }
            ],
        )
        LOGGER.info("ORCA application user created.")

        # Change to DBO role and set search path
        LOGGER.debug("Changing to the dbo role to create objects ...")
        connection.execute(sql.text("SET ROLE orca_dbo;"))

        LOGGER.debug("Setting search path to the ORCA schema to create objects ...")
        connection.execute(sql.text("SET search_path TO orca, public;"))

        # Create the new tables. We do this individually in case the create
        # function changes over the various versions.
        LOGGER.debug("Creating schema_versions table ...")
        connection.execute(sql.schema_versions_table_sql())
        LOGGER.info("schema_versions table created.")

        LOGGER.debug("Creating recovery_status table ...")
        connection.execute(sql.recovery_status_table_sql())
        LOGGER.info("recovery_status table created.")

        LOGGER.debug("Creating recovery_job table ...")
        connection.execute(sql.recovery_job_table_sql())
        LOGGER.info("recovery_job table created.")

        LOGGER.debug("Creating recovery_file table ...")
        connection.execute(sql.recovery_file_table_sql())
        LOGGER.info("recovery_file table created.")

        # Commit if there are no issues
        connection.commit()

    # Migrate the data and drop old tables, schema, users, roles
    with user_admin_engine.connect() as connection:
        # Change to admin role and set search path
        LOGGER.debug("Changing to the admin role ...")
        connection.execute(sql.text("RESET ROLE;"))

        # Set the search path
        LOGGER.debug("Setting search path to the ORCA and dr schema ...")
        connection.execute(sql.text("SET search_path TO orca, dr, public;"))

        # Add static data to tables
        LOGGER.debug("Populating the recovery_status table with data ...")
        connection.execute(sql.recovery_status_data_sql())
        LOGGER.info("Data added to the recovery_status table.")

        # Migrate the data from the old table to the new tables
        LOGGER.debug("Migrating data from request_status to recovery_job ...")
        connection.execute(sql.migrate_recovery_job_data_sql())
        LOGGER.info("Data migrated to recovery_job table.")

        LOGGER.debug("Migrating data from request_status to recovery_file ...")
        connection.execute(sql.migrate_recovery_file_data_sql())
        LOGGER.info("Data migrated to recovery_file table.")

        # Drop the old objects
        LOGGER.debug("Dropping dr.request_status table ...")
        connection.execute(sql.drop_request_status_table_sql())
        LOGGER.info("dr.request_status table removed.")

        LOGGER.debug("Changing to the dbo role ...")
        connection.execute(sql.text("SET ROLE dbo;"))

        LOGGER.debug("Dropping dr schema ...")
        connection.execute(sql.drop_dr_schema_sql())
        LOGGER.info("dr schema removed.")

        LOGGER.debug("Changing to the admin role ...")
        connection.execute(sql.text("RESET ROLE;"))

        # Remove the users and roles
        LOGGER.debug("Dropping drdbo_role role ...")
        connection.execute(sql.drop_drdbo_role_sql(config.user_database_name))
        LOGGER.info("drdbo_role role removed.")

        LOGGER.debug("Dropping dr_role role ...")
        connection.execute(sql.drop_dr_role_sql(config.user_database_name))
        LOGGER.info("dr_role role removed.")

        LOGGER.debug("Dropping dbo user ...")
        connection.execute(sql.drop_dbo_user_sql(config.user_database_name))
        LOGGER.info("dbo user removed")

        LOGGER.debug("Dropping druser user ...")
        connection.execute(sql.drop_druser_user_sql())
        LOGGER.info("druser user removed.")

        # If v2 is the latest version, update the schema_versions table.
        if is_latest_version:
            LOGGER.debug("Populating the schema_versions table with data ...")
            connection.execute(sql.schema_versions_data_sql())
            LOGGER.info("Data added to the schema_versions table.")

        # Commit if there are no issues
        connection.commit()
