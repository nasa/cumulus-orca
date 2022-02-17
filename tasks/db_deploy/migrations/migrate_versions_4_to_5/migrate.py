"""
Name: migrate.py

Description: Migrates the ORCA schema from version 4 to version 5.
"""
from typing import Dict, List

from orca_shared.database.shared_db import get_admin_connection, logger
from orca_shared.reconciliation.shared_reconciliation import (
    get_partition_name_from_bucket_name,
)

import migrations.migrate_versions_4_to_5.migrate_sql as sql


def migrate_versions_4_to_5(
    config: Dict[str, str], is_latest_version: bool, orca_buckets: List[str]
) -> None:
    """
    Performs the migration of the ORCA schema from version 4 to version 5 of
    the ORCA schema. This includes adding the aws s3 extension and adding the
    following tables:
    - reconcile_status
    - reconcile_job
    - reconcile_s3_object (and partitions)
    - reconcile_catalog_mismatch_report
    - reconcile_phantom_report
    - reconcile_orphan_report

    Args:
        config (Dict): Connection information for the database.
        is_latest_version (bool): Flag to determine if version 5 is the latest
                                  schema version.
        orca_buckets: List[str]): List of ORCA buckets names needed to create
                                  partition tables for v5.
    Returns:
        None
    """
    # Get the admin engine to the app database
    admin_app_connection = get_admin_connection(config, config["user_database"])

    with admin_app_connection.connect() as connection:

        # Create extension for the database as the admin user
        logger.debug("Creating extension aws_s3 ...")
        connection.execute(sql.create_extension())
        logger.info("extension aws_s3 created.")

        # Change to DBO role and set search path
        logger.debug("Changing to the dbo role to create objects ...")
        connection.execute(sql.text("SET ROLE orca_dbo;"))

        # Set the search path
        logger.debug("Setting search path to the ORCA schema to create objects ...")
        connection.execute(sql.text("SET search_path TO orca, public;"))

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

        # If v5 is the latest version, update the schema_versions table.
        if is_latest_version:
            logger.debug("Populating the schema_versions table with data ...")
            connection.execute(sql.schema_versions_data_sql())
            logger.info("Data added to the schema_versions table.")

        # Commit if there is no issues
        connection.commit()
