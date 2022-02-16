DROP EXTENSION IF EXISTS aws_s3 CASCADE;
DROP TABLE IF EXISTS orca.reconcile_catalog_mismatch_report;
DROP TABLE IF EXISTS orca.reconcile_orphan_report;
DROP TABLE IF EXISTS orca.reconcile_phantom_report;
DROP TABLE IF EXISTS orca.reconcile_s3_object_orca_worm_backup;
DROP TABLE IF EXISTS orca.reconcile_s3_object_orca_special_backup;
DROP TABLE IF EXISTS orca.reconcile_s3_object_orca_versioned_backup;
DROP TABLE IF EXISTS orca.reconcile_s3_object;
DROP TABLE IF EXISTS orca.reconcile_job;
DROP TABLE IF EXISTS orca.reconcile_status;
DELETE FROM orca.schema_versions
    WHERE version_id=5;
-- Upsert the current version
INSERT INTO orca.schema_versions
VALUES (4, 'Updated recovery schema for v4.x of ORCA application', NOW(), True)
ON CONFLICT (version_id)
DO UPDATE SET is_latest = True;
COMMIT;