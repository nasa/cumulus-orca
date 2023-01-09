-- Perform initial population
INSERT INTO dr.request_status
SELECT
    uuid_generate_v4() AS request_id,
    uuid_generate_v4() AS request_group_id,
    substr(md5(random()::text), 0, 25) AS granule_id,
    substr(md5(random()::text), 0, 25) AS object_key,
    'restore' AS job_type,
    'myarchivebucket' AS restore_bucket_dest,
    substr(md5(random()::text), 0, 25) AS archive_bucket_dest,
    'inprogress' as job_status,
    generate_series(now()-'14 days'::interval, now(), '1 hour'::interval) AS request_time,
    now() AS last_update,
    NULL AS error_message;

-- Update some files to complete
WITH cte AS (
    SELECT request_id
      FROM dr.request_status
     WHERE job_status = 'inprogress'
     LIMIT 110
)
UPDATE dr.request_status rs
   SET job_status = 'complete'
  FROM cte
 WHERE rs.request_id = cte.request_id;

-- update some files to error
WITH cte AS (
    SELECT request_id
      FROM dr.request_status
     WHERE job_status = 'inprogress'
     LIMIT 110
)
UPDATE dr.request_status rs
   SET job_status = 'error',
       err_msg = 'Some error occurred here'
  FROM cte
 WHERE rs.request_id = cte.request_id;

COMMIT;
