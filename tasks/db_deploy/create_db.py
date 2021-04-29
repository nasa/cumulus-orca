"""
Name: create_db.py

Description: Creates the current version on the ORCA database.
"""
from shared_db import get_configuration, get_root_connection, logger
from orca_sql import *


def create_orca_database():
    # Check to see if database exists if it does not create the database.
    # root_connection = shared_db.get_root_connection(config)

    # TODO: Need to fix this so it is not in a transaction
    # with root_connection.connect() as conn:
    #    _create_app_database(conn, config["database"], config["root_user"])

    # Check to see if database exists if it does then perform more checks to
    # determine the next actions to take otherwise create the database, users,
    # roles and install the schema
    pass


def create_fresh_orca_install(config):
    """
    This task will create the ORCA roles, users, schema, and tables needed
    by the ORCA application as a fresh install.

    Args:
        config (Dict): Dictionary with database connection information
    """
    # Assume the database has been created at this point. Connect to the ORCA
    # database as a super user and create the roles, users,  schema, and
    # objects.
    root_app_connection = get_root_connection(config, config["database"])

    with root_app_connection.connect() as conn:
        # Create the roles, schema and user
        create_app_schema_role_users(conn, config)

        # Change to DBO role and set search path
        set_search_path_and_role(conn)

        # Create the database objects
        create_metadata_objects(conn)
        create_recovery_objects(conn)

        # If everything is good, commit.
        conn.commit()


def create_app_schema_role_users(connection, config):
    """
    Creates the ORCA application database schema, users and roles.

    Args:
        connection (sqlalchemy.engine.future.connect): Database connection.
    """
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
    connection.execute(app_user_sql(config["app_user_password"]))
    logger.info("ORCA application user created.")


def set_search_path_and_role(connection):
    """
    Sets the role to the dbo role to create/modify ORCA objects and sets the
    search_path to make the orca schema first. This must be run before any
    creations or modifications to ORCA objects in the ORCA schema.

    Args:
        connection (sqlalchemy.engine.future.connect): Database connection.
    """
    # Set the user and search_path for the install
    logger.debug("Changing to the dbo role to create objects ...")
    connection.execute(text("SET ROLE orca_dbo;"))

    logger.debug("Setting search path to the ORCA schema to create objects ...")
    connection.execute(text("SET search_path TO orca, public;"))


def create_metadata_objects(connection):
    """
    Create the ORCA application metadata tables used to manage application
    versions and other ORCA internal information in the proper order.
    - schema_versions

    Args:
        connection (sqlalchemy.engine.future.connect): Database connection.
    """
    # Create metadata tables
    logger.debug("Creating schema_versions table ...")
    connection.execute(schema_versions_table_sql())
    logger.info("schema_versions table created.")

    # Populate the table with data
    logger.debug("Populating the schema_versions table with data ...")
    connection.execute(schema_versions_data_sql())
    logger.info("Data added to the schema_versions table.")


def create_recovery_objects(connection):
    """
    Creates the ORCA recovery tables in the proper order.
    - recovery_status
    - recovery_job
    - recovery_table

    Args:
        connection (sqlalchemy.engine.future.connect): Database connection.
    """
    # Create recovery table objects
    # Create the recovery_status table
    logger.debug("Creating recovery_status table ...")
    connection.execute(recovery_status_table_sql())
    logger.info("recovery_status table created.")

    # Populate the table with data
    logger.debug("Populating the recovery_status table with data ...")
    connection.execute(recovery_status_data_sql())
    logger.info("Data added to the recovery_status table.")

    # Create the recovery_job and recovery_file tables
    logger.debug("Creating recovery_job table ...")
    connection.execute(recovery_job_table_sql())
    logger.info("recovery_job table created.")

    logger.debug("Creating recovery_file table ...")
    connection.execute(recovery_file_table_sql())
    logger.info("recovery_file table created.")
