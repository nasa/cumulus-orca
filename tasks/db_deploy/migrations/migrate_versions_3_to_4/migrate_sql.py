"""
Name: migrate_sql.py

Description: All of the SQL used for creating and migrating the ORCA schema to version 4.
"""

# Imports
from sqlalchemy import text

# ----------------------------------------------------------------------------
# ORCA SQL used for creating ORCA inventory metadata tables
# ----------------------------------------------------------------------------


def providers_table_sql() -> text:  # pragma: no cover
    """
    Full SQL for creating the providers table.

    Returns:
        SQL for creating providers table.
    """
    return text(
        """
        -- Create table
        CREATE TABLE IF NOT EXISTS providers
        (
          provider_id         text NOT NULL
        , name                text
        , CONSTRAINT PK_providers PRIMARY KEY (provider_id)
        );

        -- Comments
        COMMENT ON TABLE providers
            IS 'Providers that are in the ORCA holdings.';
        COMMENT ON COLUMN providers.provider_id
            IS 'Provider ID supplied by Cumulus.';
        COMMENT ON COLUMN providers.name
            IS 'User friendly name of the provider provided by Cumulus.';
        -- Grants
        GRANT SELECT, INSERT, UPDATE, DELETE ON providers TO orca_app;
    """
    )


def collections_table_sql() -> text:  # pragma: no cover
    """
    Full SQL for creating the collections table.

    Returns:
        SQL for creating collections table.
    """
    return text(
        """
        -- Create table
        CREATE TABLE IF NOT EXISTS collections
        (
          collection_id         text NOT NULL
        , shortname             text NOT NULL
        , version               text NOT NULL
        , CONSTRAINT PK_collections PRIMARY KEY (collection_id)
        );

        -- Comments
        COMMENT ON TABLE collections
            IS 'Collections that are in the ORCA archive holdings.';
        COMMENT ON COLUMN collections.collection_id
            IS 'Collection ID from Cumulus usually in the format shortname__version.';
        COMMENT ON COLUMN collections.shortname
            IS 'Collection short name from Cumulus.';
        COMMENT ON COLUMN collections.version
            IS 'Collection version from Cumulus.';
        -- Grants
        GRANT SELECT, INSERT, UPDATE, DELETE ON collections TO orca_app;
    """
    )


def granules_table_sql() -> text:  # pragma: no cover
    """
    Full SQL for creating the catalog granules table.

    Returns:
        SQL for creating granules table.
    """
    return text(
        """
        -- Create table
        CREATE TABLE IF NOT EXISTS granules
        (
          id                    bigserial NOT NULL
        , provider_id           text NOT NULL
        , collection_id         text NOT NULL
        , cumulus_granule_id    text NOT NULL
        , execution_id          text NOT NULL
        , ingest_time           timestamp with time zone NOT NULL
        , cumulus_create_time   timestamp with time zone NOT NULL
        , last_update           timestamp with time zone NOT NULL

        , CONSTRAINT PK_granules
            PRIMARY KEY (id)
        , CONSTRAINT FK_provider_granule
            FOREIGN KEY (provider_id) REFERENCES providers (provider_id)
        , CONSTRAINT FK_collection_granule
            FOREIGN KEY (collection_id) REFERENCES collections (collection_id)
        , CONSTRAINT UNIQUE_collection_granule_id
            UNIQUE (collection_id, cumulus_granule_id)
        );

        -- Comments
        COMMENT ON TABLE granules
            IS 'Granules that are in the ORCA archive holdings.';
        COMMENT ON COLUMN granules.id
            IS 'Internal orca granule ID pseudo key';
        COMMENT ON COLUMN granules.provider_id
            IS 'Provider ID from Cumulus that references the Providers table.';
        COMMENT ON COLUMN granules.collection_id
            IS 'Collection ID from Cumulus that references the Collections table.';
         COMMENT ON COLUMN granules.cumulus_granule_id
            IS 'Granule ID from Cumulus';
         COMMENT ON COLUMN granules.execution_id
            IS 'AWS step function execution id';
        COMMENT ON COLUMN granules.ingest_time
            IS 'Date and time the granule was originally ingested into ORCA.';
        COMMENT ON COLUMN granules.cumulus_create_time
            IS 'createdAt time from Cumulus';
        COMMENT ON COLUMN granules.last_update
            IS 'Last time the data for the granule was updated.';
        -- Grants
        GRANT SELECT, INSERT, UPDATE, DELETE ON granules TO orca_app;
    """
    )


def files_table_sql() -> text:  # pragma: no cover
    """
    Full SQL for creating the catalog files table.

    Returns:
        SQL for creating files table.
    """
    return text(
        """
        -- Create table
        CREATE TABLE IF NOT EXISTS files
        (
          id                        bigserial NOT NULL
        , granule_id                bigint NOT NULL
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
        , CONSTRAINT PK_files
            PRIMARY KEY (id)
        , CONSTRAINT FK_granule_file
            FOREIGN KEY (granule_id) REFERENCES granules (id)
        , CONSTRAINT UNIQUE_orca_archive_location_key_path
            UNIQUE (orca_archive_location, key_path)
        , CONSTRAINT UNIQUE_cumulus_archive_location_key_path
            UNIQUE (cumulus_archive_location, key_path)
        );

        -- Comments
        COMMENT ON TABLE files
            IS 'Files that are in the ORCA holdings. (Latest version only)';
        COMMENT ON COLUMN files.id
            IS 'Internal ORCA file ID';
        COMMENT ON COLUMN files.granule_id
            IS 'Granule that the file belongs to references the internal ORCA granule ID.';
         COMMENT ON COLUMN files.name
            IS 'Name of the file including extension';
         COMMENT ON COLUMN files.orca_archive_location
            IS 'Archive bucket that the file object is stored in';
         COMMENT ON COLUMN files.cumulus_archive_location
            IS 'Cumulus S3 bucket where the file is thought to be stored.';
         COMMENT ON COLUMN files.key_path
            IS 'Full AWS key path including file name.';
        COMMENT ON COLUMN files.ingest_time
            IS 'Date and time the file was ingested into ORCA';
        COMMENT ON COLUMN files.etag
            IS 'etag of the file object in the archive bucket.';
        COMMENT ON COLUMN files.version
            IS 'Latest version of the file in the archive bucket';
        COMMENT ON COLUMN files.size_in_bytes
            IS 'Size of the object in bytes';
        COMMENT ON COLUMN files.hash
            IS 'Hash of the object from Cumulus';
        COMMENT ON COLUMN files.hash_type
            IS 'Hash type used to hash the object. Supplied by Cumulus.';
        -- Grants
        GRANT SELECT, INSERT, UPDATE, DELETE ON files TO orca_app;
    """
    )


def schema_versions_data_sql() -> text:  # pragma: no cover
    """
    Data for the schema_versions table. Inserts the current schema
    version into the table.

    Returns:
        SQL for populating schema_versions table.
    """
    return text(
        """
        -- Populate with the current version
        -- Update is_latest to false for all records first to prevent error
        UPDATE schema_versions
        SET is_latest = False;

        -- Upsert the current version
        INSERT INTO schema_versions
        VALUES (4, 'Added inventory schema for v4.x of ORCA application', NOW(), True)
        ON CONFLICT (version_id)
        DO UPDATE SET is_latest = True;
    """
    )
