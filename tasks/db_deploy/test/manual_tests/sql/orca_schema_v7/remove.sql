-- Remove Updates
ALTER TABLE orca.recovery_file
    DROP CONSTRAINT IF EXISTS FK_recovery_file_recoverjob,
    DROP CONSTRAINT IF EXISTS PK_recovery_file,
    DROP COLUMN IF EXISTS collection_id;

ALTER TABLE orca.recovery_job
    DROP CONSTRAINT IF EXISTS PK_recovery_job,
    DROP COLUMN IF EXISTS collection_id;

-- Restore previous constraint values
ALTER TABLE orca.recovery_job
    ADD CONSTRAINT PK_recovery_job PRIMARY KEY (job_id, granule_id);

ALTER TABLE orca.recovery_file
    ADD CONSTRAINT PK_recovery_file
        PRIMARY KEY (job_id, granule_id, filename),
    ADD CONSTRAINT FK_recovery_file_recoverjob
        FOREIGN KEY (job_id, granule_id)
            REFERENCES orca.recovery_job (job_id, granule_id);

-- Upsert the current version
DELETE FROM orca.schema_versions WHERE version_id = 7; 
INSERT INTO orca.schema_versions
  VALUES 
    (6, 'Added storage class to catalog and internal reconciliation', NOW(), True)
ON CONFLICT (version_id)
  DO
    UPDATE
    SET is_latest = True;

COMMIT;