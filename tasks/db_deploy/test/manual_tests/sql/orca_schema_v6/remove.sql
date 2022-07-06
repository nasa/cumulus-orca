ALTER TABLE files DROP COLUMN IF EXISTS storage_class_id;
DROP CONSTRAINT IF EXISTS FK_recovery_file_storage_class;
DROP TABLE IF EXISTS orca.storage_class;
DELETE FROM orca.schema_versions
    WHERE version_id=6;
-- Upsert the current version
INSERT INTO orca.schema_versions
VALUES (5, 'Added internal reconciliation schema for v5.x of ORCA application', NOW(), True)
ON CONFLICT (version_id)
DO UPDATE SET is_latest = True;
COMMIT;