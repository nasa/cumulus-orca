"""
Name: migrate_sql.py

Description: All of the SQL used for creating and migrating the ORCA schema to version 5.
"""
# Imports
import re

from sqlalchemy import text
from sqlalchemy.sql.elements import TextClause


# ----------------------------------------------------------------------------
# Version table information
# ----------------------------------------------------------------------------
def schema_versions_data_sql() -> TextClause:
    """
    Data for the schema_versions table. Inserts the current schema
    version into the table.

    Returns:
        (sqlalchemy.sql.element.TextClause): SQL for populating schema_versions table.
    """
    return text(
        """
        -- Populate with the current version
        -- Update is_latest to false for all records first to prevent error
        UPDATE schema_versions
        SET is_latest = False;

        -- Upsert the current version
        INSERT INTO schema_versions
          VALUES
            (5, 'Added internal reconciliation schema for v5.x of ORCA application', NOW(), True)
        ON CONFLICT (version_id)
        DO UPDATE SET is_latest = True;
    """
    )


# ----------------------------------------------------------------------------
# Database extension
# ----------------------------------------------------------------------------
def create_extension() -> TextClause:
    """
    Full SQL for creating the aws_s3 extension used for COPYING S3 reporting data
    from a CSV file in an AWS bucket into the database.

    Returns:
        (sqlalchemy.sql.element.TextClause): SQL for creating extension for the database.
    """

    return text(
        """
            -- Create extension
            CREATE EXTENSION IF NOT EXISTS aws_s3 CASCADE;
        """
    )


# ----------------------------------------------------------------------------
# ORCA SQL used for creating ORCA internal reconciliation tables
# ----------------------------------------------------------------------------
def reconcile_status_table_sql() -> TextClause:
    """
    Full SQL for creating the reconcile_status table.

    Returns:
        (sqlalchemy.sql.element.TextClause): SQL for creating reconcile_status table.
    """
    return text(
        """
        -- Create table
        CREATE TABLE IF NOT EXISTS reconcile_status
        (
          id       int2 NOT NULL
        , value    text NOT NULL
        , CONSTRAINT PK_reconcile_status PRIMARY KEY(id)
        , CONSTRAINT UNIQUE_reconcile_status_value UNIQUE (value)
        );

        -- Comments
        COMMENT ON TABLE reconcile_status
            IS 'Reference table for valid status values and status order.';
        COMMENT ON COLUMN reconcile_status.id
            IS 'Status ID';
        COMMENT ON COLUMN reconcile_status.value
            IS 'Human readable status value';

        -- Upsert the data lookup rows for the table
        INSERT INTO reconcile_status VALUES (1, 'getting S3 list')
            ON CONFLICT (id) DO NOTHING;
        INSERT INTO reconcile_status VALUES (2, 'staged')
            ON CONFLICT (id) DO NOTHING;
        INSERT INTO reconcile_status VALUES (3, 'generating reports')
            ON CONFLICT (id) DO NOTHING;
        INSERT INTO reconcile_status VALUES (4, 'error')
            ON CONFLICT (id) DO NOTHING;
        INSERT INTO reconcile_status VALUES (5, 'success')
            ON CONFLICT (id) DO NOTHING;
        """
    )


def reconcile_job_table_sql() -> TextClause:
    """
    Full SQL for creating the reconcile_job table.

    Returns:
        (sqlalchemy.sql.element.TextClause): SQL for creating reconcile_job table.
    """
    return text(
        """
        -- Create reconcile_job table
        CREATE TABLE IF NOT EXISTS reconcile_job
        (
          id                         bigserial NOT NULL
        , orca_archive_location      text NOT NULL
        , status_id                  int2 NOT NULL
        , inventory_creation_time    timestamp with time zone NOT NULL
        , start_time                 timestamp with time zone NOT NULL
        , last_update                timestamp with time zone NOT NULL
        , end_time                   timestamp with time zone NULL
        , error_message              text NULL
        , CONSTRAINT PK_reconcile_job PRIMARY KEY(id)
        , CONSTRAINT FK_reconcile_job_status FOREIGN KEY(status_id) REFERENCES reconcile_status(id)
        );

        -- Comments
        COMMENT ON TABLE reconcile_job
          IS 'Manages internal reconciliation job information.';
        COMMENT ON COLUMN reconcile_job.id
          IS 'Job ID unique to each internal reconciliation job.';
        COMMENT ON COLUMN reconcile_job.orca_archive_location
          IS 'ORCA S3 Glacier bucket the reconciliation targets.';
        COMMENT ON COLUMN reconcile_job.status_id IS
          'Current status of the job.';
        COMMENT ON COLUMN reconcile_job.inventory_creation_time
          IS 'Inventory report initiation time from the s3 manifest.';
        COMMENT ON COLUMN reconcile_job.start_time
          IS 'Date and time the internal reconcile job started.';
        COMMENT ON COLUMN reconcile_job.last_update
          IS 'Date and time the job status was last updated.';
        COMMENT ON COLUMN reconcile_job.end_time
          IS 'Time the job completed and wrote the report information.';
        COMMENT ON COLUMN reconcile_job.error_message
          IS 'Critical error the job ran into that prevented it from finishing.';
        """
    )


def reconcile_s3_object_table_sql() -> TextClause:
    """
    Full SQL for creating the reconcile_s3_object table.

    Returns:
        (sqlalchemy.sql.element.TextClause): SQL for creating reconcile_s3_object table.
    """
    return text(
        """
            -- Create reconcile_s3_object table
            CREATE TABLE IF NOT EXISTS reconcile_s3_object
            (
              job_id                   int8 NOT NULL
            , orca_archive_location    text NOT NULL
            , key_path                 text NOT NULL
            , etag                     text NOT NULL
            , last_update              timestamp with time zone NOT NULL
            , size_in_bytes            int8 NOT NULL
            , storage_class            text NOT NULL
            , delete_marker            bool NOT NULL DEFAULT False
            )
            PARTITION BY LIST (orca_archive_location);

            -- Comment
            COMMENT ON TABLE reconcile_s3_object
              IS 'Holds the listing from the ORCA S3 buckets to use for internal comparisons.';
            COMMENT ON COLUMN reconcile_s3_object.job_id
              IS 'Job the S3 listing is a part of for the comparison.';
            COMMENT ON COLUMN reconcile_s3_object.orca_archive_location
              IS 'ORCA S3 Glacier bucket name where the file is stored.';
            COMMENT ON COLUMN reconcile_s3_object.key_path
              IS 'Full path and file name of the object in the S3 bucket.';
            COMMENT ON COLUMN reconcile_s3_object.etag
              IS 'AWS etag value from the s3 inventory report.';
            COMMENT ON COLUMN reconcile_s3_object.last_update
              IS 'AWS Last Update from the s3 inventory report.';
            COMMENT ON COLUMN reconcile_s3_object.size_in_bytes
              IS 'AWS size of the file in bytes from the s3 inventory report.';
            COMMENT ON COLUMN reconcile_s3_object.storage_class
              IS 'AWS storage class the object is in from the s3 inventory report.';
            COMMENT ON COLUMN reconcile_s3_object.delete_marker
              IS 'Set to True if object is marked as deleted.';
        """
    )


def reconcile_s3_object_partition_sql(partition_name: str) -> TextClause:
    """
    Full SQL for creating the reconcile_s3_object partition table. Requires the
    user to pass the orca_archive_location value for the partition in the form
    of `{"bucket_name": value}` when executing the SQL via the driver.

    Args:
        partition_name(str): Name of the partition table.

    Returns:
        (sqlalchemy.sql.element.TextClause): SQL for creating reconcile_s3_object partition table.
    """
    try:
        if not re.match("^[\w+]+$", partition_name):  # noqa: W605
            raise ValueError(f"Table name {partition_name} is invalid.")
    except TypeError:
        raise ValueError("Table name must be a string and cannot be None.")

    return text(
        f"""
            -- Create orca_archive_location_:bucket_name
            CREATE TABLE {partition_name} PARTITION OF reconcile_s3_object
            (
              CONSTRAINT PK_{partition_name}
                PRIMARY KEY(key_path)
            , CONSTRAINT FK_reconcile_job_{partition_name}
                FOREIGN KEY(job_id) REFERENCES reconcile_job(id)
            )
            FOR VALUES IN (:bucket_name);

            -- Comment
            COMMENT ON TABLE {partition_name}
              IS 'Partition table for reconcile_s3_object based on orca_archive_location.';
            """
    )


def reconcile_catalog_mismatch_report_table_sql() -> TextClause:
    """
    Full SQL for creating the reconcile_catalog_mismatch_report table.

    Returns:
        (sqlalchemy.sql.element.TextClause): SQL for creating reconcile_catalog_mismatch_report.
    """
    return text(
        """
            -- Create reconcile_catalog_mismatch_report table
            CREATE TABLE IF NOT EXISTS reconcile_catalog_mismatch_report
            (
              job_id                      int8 NOT NULL
            , collection_id               text NOT NULL
            , granule_id                  text NOT NULL
            , filename                    text NOT NULL
            , key_path                    text NOT NULL
            , cumulus_archive_location    text NOT NULL
            , orca_etag                   text NOT NULL
            , s3_etag                     text NOT NULL
            , orca_last_update            timestamp with time zone NOT NULL
            , s3_last_update              timestamp with time zone NOT NULL
            , orca_size_in_bytes        int8 NOT NULL
            , s3_size_in_bytes            int8 NOT NULL
            , discrepancy_type            text NOT NULL
            , CONSTRAINT PK_reconcile_catalog_mismatch_report
                PRIMARY KEY(job_id,collection_id,granule_id,key_path)
            , CONSTRAINT FK_reconcile_job_mismatch_report
                FOREIGN KEY(job_id) REFERENCES reconcile_job(id)
            );

            -- Comment
            COMMENT ON TABLE reconcile_catalog_mismatch_report
              IS 'Identifies objects that have mismatched values between the ORCA catalog and s3.';
            COMMENT ON COLUMN reconcile_catalog_mismatch_report.job_id
              IS 'Job the mismatch granule was found in. References the reconcile_job table.';
            COMMENT ON COLUMN reconcile_catalog_mismatch_report.collection_id
              IS 'Cumulus Collection ID value from the ORCA catalog.';
            COMMENT ON COLUMN reconcile_catalog_mismatch_report.granule_id
              IS 'Cumulus granuleID value from the ORCA catalog.';
            COMMENT ON COLUMN reconcile_catalog_mismatch_report.filename
              IS 'Filename of the object from the ORCA catalog.';
            COMMENT ON COLUMN reconcile_catalog_mismatch_report.key_path
              IS 'key path and filename of the object in the ORCA catalog.';
            COMMENT ON COLUMN reconcile_catalog_mismatch_report.cumulus_archive_location
              IS 'Expected S3 bucket the object is located in Cumulus. From the ORCA catalog.';
            COMMENT ON COLUMN reconcile_catalog_mismatch_report.orca_etag
              IS 'etag of the object as reported in the ORCA catalog.';
            COMMENT ON COLUMN reconcile_catalog_mismatch_report.s3_etag
              IS 'etag of the object as reported in the S3 bucket.';
            COMMENT ON COLUMN reconcile_catalog_mismatch_report.orca_last_update
              IS 'Last update of the object as reported in the ORCA catalog.';
            COMMENT ON COLUMN reconcile_catalog_mismatch_report.s3_last_update
              IS 'Last update of the object as reported in the S3 bucket.';
            COMMENT ON COLUMN reconcile_catalog_mismatch_report.orca_size_in_bytes
              IS 'Size in bytes of the object as reported in the ORCA catalog.';
            COMMENT ON COLUMN reconcile_catalog_mismatch_report.s3_size_in_bytes
              IS 'Size in bytes of the object as reported in the S3 bucket.';
            COMMENT ON COLUMN reconcile_catalog_mismatch_report.discrepancy_type
              IS 'Type of discrepancy found during reconciliation.';
        """
    )


def reconcile_orphan_report_table_sql() -> TextClause:
    """
    Full SQL for creating the reconcile_orphan_report table.

    Returns:
        (sqlalchemy.sql.element.TextClause): SQL for creating reconcile_orphan_report table.
    """
    return text(
        """
            -- Create reconcile_orphan_report table
            CREATE TABLE IF NOT EXISTS reconcile_orphan_report
            (
              job_id           int8 NOT NULL
            , key_path         text NOT NULL
            , etag             text NOT NULL
            , last_update      timestamp with time zone NOT NULL
            , size_in_bytes    int8 NOT NULL
            , storage_class    text NOT NULL
            , CONSTRAINT PK_reconcile_orphan_report
                PRIMARY KEY(job_id,key_path)
            , CONSTRAINT FK_reconcile_job_orphan_report
                FOREIGN KEY(job_id) REFERENCES reconcile_job(id)
            );

            -- Comment
            COMMENT ON TABLE reconcile_orphan_report
              IS 'Identifies objects in the ORCA S3 Glacier bucket that are not in the catalog.';
            COMMENT ON COLUMN reconcile_orphan_report.job_id
              IS 'Associates the orphaned file to a internal reconciliation job.';
            COMMENT ON COLUMN reconcile_orphan_report.key_path
              IS 'Contains the path and file name from the reconcile_s3_object (key_path) column.';
            COMMENT ON COLUMN reconcile_orphan_report.etag
              IS 'AWS Etag of the object from the reconcile_s3_object (etag) column.';
            COMMENT ON COLUMN reconcile_orphan_report.last_update
              IS 'AWS last update of the object from the reconcile_s3_object (lst_update) column.';
            COMMENT ON COLUMN reconcile_orphan_report.size_in_bytes
              IS 'AWS size of the object in bytes from the reconcile_s3_object (size) column.';
            COMMENT ON COLUMN reconcile_orphan_report.storage_class
              IS 'AWS storage class from the reconcile_s3_object (storage_class) column.';
        """
    )


def reconcile_phantom_report_table_sql() -> TextClause:
    """
    Full SQL for creating the reconcile_phantom_report table.

    Returns:
        (sqlalchemy.sql.element.TextClause): SQL for creating reconcile_phantom_report table.
    """
    return text(
        """
            -- Create reconcile_phantom_report table
            CREATE TABLE IF NOT EXISTS reconcile_phantom_report
            (
              job_id              int8 NOT NULL
            , collection_id       text NOT NULL
            , granule_id          text NOT NULL
            , filename            text NOT NULL
            , key_path            text NOT NULL
            , orca_etag           text NOT NULL
            , orca_last_update    timestamp with time zone NOT NULL
            , orca_size           int8 NOT NULL
            , CONSTRAINT PK_reconcile_phantom_report
                PRIMARY KEY(job_id,collection_id,granule_id,key_path)
            , CONSTRAINT FK_reconcile_job_phantom_report
                FOREIGN KEY(job_id) REFERENCES reconcile_job(id)
            );
            -- Comment
            COMMENT ON TABLE reconcile_phantom_report
              IS 'Identifies objects that exist in the ORCA catalog and do not exist in S3.';
            COMMENT ON COLUMN reconcile_phantom_report.job_id
              IS 'Job the missing granule was found in. References the reconcile_job table.';
            COMMENT ON COLUMN reconcile_phantom_report.collection_id
              IS 'Cumulus Collection ID value from the ORCA catalog.';
            COMMENT ON COLUMN reconcile_phantom_report.granule_id
              IS 'Cumulus granuleID value from the ORCA catalog.';
            COMMENT ON COLUMN reconcile_phantom_report.filename
              IS 'Filename of the object from the ORCA catalog.';
            COMMENT ON COLUMN reconcile_phantom_report.key_path
              IS 'key path and filename of the object in the ORCA catalog.';
            COMMENT ON COLUMN reconcile_phantom_report.orca_etag
              IS 'etag of the object as reported in the ORCA catalog.';
            COMMENT ON COLUMN reconcile_phantom_report.orca_last_update
              IS 'Last update of the object as reported in the ORCA catalog.';
            COMMENT ON COLUMN reconcile_phantom_report.orca_size
              IS 'Size in bytes of the object as reported in the ORCA catalog.';
        """
    )
