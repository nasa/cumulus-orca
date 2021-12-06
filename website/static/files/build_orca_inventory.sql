-- Set the Role and Path
SET ROLE orca_dbo;
SET search_path TO orca, public;


-- Create the objects in a transaction.
BEGIN

    -- Create the Providers Table
    CREATE TABLE IF NOT EXISTS providers
    (
      provider_id text NOT NULL
    , name        text NOT NULL
    , CONSTRAINT PK_providers PRIMARY KEY(provider_id)
    );

    COMMENT ON TABLE providers
      IS 'Providers that are in the ORCA holdings.';
    COMMENT ON COLUMN providers.provider_id
      IS 'Provider ID supplied by Cumulus';
    COMMENT ON COLUMN providers.name
      IS 'User friendly name of the provider provided by Cumulus';


    -- Create the Collections Table
    CREATE TABLE IF NOT EXISTS collections
    (
      collection_id   text NOT NULL
    , shortname       text NOT NULL
    , version         text NOT NULL
    , CONSTRAINT PK_collections PRIMARY KEY(collection_id)
    , CONSTRAINT UNIQUE_collections UNIQUE (shortname, version)
    );

    COMMENT ON TABLE collections
      IS 'Collections that are in the ORCA archive holdings.';
    COMMENT ON COLUMN collections.collection_id
      IS 'Collection ID from Cumulus usually in the format shortname__version.';
    COMMENT ON COLUMN collections.shortname
      IS 'Collection short name from Cumulus';
    COMMENT ON COLUMN collections.version
      IS 'Collection version from Cumulus';

    -- Create the Providers Collection XREF table
    CREATE TABLE IF NOT EXISTS provider_collection_xref
    (
      provider_id     text NOT NULL
    , collection_id   text NOT NULL
    , CONSTRAINT PK_provider_collection_xref PRIMARY KEY(provider_id,collection_id)
    , CONSTRAINT provider_collection_fk FOREIGN KEY(provider_id) REFERENCES providers(provider_id)
    , CONSTRAINT collection_provider_fk FOREIGN KEY(collection_id) REFERENCES collections(collection_id)
    );

    COMMENT ON TABLE provider_collection_xref
      IS 'Cross refrence table that ties a collection and provider together and resolves the many to many relationship.';
    COMMENT ON COLUMN provider_collection_xref.provider_id
      IS 'Provider ID from the providers table.';
    COMMENT ON COLUMN provider_collection_xref.collection_id
      IS 'Collection ID from the collections table.';


    -- Create the Granules table
    CREATE TABLE IF NOT EXISTS granules
    (
      id                  int8 NOT NULL
    , collection_id       text NOT NULL
    , cumulus_granule_id  text NOT NULL
    , acquisition_time    timestamp with time zone NOT NULL
    , ingest_time         timestamp with time zone NOT NULL
    , last_update         timestamp with time zone NOT NULL
    , archive_location    text NOT NULL
    , CONSTRAINT PK_granules PRIMARY KEY(id)
    , CONSTRAINT UNIQUE_granules UNIQUE (collection_id, cumulus_granule_id)
    , CONSTRAINT collection_granule_fk FOREIGN KEY(collection_id) REFERENCES collections(collection_id)
    );

    COMMENT ON TABLE granules
      IS 'Granules that are in the ORCA archive holdings.';
    COMMENT ON COLUMN granules.id
      IS 'Internal orca granule ID pseudo key';
    COMMENT ON COLUMN granules.collection_id
      IS 'Collection ID from Cumulus that refrences the Collections table.';
    COMMENT ON COLUMN granules.cumulus_granule_id
      IS 'Granule ID from Cumulus';
    COMMENT ON COLUMN granules.acquisition_time
      IS 'Data acquistion time in UTC.';
    COMMENT ON COLUMN granules.ingest_time
      IS 'Date and time the granule was originally ingested into ORCA.';
    COMMENT ON COLUMN granules.last_update
      IS 'Last time the data for the granule was updated. This generally will coincide with a duplicate or a change to the underlying data file.';
    COMMENT ON COLUMN granules.archive_location
      IS 'ORCA S3 bucket the granules files were archived in.';


    -- Create the Files table
    CREATE TABLE IF NOT EXISTS files
    (
      id                          int8 NOT NULL
    , granule_id                  int8 NOT NULL
    , name                        text NOT NULL
    , orca_archive_location       text NOT NULL
    , cumulus_archive_location    text NOT NULL
    , key_path                    text NOT NULL
    , ingest_time                 timestamp with time zone NOT NULL
    , etag                        text NOT NULL
    , version                     text NOT NULL
    , size_in_bytes               int8 NOT NULL
    , hash                        text NOT NULL
    , hash_type                   text NOT NULL
    , CONSTRAINT PK_files PRIMARY KEY(id)
    , CONSTRAINT UNIQUE_files_1 UNIQUE (cumulus_archive_location, key_path)
    , CONSTRAINT UNIQUE_files_2 UNIQUE (orca_archive_location, key_path)
    , CONSTRAINT granule_file_fk FOREIGN KEY(granule_id) REFERENCES granules(id)
    );

    COMMENT ON TABLE files
      IS 'Files that are in the ORCA holdings. (Latest version only)';
    COMMENT ON COLUMN files.id
      IS 'Internal ORCA file ID';
    COMMENT ON COLUMN files.granule_id
      IS 'Granule that the file belongs to refrences the internal ORCA granule ID.';
    COMMENT ON COLUMN files.name
      IS 'Name of the file including extension';
    COMMENT ON COLUMN files.orca_archive_location
      IS 'S3 Glacier bucket that the file object is stored in';
    COMMENT ON COLUMN files.cumulus_archive_location
      IS 'Cumulus S3 bucket where the file is thought to be stored.';
    COMMENT ON COLUMN files.key_path
      IS 'Full AWS key path including file name of the file (does not include bucket name) where the file resides in ORCA.';
    COMMENT ON COLUMN files.ingest_time
      IS 'Date and time the file was ingested into ORCA';
    COMMENT ON COLUMN files.etag
      IS 'etag of the file object in the AWS S3 Glacier bucket.';
    COMMENT ON COLUMN files.version
      IS 'Version of the file in the S3 Glacier bucket';
    COMMENT ON COLUMN files.size_in_bytes
      IS 'Size of the object in bytes';
    COMMENT ON COLUMN files.hash
      IS 'Hash of the object from Cumulus';
    COMMENT ON COLUMN files.hash_type
      IS 'Hash type used to hash the object. Supplied by Cumulus.';

COMMIT;

