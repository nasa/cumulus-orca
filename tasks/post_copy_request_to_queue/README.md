[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/post_copy_request_to_queue/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/copy_files_to_archive/requirements.txt)

# Lambda function post_copy_request_to_queue

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro) for information on environment setup and testing.

- [Input Schema and Example](#input-schema-and-example)
- [pydoc post_copy_request_to_queue](#pydoc-post_copy_request_to_queue)


## Input Schema and Example
Fully defined json schemas written in the schema of https://json-schema.org/ can be found in the [schemas folder](schemas).

### Example Input
Input coming from ORCA S3 bucket trigger event.
```json
{
    "Records": [
      {
        "eventSource": "aws:s3",
        "eventName": "ObjectRestore:Completed",
        "s3": {
          "bucket": {
            "name": "orca-bucket",
            "arn": "arn:aws:s3:::orca-bucket"
          },
          "object": {
            "key": "f1.doc",
          }
        }
      }
    ]
  }
```

## pydoc post_copy_request_to_queue
```
Help on module post_copy_request_to_queue:

NAME
    post_copy_request_to_queue

DESCRIPTION
    Name: post_copy_request_to_queue.py
    Description:  lambda function that queries the db for file metadata, updates the status
    of recovered file to staged,
    and sends the staged file info to staged_recovery queue for further processing.

FUNCTIONS
    exponential_delay(base_delay: int, exponential_backoff: int = 2) -> int
        Exponential delay function. This function is used for retries during failure.
        Args:
            base_delay: Number of seconds to wait between recovery failure retries.
            exponential_backoff: The multiplier by which the retry interval increases during each attempt.
        Returns:
            An integer which is multiplication of base_delay and exponential_backoff.
        Raises:
            None
    
    get_metadata_sql(key_path: str) -> <function text at 0x10d7284c0>
        Query for finding metadata based on key_path and PENDING status.
        
        Args:
            key_path (str): s3 key for the file less the bucket name
        
        Returns:
            (sqlalchemy.text): SQL statement
    
    handler(event: Dict[str, Any], context) -> None
        Lambda handler. This lambda calls the task function to perform db queries
        and send message to SQS.
        
            Environment Vars:
                RECOVERY_QUEUE_URL (string): the SQS URL for staged_recovery_queue
                DB_QUEUE_URL (string): the SQS URL for status-update-queue
                MAX_RETRIES (string): Number of times the code will retry in case of failure.
                RETRY_SLEEP_SECS (string): Number of seconds to wait between recovery failure retries.
                RETRY_BACKOFF (string): The multiplier by which the retry interval increases during each attempt.
        
                Required by shared_db.get_configuration():
                    PREFIX (string): the prefix
                    DATABASE_PORT (string): the database port. The standard is 5432.
                    DATABASE_NAME (string): the name of the database.
                    DATABASE_USER (string): the name of the application user.
            Parameter store:
                {prefix}-drdb-host (string): host name that will be retrieved from secrets manager
                {prefix}-drdb-user-pass (string):db password that will be retrieved from secrets manager
        Args:
            event:
                A dictionary from the S3 bucket. See schemas/input.json for more information.
            context: An object required by AWS Lambda. Unused.
        Returns:
            None
        Raises:
            Exception: If unable to retrieve the SQS URLs or exponential retry fields from env variables.
    
    query_db(key_path: str, bucket_name: str) -> List[Dict[str, str]]
        Connect and query the recover_file status table return needed metadata for posting to the recovery status SQS Queue.
        
        Args:
            key_path:
               Full AWS key path including file name of the file where the file resides.
            bucket_name: Name of the source S3 bucket.
        Returns:
            A list of dict containing the following keys, matching the input format from copy_files_to_archive:
                "jobId" (str):
                "granuleId"(str):
                "filename" (str):
                "restoreDestination" (str):
                "s3MultipartChunksizeMb" (str):
                "sourceKey" (str):
                "targetKey" (str):
                "sourceBucket" (str):
        Raises:
            Exception: If unable to retrieve the metadata by querying the DB.
    
    task(key_path: str, bucket_name: str, status_update_queue_url: str, recovery_queue_url: str, max_retries: int, retry_sleep_secs: int, retry_backoff: int) -> None
        Task called by the handler to perform the work.
        
        This task queries all entries from orca_recoverfile table
        that match the given filename and whose status_id is 'PENDING'.
        The result is then sent to the staged-recovery-queue SQS and status-update-queue SQS.
        
        Args:
            key_path:
               Full AWS key path including file name of the file where the file resides.
            bucket_name: Name of the source S3 bucket.
            status_update_queue_url: The SQS URL of status_update_queue
            recovery_queue_url: The SQS URL of staged_recovery_queue
            max_retries: Number of times the code will retry in case of failure.
            retry_sleep_secs: Number of seconds to wait between recovery failure retries.
            retry_backoff: The multiplier by which the retry interval increases during each attempt.
        Returns:
            None
        Raises:
            Exception: If unable to retrieve key_path or db parameters, convert db result to json,
            or post to queue.

DATA
    Any = typing.Any
    Dict = typing.Dict
    FILENAME_KEY = 'filename'
    GRANULE_ID_KEY = 'granuleId'
    JOB_ID_KEY = 'jobId'
    LOGGER = <cumulus_logger.CumulusLogger object>
    List = typing.List
    MULTIPART_CHUNKSIZE_MB_KEY = 's3MultipartChunksizeMb'
    OS_ENVIRON_MAX_RETRIES_KEY = 'MAX_RETRIES'
    OS_ENVIRON_RECOVERY_QUEUE_URL_KEY = 'RECOVERY_QUEUE_URL'
    OS_ENVIRON_RETRY_BACKOFF_KEY = 'RETRY_BACKOFF'
    OS_ENVIRON_RETRY_SLEEP_SECS_KEY = 'RETRY_SLEEP_SECS'
    OS_ENVIRON_STATUS_UPDATE_QUEUE_URL_KEY = 'STATUS_UPDATE_QUEUE_URL'
    RESTORE_DESTINATION_KEY = 'restoreDestination'
    SOURCE_BUCKET_KEY = 'sourceBucket'
    SOURCE_KEY_KEY = 'sourceKey'
    TARGET_KEY_KEY = 'targetKey'
```