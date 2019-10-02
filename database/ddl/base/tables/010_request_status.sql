/*
** SCHEMA: dr
** 
** TABLE: request_status
**
** 
*/

-- Start a transaction
BEGIN;
    -- Set Save point
    SAVEPOINT request_status;

    -- Set search path
    SET search_path TO dr, public;

    -- Remove Foreign Constraints if they exist

    -- Drop table if it exists
    --DROP TABLE IF EXISTS request_status;

    -- Create table
    CREATE TABLE request_status
        (
          request_id          varchar(36) NOT NULL
        , request_group_id    uuid NOT NULL
        , granule_id          varchar(100) NOT NULL
        , object_key          text NOT NULL
        , job_type            varchar(12) NULL DEFAULT 'restore' CHECK (job_type IN ('restore', 'regenerate'))
        , restore_bucket_dest text NULL
        , job_status          varchar(12) NULL DEFAULT 'inprogress' CHECK (job_status IN ('inprogress', 'complete','error'))
        , request_time        timestamptz NOT NULL
        , last_update_time    timestamptz NOT NULL
        , err_msg             text NULL
        , PRIMARY KEY(request_id)
        )
    ;


    -- Comments
    COMMENT ON TABLE request_status IS 'Disaster recovery jobs status table';
    COMMENT ON COLUMN request_status.request_id IS 'unique job identifier';
    COMMENT ON COLUMN request_status.request_group_id IS 'request identifier assigned to all objects being requested for the granule';
    COMMENT ON COLUMN request_status.granule_id IS 'granule id of the granule being restored';
    COMMENT ON COLUMN request_status.object_key IS 'object key being restored';
    COMMENT ON COLUMN request_status.job_type IS 'type of restore request that was made';
    COMMENT ON COLUMN request_status.restore_bucket_dest IS 'S3 bucket to restore the file to';
    COMMENT ON COLUMN request_status.job_status IS 'current status of the request';
    COMMENT ON COLUMN request_status.request_time IS 'Time the request was made';
    COMMENT ON COLUMN request_status.last_update_time IS 'The last time the request was updated';
	COMMENT ON COLUMN request_status.err_msg IS 'The error message when job_status is error';

    -- Non-inline Constraints

    --DROP INDEX IF EXISTS idx_reqstat_reqgidgranid;
    CREATE INDEX idx_reqstat_reqgidgranid
         ON request_status USING btree (request_group_id, granule_id);

    CREATE INDEX idx_reqstat_keystatus
         ON request_status USING btree (object_key, job_status);


    -- Additional Grants

COMMIT;
