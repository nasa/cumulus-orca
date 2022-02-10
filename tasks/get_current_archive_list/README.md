[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/get_current_archive_list/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/get_current_archive_list/requirements.txt)

**Lambda function get_current_archive_list **

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro) for information on environment setup and testing.

- [Deployment](#deployment)
- [pydoc get_current_archive_list](#pydoc)

<a name="deployment"></a>
## Deployment
```
    see /bin/build_tasks.sh to build the zip file. Upload the zip file to AWS.
```
<a name="pydoc"></a>
## pydoc get_current_archive_list
```
Help on module get_current_archive_list:

NAME
    get_current_archive_list - Name: get_current_archive_list.py

DESCRIPTION
    Description: Receives a list of s3 events from an SQS queue, and loads the s3 inventory specified into postgres.

FUNCTIONS
    add_metadata_to_gzip(report_bucket_name: str, gzip_key_path: str) -> None
        AWS does not add proper metadata to gzip files, which breaks aws_s3.table_import_from_s3
        Must add manually.
        Args:
            report_bucket_name: The name of the bucket the csv is located in.
            gzip_key_path: The path within the bucket to the gzip file that needs metadata updated.
    
    create_job(orca_archive_location: str, inventory_creation_time: datetime.datetime, engine: sqlalchemy.future.engine.Engine) -> int
        Creates the initial status entry for a job.
        
        Args:
            orca_archive_location: The name of the bucket to generate the reports for.
            inventory_creation_time: The time the s3 Inventory report was created.
            engine: The sqlalchemy engine to use for contacting the database.
        
        Returns: The auto-incremented job_id from the database.
    
    create_job_sql()
    
    create_temporary_table_sql(temporary_s3_column_list: str)
        Creates a temporary table to store inventory data.
        Args:
            temporary_s3_column_list: The list of columns that need to be created to store csv data.
                Be very careful to avoid injection.
    
    generate_temporary_s3_column_list(manifest_file_schema: str) -> str
        Creates a list of columns that matches the order of columns in the manifest.
        Columns used by our database are given standardized names.
        Args:
            manifest_file_schema: An ordered CSV representing columns in the CSV the manifest points to.
        
        Returns: A string representing SQL columns to create.
            Columns required for import but unused by orca will be filled in with `junk` values.
            For example, 'orca_archive_location text, key_path text, size_in_bytes bigint, last_update timestamptz, etag text, storage_class text, junk7 text, junk8 text, junk9 text, junk10 text, junk11 text, junk12 text, junk13 text, junk14 text'
    
    get_manifest(manifest_key_path: str, report_bucket_name: str, report_bucket_region: str) -> Dict[str, Any]
        Args:
            manifest_key_path: The full path within the s3 bucket to the manifest.
            report_bucket_name: The name of the bucket the manifest is located in.
            report_bucket_region: The name of the region the report bucket resides in.
        
        Returns: The key of the csv specified in the manifest.
    
    handler(event: Dict[str, List], context) -> Dict[str, Any]
        Lambda handler. Receives a list of s3 events from an SQS queue, and loads the s3 inventory specified into postgres.
        
        Args:
            event: See input.json for details.
            context: An object passed through by AWS. Used for tracking.
        Environment Vars:
            S3_ACCESS_KEY: The access key that, when paired with s3_secret_key, allows postgres to access s3.
            S3_SECRET_KEY: The secret key that, when paired with s3_access_key, allows postgres to access s3.
            See shared_db.py's get_configuration for further details.
        
        Returns: See output.json for details.
    
    task(record: Dict[str, Any], s3_access_key: str, s3_secret_key: str, db_connect_info: Dict) -> Dict[str, Any]
        Sends each individual record to send_record_to_database.
        
        Args:
            record: See input.json for details.
            s3_access_key: The access key that, when paired with s3_secret_key, allows postgres to access s3.
            s3_secret_key: The secret key that, when paired with s3_access_key, allows postgres to access s3.
            db_connect_info: See shared_db.py's get_configuration for further details.
        
        Returns: See output.json for details.
    
    translate_s3_import_to_partitioned_data_sql(report_table_name: str)
        SQL for translating between the temporary table and Orca table.
    
    trigger_csv_load_from_s3_sql()
        SQL for telling postgres where/how to copy in the s3 inventory data.
    
    truncate_s3_partition(orca_archive_location: str, engine: sqlalchemy.future.engine.Engine) -> None
        Truncates the partition for the given orca_archive_location, removing its data.
        
        Args:
            orca_archive_location: The name of the bucket to generate the reports for.
            engine: The sqlalchemy engine to use for contacting the database.
    
    truncate_s3_partition_sql(partition_name: str)
    
    update_job_sql()
    
    update_job_with_failure(job_id: int, error_message: str, engine: sqlalchemy.future.engine.Engine) -> None
        Updates the status entry for a job.
        
        Args:
            job_id: The id of the job to associate info with.
            error_message: The error to post to the job.
            engine: The sqlalchemy engine to use for contacting the database.
    
    update_job_with_s3_inventory_in_postgres(s3_access_key: str, s3_secret_key: str, orca_archive_location: str, report_bucket_name: str, report_bucket_region: str, csv_key_paths: List[str], manifest_file_schema: str, job_id: int, engine: sqlalchemy.future.engine.Engine) -> None
        Deconstructs a record to its components and calls send_values_to_database with the result.
        
        Args:
            s3_access_key: The access key that, when paired with s3_secret_key, allows postgres to access s3.
            s3_secret_key: The secret key that, when paired with s3_access_key, allows postgres to access s3.
            orca_archive_location: The name of the bucket to generate the reports for.
            report_bucket_name: The name of the bucket the csv is located in.
            report_bucket_region: The name of the region the report bucket resides in.
            csv_key_paths: The paths of the csvs within the report bucket.
            manifest_file_schema: The string representing columns present in the csv.
            job_id: The id of the job to associate info with.
            engine: The sqlalchemy engine to use for contacting the database.

DATA
    Any = typing.Any
    BUCKET_NAME_KEY = 'name'
    Dict = typing.Dict
    EVENT_RECORDS_KEY = 'Records'
    FILES_KEY_KEY = 'key'
    LOGGER = <cumulus_logger.CumulusLogger object>
    List = typing.List
    MANIFEST_CREATION_TIMESTAMP_KEY = 'creationTimestamp'
    MANIFEST_FILES_KEY = 'files'
    MANIFEST_FILE_SCHEMA_KEY = 'fileSchema'
    MANIFEST_SOURCE_BUCKET_KEY = 'sourceBucket'
    OBJECT_KEY_KEY = 'key'
    OS_S3_ACCESS_KEY_KEY = 'S3_ACCESS_KEY'
    OS_S3_SECRET_KEY_KEY = 'S3_SECRET_KEY'
    OUTPUT_JOB_ID_KEY = 'jobId'
    RECORD_AWS_REGION_KEY = 'awsRegion'
    RECORD_S3_KEY = 's3'
    S3_BUCKET_KEY = 'bucket'
    S3_OBJECT_KEY = 'object'
    column_mappings = {'Bucket': 'orca_archive_location text', 'ETag': 'et...
    raw_schema = <_io.TextIOWrapper name='schemas/output.json' mode='r' en...
```
