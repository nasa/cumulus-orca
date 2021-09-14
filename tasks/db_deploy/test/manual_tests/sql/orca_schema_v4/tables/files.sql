
/*
** SCHEMA: orca
** 
** TABLE: files
**
** 
*/

-- Start a transaction
BEGIN;
    -- Set search path
    SET search_path TO orca, public;

    CREATE TABLE IF NOT EXISTS files
    (
      id                        bigserial NOT NULL
    , granule_id                text NOT NULL         
    , name                      text NOT NULL
    , orca_archive_location     text NOT NULL
    , cumulus_archive_location  text NOT NULL
    , key_path                  text NOT NULL
    , ingest_time               timestamp with time zone NOT NULL
    , etag                      text NOT NULL
    , version                   text NOT NULL
    , size_in_bytes             int8 NOT NULL
    , hash                      text NULL
    , hash_type                 text NULL
    , CONSTRAINT PK_files PRIMARY KEY (id)
    , CONSTRAINT UNIQUE_orca_archive_location_key_path UNIQUE (orca_archive_location, key_path)
    , CONSTRAINT UNIQUE_cumulus_archive_location_key_path UNIQUE (cumulus_archive_location, key_path)
    );

    -- Comments
    COMMENT ON TABLE files
        IS 'Files that are in the ORCA holdings. (Latest version only)';
    COMMENT ON COLUMN files.id
        IS 'Internal ORCA file ID';
    COMMENT ON COLUMN files.granule_id
        IS 'Granule that the file belongs to refrences the internal ORCA granule ID.';
        COMMENT ON COLUMN files.name
        IS 'Name of the file including extension';
        COMMENT ON COLUMN files.orca_archive_location
        IS 'ORCA S3 Glacier bucket that the file object is stored in';
        COMMENT ON COLUMN files.cumulus_archive_location
        IS 'Cumulus S3 bucket where the file is thought to be stored.';
        COMMENT ON COLUMN files.key_path
        IS 'Full AWS key path including file name of the file (does not include bucket name) where the file resides in ORCA.';
    COMMENT ON COLUMN files.ingest_time
        IS 'Date and time the file was ingested into ORCA';              
    COMMENT ON COLUMN files.etag
        IS 'etag of the file object in the AWS S3 Glacier bucket.';
    COMMENT ON COLUMN files.version
        IS 'Latest version of the file in the S3 Glacier bucket';   
    COMMENT ON COLUMN files.size_in_bytes
        IS 'Size of the object in bytes';
    COMMENT ON COLUMN files.hash
        IS 'Hash of the object from Cumulus';
    COMMENT ON COLUMN files.hash_type
        IS 'Hash type used to hash the object. Supplied by Cumulus.';                 
    -- Grants
    GRANT SELECT, INSERT, UPDATE, DELETE ON files TO orca_app;

COMMIT;