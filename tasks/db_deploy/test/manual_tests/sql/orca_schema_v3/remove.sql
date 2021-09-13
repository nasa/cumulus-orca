ALTER TABLE orca.recovery_file
	DROP COLUMN multipart_chunksize_mb
GO
DELETE FROM orca.schema_versions
    WHERE version_id=3
GO
UPDATE orca.schema_versions
    SET is_latest=true
    WHERE version_id=2
GO
COMMIT;
