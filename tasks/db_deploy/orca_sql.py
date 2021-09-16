"""
Name: orca_sql.py

Description: All of the SQL used for creating and migrating the ORCA schema.
"""
# Imports
from sqlalchemy import text
from sqlalchemy.sql.elements import TextClause
# ----------------------------------------------------------------------------
# ORCA SQL used for creating the Database
# ----------------------------------------------------------------------------
def app_database_sql() -> TextClause:
    """
    Full SQL for creating the ORCA application database.

    Returns:
        (sqlalchemy.sql.element.TextClause): SQL for creating database.
    """
    return text(
        """
        CREATE DATABASE disaster_recovery
            OWNER postgres
            TEMPLATE template1
            ENCODING 'UTF8';

        COMMENT ON DATABASE disaster_recovery
            IS 'Operational Recovery Cloud Archive (ORCA) database.';
    """
    )


# ----------------------------------------------------------------------------
# ORCA SQL used for creating ORCA schema, roles, and users
# ----------------------------------------------------------------------------
def dbo_role_sql() -> TextClause:
    """
    Full SQL for creating the ORCA dbo role that owns the ORCA schema and
    objects.

    Returns:
        (sqlalchemy.sql.element.TextClause): SQL for creating orca_dbo role.
    """
    return text(
        """
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
                IS 'Group that contains all the permissions necessary for the ORCA application owner.';

            END IF;

            -- Grants
            GRANT CONNECT ON DATABASE disaster_recovery TO orca_dbo;
            GRANT CREATE ON DATABASE disaster_recovery TO orca_dbo;
            GRANT orca_dbo TO postgres;
          END
        $$
    """
    )


def app_role_sql() -> TextClause:
    """
    Full SQL for creating the ORCA application role that has all the privileges
    to interact with the ORCA schema.

    Returns:
        (sqlalchemy.sql.element.TextClause): SQL for creating orca_app role.
    """
    return text(
        """
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
              IS 'Group that contains all the permissions necessary for the ORCA application user.';

          END IF;

          -- Add Grants
          GRANT CONNECT ON DATABASE disaster_recovery TO orca_app;
        END
        $$;
    """
    )


def orca_schema_sql() -> TextClause:
    """
    Full SQL for creating the ORCA application schema that contains all the
    ORCA tables and objects. This SQL must be used after the dbo_role_sql and
    before the app_user_sql and ORCA objects.

    Returns:
        (sqlalchemy.sql.element.TextClause): SQL for creating orca schema.
    """
    return text(
        """
        --CREATE SCHEMA orca
        CREATE SCHEMA IF NOT EXISTS orca AUTHORIZATION orca_dbo;

        -- Comment
        COMMENT ON SCHEMA orca
            IS 'Contains all the objects needed to operate the ORCA application';

        -- GRANT the privelages needed
        GRANT USAGE ON SCHEMA orca TO orca_app;

        -- Setup Default Privelages for application user as a catch all
        ALTER DEFAULT PRIVILEGES FOR USER orca_dbo IN SCHEMA orca GRANT SELECT ON TABLES TO orca_app;
        ALTER DEFAULT PRIVILEGES FOR USER orca_dbo IN SCHEMA orca GRANT INSERT ON TABLES TO orca_app;
        ALTER DEFAULT PRIVILEGES FOR USER orca_dbo IN SCHEMA orca GRANT UPDATE ON TABLES TO orca_app;
        ALTER DEFAULT PRIVILEGES FOR USER orca_dbo IN SCHEMA orca GRANT DELETE ON TABLES TO orca_app;
        ALTER DEFAULT PRIVILEGES FOR USER orca_dbo IN SCHEMA orca GRANT EXECUTE ON FUNCTIONS TO orca_app;
        ALTER DEFAULT PRIVILEGES FOR USER orca_dbo IN SCHEMA orca GRANT USAGE ON SEQUENCES TO orca_app;
        ALTER DEFAULT PRIVILEGES FOR USER orca_dbo IN SCHEMA orca GRANT SELECT ON SEQUENCES TO orca_app;
        ALTER DEFAULT PRIVILEGES FOR USER orca_dbo IN SCHEMA orca GRANT UPDATE ON SEQUENCES TO orca_app;
        ALTER DEFAULT PRIVILEGES FOR USER orca_dbo IN SCHEMA orca GRANT USAGE ON TYPES TO orca_app;
        ALTER DEFAULT PRIVILEGES FOR USER orca_dbo IN SCHEMA orca GRANT REFERENCES ON TABLES TO orca_app;
        ALTER DEFAULT PRIVILEGES FOR USER orca_dbo IN SCHEMA orca GRANT TRIGGER ON TABLES TO orca_app;
    """
    )


def app_user_sql(user_password: str) -> TextClause:
    """
    Full SQL for creating the ORCA application database user. Must be created
    after the app_role_sql and orca_schema_sql.

    Args:
        user_password (str): Password for the application user

    Returns:
        (sqlalchemy.sql.element.TextClause): SQL for creating orcauser user.
    """
    if user_password is None or len(user_password) < 12:
        logger.critical("User password must be at least 12 characters long.")
        raise Exception("Password not long enough.")

    return text(
        f"""
        DO
        $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_user WHERE usename = 'orcauser' ) THEN
                -- Create orcauser
                CREATE ROLE orcauser
                    LOGIN
                    INHERIT
                    ENCRYPTED PASSWORD '{user_password}'
                    IN ROLE orca_app;

                -- Add comment
                COMMENT ON ROLE orcauser
                    IS 'ORCA application user.';

                RAISE NOTICE 'USER CREATED orcauser. PLEASE UPDATE THE USERS PASSWORD!';

            END IF;

            -- Alter the roles search path so on login it has what it needs for a path
            ALTER ROLE orcauser SET search_path = orca, public;
        END
        $$;
    """
    )


# ----------------------------------------------------------------------------
# ORCA SQL used for creating ORCA general metadata tables
# ----------------------------------------------------------------------------
def schema_versions_table_sql() -> TextClause:
    """
    Full SQL for creating the schema_versions table.

    Returns:
        (sqlalchemy.sql.element.TextClause): SQL for creating schema_versions table.
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


def schema_versions_data_sql() -> TextClause:
    """
    Data for the schema_versions table. Inserts the current schema
    version into the table.

    Returns:
        (sqlalchemy.sql.element.TextClause): SQL for populating schema_versions table.
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


# ----------------------------------------------------------------------------
# ORCA SQL used for creating ORCA recovery tables
# ----------------------------------------------------------------------------
def recovery_status_table_sql() -> TextClause:
    """
    Full SQL for creating the recovery_status table. This SQL must be run
    before any of the other recovery table sql.

    Returns:
        (sqlalchemy.sql.element.TextClause): SQL for creating recovery_status table.
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


def recovery_status_data_sql() -> TextClause:
    """
    Data for the recovery_status table. Inserts the current status values into
    the table.

    Returns:
        (sqlalchemy.sql.element.TextClause): SQL for populating recovery_status table.
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
        INSERT INTO recovery_status VALUES (4, 'complete')
            ON CONFLICT (id) DO NOTHING;
    """
    )


def recovery_job_table_sql() -> TextClause:
    """
    Full SQL for creating the recovery_job table. This SQL must be run
    before the other recovery_file table sql and after the recovery_status
    table sql to maintain key dependencies.

    Returns:
        (sqlalchemy.sql.element.TextClause): SQL for creating recovery_job table.
    """
    return text(
        """
        -- Create table
        CREATE TABLE IF NOT EXISTS recovery_job
        (
          job_id              text NOT NULL
        , granule_id          text NOT NULL
        , archive_destination text NOT NULL
        , status_id           int2 NOT NULL
        , request_time        timestamp with time zone NOT NULL
        , completion_time     timestamp with time zone NULL
        , CONSTRAINT PK_recovery_job PRIMARY KEY (job_id, granule_id)
        , CONSTRAINT FK_recovery_job_status FOREIGN KEY (status_id) REFERENCES recovery_status (id)
        );

        -- Comments
        COMMENT ON TABLE recovery_job
            IS 'ORCA Job Recovery table that contains basic information at the granule level.';
        COMMENT ON COLUMN recovery_job.job_id
            IS 'This is the Cumulus AsyncOperationId value used to group all recovery executions for granule recovery together.';
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


def recovery_file_table_sql() -> TextClause:
    """
    Full SQL for creating the recovery_file table. This SQL must be run
    after the recovery_job table sql to maintain key dependencies.

    Returns:
        (sqlalchemy.sql.element.TextClause): SQL for creating recovery_file table.
    """
    return text(
        """
        -- Create table
        CREATE TABLE IF NOT EXISTS recovery_file
        (
          job_id              text NOT NULL
        , granule_id          text NOT NULL
        , filename            text NOT NULL
        , key_path            text NOT NULL
        , restore_destination text NOT NULL
        , status_id           int2 NOT NULL
        , error_message       text NULL
        , request_time        timestamp with time zone NOT NULL
        , last_update         timestamp with time zone NOT NULL
        , completion_time     timestamp with time zone NULL
        , CONSTRAINT PK_recovery_file PRIMARY KEY (job_id, granule_id, filename)
        , CONSTRAINT FK_recovery_file_status FOREIGN KEY (status_id) REFERENCES recovery_status (id)
        , CONSTRAINT FK_recovery_file_recoverjob FOREIGN KEY (job_id, granule_id) REFERENCES recovery_job (job_id, granule_id)
        );

        -- Comments
        COMMENT ON TABLE recovery_file
            IS 'ORCA Recovery table that contains basic information at the file level.';
        COMMENT ON COLUMN recovery_file.job_id
            IS 'This is the Cumulus AsyncOperationId value used to group all recovery executions for granule recovery together.';
        COMMENT ON COLUMN recovery_file.granule_id
            IS 'This is the granule id for the granule to be recovered.';
        COMMENT ON COLUMN recovery_file.filename
            IS 'Name of the file being restored.';
        COMMENT ON COLUMN recovery_file.key_path
            IS 'Full key value of the data being restored.';
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

def providers_table_sql() -> TextClause:
    """
    Full SQL for creating the providers table. 

    Returns:
        (sqlalchemy.sql.element.TextClause): SQL for creating providers table.
    """
    return text(
        """
        -- Create table
        CREATE TABLE IF NOT EXISTS providers
        (
          provider_id         text NOT NULL
        , name                text NOT NULL
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


def collections_table_sql() -> TextClause:
    """
    Full SQL for creating the collections table. 

    Returns:
        (sqlalchemy.sql.element.TextClause): SQL for creating collections table.
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


def provider_collection_xref_table_sql() -> TextClause:
    """
    Full SQL for creating the cross reference table that ties a collection and provider together and resolves the many to many relationships.

    Returns:
        (sqlalchemy.sql.element.TextClause): SQL for creating provider_collection_xref table.
    """
    return text(
        """
        -- Create table
        CREATE TABLE IF NOT EXISTS provider_collection_xref
        (
          provider_id           text NOT NULL
        , collection_id         text NOT NULL
        , CONSTRAINT PK_provider_collection_xref PRIMARY KEY (provider_id,collection_id)
        , CONSTRAINT FK_provider_collection FOREIGN KEY (provider_id) REFERENCES providers (provider_id)
        , CONSTRAINT FK_collection_provider FOREIGN KEY (collection_id) REFERENCES collections (collection_id)
        );

        -- Comments
        COMMENT ON TABLE provider_collection_xref
            IS 'Cross refrence table that ties a collection and provider together and resolves the many to many relationship.';
        COMMENT ON COLUMN provider_collection_xref.provider_id
            IS 'Provider ID from the providers table.';
        COMMENT ON COLUMN provider_collection_xref.collection_id
            IS 'Collection ID from the collections table.';     
        -- Grants
        GRANT SELECT, INSERT, UPDATE, DELETE ON provider_collection_xref TO orca_app;
    """
    )


def granules_table_sql() -> TextClause:
    """
    Full SQL for creating the catalog granules table.

    Returns:
        (sqlalchemy.sql.element.TextClause): SQL for creating granules table.
    """
    return text(
        """
        -- Create table
        CREATE TABLE IF NOT EXISTS granules
        (
          id                    bigserial NOT NULL
        , collection_id         text NOT NULL
        , cumulus_granule_id    text NOT NULL
        , execution_id          text NOT NULL
        , ingest_time           timestamp with time zone NOT NULL
        , last_update           timestamp with time zone NOT NULL

        , CONSTRAINT PK_granules PRIMARY KEY (id)
        , CONSTRAINT FK_collection_granule FOREIGN KEY (collection_id) REFERENCES collections (collection_id)
        , CONSTRAINT UNIQUE_collection_granule_id UNIQUE (collection_id, cumulus_granule_id)
        );

        -- Comments
        COMMENT ON TABLE granules
            IS 'Granules that are in the ORCA archive holdings.';
        COMMENT ON COLUMN granules.id
            IS 'Internal orca granule ID pseudo key';
        COMMENT ON COLUMN granules.collection_id
            IS 'Collection ID from Cumulus that refrences the Collections table.';
         COMMENT ON COLUMN granules.cumulus_granule_id
            IS 'Granule ID from Cumulus';
         COMMENT ON COLUMN granules.execution_id
            IS 'AWS step function execution id';
        COMMENT ON COLUMN granules.ingest_time
            IS 'Date and time the granule was originally ingested into ORCA.';
        COMMENT ON COLUMN granules.last_update
            IS 'Last time the data for the granule was updated. This generally will coincide with a duplicate or a change to the underlying data file.';                    
        -- Grants
        GRANT SELECT, INSERT, UPDATE, DELETE ON granules TO orca_app;
    """
    )

def files_table_sql() -> TextClause:
    """
    Full SQL for creating the catalog files table.

    Returns:
        (sqlalchemy.sql.element.TextClause): SQL for creating files table.
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
        , CONSTRAINT PK_files PRIMARY KEY (id)
        , CONSTRAINT FK_granule_file FOREIGN KEY (granule_id) REFERENCES granules (id)
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
    """
    )


# ----------------------------------------------------------------------------
# ORCA SQL used for migration of schema
# ----------------------------------------------------------------------------
def migrate_recovery_job_data_sql() -> TextClause:
    """
    SQL that migrates data from the old dr.request_status table to the new
    orca.recovery_job table.

    Returns:
        (sqlalchemy.sql.element.TextClause): SQL for populating recovery_job table.
    """
    return text(
        """
        INSERT INTO recovery_job
        WITH reformatted_table AS (
        SELECT
            request_group_id AS job_id,
            granule_id,
            CASE job_status
              WHEN 'error' THEN 3::int2
              WHEN 'complete' THEN 4::int2
              ELSE 1::int2
            END AS status_id,
            request_time,
            CASE job_status
              WHEN 'error' THEN last_update_time
              WHEN 'complete' THEN last_update_time
              ELSE NULL
            END AS completion_time,
            restore_bucket_dest AS archive_destination
        FROM dr.request_status
        )
        SELECT
            job_id,
            granule_id,
            archive_destination,
            MIN(status_id) AS status_id,
            MIN(request_time) AS request_time,
            MAX(completion_time) AS completion_time
        FROM reformatted_table
        GROUP BY job_id, granule_id, archive_destination
        ORDER BY job_id, granule_id;
    """
    )


def migrate_recovery_file_data_sql() -> TextClause:
    """
    SQL that migrates data from the old dr.request_status table to the new
    orca.recovery_file table.

    Returns:
        (sqlalchemy.sql.element.TextClause): SQL for populating recovery_file table.
    """
    return text(
        """
        INSERT INTO recovery_file
        SELECT
            request_group_id AS job_id,
            granule_id,
            REVERSE(SPLIT_PART(REVERSE(object_key), '/', 1)) AS filename,
            object_key AS key_path,
            archive_bucket_dest AS restore_destination,
            CASE job_status
              WHEN 'error' THEN 3::int2
              WHEN 'complete' THEN 4::int2
              ELSE 1::int2
            END AS status_id,
            err_msg AS error_message,
            request_time,
            last_update_time AS last_update,
            CASE job_status
              WHEN 'error' THEN last_update_time
              WHEN 'complete' THEN last_update_time
              ELSE NULL
            END AS completion_time
        FROM request_status;
    """
    )


def drop_request_status_table_sql() -> TextClause:
    """
    SQL that removes the dr.request_status table.

    Returns:
        (sqlalchemy.sql.element.TextClause): SQL for dropping request_status table.
    """
    return text(
        """
        DROP TABLE IF EXISTS dr.request_status CASCADE;
    """
    )


def drop_dr_schema_sql() -> TextClause:
    """
    SQL that removes the dr schema.

    Returns:
        (sqlalchemy.sql.element.TextClause): SQL for dropping dr schema.
    """
    return text(
        """
        DROP SCHEMA IF EXISTS dr CASCADE;
    """
    )


def drop_druser_user_sql() -> TextClause:
    """
    SQL that removes the druser user.

    Returns:
        (sqlalchemy.sql.element.TextClause): SQL for dropping druser user.
    """
    return text(
        """
        DROP USER IF EXISTS druser;
    """
    )


def drop_dbo_user_sql() -> TextClause:
    """
    SQL that removes the dbo user.

    Returns:
        (sqlalchemy.sql.element.TextClause): SQL for dropping dbo user.
    """
    return text(
        """
        REVOKE CONNECT ON DATABASE disaster_recovery FROM dbo;
        DROP USER IF EXISTS dbo;
    """
    )


def drop_dr_role_sql() -> TextClause:
    """
    SQL that removes the dr_role role.

    Returns:
        (sqlalchemy.sql.element.TextClause): SQL for dropping dr_role role.
    """
    return text(
        """
        REVOKE CONNECT ON DATABASE disaster_recovery FROM GROUP dr_role;
        DROP ROLE IF EXISTS dr_role;
    """
    )


def drop_drdbo_role_sql() -> TextClause:
    """
    SQL that removes the drdbo_role role.

    Returns:
        (sqlalchemy.sql.element.TextClause): SQL for dropping drdbo_role role.
    """
    return text(
        """
        REVOKE CONNECT ON DATABASE disaster_recovery FROM GROUP drdbo_role;
        REVOKE CREATE ON DATABASE disaster_recovery FROM GROUP drdbo_role;
        DROP ROLE IF EXISTS drdbo_role;
    """
    )
