DROP TABLE IF EXISTS orca.files;
DROP TABLE IF EXISTS orca.granules;
DROP TABLE IF EXISTS orca.provider_collection_xref;
DROP TABLE IF EXISTS orca.collections;
DROP TABLE IF EXISTS orca.providers;
GO
DELETE FROM orca.schema_versions
    WHERE version_id=4
GO
UPDATE orca.schema_versions
    SET is_latest=true
    WHERE version_id=3
GO
COMMIT;