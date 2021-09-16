DROP TABLE IF EXISTS orca.files;
DROP TABLE IF EXISTS orca.granules;
DROP TABLE IF EXISTS orca.provider_collection_xref;
DROP TABLE IF EXISTS orca.collections;
DROP TABLE IF EXISTS orca.providers;
DELETE FROM orca.schema_versions
    WHERE version_id=4;
-- Upsert the current version
INSERT INTO orca.schema_versions
VALUES (3, 'Updated recovery schema for v3.x of ORCA application', NOW(), True)
ON CONFLICT (version_id)
DO UPDATE SET is_latest = True;
COMMIT;