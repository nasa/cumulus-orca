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
TODO: Rework this section once we are integrated with the dashboard.
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
    enum.Enum(builtins.object)
        RequestMethod
    
    class RequestMethod(enum.Enum)
     |  RequestMethod(value, names=None, *, module=None, qualname=None, type=None, start=1)
     |  
     |  An enumeration.
     |  
     |  Method resolution order:
     |      RequestMethod
     |      enum.Enum
     |      builtins.object
     |  
     |  Data and other attributes defined here:
     |  
     |  POST = <RequestMethod.POST: 'post'>
     |  
     |  PUT = <RequestMethod.PUT: 'put'>
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors inherited from enum.Enum:
     |  
     |  name
     |      The name of the Enum member.
     |  
     |  value
     |      The value of the Enum member.
     |  
     |  ----------------------------------------------------------------------
     |  Readonly properties inherited from enum.EnumMeta:
     |  
     |  __members__
     |      Returns a mapping of member name->value.
     |      
     |      This mapping lists all enum members, including aliases. Note that this
     |      is a read-only view of the internal mapping.
    
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
        accepted, and a failure occured, at present, it would fail all of them.
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
            Args:
                event: A dict with the following keys:
                    'config' (dict): A dict with the following keys:
                        'glacier_bucket' (str): The name of the glacier bucket from which the files
                        will be restored.
                    'input' (dict): A dict with the following keys:
                        'granules' (list(dict)): A list of dicts with the following keys:
                            'granuleId' (str): The id of the granule being restored.
                            'keys' (list(dict)): A list of dicts with the following keys:  # TODO: rename.
                                'key' (str): Name of the file within the granule.  # TODO: This or example lies.
                                'dest_bucket' (str): The bucket the restored file will be moved
                                    to after the restore completes.
                        'job_id' (str): The unique identifier used for tracking requests. If not present, will be generated.
                    Example: {
                        'config': {'glacierBucket': 'some_bucket'}
                        'input': {
                            'granules':
                            [
                                {
                                    'granuleId': 'granxyz',
                                    'keys': [
                                        {'key': 'path1', 'dest_bucket': 'some_bucket'},
                                        {'key': 'path2', 'dest_bucket': 'some_other_bucket'}
                                    ]
                                }
                            ]
                        }
                context: An object required by AWS Lambda. Unused.
            Returns:
                dict: The dict returned from the task. All 'success' values will be True. If they were
                not all True, the RestoreRequestError exception would be raised.
            Raises:
                RestoreRequestError: An error occurred calling restore_object for one or more files.
                The same dict that is returned for a successful granule restore, will be included in the
                message, with 'success' = False for the files for which the restore request failed to
                submit.
    
    inner_task(event: Dict, max_retries: int, retry_sleep_secs: float, retrieval_type: str, restore_expire_days: int, db_queue_url: str)
    
    object_exists(s3_cli: botocore.client.BaseClient, glacier_bucket: str, file_key: str) -> bool
        Check to see if an object exists in S3 Glacier.
        Args:
            s3_cli: An instance of boto3 s3 client
            glacier_bucket: The S3 glacier bucket name
            file_key: The key of the Glacier object
        Returns:
            True if the object exists, otherwise False.
    
    post_entry_to_queue(table_name: str, new_data: Dict[str, Any], request_method: request_files.RequestMethod, db_queue_url: str, max_retries: int, retry_sleep_secs: float)
        # todo: Move to shared lib
    
    post_status_for_file_to_queue(job_id: str, granule_id: str, filename: str, key_path: Union[str, NoneType], restore_destination: Union[str, NoneType], status_id: Union[int, NoneType], error_message: Union[str, NoneType], request_time: Union[str, NoneType], last_update: str, completion_time: Union[str, NoneType], request_method: request_files.RequestMethod, db_queue_url: str, max_retries: int, retry_sleep_secs: float)
        # todo: Move to shared lib
    
    post_status_for_job_to_queue(job_id: str, granule_id: str, status_id: Union[int, NoneType], request_time: Union[str, NoneType], completion_time: Union[str, NoneType], archive_destination: Union[str, NoneType], request_method: request_files.RequestMethod, db_queue_url: str, max_retries: int, retry_sleep_secs: float)
        # todo: Move to shared lib
    
    process_granule(s3: botocore.client.BaseClient, granule: Dict[str, Union[str, List[Dict]]], glacier_bucket: str, restore_expire_days: int, max_retries: int, retry_sleep_secs: float, retrieval_type: str, job_id: str, db_queue_url: str)
        Call restore_object for the files in the granule_list. Modifies granule for output.
        Args:
            s3: An instance of boto3 s3 client
            granule: A dict with the following keys:
                'granuleId' (str): The id of the granule being restored.
                'recover_files' (list(dict)): A list of dicts with the following keys:
                    'key' (str): Name of the file within the granule.
                    'dest_bucket' (str): The bucket the restored file will be moved
                        to after the restore completes
                    'success' (bool): Should enter this method set to False. Modified to 'True' if no error occurs.
                    'err_msg' (str): Will be modified if error occurs.
        
        
            glacier_bucket: The S3 glacier bucket name. todo: For what?
            restore_expire_days:
                The number of days the restored file will be accessible in the S3 bucket before it expires.
            max_retries: todo
            retry_sleep_secs: todo
            retrieval_type: todo
            db_queue_url: todo
            job_id: The unique identifier used for tracking requests.
    
    restore_object(s3_cli: botocore.client.BaseClient, obj: Dict[str, Any], attempt: int, job_id: str, retrieval_type: str = 'Standard') -> None
    
    task(event: Dict, context: object) -> Dict[str, Any]
        Task called by the handler to perform the work.
        This task will call the restore_request for each file. Restored files will be kept
        for {exp_days} days before they expire. A restore request will be tried up to {retries} times
        if it fails, waiting {retry_sleep_secs} between each attempt.
            Args:
                event: Passed through from the handler via run_cumulus_task.
                context: Passed through from the handler. Unused, but required by framework.
            Environment Vars:
                RESTORE_EXPIRE_DAYS (int, optional, default = 5): The number of days
                    the restored file will be accessible in the S3 bucket before it expires.
                RESTORE_REQUEST_RETRIES (int, optional, default = 3): The number of
                    attempts to retry a restore_request that failed to submit.
                RESTORE_RETRY_SLEEP_SECS (int, optional, default = 0): The number of seconds
                    to sleep between retry attempts.
                RESTORE_RETRIEVAL_TYPE (str, optional, default = 'Standard'): the Tier
                    for the restore request. Valid values are 'Standard'|'Bulk'|'Expedited'.
            Returns:
                A dict with the following keys:
                    'granules' (List): A list of dicts, each with the following keys:
                        'granuleId' (string): The id of the granule being restored.
                        'recover_files' (list(dict)): A list of dicts with the following keys:
                            'key' (str): Name of the file within the granule.
                            'dest_bucket' (str): The bucket the restored file will be moved
                                to after the restore completes.
                            'success' (boolean): True, indicating the restore request was submitted successfully,
                                otherwise False.
                            'err_msg' (string): when success is False, this will contain
                                the error message from the restore error.
                        'keys': Same as recover_files, but without 'success' and 'err_msg'.
                    'job_id' (str): The 'job_id' from event if present, otherwise a newly-generated uuid.
                Example:
                    {'granules': [
                        {
                            'granuleId': 'granxyz',
                            'recover_files': [
                                {'key': 'path1', 'dest_bucket': 'bucket_name', 'success': True},
                                {'key': 'path2', 'success': False, 'err_msg': 'because'}
                            ]
                        }]}
            Raises:
                RestoreRequestError: Thrown if there are errors with the input request.

DATA
    Any = typing.Any
    CONFIG_GLACIER_BUCKET_KEY = 'glacier-bucket'
    DEFAULT_MAX_REQUEST_RETRIES = 2
    DEFAULT_RESTORE_EXPIRE_DAYS = 5
    DEFAULT_RESTORE_RETRIEVAL_TYPE = 'Standard'
    DEFAULT_RESTORE_RETRY_SLEEP_SECS = 0
    Dict = typing.Dict
    EVENT_CONFIG_KEY = 'config'
    EVENT_INPUT_KEY = 'input'
    FILE_DEST_BUCKET_KEY = 'dest_bucket'
    FILE_ERROR_MESSAGE_KEY = 'err_msg'
    FILE_KEY_KEY = 'key'
    FILE_SUCCESS_KEY = 'success'
    GRANULE_GRANULE_ID_KEY = 'granuleId'
    GRANULE_KEYS_KEY = 'keys'
    GRANULE_RECOVER_FILES_KEY = 'recover_files'
    INPUT_GRANULES_KEY = 'granules'
    INPUT_JOB_ID_KEY = 'job_id'
    LOGGER = <cumulus_logger.CumulusLogger object>
    List = typing.List
    ORCA_STATUS_FAILED = 3
    ORCA_STATUS_PENDING = 0
    OS_ENVIRON_DB_QUEUE_URL_KEY = 'DB_QUEUE_URL'
    OS_ENVIRON_RESTORE_EXPIRE_DAYS_KEY = 'RESTORE_EXPIRE_DAYS'
    OS_ENVIRON_RESTORE_REQUEST_RETRIES_KEY = 'RESTORE_REQUEST_RETRIES'
    OS_ENVIRON_RESTORE_RETRIEVAL_TYPE_KEY = 'RESTORE_RETRIEVAL_TYPE'
    OS_ENVIRON_RESTORE_RETRY_SLEEP_SECS_KEY = 'RESTORE_RETRY_SLEEP_SECS'
    Optional = typing.Optional
    REQUESTS_DB_DEST_BUCKET_KEY = 'dest_bucket'
    REQUESTS_DB_ERROR_MESSAGE_KEY = 'err_msg'
    REQUESTS_DB_GLACIER_BUCKET_KEY = 'glacier_bucket'
    REQUESTS_DB_GRANULE_ID_KEY = 'granule_id'
    REQUESTS_DB_JOB_STATUS_KEY = 'job_status'
    Union = typing.Union
    sqs = <botocore.client.SQS object>
```
