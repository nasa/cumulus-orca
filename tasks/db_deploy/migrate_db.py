"""
Name: migrate_db.py

Description: Migrates the current ORCA schema version to the latest version.
"""
from typing import Dict
from orca_sql import *
from orca_shared.shared_db import get_admin_connection, logger, retry_operational_error

MAX_RETRIES = 3

def perform_migration(current_schema_version: int, config: Dict[str, str]) -> None:
    """
    Performs a migration of the ORCA database. Determines the order and
    migrations to run.

    Args:
        current_schema_version (int): Current version of the ORCA schema
        config (Dict): Dictionary containing database connection information

    Returns:
        None
    """
    # Determine migrations to run based on current_schema_version and
    # update the versions table based on the latest_schema_version.
    if current_schema_version == 1:
        # Run migrations from version 1 to version 2
        migrate_versions_1_to_2(config, False)
        current_schema_version = 2
        # Run migrations from version 2 to version 3
        migrate_versions_2_to_3(config, True)

    elif current_schema_version == 2:
        # Run migrations from version 2 to the latest version
        # in this case version 3 is the latest so we set the latest version
        # flag to True
        migrate_versions_2_to_3(config, True)

@retry_operational_error(MAX_RETRIES)
def migrate_versions_2_to_3(config: Dict[str, str], is_latest_version: bool) -> None:
    """
    Performs the migration of the ORCA schema from version 2 to version 3 of
    the ORCA schema.

    Args:
        config (Dict): Connection information for the database.
        is_latest_version (bool): Flag to determine if version 3 is the latest schema version.

    Returns:
        None
    """
    # Get the admin engine to the app database
    admin_app_connection = get_admin_connection(config, config["user_database"])

    with admin_app_connection.connect() as connection:
        #Create ORCA inventory tables
        #Create providers table
        logger.debug("Creating providers table ...")
        connection.execute(providers_table_sql())
        logger.info("providers table created.")

        #Create collections table
        logger.debug("Creating collections table ...")
        connection.execute(collections_table_sql())
        logger.info("collections table created.")

        #Create provider and collection cross reference table
        logger.debug("Creating provider and collection cross reference table ...")
        connection.execute(provider_collection_xref_table_sql())
        logger.info("provider and collection cross reference table created.")

        #Create granules table
        logger.debug("Creating granules table ...")
        connection.execute(granules_table_sql())
        logger.info("granules table created.")

        #Create files table
        logger.debug("Creating files table ...")
        connection.execute(files_table_sql())
        logger.info("files table created.")

        # Commit if there is no issues
        connection.commit()

        # If v3 is the latest version, update the schema_versions table.
        if is_latest_version:
            logger.debug("Populating the schema_versions table with data ...")
            connection.execute(schema_versions_data_sql())
            logger.info("Data added to the schema_versions table.")

        # Commit if there is no issues
        connection.commit()

@retry_operational_error(MAX_RETRIES)
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
        connection.execute(dbo_role_sql())
        logger.info("ORCA dbo role created.")

        logger.debug("Creating the ORCA app role ...")
        connection.execute(app_role_sql())
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
        connection.execute(drop_drdbo_role_sql())
        logger.info("drdbo_role role removed.")

        logger.debug("Dropping dr_role role ...")
        connection.execute(drop_dr_role_sql())
        logger.info("dr_role role removed.")

        logger.debug("Dropping dbo user ...")
        connection.execute(drop_dbo_user_sql())
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