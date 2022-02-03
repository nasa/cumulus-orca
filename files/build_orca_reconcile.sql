-- Set the Role and Path
SET ROLE orca_dbo;
SET search_path TO orca, public;


-- Create the objects in a transaction.
BEGIN

    -- Create reconcile_jobs table
    CREATE TABLE IF NOT EXISTS reconcile_jobs
    (
      id              int8 NOT NULL
    , status          text NOT NULL
    , start_time      timestamp with time zone NOT NULL
    , last_update     timestamp with time zone NOT NULL
    , end_time        timestamp with time zone NULL
    , error_message   text NULL
    , CONSTRAINT PK_reconcile_jobs_1 PRIMARY KEY(id)
    , CONSTRAINT CHECK_reconcile_jobs_status CHECK status in ('pending', 'getting S3 list', 'finding orphans', 'finding mismatches', 'error', 'complete')
    );

    COMMENT ON TABLE reconcile_jobs
      IS 'Manages internal reconciliation job information.';
    COMMENT ON COLUMN reconcile_jobs.id
      IS 'Job ID unique to each internal reconciliation job.';
    COMMENT ON COLUMN reconcile_jobs.status
      IS 'Current status of the job.';
    COMMENT ON COLUMN reconcile_jobs.start_time
      IS 'Date and time the internal reconcile job started.';
    COMMENT ON COLUMN reconcile_jobs.last_update
      IS 'Date and time the job status was last updated.';
    COMMENT ON COLUMN reconcile_jobs.end_time
      IS 'Time the job completed and wrote the report information.';
    COMMENT ON COLUMN reconcile_jobs.error_message
      IS 'Critical error the job ran into that prevented it from finishing.';


    -- Create reconcile_s3_objects table
    CREATE TABLE IF NOT EXISTS reconcile_s3_objects  (
      job_id               	int8 NOT NULL
    , orca_archive_location	text NOT NULL
    , key_path             	text NOT NULL
    , etag                 	text NOT NULL
    , last_update          	timestamp with time zone NOT NULL
    , size_in_bytes        	int8 NOT NULL
    , storage_class        	text NOT NULL
    , delete_marker        	bool NOT NULL
    , CONSTRAINT FK_reconcile_jobs_s3_objects FOREIGN KEY(job_id) REFERENCES reconcile_jobs(id)
    ) PARTITION BY LIST (orca_archive_location);
    COMMENT ON TABLE reconcile_s3_objects IS 'Temporary table that holds the listing from the ORCA S3 bucket to use for comparisons against the ORCA catalog. Partitions should be placed around orca_archive_location, followed by indexing on key_path once data is ingested.';
    COMMENT ON COLUMN reconcile_s3_objects.job_id IS 'Job the S3 listing is a part of for the comparison. Foreign key to the reconcile jobs table.';
    COMMENT ON COLUMN reconcile_s3_objects.orca_archive_location IS 'ORCA S3 Glacier bucket name where the file is stored.';
    COMMENT ON COLUMN reconcile_s3_objects.key_path IS 'Full path and file name of the object in the S3 bucket.';
    COMMENT ON COLUMN reconcile_s3_objects.etag IS 'AWS etag value from the s3 inventory report.';
    COMMENT ON COLUMN reconcile_s3_objects.last_update IS 'AWS Last Update from the s3 inventory report.';
    COMMENT ON COLUMN reconcile_s3_objects.size_in_bytes IS 'AWS size of the file in bytes from the s3 inventory report.';
    COMMENT ON COLUMN reconcile_s3_objects.storage_class IS 'AWS storage class the object is in from the s3 inventory report.';
    COMMENT ON COLUMN reconcile_s3_objects.delete_marker IS 'Set to `True` if object is a delete marker.';


    -- Create reconcile_orphan_report table
    CREATE TABLE IF NOT EXISTS reconcile_orphan_report
    (
      job_id                  int8 NOT NULL
    , orca_archive_location   text NOT NULL
    , key_path                text NOT NULL
    , etag                    text NOT NULL
    , last_update             timestamp with time zone NOT NULL
    , size_in_bytes           int8 NOT NULL
    , storage_class           text NOT NULL
    , CONSTRAINT PK_reconcile_orphan_report_1 PRIMARY KEY(job_id,orca_archive_location,key_path)
    , CONSTRAINT reconcile_jobs_orphan_report_fk FOREIGN KEY(job_id) REFERENCES reconcile_jobs(id)
    );

    COMMENT ON TABLE reconcile_orphan_report
      IS 'Table that identifies objects in the ORCA S3 Glacier bucket that are not in the ORCA catalog from the internal reconciliation job.';
    COMMENT ON COLUMN reconcile_orphan_report.job_id
      IS 'Associates the orphaned file to a internal reconcilation job. Refrences the reconcile jobs table.';
    COMMENT ON COLUMN reconcile_orphan_report.orca_archive_location
      IS 'ORCA S3 Glacier bucket the orphan was found in. Value is obtained from the reconcile_s3_objects (orca_archive_location) column.';
    COMMENT ON COLUMN reconcile_orphan_report.key_path
      IS 'Key that contains the path and file name. Value is obtained from the reconcile_s3_objects (key_path) column.';
    COMMENT ON COLUMN reconcile_orphan_report.etag
      IS 'AWS Etag of the object. Value is obtained from the reconcile_s3_objects (etag) column.';
    COMMENT ON COLUMN reconcile_orphan_report.last_update
      IS 'AWS last update of the object. Value is obtained from the reconcile_s3_objects (lst_update) column.';
    COMMENT ON COLUMN reconcile_orphan_report.size_in_bytes
      IS 'AWS size of the object in bytes. Value is obtained from the reconcile_s3_objects (size_in_bytes) column.';
    COMMENT ON COLUMN reconcile_orphan_report.storage_class
      IS 'ASWS storage class the object is in. Value is obtained from the reconcile_s3_objects (storage_class) column.';


    -- Create reconcile_catalog_mismatch_report table
    CREATE TABLE IF NOT EXISTS reconcile_catalog_mismatch_report
    (
      job_id                      int8 NOT NULL
    , collection_id               text NOT NULL
    , granule_id                  text NOT NULL
    , orca_archive_location       text NOT NULL
    , key_path                    text NOT NULL
    , cumulus_archive_location    text NOT NULL
    , filename                    text NOT NULL
    , orca_etag                   text NOT NULL
    , s3_etag                     text NULL
    , orca_last_update            timestamp with time zone NOT NULL
    , s3_last_update              timestamp with time zone NULL
    , orca_size                   int8 NOT NULL
    , s3_size                     int8 NULL
    , discrepancy_type            text NOT NULL
    , CONSTRAINT PK_reconcile_catalog_mismatch_report_1 PRIMARY KEY(job_id,collection_id,granule_id,orca_archive_location,key_path)
    , CONSTRAINT reconcile_jobs_catalog_mismatch_fk FOREIGN KEY(job_id) REFERENCES reconcile_jobs(id)
    );

    COMMENT ON TABLE reconcile_catalog_mismatch_report
      IS 'Table that identifies objects that exist in the ORCA catalog and either do not exist in the ORCA S3 bucket or have mismatched values from the s3 objects table.';
    COMMENT ON COLUMN reconcile_catalog_mismatch_report.job_id
      IS 'Job the mismatch or missing granule was foundin. Refrences the reconcile_job table.';
    COMMENT ON COLUMN reconcile_catalog_mismatch_report.collection_id
      IS 'Cumulus Collection ID value from the ORCA catalog.';
    COMMENT ON COLUMN reconcile_catalog_mismatch_report.granule_id
      IS 'Cumulus granuleID value from the ORCA catalog.';
    COMMENT ON COLUMN reconcile_catalog_mismatch_report.orca_archive_location
      IS 'ORCA S3 bucket the object is stored in.';
    COMMENT ON COLUMN reconcile_catalog_mismatch_report.key_path
      IS 'key path and filename of the object in the ORCA catalog.';
    COMMENT ON COLUMN reconcile_catalog_mismatch_report.cumulus_archive_location
      IS 'Expected S3 bucket the object is located in Cumulus. From the ORCA catalog.';
    COMMENT ON COLUMN reconcile_catalog_mismatch_report.filename
      IS 'Filename of the object from the ORCA catalog.';
    COMMENT ON COLUMN reconcile_catalog_mismatch_report.orca_etag
      IS 'etag of the object as reported in the ORCA catalog.';
    COMMENT ON COLUMN reconcile_catalog_mismatch_report.s3_etag
      IS 'etag of the object as reported in the S3 bucket.';
    COMMENT ON COLUMN reconcile_catalog_mismatch_report.orca_last_update
      IS 'Last update of the object as reported in the ORCA catalog.';
    COMMENT ON COLUMN reconcile_catalog_mismatch_report.s3_last_update
      IS 'Last update of the object as reported in the S3 bucket.';
    COMMENT ON COLUMN reconcile_catalog_mismatch_report.orca_size
      IS 'Size in bytes of the object as reported in the ORCA catalog.';
    COMMENT ON COLUMN reconcile_catalog_mismatch_report.s3_size
      IS 'Size in bytes of the object as reported in the S3 bucket.';
    COMMENT ON COLUMN reconcile_catalog_mismatch_report.discrepancy_type
      IS 'Type of discrepancy found during reconciliation.';

COMMIT;

