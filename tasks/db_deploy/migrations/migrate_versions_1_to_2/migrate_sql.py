"""
Name: orca_sql_v2.py

Description: All of the SQL used for creating and migrating the ORCA schema to version 2.
"""
from orca_shared.database.shared_db import logger
from sqlalchemy import text


# ----------------------------------------------------------------------------
# ORCA SQL used for creating ORCA schema, roles, and users
# ----------------------------------------------------------------------------
def dbo_role_sql(db_name: str, admin_username: str) -> text:
    """
    Full SQL for creating the ORCA dbo role that owns the ORCA schema and
    objects.

    Returns:
        (sqlalchemy.sql.element.TextClause): SQL for creating orca_dbo role.
    """
    return text(
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
            GRANT CONNECT ON DATABASE {db_name} TO orca_dbo;
            GRANT CREATE ON DATABASE {db_name} TO orca_dbo;
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
        (sqlalchemy.sql.element.TextClause): SQL for creating orca_app role.
    """
    return text(
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
          GRANT CONNECT ON DATABASE {db_name} TO orca_app;
        END
        $$;
    """  # nosec
    )


def orca_schema_sql() -> text:
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


def app_user_sql(user_name: str, user_password: str) -> text:
    """
    Full SQL for creating the ORCA application database user. Must be created
    after the app_role_sql and orca_schema_sql.

    Args:
        user_password (str): Password for the application user

    Returns:
        (sqlalchemy.sql.element.TextClause): SQL for creating PREFIX_orcauser user.
    """
    if user_name is None or len(user_name) == 0:
        logger.critical("Username must be non-empty.")
        raise Exception("Username must be non-empty.")
    if len(user_name) > 63:
        logger.critical("Username must be less than 64 characters.")
        raise Exception("Username must be less than 64 characters.")

    if user_password is None or len(user_password) < 12:
        logger.critical("User password must be at least 12 characters long.")
        raise Exception("User password must be at least 12 characters long.")

    return text(
        f"""
        DO
        $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_user WHERE usename = '{user_name}' ) THEN
                -- Create {user_name}
                CREATE ROLE "{user_name}"
                    LOGIN
                    INHERIT
                    ENCRYPTED PASSWORD '{user_password}'
                    IN ROLE orca_app;

                -- Add comment
                COMMENT ON ROLE "{user_name}"
                    IS 'ORCA application user.';

                RAISE NOTICE 'USER CREATED {user_name}.';

            END IF;

            -- Alter the roles search path so on login it has what it needs for a path
            ALTER ROLE "{user_name}" SET search_path = orca, public;
        END
        $$;
    """  # nosec
    )


# ----------------------------------------------------------------------------
# ORCA SQL used for creating ORCA general metadata tables
# ----------------------------------------------------------------------------
def schema_versions_table_sql() -> text:
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


def schema_versions_data_sql() -> text:
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
        VALUES (2, 'Added inventory schema for v2.x of ORCA application', NOW(), True)
        ON CONFLICT (version_id)
        DO UPDATE SET is_latest = True;
    """
    )


# ----------------------------------------------------------------------------
# ORCA SQL used for creating ORCA recovery tables
# ----------------------------------------------------------------------------
def recovery_status_table_sql() -> text:
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


def recovery_status_data_sql() -> text:
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
        INSERT INTO recovery_status VALUES (4, 'success')
            ON CONFLICT (id) DO NOTHING;
    """
    )


def recovery_job_table_sql() -> text:
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


def recovery_file_table_sql() -> text:
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
          job_id                 text NOT NULL
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
            PRIMARY KEY (job_id, granule_id, filename)
        , CONSTRAINT FK_recovery_file_status
            FOREIGN KEY (status_id) REFERENCES recovery_status (id)
        , CONSTRAINT FK_recovery_file_recoverjob
            FOREIGN KEY (job_id, granule_id) REFERENCES recovery_job (job_id, granule_id)
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
# ORCA SQL used for migration of schema
# ----------------------------------------------------------------------------
def migrate_recovery_job_data_sql() -> text:
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


def migrate_recovery_file_data_sql() -> text:
    """
    SQL that migrates data from the old dr.request_status table to the new
    orca.recovery_file table.

    Returns:
        (sqlalchemy.sql.element.TextClause): SQL for populating recovery_file table.
    """
    return text(
        """
        INSERT INTO recovery_file (
          job_id
        , granule_id
        , filename
        , key_path
        , restore_destination
        , status_id
        , error_message
        , request_time
        , last_update
        , completion_time
        )
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


def drop_request_status_table_sql() -> text:
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


def drop_dr_schema_sql() -> text:
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


def drop_druser_user_sql() -> text:
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


# todo: rebuild API.md
def drop_dbo_user_sql(db_name: str) -> text:
    """
    SQL that removes the dbo user.

    Returns:
        (sqlalchemy.sql.element.TextClause): SQL for dropping dbo user.
    """
    return text(
        f"""
        REVOKE CONNECT ON DATABASE {db_name} FROM dbo;
        DROP USER IF EXISTS dbo;
    """
    )


def drop_dr_role_sql(db_name: str) -> text:
    """
    SQL that removes the dr_role role.

    Returns:
        (sqlalchemy.sql.element.TextClause): SQL for dropping dr_role role.
    """
    return text(
        f"""
        REVOKE CONNECT ON DATABASE {db_name} FROM GROUP dr_role;
        DROP ROLE IF EXISTS dr_role;
    """
    )


def drop_drdbo_role_sql(db_name: str) -> text:
    """
    SQL that removes the drdbo_role role.

    Returns:
        (sqlalchemy.sql.element.TextClause): SQL for dropping drdbo_role role.
    f"""
    return text(
        f"""
        REVOKE CONNECT ON DATABASE {db_name} FROM GROUP drdbo_role;
        REVOKE CREATE ON DATABASE {db_name} FROM GROUP drdbo_role;
        DROP ROLE IF EXISTS drdbo_role;
    """
    )
