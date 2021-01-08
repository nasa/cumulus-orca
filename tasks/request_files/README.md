[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/request_files/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/request_files/requirements.txt)

**Lambda function request_files **

- [Deployment](#deployment)
  * [Deployment Validation](#deployment-validation)
- [pydoc request_files](#pydoc-request-files)
- [pydoc copy_files_to_archive](#pydoc-copy-files)
- [pydoc request_status](#pydoc-request-status)

<a name="development"></a>
# Development

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
                DATABASE_PORT (str): the database port. The default is 5432
                    Hidden requirement for requests_db.get_dbconnect_info.
                DATABASE_NAME (str): the name of the database.
                    Hidden requirement for requests_db.get_dbconnect_info.
                DATABASE_USER (str): the name of the application user.
                    Hidden requirement for requests_db.get_dbconnect_info.
            Parameter Store:
                drdb-user-pass (str): the password for the application user (DATABASE_USER).
                    Hidden requirement for requests_db.get_dbconnect_info.
                drdb-host (str): the database host.
                    Hidden requirement for requests_db.get_dbconnect_info.
            Args:
                event (dict): A dict with the following keys:
                    'config' (dict): A dict with the following keys:
                        'glacier_bucket' (str): The name of the glacier bucket from which the files
                        will be restored.
                    'input' (dict): A dict with the following keys:
                        'granules' (list(dict)): A list of dicts with the following keys:
                            'granuleId' (str): The id of the granule being restored.
                            'keys' (list(dict)): A list of dicts with the following keys:  # TODO: rename.
                                'key' (str): Name of the file within the granule.
                                'dest_bucket' (str): The bucket the restored file will be moved
                                    to after the restore completes.
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
    
    inner_task(event: Dict, max_retries: int, retry_sleep_secs: float, retrieval_type: str, restore_expire_days: int)
    
    object_exists(s3_cli: botocore.client.BaseClient, glacier_bucket: str, file_key: str) -> bool
        Check to see if an object exists in S3 Glacier.
        Args:
            s3_cli: An instance of boto3 s3 client
            glacier_bucket: The S3 glacier bucket name
            file_key: The key of the Glacier object
        Returns:
            True if the object exists, otherwise False.
    
    process_granule(s3: botocore.client.BaseClient, granule: Dict[str, Union[str, List[Dict]]], glacier_bucket: str, restore_expire_days: int, max_retries: int, retry_sleep_secs: float, retrieval_type: str)
    
    restore_object(s3_cli: botocore.client.BaseClient, obj: Dict[str, Any], attempt: int, max_retries: int, retrieval_type: str = 'Standard') -> None
    
    task(event: Dict, context: object) -> Dict[str, Any]
        Task called by the handler to perform the work.
        This task will call the restore_request for each file. Restored files will be kept
        for {exp_days} days before they expire. A restore request will be tried up to {retries} times
        if it fails, waiting {retry_sleep_secs} between each attempt.
            Args:
                event: Passed through from the handler.
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
                DATABASE_PORT (str): the database port. The default is 5432
                    Hidden requirement for requests_db.get_dbconnect_info.
                DATABASE_NAME (str): the name of the database.
                    Hidden requirement for requests_db.get_dbconnect_info.
                DATABASE_USER (str): the name of the application user.
                    Hidden requirement for requests_db.get_dbconnect_info.
            Parameter Store:
                drdb-user-pass (str): the password for the application user (DATABASE_USER).
                    Hidden requirement for requests_db.get_dbconnect_info.
                drdb-host (str): the database host.
                    Hidden requirement for requests_db.get_dbconnect_info.
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
    LOGGER = <cumulus_logger.CumulusLogger object>
    List = typing.List
    OS_ENVIRON_RESTORE_EXPIRE_DAYS_KEY = 'RESTORE_EXPIRE_DAYS'
    OS_ENVIRON_RESTORE_REQUEST_RETRIES_KEY = 'RESTORE_REQUEST_RETRIES'
    OS_ENVIRON_RESTORE_RETRIEVAL_TYPE_KEY = 'RESTORE_RETRIEVAL_TYPE'
    OS_ENVIRON_RESTORE_RETRY_SLEEP_SECS_KEY = 'RESTORE_RETRY_SLEEP_SECS'
    REQUESTS_DB_DEST_BUCKET_KEY = 'dest_bucket'
    REQUESTS_DB_ERROR_MESSAGE_KEY = 'err_msg'
    REQUESTS_DB_GLACIER_BUCKET_KEY = 'glacier_bucket'
    REQUESTS_DB_GRANULE_ID_KEY = 'granule_id'
    REQUESTS_DB_JOB_STATUS_KEY = 'job_status'
    REQUESTS_DB_REQUEST_GROUP_ID_KEY = 'request_group_id'
    REQUESTS_DB_REQUEST_ID_KEY = 'request_id'
    Union = typing.Union
```
