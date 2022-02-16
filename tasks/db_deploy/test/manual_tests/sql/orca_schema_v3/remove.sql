-- Drop our changes for V3
ALTER TABLE orca.recovery_file
	DROP COLUMN IF EXISTS multipart_chunksize_mb;

-- Reset the versions table
DELETE FROM orca.schema_versions
    WHERE version_id=3;
-- Upsert the old version
INSERT INTO orca.schema_versions
     VALUES (2, 'Updated recovery schema for ORCA v3.x.', NOW(), True)
     ON CONFLICT (version_id)
     DO UPDATE SET is_latest = True;

COMMIT;