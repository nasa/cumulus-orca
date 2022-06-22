"""
Name: create_db.py

Description: Creates the current version on the ORCA database.
"""
from typing import Dict, List

from orca_shared.database.shared_db import get_admin_connection, logger
from orca_shared.reconciliation.shared_reconciliation import (
    get_partition_name_from_bucket_name,
)
from sqlalchemy.future import Connection

import install.orca_sql as sql


def create_fresh_orca_install(config: Dict[str, str], orca_buckets: List[str]) -> None:
    """
    This task will create the ORCA roles, users, schema, and tables needed
    by the ORCA application as a fresh install.

    Args:
        config (Dict): Dictionary with database connection information
        orca_buckets: List[str]): List of ORCA buckets needed to create
                                  partitioned tables for reporting.

    Returns:
        None
    """
    # Assume the database has been created at this point. Connect to the ORCA
    # database as a super user and create the roles, users,  schema, and
    # objects.
    admin_app_connection = get_admin_connection(config, config["user_database"])

    with admin_app_connection.connect() as conn:
        # Create the roles, schema and user
        create_app_schema_role_users(
            conn,
            config["user_username"],
            config["user_password"],
            config["user_database"],
            config["admin_username"]
        )

        # Change to DBO role and set search path
        set_search_path_and_role(conn)

        # Create the database objects
        create_metadata_objects(conn)
        create_recovery_objects(conn)
        create_inventory_objects(conn)

        # Create internal reconciliation objects
        create_internal_reconciliation_objects(conn, orca_buckets)

        # If everything is good, commit.
        conn.commit()


def create_database(config: Dict[str, str]) -> None:
    """
    Creates the orca database
    """
    # Create the connection as an admin
    postgres_admin_engine = get_admin_connection(config)
    # Connect as admin user to the postgres database
    with postgres_admin_engine.connect() as connection:
        # Code to create the database
        connection.execute(
            sql.commit_sql()
        )  # exit the default transaction to allow database creation.
        connection.execute(sql.app_database_sql(config["user_database"], config["admin_username"]))
        connection.execute(sql.app_database_comment_sql(config["user_database"]))
        logger.info("Database created.")


def create_app_schema_role_users(
    connection: Connection, app_username: str, app_password: str, db_name: str, admin_username: str
) -> None:
    """
    Creates the ORCA application database schema, users and roles.

    Args:
        connection (sqlalchemy.future.Connection): Database connection.
        app_username: The name for the created scoped user.
        app_password: The password for the created scoped user.
        db_name: The name of the Orca database within the RDS cluster.
        admin_username: The name of the admin user for the Orca database.

    Returns:
        None
    """
    # Create the roles first since they are needed by schema and users
    logger.debug("Creating the ORCA dbo role ...")
    connection.execute(sql.dbo_role_sql(db_name, admin_username))
    logger.info("ORCA dbo role created.")

    logger.debug("Creating the ORCA app role ...")
    connection.execute(sql.app_role_sql(db_name))
    logger.info("ORCA app role created.")

    # Create the schema next
    logger.debug("Creating the ORCA schema ...")
    connection.execute(sql.orca_schema_sql())
    logger.info("ORCA schema created.")

    # Create the users last
    logger.debug("Creating the ORCA application user ...")
    connection.execute(sql.app_user_sql(app_username, app_password))
    logger.info("ORCA application user created.")

    # Create extension for the database
    logger.debug("Creating extension aws_s3 ...")
    connection.execute(sql.create_extension())
    logger.info("extension aws_s3 created.")


def set_search_path_and_role(connection: Connection) -> None:
    """
    Sets the role to the dbo role to create/modify ORCA objects and sets the
    search_path to make the orca schema first. This must be run before any
    creations or modifications to ORCA objects in the ORCA schema.

    Args:
        connection (sqlalchemy.future.Connection): Database connection.

    Returns:
        None
    """
    # Set the user and search_path for the install
    logger.debug("Changing to the dbo role to create objects ...")
    connection.execute(sql.text("SET ROLE orca_dbo;"))

    logger.debug("Setting search path to the ORCA schema to create objects ...")
    connection.execute(sql.text("SET search_path TO orca, public;"))


def create_metadata_objects(connection: Connection) -> None:
    """
    Create the ORCA application metadata tables used to manage application
    versions and other ORCA internal information in the proper order.
    - schema_versions

    Args:
        connection (sqlalchemy.future.Connection): Database connection.

    Returns:
        None
    """
    # Create metadata tables
    logger.debug("Creating schema_versions table ...")
    connection.execute(sql.schema_versions_table_sql())
    logger.info("schema_versions table created.")

    # Populate the table with data
    logger.debug("Populating the schema_versions table with data ...")
    connection.execute(sql.schema_versions_data_sql())
    logger.info("Data added to the schema_versions table.")


def create_recovery_objects(connection: Connection) -> None:
    """
    Creates the ORCA recovery tables in the proper order.
    - recovery_status
    - recovery_job
    - recovery_table

    Args:
        connection (sqlalchemy.future.Connection): Database connection.

    Returns:
        None
    """
    # Create recovery table objects
    # Create the recovery_status table
    logger.debug("Creating recovery_status table ...")
    connection.execute(sql.recovery_status_table_sql())
    logger.info("recovery_status table created.")

    # Populate the table with data
    logger.debug("Populating the recovery_status table with data ...")
    connection.execute(sql.recovery_status_data_sql())
    logger.info("Data added to the recovery_status table.")

    # Create the recovery_job and recovery_file tables
    logger.debug("Creating recovery_job table ...")
    connection.execute(sql.recovery_job_table_sql())
    logger.info("recovery_job table created.")

    logger.debug("Creating recovery_file table ...")
    connection.execute(sql.recovery_file_table_sql())
    logger.info("recovery_file table created.")


def create_inventory_objects(connection: Connection) -> None:
    """
    Creates the ORCA catalog metadata tables used for reconciliation with
    Cumulus in the proper order.
    - providers
    - collections
    - provider_collection_xref
    - granules
    - files

    Args:
        connection (sqlalchemy.future.Connection): Database connection.

    Returns:
        None
    """
    # Create providers table
    logger.debug("Creating providers table ...")
    connection.execute(sql.providers_table_sql())
    logger.info("providers table created.")

    # Create collections table
    logger.debug("Creating collections table ...")
    connection.execute(sql.collections_table_sql())
    logger.info("collections table created.")

    # Create granules table
    logger.debug("Creating granules table ...")
    connection.execute(sql.granules_table_sql())
    logger.info("granules table created.")

    # Create files table
    logger.debug("Creating files table ...")
    connection.execute(sql.files_table_sql())
    logger.info("files table created.")


def create_internal_reconciliation_objects(
    connection: Connection, orca_buckets: List[str]
) -> None:
    """
    Creates the ORCA internal reconciliation tables in the proper order.
    - reconcile_status
    - reconcile_job
    - reconcile_s3_object
    - reconcile_catalog_mismatch_report
    - reconcile_orphan_report
    - reconcile_phantom_report

    Args:
        connection (sqlalchemy.future.Connection): Database connection.
        orca_buckets: List[str]): List of ORCA buckets needed to create
                                  partitioned tables for reporting.

    Returns:
        None
    """
    # Create reconcile_status table
    logger.debug("Creating reconcile_status table ...")
    connection.execute(sql.reconcile_status_table_sql())
    logger.info("reconcile_status table created.")

    # Create reconcile_job table
    logger.debug("Creating reconcile_job table ...")
    connection.execute(sql.reconcile_job_table_sql())
    logger.info("reconcile_job table created.")

    # Create reconcile_s3_object table
    logger.debug("Creating reconcile_s3_object table ...")
    connection.execute(sql.reconcile_s3_object_table_sql())
    logger.info("reconcile_s3_object table created.")

    # Create partitioned tables for the reconcile_s3_object table
    for bucket_name in orca_buckets:
        _partition_name = get_partition_name_from_bucket_name(bucket_name)
        logger.debug(
            f"Creating partition table {_partition_name} for reconcile_s3_object ..."
        )
        connection.execute(
            sql.reconcile_s3_object_partition_sql(_partition_name),
            {"bucket_name": bucket_name},
        )
        logger.info(
            f"Partition table {_partition_name} for reconcile_s3_object created."
        )

    # Create reconcile_catalog_mismatch_report table
    logger.debug("Creating reconcile_catalog_mismatch_report table ...")
    connection.execute(sql.reconcile_catalog_mismatch_report_table_sql())
    logger.info("reconcile_catalog_mismatch_report table created.")

    # Create reconcile_orphan_report table
    logger.debug("Creating reconcile_orphan_report table ...")
    connection.execute(sql.reconcile_orphan_report_table_sql())
    logger.info("reconcile_orphan_report table created.")

    # Create reconcile_phantom_report table
    logger.debug("Creating reconcile_phantom_report table ...")
    connection.execute(sql.reconcile_phantom_report_table_sql())
    logger.info("reconcile_phantom_report table created.")
