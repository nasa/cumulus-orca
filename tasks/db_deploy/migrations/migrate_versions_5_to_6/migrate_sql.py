"""
Name: migrate_sql.py

Description: All the SQL used for creating and migrating the ORCA schema to version 6.
"""
# Imports
from sqlalchemy import text


# ----------------------------------------------------------------------------
# Version table information
# ----------------------------------------------------------------------------
def schema_versions_data_sql() -> text:  # pragma: no cover
    """
    Data for the schema_versions table. Inserts the current schema
    version into the table.

    Returns: SQL for populating schema_versions table.
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
            (6, 'Added storage class to catalog and internal reconciliation', NOW(), True)
        ON CONFLICT (version_id)
        DO UPDATE SET is_latest = True;
    """
    )


def storage_class_table_sql() -> text:  # pragma: no cover
    """
    Full SQL for creating the storage_class table. This SQL must be run
    before any of the other recovery table sql.

    Returns: SQL for creating storage_class table.
    """
    return text(
        """
        -- Create table
        CREATE TABLE IF NOT EXISTS storage_class
        (
          id    int2 NOT NULL
        , value text NOT NULL
        , CONSTRAINT PK_storage_class PRIMARY KEY(id)
        , CONSTRAINT UNIQUE_storage_class_value UNIQUE (value)
        );

        -- Comments
        COMMENT ON TABLE storage_class
            IS 'Reference table for valid storage classes.';
        COMMENT ON COLUMN storage_class.id
            IS 'Storage Class ID';
        COMMENT ON COLUMN storage_class.value
            IS 'Human readable storage class';

        -- Grants
        GRANT SELECT ON storage_class TO orca_app;
    """
    )


def storage_class_data_sql() -> text:  # pragma: no cover
    """
    Data for the storage_class table. Inserts the currently valid storage classes into
    the table.

    Returns: SQL for populating storage_class table.
    """
    return text(
        """
        -- Upsert the data lookup rows for the table
        INSERT INTO storage_class VALUES (1, 'GLACIER')
            ON CONFLICT (id) DO NOTHING;
        INSERT INTO storage_class VALUES (2, 'DEEP_ARCHIVE')
            ON CONFLICT (id) DO NOTHING;
    """
    )


def add_files_storage_class_id_column_sql() -> text:  # pragma: no cover
    """
    SQL for adding the storage_class_id column to the files table.
    New cells will contain '1', the id for GLACIER.

    Returns: SQL for adding the column.
    """
    return text(
        """
        -- Add the storage_class_id column with a default of 1 (GLACIER)
        ALTER TABLE files
        ADD COLUMN IF NOT EXISTS storage_class_id int2 NOT NULL default 1;
        
        -- Remove the default now that new cells are populated.
        ALTER TABLE files
        ALTER COLUMN storage_class_id DROP DEFAULT;
        
        -- Drop the FK constraint since ADD CONSTRAINT IF NOT EXISTS isn't an option
        ALTER TABLE files
            DROP CONSTRAINT IF EXISTS FK_recovery_file_storage_class;
        
        -- Add the FK constraint
        ALTER TABLE files
        ADD CONSTRAINT FK_recovery_file_storage_class
            FOREIGN KEY (storage_class_id) REFERENCES storage_class (id);
    """
    )


def add_mismatch_storage_class_columns_sql() -> text:  # pragma: no cover
    """
    SQL for adding the orca_storage_class and s3_storage_class columns to the reconcile_catalog_mismatch_report table.
    New cells will contain 'GLACIER'.

    Returns: SQL for adding the column.

    # todo: We could use the storage_class_id if we want.
    """
    return text(
        """
        -- Add the storage_class columns with a default of GLACIER
        ALTER TABLE reconcile_catalog_mismatch_report
        ADD COLUMN IF NOT EXISTS orca_storage_class text NOT NULL default 'GLACIER';
        COMMENT ON COLUMN reconcile_catalog_mismatch_report.orca_storage_class
            IS 'Storage class of the file as reported in the ORCA catalog.';
        ADD COLUMN IF NOT EXISTS s3_storage_class text NOT NULL default 'GLACIER';
        COMMENT ON COLUMN reconcile_catalog_mismatch_report.s3_storage_class
            IS 'Storage class of the file as reported in the S3 bucket.';

        -- Remove the default now that new cells are populated.
        ALTER TABLE reconcile_catalog_mismatch_report
        ALTER COLUMN orca_storage_class DROP DEFAULT;
        ALTER COLUMN s3_storage_class DROP DEFAULT;
    """
    )


def add_phantom_storage_class_column_sql() -> text:  # pragma: no cover
    """
    SQL for adding the orca_storage_class column to the reconcile_phantom_report table.
    New cells will contain 'GLACIER'.

    Returns: SQL for adding the column.

    # todo: We could use the storage_class_id if we want.
    """
    return text(
        """
        -- Add the orca_storage_class column with a default of GLACIER
        ALTER TABLE reconcile_phantom_report
        ADD COLUMN IF NOT EXISTS orca_storage_class text NOT NULL default 'GLACIER';
        COMMENT ON COLUMN reconcile_phantom_report.orca_storage_class
            IS 'Storage class of the file as reported in the ORCA catalog.';

        -- Remove the default now that new cells are populated.
        ALTER TABLE reconcile_phantom_report
        ALTER COLUMN orca_storage_class DROP DEFAULT;
    """
    )
