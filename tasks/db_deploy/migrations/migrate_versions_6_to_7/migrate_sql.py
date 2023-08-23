"""
Name: migrate_sql.py

Description: All the SQL used for creating and migrating the ORCA schema to version 7.
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
            (7, 'Added collection_id to recovery job tables.', NOW(), True)
        ON CONFLICT (version_id)
        DO UPDATE SET is_latest = True;
    """
    )


def add_collection_id_to_recovery_job_and_recovery_file_sql() -> text:
    """ """
    return text(  # nosec
        """
        -- Remove old constraints and add collection_id
        -- ##############################################
        ALTER TABLE orca.recovery_file
            DROP CONSTRAINT IF EXISTS FK_recovery_file_recoverjob,
            DROP CONSTRAINT IF EXISTS PK_recovery_file,
            ADD COLUMN IF NOT EXISTS collection_id text;
        ALTER TABLE orca.recovery_job
            DROP CONSTRAINT IF EXISTS PK_recovery_job,
            ADD COLUMN IF NOT EXISTS collection_id text;

        -- Populate the collection_id column setting
        -- non-matches to a value of "UNKNOWN"
        -- ##############################################
        UPDATE orca.recovery_file
            SET collection_id = granules.collection_id
            FROM orca.granules
            WHERE granules.cumulus_granule_id = recovery_file.granule_id;
        UPDATE orca.recovery_file
            SET collection_id = 'UNKNOWN'
            WHERE collection_id IS NULL;

        UPDATE orca.recovery_job
            SET collection_id = granules.collection_id
            FROM orca.granules
            WHERE granules.cumulus_granule_id = recovery_job.granule_id;
        UPDATE orca.recovery_job
            SET collection_id = 'UNKNOWN'
            WHERE collection_id IS NULL;

        -- Add in new Primary Key constraints
        -- ##############################################
        ALTER TABLE orca.recovery_file
            ALTER COLUMN collection_id SET NOT NULL,
            ADD CONSTRAINT PK_recovery_file
                PRIMARY KEY (job_id, collection_id, granule_id, filename);
        ALTER TABLE orca.recovery_job
            ALTER COLUMN collection_id SET NOT NULL,
            ADD CONSTRAINT PK_recovery_job PRIMARY KEY (job_id, collection_id, granule_id);

        -- Add in new Foreign Key constraints
        -- ##############################################
        ALTER TABLE orca.recovery_file
            ADD CONSTRAINT FK_recovery_file_recoverjob
                FOREIGN KEY (job_id, collection_id, granule_id)
                REFERENCES orca.recovery_job (job_id, collection_id, granule_id);
        """
    )
