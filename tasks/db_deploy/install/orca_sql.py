"""
Name: orca_sql.py

Description: All the SQL used for creating and migrating the ORCA schema.
"""
# Imports
from sqlalchemy import text


# ----------------------------------------------------------------------------
# ORCA SQL used for creating the Database
# ----------------------------------------------------------------------------
def commit_sql() -> text:  # pragma: no cover
    """
    SQL for a simple 'commit' to exit the current transaction.
    """
    return text("commit")


def app_database_sql(db_name: str, admin_username: str) -> text:
    """
    Full SQL for creating the ORCA application database.

    Returns:
        SQL for creating database.
    """
    return text(  # nosec
        f"""
        CREATE DATABASE {db_name}
            OWNER "{admin_username}"
            TEMPLATE template1
            ENCODING 'UTF8';
    """
    )


def app_database_comment_sql(db_name: str) -> text:
    """
    SQL for adding a documentation comment to the database.
    Cannot be merged with DB creation due to SQLAlchemy limitations.
    """
    return text(  # nosec
        f"""
        COMMENT ON DATABASE {db_name}
            IS 'Operational Recovery Cloud Archive (ORCA) database.'
"""
    )


# ----------------------------------------------------------------------------
# ORCA SQL used for creating ORCA schema, roles, and users
# ----------------------------------------------------------------------------
def dbo_role_sql(db_name: str, admin_username: str) -> text:
    """
    Full SQL for creating the ORCA dbo role that owns the ORCA schema and
    objects.

    Returns:
        SQL for creating orca_dbo role.
    """
    return text(  # nosec
        f"""
        DO
        $$
          BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_group WHERE groname = 'orca_dbo' ) THEN
              -- Create Application Role
              CREATE ROLE orca_dbo
                NOLOGIN
                INHERIT;

              -- Add role comment
              COMMENT ON ROLE orca_dbo
                IS 'Group that contains the permissions needed for the ORCA application owner.';

            END IF;

            -- Grants
            GRANT CONNECT ON DATABASE "{db_name}" TO orca_dbo;
            GRANT CREATE ON DATABASE "{db_name}" TO orca_dbo;
            GRANT orca_dbo TO "{admin_username}";
          END
        $$
    """  # nosec
    )


def app_role_sql(db_name: str) -> text:
    """
    Full SQL for creating the ORCA application role that has all the privileges
    to interact with the ORCA schema.

    Returns:
        SQL for creating orca_app role.
    """
    return text(  # nosec
        f"""
        DO
        $$
        BEGIN
          IF NOT EXISTS (SELECT 1 FROM pg_group WHERE groname = 'orca_app' ) THEN
            -- Create Application Role
            CREATE ROLE orca_app
              NOLOGIN
              INHERIT;

            -- Add role comment
            COMMENT ON ROLE orca_app
              IS 'Group that contains the permissions needed for the ORCA application user.';

          END IF;

          -- Add Grants
          GRANT CONNECT ON DATABASE "{db_name}" TO orca_app;
        END
        $$;
    """  # nosec
    )


def orca_schema_sql() -> text:  # pragma: no cover
    """
    Full SQL for creating the ORCA application schema that contains all the
    ORCA tables and objects. This SQL must be used after the dbo_role_sql and
    before the app_user_sql and ORCA objects.

    Returns:
        SQL for creating orca schema.
    """
    return text(
        """
        --CREATE SCHEMA orca
        CREATE SCHEMA IF NOT EXISTS orca AUTHORIZATION orca_dbo;

        -- Comment
        COMMENT ON SCHEMA orca
            IS 'Contains all the objects needed to operate the ORCA application';

        -- GRANT the privileges needed
        GRANT USAGE ON SCHEMA orca TO orca_app;

        -- Setup Default Privileges for application user as a catch all
        ALTER DEFAULT PRIVILEGES FOR USER orca_dbo IN SCHEMA orca
          GRANT SELECT ON TABLES TO orca_app;
        ALTER DEFAULT PRIVILEGES FOR USER orca_dbo IN SCHEMA orca
          GRANT INSERT ON TABLES TO orca_app;
        ALTER DEFAULT PRIVILEGES FOR USER orca_dbo IN SCHEMA orca
          GRANT UPDATE ON TABLES TO orca_app;
        ALTER DEFAULT PRIVILEGES FOR USER orca_dbo IN SCHEMA orca
          GRANT DELETE ON TABLES TO orca_app;
        ALTER DEFAULT PRIVILEGES FOR USER orca_dbo IN SCHEMA orca
          GRANT EXECUTE ON FUNCTIONS TO orca_app;
        ALTER DEFAULT PRIVILEGES FOR USER orca_dbo IN SCHEMA orca
          GRANT USAGE ON SEQUENCES TO orca_app;
        ALTER DEFAULT PRIVILEGES FOR USER orca_dbo IN SCHEMA orca
          GRANT SELECT ON SEQUENCES TO orca_app;
        ALTER DEFAULT PRIVILEGES FOR USER orca_dbo IN SCHEMA orca
          GRANT UPDATE ON SEQUENCES TO orca_app;
        ALTER DEFAULT PRIVILEGES FOR USER orca_dbo IN SCHEMA orca
          GRANT USAGE ON TYPES TO orca_app;
        ALTER DEFAULT PRIVILEGES FOR USER orca_dbo IN SCHEMA orca
          GRANT REFERENCES ON TABLES TO orca_app;
        ALTER DEFAULT PRIVILEGES FOR USER orca_dbo IN SCHEMA orca
          GRANT TRIGGER ON TABLES TO orca_app;
    """
    )


def app_user_sql(user_name: str) -> text:
    """
    Full SQL for creating the ORCA application database user. Must be created
    after the app_role_sql and orca_schema_sql.

    Args:
        user_name: Username for the application user

    Returns:
        SQL for creating PREFIX_orcauser user.
    """
    return text(  # nosec
        f"""
        DO
        $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_user WHERE usename = :user_name ) THEN
                -- Create user
                CREATE ROLE "{user_name}"
                    LOGIN
                    INHERIT
                    ENCRYPTED PASSWORD :user_password
                    IN ROLE orca_app;

                -- Add comment
                COMMENT ON ROLE "{user_name}"
                    IS 'ORCA application user.';

                RAISE NOTICE 'USER CREATED "{user_name}".';

            END IF;

            -- Alter the roles search path so on login it has what it needs for a path
            ALTER ROLE "{user_name}" SET search_path = orca, public;
        END
        $$;
    """  # nosec
    )


def create_extension() -> text:  # pragma: no cover
    """
    Full SQL for creating the aws_s3 extension used for COPYING S3 reporting data
    from a CSV file in an AWS bucket into the database.

    Returns:
        SQL for creating extension for the database.
    """

    return text(
        """
            -- Create extension
            CREATE EXTENSION IF NOT EXISTS aws_s3 CASCADE;
        """
    )


# ----------------------------------------------------------------------------
# ORCA SQL used for creating ORCA general metadata tables
# ----------------------------------------------------------------------------
def schema_versions_table_sql() -> text:  # pragma: no cover
    """
    Full SQL for creating the schema_versions table.

    Returns:
        SQL for creating schema_versions table.
    """
    return text(
        """
        CREATE TABLE IF NOT EXISTS schema_versions
        (
          version_id   int                      NOT NULL
        , description  text                     NOT NULL
        , install_date timestamp with time zone NOT NULL
        , is_latest    boolean                  NOT NULL DEFAULT False
        , CONSTRAINT PK_schema_versions PRIMARY KEY(version_id)
        );

        -- Comments
        COMMENT ON TABLE schema_versions
            IS 'Migration management table that tracks ORCA installed schema versions.';
        COMMENT ON COLUMN schema_versions.version_id
            IS 'Version of the ORCA schema that is installed.';
        COMMENT ON COLUMN schema_versions.description
            IS 'Description of the schema version.';
        COMMENT ON COLUMN schema_versions.install_date
            IS 'Date and time the schema was installed.';
        COMMENT ON COLUMN schema_versions.is_latest
            IS 'Flag denoting the current schema installed.';

        -- Indexes - Partial index to enforce only having 1 is_latest set to true
        CREATE UNIQUE INDEX IF NOT EXISTS idx_uniq_schema_versions_latest
            ON schema_versions (is_latest)
            WHERE is_latest = True;

        -- Grants
        GRANT SELECT ON schema_versions TO orca_app;
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
          VALUES
            (5, 'Added internal reconciliation schema for v5.x of ORCA application', NOW(), True)
        ON CONFLICT (version_id)
        DO UPDATE SET is_latest = True;
    """
    )


# ----------------------------------------------------------------------------
# ORCA SQL used for creating ORCA recovery tables
# ----------------------------------------------------------------------------
def recovery_status_table_sql() -> text:  # pragma: no cover
    """
    Full SQL for creating the recovery_status table. This SQL must be run
    before any of the other recovery table sql.

    Returns:
        SQL for creating recovery_status table.
    """
    return text(
        """
        -- Create table
        CREATE TABLE IF NOT EXISTS recovery_status
        (
          id    int2 NOT NULL
        , value text NOT NULL
        , CONSTRAINT PK_recovery_status PRIMARY KEY(id)
        , CONSTRAINT UNIQUE_recovery_status_value UNIQUE (value)
        );

        -- Comments
        COMMENT ON TABLE recovery_status
            IS 'Reference table for valid status values and status order.';
        COMMENT ON COLUMN recovery_status.id
            IS 'Status ID';
        COMMENT ON COLUMN recovery_status.value
            IS 'Human readable status value';

        -- Grants
        GRANT SELECT ON recovery_status TO orca_app;
    """
    )


def recovery_status_data_sql() -> text:  # pragma: no cover
    """
    Data for the recovery_status table. Inserts the current status values into
    the table.

    Returns:
        SQL for populating recovery_status table.
    """
    return text(
        """
        -- Upsert the data lookup rows for the table
        INSERT INTO recovery_status VALUES (1, 'pending')
            ON CONFLICT (id) DO NOTHING;
        INSERT INTO recovery_status VALUES (2, 'staged')
            ON CONFLICT (id) DO NOTHING;
        INSERT INTO recovery_status VALUES (3, 'error')
            ON CONFLICT (id) DO NOTHING;
        INSERT INTO recovery_status VALUES (4, 'success')
            ON CONFLICT (id) DO NOTHING;
    """
    )


def recovery_job_table_sql() -> text:  # pragma: no cover
    """
    Full SQL for creating the recovery_job table. This SQL must be run
    before the other recovery_file table sql and after the recovery_status
    table sql to maintain key dependencies.

    Returns:
        SQL for creating recovery_job table.
    """
    return text(
        """
        -- Create table
        CREATE TABLE IF NOT EXISTS recovery_job
        (
          job_id              text NOT NULL
        , collection_id       text NOT NULL
        , granule_id          text NOT NULL
        , archive_destination text NOT NULL
        , status_id           int2 NOT NULL
        , request_time        timestamp with time zone NOT NULL
        , completion_time     timestamp with time zone NULL
        , CONSTRAINT PK_recovery_job
            PRIMARY KEY (job_id, collection_id, granule_id)
        , CONSTRAINT FK_recovery_job_status
            FOREIGN KEY (status_id) REFERENCES recovery_status (id)
        );

        -- Comments
        COMMENT ON TABLE recovery_job
            IS 'ORCA Job Recovery table that contains basic information at the granule level.';
        COMMENT ON COLUMN recovery_job.job_id
            IS 'This is the Cumulus AsyncOperationId value or a generated id value.';
        COMMENT ON COLUMN recovery_job.granule_id
            IS 'This is the granule id for the granule to be recovered.';
        COMMENT ON COLUMN recovery_job.archive_destination
            IS 'ORCA archive bucket where the data being restored lives.';
        COMMENT ON COLUMN recovery_job.status_id
            IS 'The current status of the recovery for the granule.';
        COMMENT ON COLUMN recovery_job.request_time
            IS 'The date and time the recovery was requested for the granule.';
        COMMENT ON COLUMN recovery_job.completion_time
            IS 'Date and time the recovery reached an end state for all the files in the granule.';

        -- Grants
        GRANT SELECT, INSERT, UPDATE, DELETE ON recovery_job TO orca_app;
    """
    )


def recovery_file_table_sql() -> text:  # pragma: no cover
    """
    Full SQL for creating the recovery_file table. This SQL must be run
    after the recovery_job table sql to maintain key dependencies.

    Returns:
        SQL for creating recovery_file table.
    """
    return text(
        """
        -- Create table
        CREATE TABLE IF NOT EXISTS recovery_file
        (
          job_id                 text NOT NULL
        , collection_id          text NOT NULL
        , granule_id             text NOT NULL
        , filename               text NOT NULL
        , key_path               text NOT NULL
        , multipart_chunksize_mb integer NULL
        , restore_destination    text NOT NULL
        , status_id              int2 NOT NULL
        , error_message          text NULL
        , request_time           timestamp with time zone NOT NULL
        , last_update            timestamp with time zone NOT NULL
        , completion_time        timestamp with time zone NULL
        , CONSTRAINT PK_recovery_file
            PRIMARY KEY (job_id, collection_id, granule_id, filename)
        , CONSTRAINT FK_recovery_file_status
            FOREIGN KEY (status_id) REFERENCES recovery_status (id)
        , CONSTRAINT FK_recovery_file_recoverjob
            FOREIGN KEY (job_id, collection_id, granule_id)
            REFERENCES recovery_job (job_id, collection_id, granule_id)
        );

        -- Comments
        COMMENT ON TABLE recovery_file
            IS 'ORCA Recovery table that contains basic information at the file level.';
        COMMENT ON COLUMN recovery_file.job_id
            IS 'Job the recovered file is a part of that references recovery_job.';
        COMMENT ON COLUMN recovery_file.granule_id
            IS 'This is the granule id for the granule to be recovered.';
        COMMENT ON COLUMN recovery_file.filename
            IS 'Name of the file being restored.';
        COMMENT ON COLUMN recovery_file.key_path
            IS 'Full key value of the data being restored.';
        COMMENT ON COLUMN recovery_file.multipart_chunksize_mb
            IS 'Overrides default_multipart_chunksize_mb in TF.';
        COMMENT ON COLUMN recovery_file.restore_destination
            IS 'S3 ORCA restoration bucket for the data.';
        COMMENT ON COLUMN recovery_file.status_id
            IS 'Current restore status of the file.';
        COMMENT ON COLUMN recovery_file.error_message
            IS 'Error message that occurred during failure.';
        COMMENT ON COLUMN recovery_file.request_time
            IS 'Time the file was requested to be restored.';
        COMMENT ON COLUMN recovery_file.last_update
            IS 'Time the status was last updated for the file.';
        COMMENT ON COLUMN recovery_file.completion_time
            IS 'Time the file restoration hit a complete state.';

        -- Grants
        GRANT SELECT, INSERT, UPDATE, DELETE ON recovery_file TO orca_app;
    """
    )


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


def storage_class_table_sql() -> text:  # pragma: no cover
    """
    Full SQL for creating the storage_class table. This SQL must be run
    before any of the other recovery table sql.

    Returns:
        (sqlalchemy.sql.element.TextClause): SQL for creating storage_class table.
    """
    return text(
        """
        -- Create table
        CREATE TABLE IF NOT EXISTS storage_class
        (
          id    int2 NOT NULL
        , value text NOT NULL
        , CONSTRAINT PK_storage_class PRIMARY KEY(id)
        , CONSTRAINT UNIQUE_storage_class_value UNIQUE (value)
        );

        -- Comments
        COMMENT ON TABLE storage_class
            IS 'Reference table for valid storage classes.';
        COMMENT ON COLUMN storage_class.id
            IS 'Storage Class ID';
        COMMENT ON COLUMN storage_class.value
            IS 'Human readable storage class';

        -- Grants
        GRANT SELECT ON storage_class TO orca_app;
    """
    )


def storage_class_data_sql() -> text:  # pragma: no cover
    """
    Data for the storage_class table. Inserts the currently valid storage classes into
    the table.

    Returns:
        (sqlalchemy.sql.element.TextClause): SQL for populating storage_class table.
    """
    return text(
        """
        -- Upsert the data lookup rows for the table
        INSERT INTO storage_class VALUES (1, 'GLACIER')
            ON CONFLICT (id) DO NOTHING;
        INSERT INTO storage_class VALUES (2, 'DEEP_ARCHIVE')
            ON CONFLICT (id) DO NOTHING;
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
        , storage_class_id          int2 NOT NULL
        , CONSTRAINT PK_files
            PRIMARY KEY (id)
        , CONSTRAINT FK_granule_file
            FOREIGN KEY (granule_id) REFERENCES granules (id)
        , CONSTRAINT UNIQUE_orca_archive_location_key_path
            UNIQUE (orca_archive_location, key_path)
        , CONSTRAINT UNIQUE_cumulus_archive_location_key_path
            UNIQUE (cumulus_archive_location, key_path)
        , CONSTRAINT FK_recovery_file_storage_class
            FOREIGN KEY (storage_class_id) REFERENCES storage_class (id)
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
        COMMENT ON COLUMN files.storage_class_id
            IS 'Storage class of the file.';
        -- Grants
        GRANT SELECT, INSERT, UPDATE, DELETE ON files TO orca_app;
    """
    )


# ----------------------------------------------------------------------------
# ORCA SQL used for creating ORCA internal reconciliation tables
# ----------------------------------------------------------------------------
def reconcile_status_table_sql() -> text:  # pragma: no cover
    """
    Full SQL for creating the reconcile_status table.

    Returns:
        SQL for creating reconcile_status table.
    """
    return text(
        """
        -- Create table
        CREATE TABLE IF NOT EXISTS reconcile_status
        (
          id       int2 NOT NULL
        , value    text NOT NULL
        , CONSTRAINT PK_reconcile_status PRIMARY KEY(id)
        , CONSTRAINT UNIQUE_reconcile_status_value UNIQUE (value)
        );

        -- Comments
        COMMENT ON TABLE reconcile_status
            IS 'Reference table for valid status values and status order.';
        COMMENT ON COLUMN reconcile_status.id
            IS 'Status ID';
        COMMENT ON COLUMN reconcile_status.value
            IS 'Human readable status value';

        -- Upsert the data lookup rows for the table
        INSERT INTO reconcile_status VALUES (1, 'getting S3 list')
            ON CONFLICT (id) DO NOTHING;
        INSERT INTO reconcile_status VALUES (2, 'staged')
            ON CONFLICT (id) DO NOTHING;
        INSERT INTO reconcile_status VALUES (3, 'generating reports')
            ON CONFLICT (id) DO NOTHING;
        INSERT INTO reconcile_status VALUES (4, 'error')
            ON CONFLICT (id) DO NOTHING;
        INSERT INTO reconcile_status VALUES (5, 'success')
            ON CONFLICT (id) DO NOTHING;
        """
    )


def reconcile_job_table_sql() -> text:  # pragma: no cover
    """
    Full SQL for creating the reconcile_job table.

    Returns:
        SQL for creating reconcile_job table.
    """
    return text(
        """
        -- Create reconcile_job table
        CREATE TABLE IF NOT EXISTS reconcile_job
        (
          id                         bigserial NOT NULL
        , orca_archive_location      text NOT NULL
        , status_id                  int2 NOT NULL
        , inventory_creation_time    timestamp with time zone NOT NULL
        , start_time                 timestamp with time zone NOT NULL
        , last_update                timestamp with time zone NOT NULL
        , end_time                   timestamp with time zone NULL
        , error_message              text NULL
        , CONSTRAINT PK_reconcile_job
            PRIMARY KEY(id)
        , CONSTRAINT FK_reconcile_job_status
            FOREIGN KEY(status_id) REFERENCES reconcile_status(id)
        );

        -- Comments
        COMMENT ON TABLE reconcile_job
          IS 'Manages internal reconciliation job information.';
        COMMENT ON COLUMN reconcile_job.id
          IS 'Job ID unique to each internal reconciliation job.';
        COMMENT ON COLUMN reconcile_job.orca_archive_location
          IS 'Archive bucket the reconciliation targets.';
        COMMENT ON COLUMN reconcile_job.status_id
          IS 'Current status of the job.';
        COMMENT ON COLUMN reconcile_job.inventory_creation_time
          IS 'Inventory report initiation time from the s3 manifest.';
        COMMENT ON COLUMN reconcile_job.start_time
          IS 'Date and time the internal reconcile job started.';
        COMMENT ON COLUMN reconcile_job.last_update
          IS 'Date and time the job status was last updated.';
        COMMENT ON COLUMN reconcile_job.end_time
          IS 'Time the job completed and wrote the report information.';
        COMMENT ON COLUMN reconcile_job.error_message
          IS 'Critical error the job ran into that prevented it from finishing.';
        """
    )


def reconcile_s3_object_table_sql() -> text:  # pragma: no cover
    """
    Full SQL for creating the reconcile_s3_object table.

    Returns:
        SQL for creating reconcile_s3_object table.
    """
    return text(
        """
            -- Create reconcile_s3_object table
            CREATE TABLE IF NOT EXISTS reconcile_s3_object
            (
              job_id                   int8 NOT NULL
            , orca_archive_location    text NOT NULL
            , key_path                 text NOT NULL
            , etag                     text NOT NULL
            , last_update              timestamp with time zone NOT NULL
            , size_in_bytes            int8 NOT NULL
            , storage_class            text NOT NULL
            , delete_marker            bool NOT NULL DEFAULT False
            )
            PARTITION BY LIST (orca_archive_location);

            -- Comment
            COMMENT ON TABLE reconcile_s3_object
              IS 'Holds the listing from the buckets to use for internal comparisons.';
            COMMENT ON COLUMN reconcile_s3_object.job_id
              IS 'Job the S3 listing is a part of for the comparison.';
            COMMENT ON COLUMN reconcile_s3_object.orca_archive_location
              IS 'Archive bucket name where the file is stored.';
            COMMENT ON COLUMN reconcile_s3_object.key_path
              IS 'Full path and file name of the object in the S3 bucket.';
            COMMENT ON COLUMN reconcile_s3_object.etag
              IS 'AWS etag value from the s3 inventory report.';
            COMMENT ON COLUMN reconcile_s3_object.last_update
              IS 'AWS Last Update from the s3 inventory report.';
            COMMENT ON COLUMN reconcile_s3_object.size_in_bytes
              IS 'AWS size of the file in bytes from the s3 inventory report.';
            COMMENT ON COLUMN reconcile_s3_object.storage_class
              IS 'AWS storage class the object is in from the s3 inventory report.';
            COMMENT ON COLUMN reconcile_s3_object.delete_marker
              IS 'Set to True if object is marked as deleted.';
        """
    )


def reconcile_s3_object_partition_sql(partition_name: str) -> text:
    """
    Full SQL for creating the reconcile_s3_object partition table. Requires the
    user to pass the orca_archive_location value for the partition in the form
    of `{"bucket_name": value}` when executing the SQL via the driver.

    Args:
        partition_name(str): Name of the partition table.

    Returns:
        SQL for creating reconcile_s3_object partition table.
    """
    return text(  # nosec
        f"""
            -- Create orca_archive_location_:bucket_name
            CREATE TABLE {partition_name} PARTITION OF reconcile_s3_object
            (
              CONSTRAINT PK_{partition_name}
                PRIMARY KEY(key_path)
            , CONSTRAINT FK_reconcile_job_{partition_name}
                FOREIGN KEY(job_id) REFERENCES reconcile_job(id)
            )
            FOR VALUES IN (:bucket_name);

            -- Comment
            COMMENT ON TABLE {partition_name}
              IS 'Partition table for reconcile_s3_object based on orca_archive_location.';
            """
    )


def reconcile_catalog_mismatch_report_table_sql() -> text:  # pragma: no cover
    """
    Full SQL for creating the reconcile_catalog_mismatch_report table.

    Returns:
        SQL for creating reconcile_catalog_mismatch_report.
    """
    return text(
        """
            -- Create reconcile_catalog_mismatch_report table
            CREATE TABLE IF NOT EXISTS reconcile_catalog_mismatch_report
            (
              job_id                      int8 NOT NULL
            , collection_id               text NOT NULL
            , granule_id                  text NOT NULL
            , filename                    text NOT NULL
            , key_path                    text NOT NULL
            , cumulus_archive_location    text NOT NULL
            , orca_etag                   text NOT NULL
            , s3_etag                     text NOT NULL
            , orca_last_update            timestamp with time zone NOT NULL
            , s3_last_update              timestamp with time zone NOT NULL
            , orca_size_in_bytes          int8 NOT NULL
            , s3_size_in_bytes            int8 NOT NULL
            , orca_storage_class_id       int2 NOT NULL
            , s3_storage_class            text NOT NULL
            , discrepancy_type            text NOT NULL
            , CONSTRAINT PK_reconcile_catalog_mismatch_report
                PRIMARY KEY(job_id,collection_id,granule_id,key_path)
            , CONSTRAINT FK_reconcile_job_mismatch_report
                FOREIGN KEY(job_id) REFERENCES reconcile_job(id)
            , CONSTRAINT FK_mismatch_orca_storage_class
                FOREIGN KEY (orca_storage_class_id) REFERENCES storage_class (id)
            );

            -- Comment
            COMMENT ON TABLE reconcile_catalog_mismatch_report
              IS 'Identifies objects that have mismatched values between the ORCA catalog and s3.';
            COMMENT ON COLUMN reconcile_catalog_mismatch_report.job_id
              IS 'Job the mismatch granule was found in. References the reconcile_job table.';
            COMMENT ON COLUMN reconcile_catalog_mismatch_report.collection_id
              IS 'Cumulus Collection ID value from the ORCA catalog.';
            COMMENT ON COLUMN reconcile_catalog_mismatch_report.granule_id
              IS 'Cumulus granuleID value from the ORCA catalog.';
            COMMENT ON COLUMN reconcile_catalog_mismatch_report.filename
              IS 'Filename of the object from the ORCA catalog.';
            COMMENT ON COLUMN reconcile_catalog_mismatch_report.key_path
              IS 'key path and filename of the object in the ORCA catalog.';
            COMMENT ON COLUMN reconcile_catalog_mismatch_report.cumulus_archive_location
              IS 'Expected S3 bucket the object is located in Cumulus. From the ORCA catalog.';
            COMMENT ON COLUMN reconcile_catalog_mismatch_report.orca_etag
              IS 'etag of the object as reported in the ORCA catalog.';
            COMMENT ON COLUMN reconcile_catalog_mismatch_report.s3_etag
              IS 'etag of the object as reported in the S3 bucket.';
            COMMENT ON COLUMN reconcile_catalog_mismatch_report.orca_last_update
              IS 'Last update of the object as reported in the ORCA catalog.';
            COMMENT ON COLUMN reconcile_catalog_mismatch_report.s3_last_update
              IS 'Last update of the object as reported in the S3 bucket.';
            COMMENT ON COLUMN reconcile_catalog_mismatch_report.orca_size_in_bytes
              IS 'Size in bytes of the object as reported in the ORCA catalog.';
            COMMENT ON COLUMN reconcile_catalog_mismatch_report.s3_size_in_bytes
              IS 'Size in bytes of the object as reported in the S3 bucket.';
            COMMENT ON COLUMN reconcile_catalog_mismatch_report.orca_storage_class_id
              IS 'Storage class of the file as reported in the ORCA catalog.';
            COMMENT ON COLUMN reconcile_catalog_mismatch_report.s3_storage_class
              IS 'Storage class of the file as reported in the S3 bucket.';
            COMMENT ON COLUMN reconcile_catalog_mismatch_report.discrepancy_type
              IS 'Type of discrepancy found during reconciliation.';
        """
    )


def reconcile_orphan_report_table_sql() -> text:  # pragma: no cover
    """
    Full SQL for creating the reconcile_orphan_report table.

    Returns:
        SQL for creating reconcile_orphan_report table.
    """
    return text(
        """
            -- Create reconcile_orphan_report table
            CREATE TABLE IF NOT EXISTS reconcile_orphan_report
            (
              job_id           int8 NOT NULL
            , key_path         text NOT NULL
            , etag             text NOT NULL
            , last_update      timestamp with time zone NOT NULL
            , size_in_bytes    int8 NOT NULL
            , storage_class    text NOT NULL
            , CONSTRAINT PK_reconcile_orphan_report
                PRIMARY KEY(job_id,key_path)
            , CONSTRAINT FK_reconcile_job_orphan_report
                FOREIGN KEY(job_id) REFERENCES reconcile_job(id)
            );

            -- Comment
            COMMENT ON TABLE reconcile_orphan_report
              IS 'Identifies objects in the archive bucket that are not in the catalog.';
            COMMENT ON COLUMN reconcile_orphan_report.job_id
              IS 'Associates the orphaned file to a internal reconciliation job.';
            COMMENT ON COLUMN reconcile_orphan_report.key_path
              IS 'Contains the path and file name from the reconcile_s3_object (key_path) column.';
            COMMENT ON COLUMN reconcile_orphan_report.etag
              IS 'AWS Etag of the object from the reconcile_s3_object (etag) column.';
            COMMENT ON COLUMN reconcile_orphan_report.last_update
              IS 'AWS last update of the object from the reconcile_s3_object (lst_update) column.';
            COMMENT ON COLUMN reconcile_orphan_report.size_in_bytes
              IS 'AWS size of the object in bytes from the reconcile_s3_object (size) column.';
            COMMENT ON COLUMN reconcile_orphan_report.storage_class
              IS 'AWS storage class from the reconcile_s3_object (storage_class) column.';
        """
    )


def reconcile_phantom_report_table_sql() -> text:  # pragma: no cover
    """
    Full SQL for creating the reconcile_phantom_report table.

    Returns:
        SQL for creating reconcile_phantom_report table.
    """
    return text(
        """
            -- Create reconcile_phantom_report table
            CREATE TABLE IF NOT EXISTS reconcile_phantom_report
            (
              job_id                int8 NOT NULL
            , collection_id         text NOT NULL
            , granule_id            text NOT NULL
            , filename              text NOT NULL
            , key_path              text NOT NULL
            , orca_etag             text NOT NULL
            , orca_last_update      timestamp with time zone NOT NULL
            , orca_size             int8 NOT NULL
            , orca_storage_class_id int2 NOT NULL
            , CONSTRAINT PK_reconcile_phantom_report
                PRIMARY KEY(job_id,collection_id,granule_id,key_path)
            , CONSTRAINT FK_reconcile_job_phantom_report
                FOREIGN KEY(job_id) REFERENCES reconcile_job(id)
            , CONSTRAINT FK_phantom_orca_storage_class
                FOREIGN KEY (orca_storage_class_id) REFERENCES storage_class (id)
            );
            -- Comment
            COMMENT ON TABLE reconcile_phantom_report
              IS 'Identifies objects that exist in the ORCA catalog and do not exist in S3.';
            COMMENT ON COLUMN reconcile_phantom_report.job_id
              IS 'Job the missing granule was found in. References the reconcile_job table.';
            COMMENT ON COLUMN reconcile_phantom_report.collection_id
              IS 'Cumulus Collection ID value from the ORCA catalog.';
            COMMENT ON COLUMN reconcile_phantom_report.granule_id
              IS 'Cumulus granuleID value from the ORCA catalog.';
            COMMENT ON COLUMN reconcile_phantom_report.filename
              IS 'Filename of the object from the ORCA catalog.';
            COMMENT ON COLUMN reconcile_phantom_report.key_path
              IS 'key path and filename of the object in the ORCA catalog.';
            COMMENT ON COLUMN reconcile_phantom_report.orca_etag
              IS 'etag of the object as reported in the ORCA catalog.';
            COMMENT ON COLUMN reconcile_phantom_report.orca_last_update
              IS 'Last update of the object as reported in the ORCA catalog.';
            COMMENT ON COLUMN reconcile_phantom_report.orca_size
              IS 'Size in bytes of the object as reported in the ORCA catalog.';
        """
    )
