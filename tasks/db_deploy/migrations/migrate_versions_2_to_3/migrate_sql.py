"""
Name: orca_sql_v3.py

Description: All of the SQL used for creating and migrating the ORCA schema to version 3.
"""
# Imports
from sqlalchemy import text


def add_multipart_chunksize_sql() -> text:
    """
    SQL that adds the multipart_chunksize_mb column to recovery_file.

    Returns: SQL for adding multipart_chunksize_mb.
    """
    return text(
        """
        ALTER TABLE recovery_file
        ADD COLUMN IF NOT EXISTS multipart_chunksize_mb integer NULL;
        COMMENT ON COLUMN recovery_file.multipart_chunksize_mb
            IS 'Overrides default_multipart_chunksize in TF.';
    """
    )


def schema_versions_data_sql() -> text:
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
            (
              3,
              'Added multipart_chunksize_mb column to recovery_file for v3.x of ORCA application',
              NOW(),
              True
            )
        ON CONFLICT (version_id)
        DO UPDATE SET is_latest = True;
    """
    )
