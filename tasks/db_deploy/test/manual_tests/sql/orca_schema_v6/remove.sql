ALTER TABLE orca.reconcile_phantom_report DROP CONSTRAINT IF EXISTS FK_phantom_orca_storage_class;
ALTER TABLE orca.reconcile_phantom_report DROP COLUMN IF EXISTS orca_storage_class_id;
ALTER TABLE orca.reconcile_catalog_mismatch_report DROP CONSTRAINT IF EXISTS FK_mismatch_orca_storage_class;
ALTER TABLE orca.reconcile_catalog_mismatch_report DROP COLUMN IF EXISTS s3_storage_class;
ALTER TABLE orca.reconcile_catalog_mismatch_report DROP COLUMN IF EXISTS orca_storage_class_id;
ALTER TABLE orca.files DROP CONSTRAINT IF EXISTS FK_recovery_file_storage_class;
ALTER TABLE orca.files DROP COLUMN IF EXISTS storage_class_id;
DROP TABLE IF EXISTS orca.storage_class;
DELETE FROM orca.schema_versions
    WHERE version_id=6;
-- Upsert the current version
INSERT INTO orca.schema_versions
VALUES (5, 'Added internal reconciliation schema for v5.x of ORCA application', NOW(), True)
ON CONFLICT (version_id)
DO UPDATE SET is_latest = True;
COMMIT;