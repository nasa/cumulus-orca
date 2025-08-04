"""
Name: migrate_sql.py

Description: All the SQL used for creating and migrating the ORCA schema to version 8.
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
            (8, 'Added delete_file to files tables.', NOW(), True)
        ON CONFLICT (version_id)
        DO UPDATE SET is_latest = True;
    """
    )


def add_delete_file_to_files_table_sql() -> text:
    """ """
    return text(  # nosec
        """
        -- Add delete_file column to files table
        ALTER TABLE orca.files
            ADD COLUMN IF NOT EXISTS delete_file boolean;

        -- Populate the delete_file column setting
        -- non-matches to a value of "UNKNOWN"
        -- ##############################################
        UPDATE orca.files
            SET delete_file = 'UNKNOWN'
            WHERE delete_file IS NULL;
        """
    )
