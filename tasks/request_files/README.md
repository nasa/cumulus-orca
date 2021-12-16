[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/request_files/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/request_files/requirements.txt)

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro) for information on environment setup and testing.

**Lambda function request_files**

- [Deployment](#deployment)
  * [Deployment Validation](#deployment-validation)
- [pydoc request_files](#pydoc-request-files)
- [pydoc copy_files_to_archive](#pydoc-copy-files)
- [pydoc request_status](#pydoc-request-status)

## Deployment
```
    see /bin/build_tasks.sh to build the zip file. Upload the zip file to AWS.
```
<a name="deployment-validation"></a>
### Deployment Validation
```
1.  The easiest way to test is to use the DrRecoveryWorkflowStateMachine.
    You can use the test event in tasks/extract_filepaths_for_granule/test/testevents/StepFunction.json.
    Edit the ['payload']['granules']['keys'] values as needed to be the file(s) you wish to restore.
    Edit the ['cumulus_meta']['execution_name'] to be something unique (like yyyymmdd_hhmm). Then
    copy and paste the same value to the execution name field above the input field.
    The restore may take up to 5 hours.
Use the AWS CLI to check status of restore request:
ex> (podr) λ aws s3api head-object --bucket podaac-sndbx-cumulus-glacier --key L0A_RAD_RAW_product_0001-of-0020.iso.xml
```
<a name="pydoc-request-files"></a>
## pydoc request_files
```
Help on module request_files:

NAME
    request_files

DESCRIPTION
    Name: request_files.py
    Description:  Lambda function that makes a restore request from glacier for each input file.

CLASSES
    builtins.Exception(builtins.BaseException)
        RestoreRequestError
    
    class RestoreRequestError(builtins.Exception)
     |  Exception to be raised if the restore request fails submission for any of the files.
     |  
     |  Method resolution order:
     |      RestoreRequestError
     |      builtins.Exception
     |      builtins.BaseException
     |      builtins.object
     |  
     |  Data descriptors defined here:
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)
     |  
     |  ----------------------------------------------------------------------
     |  Methods inherited from builtins.Exception:
     |  
     |  __init__(self, /, *args, **kwargs)
     |      Initialize self.  See help(type(self)) for accurate signature.
     |  
     |  ----------------------------------------------------------------------
     |  Static methods inherited from builtins.Exception:
     |  
     |  __new__(*args, **kwargs) from builtins.type
     |      Create and return a new object.  See help(type) for accurate signature.
     |  
     |  ----------------------------------------------------------------------
     |  Methods inherited from builtins.BaseException:
     |  
     |  __delattr__(self, name, /)
     |      Implement delattr(self, name).
     |  
     |  __getattribute__(self, name, /)
     |      Return getattr(self, name).
     |  
     |  __reduce__(...)
     |      Helper for pickle.
     |  
     |  __repr__(self, /)
     |      Return repr(self).
     |  
     |  __setattr__(self, name, value, /)
     |      Implement setattr(self, name, value).
     |  
     |  __setstate__(...)
     |  
     |  __str__(self, /)
     |      Return str(self).
     |  
     |  with_traceback(...)
     |      Exception.with_traceback(tb) --
     |      set self.__traceback__ to tb and return self.
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors inherited from builtins.BaseException:
     |  
     |  __cause__
     |      exception cause
     |  
     |  __context__
     |      exception context
     |  
     |  __dict__
     |  
     |  __suppress_context__
     |  
     |  __traceback__
     |  
     |  args

FUNCTIONS
    handler(event: Dict[str, Any], context)
        Lambda handler. Initiates a restore_object request from glacier for each file of a granule.
        Note that this function is set up to accept a list of granules, (because Cumulus sends a list),
        but at this time, only 1 granule will be accepted.
        This is due to the error handling. If the restore request for any file for a
        granule fails to submit, the entire granule (workflow) fails. If more than one granule were
        accepted, and a failure ocured, at present, it would fail all of them.
        Environment variables can be set to override how many days to keep the restored files, how
        many times to retry a restore_request, and how long to wait between retries.
            Environment Vars:
                RESTORE_EXPIRE_DAYS (int, optional, default = 5): The number of days
                    the restored file will be accessible in the S3 bucket before it expires.
                RESTORE_REQUEST_RETRIES (int, optional, default = 3): The number of
                    attempts to retry a restore_request that failed to submit.
                RESTORE_RETRY_SLEEP_SECS (int, optional, default = 0): The number of seconds
                    to sleep between retry attempts.
                RESTORE_RETRIEVAL_TYPE (str, optional, default = 'Standard'): the Tier
                    for the restore request. Valid values are 'Standard'|'Bulk'|'Expedited'.
                CUMULUS_MESSAGE_ADAPTER_DISABLED (str): If set to 'true', CumulusMessageAdapter does not modify input.
                DB_QUEUE_URL
                    The URL of the SQS queue to post status to.
            Args:
                event: See schemas/input.json and combine with knowledge of CumulusMessageAdapter.
                context: An object required by AWS Lambda. Unused.
            Returns:
                A dict with the value at 'payload' matching schemas/output.json
                    Combine with knowledge of CumulusMessageAdapter for other properties.
            Raises:
                RestoreRequestError: An error occurred calling restore_object for one or more files.
                The same dict that is returned for a successful granule restore, will be included in the
                message, with 'success' = False for the files for which the restore request failed to
                submit.
    
    inner_task(event: Dict, max_retries: int, retry_sleep_secs: float, retrieval_type: str, restore_expire_days: int, db_queue_url: str) -> Dict[str, Any]
        Task called by the handler to perform the work.
        This task will call the restore_request for each file. Restored files will be kept
        for {exp_days} days before they expire. A restore request will be tried up to {retries} times
        if it fails, waiting {retry_sleep_secs} between each attempt.
            Args:
                Note that because we are using CumulusMessageAdapter, this may not directly correspond to Lambda input.
                event: A dict with the following keys:
                    'config' (dict): A dict with the following keys:
                        'orcaDefaultBucketOverride' (str): The name of the glacier bucket from which the files
                        will be restored.
                        'asyncOperationId' (str): The unique identifier used for tracking requests.
                    'input' (dict): A dict with the following keys:
                        'granules' (list(dict)): A list of dicts with the following keys:
                            'granuleId' (str): The id of the granule being restored.
                            'keys' (list(dict)): A list of dicts with the following keys:
                                'key' (str): Name of the file within the granule.  # TODO: It actually might be a path.
                                'dest_bucket' (str): The bucket the restored file will be moved
                                    to after the restore completes.
                max_retries: The maximum number of retries for network operations.
                retry_sleep_secs: The number of time to sleep between retries.
                retrieval_type: The Tier for the restore request. Valid values are 'Standard'|'Bulk'|'Expedited'.
                restore_expire_days: The number of days the restored file will be accessible in the S3 bucket before it
                    expires.
                db_queue_url: The URL of the SQS queue to post status to.
            Returns:
                A dict with the following keys:
                    'granules' (List): A list of dicts, each with the following keys:
                        'granuleId' (string): The id of the granule being restored.
                        'recover_files' (list(dict)): A list of dicts with the following keys:
                            'key' (str): Name of the file within the granule.
                            'dest_bucket' (str): The bucket the restored file will be moved
                                to after the restore completes.
                            'success' (boolean): True, indicating the restore request was submitted successfully.
                                If any value would be false, RestoreRequestError is raised instead.
                            'err_msg' (string): when success is False, this will contain
                                the error message from the restore error.
                        'keys': Same as recover_files, but without 'success' and 'err_msg'.
                    'job_id' (str): The 'job_id' from event if present, otherwise a newly-generated uuid.
            Raises:
                RestoreRequestError: Thrown if there are errors with the input request.
    
    object_exists(s3_cli: botocore.client.BaseClient, glacier_bucket: str, file_key: str) -> bool
        Check to see if an object exists in S3 Glacier.
        Args:
            s3_cli: An instance of boto3 s3 client
            glacier_bucket: The S3 glacier bucket name
            file_key: The key of the Glacier object
        Returns:
            True if the object exists, otherwise False.
    
    process_granule(s3: botocore.client.BaseClient, granule: Dict[str, Union[str, List[Dict]]], glacier_bucket: str, restore_expire_days: int, max_retries: int, retry_sleep_secs: float, retrieval_type: str, job_id: str, db_queue_url: str) -> None
        Call restore_object for the files in the granule_list. Modifies granule for output.
        Args:
            s3: An instance of boto3 s3 client
            granule: A dict with the following keys:
                'granuleId' (str): The id of the granule being restored.
                'recover_files' (list(dict)): A list of dicts with the following keys:
                    'key' (str): Name of the file within the granule.
                    'dest_bucket' (str): The bucket the restored file will be moved
                        to after the restore completes
                    'success' (bool): Should enter this method set to False. Modified to 'True' by method end.
                    'err_msg' (str): Will be modified if error occurs.
        
        
            glacier_bucket: The S3 glacier bucket name.
            restore_expire_days:
                The number of days the restored file will be accessible in the S3 bucket before it expires.
            max_retries: todo
            retry_sleep_secs: todo
            retrieval_type: todo
            db_queue_url: todo
            job_id: The unique identifier used for tracking requests.
        
        Raises: RestoreRequestError if any file restore could not be initiated.
    
    restore_object(s3_cli: botocore.client.BaseClient, key: str, days: int, db_glacier_bucket_key: str, attempt: int, job_id: str, retrieval_type: str = 'Standard') -> None
        Restore an archived S3 Glacier object in an Amazon S3 bucket.
        Args:
            s3_cli: An instance of boto3 s3 client.
            key: The key of the Glacier object being restored.
            days: How many days the restored file will be accessible in the S3 bucket before it expires.
            db_glacier_bucket_key: The S3 bucket name.
            attempt: The attempt number for logging purposes.
            job_id: The unique id of the job. Used for logging.
            retrieval_type: Glacier Tier. Valid values are 'Standard'|'Bulk'|'Expedited'. Defaults to 'Standard'.
        Raises:
            ClientError: Raises ClientErrors from restore_object.
    
    task(event: Dict, context: object) -> Dict[str, Any]
        Pulls information from os.environ, utilizing defaults if needed.
        Then calls inner_task.
            Args:
                Note that because we are using CumulusMessageAdapter, this may not directly correspond to Lambda input.
                event: A dict with the following keys:
                    'config' (dict): A dict with the following keys:
                        'orcaDefaultBucketOverride' (str): The name of the glacier bucket from which the files
                        will be restored. Defaults to os.environ['ORCA_DEFAULT_BUCKET']
                        'job_id' (str): The unique identifier used for tracking requests. If not present, will be generated.
                    'input' (dict): A dict with the following keys:
                        'granules' (list(dict)): A list of dicts with the following keys:
                            'granuleId' (str): The id of the granule being restored.
                            'keys' (list(dict)): A list of dicts with the following keys:
                                'key' (str): Name of the file within the granule.  # TODO: It actually might be a path.
                                'dest_bucket' (str): The bucket the restored file will be moved
                                    to after the restore completes.
                context: Passed through from AWS and CMA. Unused.
            Environment Vars:
                RESTORE_EXPIRE_DAYS (int, optional, default = 5): The number of days
                    the restored file will be accessible in the S3 bucket before it expires.
                RESTORE_REQUEST_RETRIES (int, optional, default = 3): The number of
                    attempts to retry a restore_request that failed to submit.
                RESTORE_RETRY_SLEEP_SECS (int, optional, default = 0): The number of seconds
                    to sleep between retry attempts.
                RESTORE_RETRIEVAL_TYPE (str, optional, default = 'Standard'): The Tier
                    for the restore request. Valid values are 'Standard'|'Bulk'|'Expedited'.
                DB_QUEUE_URL
                    The URL of the SQS queue to post status to.
                ORCA_DEFAULT_BUCKET
                    The bucket to use if dest_bucket is not set.
            Returns:
                The value from inner_task.
                Example Input:
                    {'granules': [
                        {
                            'granuleId': 'granxyz',
                            'recover_files': [
                                {'key': 'path1', 'dest_bucket': 'bucket_name', 'success': True}
                            ]
                        }]}
            Raises:
                RestoreRequestError: Thrown if there are errors with the input request.

DATA
    Any = typing.Any
    CONFIG_COLLECTION_KEY = 'collection'
    CONFIG_JOB_ID_KEY = 'asyncOperationId'
    CONFIG_MULTIPART_CHUNKSIZE_MB_KEY = 's3MultipartChunksizeMb'
    CONFIG_ORCA_DEFAULT_BUCKET_OVERRIDE_KEY = 'orcaDefaultBucketOverride'
    DEFAULT_MAX_REQUEST_RETRIES = 2
    DEFAULT_RESTORE_EXPIRE_DAYS = 5
    DEFAULT_RESTORE_RETRIEVAL_TYPE = 'Standard'
    DEFAULT_RESTORE_RETRY_SLEEP_SECS = 0
    Dict = typing.Dict
    EVENT_CONFIG_KEY = 'config'
    EVENT_INPUT_KEY = 'input'
    FILE_DEST_BUCKET_KEY = 'dest_bucket'
    FILE_ERROR_MESSAGE_KEY = 'error_message'
    FILE_KEY_KEY = 'key'
    FILE_SUCCESS_KEY = 'success'
    GRANULE_GRANULE_ID_KEY = 'granuleId'
    GRANULE_KEYS_KEY = 'keys'
    GRANULE_RECOVER_FILES_KEY = 'recover_files'
    INPUT_GRANULES_KEY = 'granules'
    LOGGER = <cumulus_logger.CumulusLogger object>
    List = typing.List
    OS_ENVIRON_DB_QUEUE_URL_KEY = 'DB_QUEUE_URL'
    OS_ENVIRON_ORCA_DEFAULT_GLACIER_BUCKET_KEY = 'ORCA_DEFAULT_BUCKET'
    OS_ENVIRON_RESTORE_EXPIRE_DAYS_KEY = 'RESTORE_EXPIRE_DAYS'
    OS_ENVIRON_RESTORE_REQUEST_RETRIES_KEY = 'RESTORE_REQUEST_RETRIES'
    OS_ENVIRON_RESTORE_RETRIEVAL_TYPE_KEY = 'RESTORE_RETRIEVAL_TYPE'
    OS_ENVIRON_RESTORE_RETRY_SLEEP_SECS_KEY = 'RESTORE_RETRY_SLEEP_SECS'
    Union = typing.Union
```
