"""
Name: migrate_db_v2.py

Description: Migrates the ORCA schema from version 1 to version 2.
"""
from typing import Dict
from migrations.migrate_versions_1_to_2.migrate_sql_v2 import *
from orca_shared.database.shared_db import get_admin_connection, logger

def migrate_versions_1_to_2(config: Dict[str, str], is_latest_version: bool) -> None:
    """
    Performs the migration of the ORCA schema from version 1 to version 2 of
    the ORCA schema.
    Args:
        config (Dict): Connection information for the database.
        is_latest_version (bool): Flag to determine if version 2 is the latest schema version.

    Returns:
        None
    """
    # Get the admin engine to the app database
    admin_app_connection = get_admin_connection(config, config["user_database"])

    # Create all of the new objects, users, roles, etc.
    with admin_app_connection.connect() as connection:
        # Create the roles first since they are needed by schema and users
        logger.debug("Creating the ORCA dbo role ...")
        connection.execute(dbo_role_sql(config["user_database"]))
        logger.info("ORCA dbo role created.")

        logger.debug("Creating the ORCA app role ...")
        connection.execute(app_role_sql(config["user_database"]))
        logger.info("ORCA app role created.")

        # Create the schema next
        logger.debug("Creating the ORCA schema ...")
        connection.execute(orca_schema_sql())
        logger.info("ORCA schema created.")

        # Create the users last
        logger.debug("Creating the ORCA application user ...")
        connection.execute(app_user_sql(config["user_password"]))
        logger.info("ORCA application user created.")

        # Change to DBO role and set search path
        logger.debug("Changing to the dbo role to create objects ...")
        connection.execute(text("SET ROLE orca_dbo;"))

        logger.debug("Setting search path to the ORCA schema to create objects ...")
        connection.execute(text("SET search_path TO orca, public;"))

        # Create the new tables. We do this individually in case the create
        # function changes over the various versions.
        logger.debug("Creating schema_versions table ...")
        connection.execute(schema_versions_table_sql())
        logger.info("schema_versions table created.")

        logger.debug("Creating recovery_status table ...")
        connection.execute(recovery_status_table_sql())
        logger.info("recovery_status table created.")

        logger.debug("Creating recovery_job table ...")
        connection.execute(recovery_job_table_sql())
        logger.info("recovery_job table created.")

        logger.debug("Creating recovery_file table ...")
        connection.execute(recovery_file_table_sql())
        logger.info("recovery_file table created.")

        # Commit if there is no issues
        connection.commit()

    # Migrate the data and drop old tables, schema, users, roles
    with admin_app_connection.connect() as connection:
        # Change to Postgres role and set search path
        logger.debug("Changing to the postgres role ...")
        connection.execute(text("RESET ROLE;"))

        # Set the search path
        logger.debug("Setting search path to the ORCA and dr schema ...")
        connection.execute(text("SET search_path TO orca, dr, public;"))

        # Add static data to tables
        logger.debug("Populating the recovery_status table with data ...")
        connection.execute(recovery_status_data_sql())
        logger.info("Data added to the recovery_status table.")

        # Migrate the data from the old table to the new tables
        logger.debug("Migrating data from request_status to recovery_job ...")
        connection.execute(migrate_recovery_job_data_sql())
        logger.info("Data migrated to recovery_job table.")

        logger.debug("Migrating data from request_status to recovery_file ...")
        connection.execute(migrate_recovery_file_data_sql())
        logger.info("Data migrated to recovery_file table.")

        # Drop the old objects
        logger.debug("Dropping dr.request_status table ...")
        connection.execute(drop_request_status_table_sql())
        logger.info("dr.request_status table removed.")

        logger.debug("Changing to the dbo role ...")
        connection.execute(text("SET ROLE dbo;"))

        logger.debug("Dropping dr schema ...")
        connection.execute(drop_dr_schema_sql())
        logger.info("dr schema removed.")

        logger.debug("Changing to the postgres role ...")
        connection.execute(text("RESET ROLE;"))

        # Remove the users and roles
        logger.debug("Dropping drdbo_role role ...")
        connection.execute(drop_drdbo_role_sql(config["user_database"]))
        logger.info("drdbo_role role removed.")

        logger.debug("Dropping dr_role role ...")
        connection.execute(drop_dr_role_sql(config["user_database"]))
        logger.info("dr_role role removed.")

        logger.debug("Dropping dbo user ...")
        connection.execute(drop_dbo_user_sql(config["user_database"]))
        logger.info("dbo user removed")

        logger.debug("Dropping druser user ...")
        connection.execute(drop_druser_user_sql())
        logger.info("druser user removed.")

        # If v2 is the latest version, update the schema_versions table.
        if is_latest_version:
            logger.debug("Populating the schema_versions table with data ...")
            connection.execute(schema_versions_data_sql())
            logger.info("Data added to the schema_versions table.")

        # Commit if there is no issues
        connection.commit()