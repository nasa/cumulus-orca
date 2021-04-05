/*
** SCHEMA: dr
**
** Drop Objects for testing
**
*/
-- Start a transactions
BEGIN;

    -- Drop tables if they exists
    DROP TABLE IF EXISTS orca_recoverfile;
    DROP TABLE IF EXISTS orca_recoveryjob;
    DROP TABLE IF EXISTS orca_status;

COMMIT;


/*
** SCHEMA: dr
**
** TABLE: orca_status
**
**
*/

-- Start a transaction
BEGIN;
    -- Set Save point
    SAVEPOINT orca_status;

    -- Set search path
    SET search_path TO dr, public;

    -- Create table
    CREATE TABLE orca_status
    (
      id    int2 NOT NULL
    , value text NOT NULL
    , CONSTRAINT PK_orca_status PRIMARY KEY(id)
    , CONSTRAINT UNIQUE_orca_status_value UNIQUE (value)
    )
    ;

    -- Comments
    COMMENT ON TABLE orca_status IS 'Refrence table for valid status values and status order.';
    COMMENT ON COLUMN orca_status.id IS 'Status ID';
    COMMENT ON COLUMN orca_status.value IS 'Human readable status value';

    -- Grants
    GRANT SELECT ON orca_status TO dr_role;

    -- Load Data
    INSERT INTO orca_status VALUES (1, 'pending');
    INSERT INTO orca_status VALUES (2, 'staged');
    INSERT INTO orca_status VALUES (3, 'complete');
    INSERT INTO orca_status VALUES (4, 'error');

COMMIT;

/*
** SCHEMA: dr
**
** TABLE: orca_recoveryjob
**
**
*/

-- Start a transaction
BEGIN;
    -- Set Save point
    SAVEPOINT orca_recoveryjob;

    -- Set search path
    SET search_path TO dr, public;

    -- Create table
    CREATE TABLE orca_recoveryjob
    (
      job_id              text NOT NULL
    , granule_id          text NOT NULL
    , status_id           int2 NOT NULL
    , request_time        timestamp with time zone NOT NULL
    , completion_time     timestamp with time zone NULL
    , archive_destination text NOT NULL
    , CONSTRAINT PK_orca_recoveryjob PRIMARY KEY (job_id, granule_id)
    , CONSTRAINT FK_orca_recoveryjob_status FOREIGN KEY (status_id) REFERENCES orca_status (id)
    );

    -- Comments
    COMMENT ON TABLE orca_recoveryjob IS 'ORCA Job Recovery table that contains basic information at the granule level.';
    COMMENT ON COLUMN orca_recoveryjob.job_id IS 'This is the Cumulus AsyncOperationId value used to group all recovery executions for granule recovery together.';
    COMMENT ON COLUMN orca_recoveryjob.granule_id IS 'This is the granule id for the granule to be recovered.';
    COMMENT ON COLUMN orca_recoveryjob.status_id IS 'The currernt status of the recovery for the granule.';
    COMMENT ON COLUMN orca_recoveryjob.request_time IS 'The date and time the recovery was requested for the granule.';
    COMMENT ON COLUMN orca_recoveryjob.completion_time IS 'Date and time the recovery reached an end state for all the files in the granule.';
    COMMENT ON COLUMN orca_recoveryjob.archive_destination IS 'ORCA archive bucket where the data being restored lives.';

    -- Grants
    GRANT SELECT, INSERT, UPDATE, DELETE ON orca_recoveryjob TO dr_role;

    -- Load Data
    INSERT INTO orca_recoveryjob
    WITH reformatted_table AS (
    SELECT
        request_group_id AS job_id,
        granule_id,
        case job_status
          when 'error' then 4::int2
          when 'complete' then 3::int2
          else 1::int2
        end AS status_id,
        request_time,
        case job_status
          when 'error' then last_update_time
          when 'complete' then last_update_time
          else NULL
        end AS completion_time,
        restore_bucket_dest AS archive_destination
    FROM DR.REQUEST_STATUS
    )
    SELECT
        job_id,
        granule_id,
        max(status_id) AS status_id,
        min(request_time) AS request_time,
        max(completion_time) AS completion_time,
        archive_destination
    FROM reformatted_table
    GROUP BY job_id, granule_id, archive_destination
    ORDER BY job_id, granule_id;

COMMIT;


/*
** SCHEMA: dr
**
** TABLE: orca_recoveryfile
**
**
*/

-- Start a transaction
BEGIN;
    -- Set Save point
    SAVEPOINT orca_recoveryfile;

    -- Set search path
    SET search_path TO dr, public;

    -- Create table
    CREATE TABLE orca_recoverfile
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
    , CONSTRAINT PK_orca_recoverfile PRIMARY KEY (job_id, granule_id, filename)
    , CONSTRAINT FK_orca_recoverfile_status FOREIGN KEY (status_id) REFERENCES orca_status (id)
    , CONSTRAINT FK_orca_recoverfile_recoverjob FOREIGN KEY (job_id, granule_id) REFERENCES orca_recoveryjob (job_id, granule_id)
    );

    -- Comments
    COMMENT ON TABLE orca_recoverfile IS 'ORCA Recovery table that contains basic information at the file level.';
    COMMENT ON COLUMN orca_recoverfile.job_id IS 'This is the Cumulus AsyncOperationId value used to group all recovery executions for granule recovery together.';
    COMMENT ON COLUMN orca_recoverfile.granule_id IS 'This is the granule id for the granule to be recovered.';
    COMMENT ON COLUMN orca_recoverfile.filename IS 'Name of the file being restored.';
    COMMENT ON COLUMN orca_recoverfile.key_path IS 'Full key value of the data being restored.';
    COMMENT ON COLUMN orca_recoverfile.restore_destination IS 'S3 ORCA resstoration bucket for the data.';
    COMMENT ON COLUMN orca_recoverfile.status_id IS 'Current restore status of the file.';
    COMMENT ON COLUMN orca_recoverfile.error_message IS 'Error message that occured during failure.';
    COMMENT ON COLUMN orca_recoverfile.request_time IS 'Time the file was requested to be restored.';
    COMMENT ON COLUMN orca_recoverfile.last_update IS 'Time the status was last updated for the file.';
    COMMENT ON COLUMN orca_recoverfile.completion_time IS 'Time the file restoration hit a complete state.';

    -- Grants
    GRANT SELECT, INSERT, UPDATE, DELETE ON orca_recoverfile TO dr_role;

    -- Load Data
    INSERT INTO orca_recoverfile
    SELECT
        request_group_id AS job_id,
        granule_id,
        reverse(split_part(reverse(object_key), '/', 1)) AS filename,
        object_key AS key_path,
        archive_bucket_dest AS restore_destination,
        case job_status
          when 'error' then 4::int2
          when 'complete' then 3::int2
          else 1::int2
        end AS status_id,
        err_msg AS error_message,
        request_time,
        last_update_time AS last_update,
        case job_status
          when 'error' then last_update_time
          when 'complete' then last_update_time
          else NULL
        end AS completion_time
    FROM request_status;


COMMIT;
