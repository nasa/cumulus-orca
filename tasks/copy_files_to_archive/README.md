[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/copy_files_to_archive/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/copy_files_to_archive/requirements.txt)

**Lambda function copy_files_to_archive **

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro) for information on environment setup and testing.

- [Deployment](#deployment)
  * [Deployment Validation](#deployment-validation)
- [pydoc copy_files_to_archive](#pydoc-copy-files)

<a name="deployment"></a>
## Deployment
```
    see /bin/build_tasks.sh to build the zip file. Upload the zip file to AWS.
```
<a name="deployment-validation"></a>
### Deployment Validation
```
1.  Paste the contents of test/testevents/copy_exp_event_1.json into
    a test event and execute it.
2.  Neither the source_key or the source_bucket should exist, so the copy will fail
    and the database update will fail.

```
<a name="pydoc-copy-files"></a>
## pydoc copy_files_to_archive
```
Help on module copy_files_to_archive:

NAME
    copy_files_to_archive

DESCRIPTION
    Name: copy_files_to_archive.py
    Description:  Lambda function that copies files from one s3 bucket
    to another s3 bucket.

CLASSES
    builtins.Exception(builtins.BaseException)
        CopyRequestError
    
    class CopyRequestError(builtins.Exception)
     |  Exception to be raised if the copy request fails for any of the files.
     |  
     |  Method resolution order:
     |      CopyRequestError
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
    copy_object(s3_cli: botocore.client.BaseClient, src_bucket_name: str, src_object_name: str, dest_bucket_name: str, multipart_chunksize_mb: int, dest_object_name: str = None) -> Union[str, NoneType]
        Copy an Amazon S3 bucket object
        Args:
            s3_cli: An instance of boto3 s3 client.
            src_bucket_name: The source S3 bucket name.
            src_object_name: The key of the s3 object being copied.
            dest_bucket_name: The target S3 bucket name.
            multipart_chunksize_mb: The maximum size of chunks to use when copying.
            dest_object_name: Optional; The key of the destination object.
                If an object with the same name exists in the given bucket, the object is overwritten.
                Defaults to {src_object_name}.
        Returns:
            None if object was copied, otherwise contains error message.
    
    get_files_from_records(records: List[Dict[str, Any]]) -> List[Dict[str, Union[str, bool]]]
        Parses the input records and returns the files to be restored.
        Args:
            records: passed through from the handler.
        Returns:
            records, parsed into Dicts, with the additional KVP 'success' = False
    
    handler(event: Dict[str, Any], context: object) -> None
        Lambda handler. Copies a file from its temporary s3 bucket to the s3 archive.
        If the copy for a file in the request fails, the lambda
        throws an exception. Environment variables can be set to override how many
        times to retry a copy before failing, and how long to wait between retries.
            Environment Vars:
                COPY_RETRIES (number, optional, default = 3): The number of
                    attempts to retry a copy that failed.
                COPY_RETRY_SLEEP_SECS (number, optional, default = 0): The number of seconds
                    to sleep between retry attempts.
                DATABASE_PORT (string): the database port. The standard is 5432.
                DATABASE_NAME (string): the name of the database.
                DATABASE_USER (string): the name of the application user.
            Parameter Store:
                    drdb-user-pass (string): the password for the application user (DATABASE_USER).
                    drdb-host (string): the database host
        Args:
            event:
                A dict from the SQS queue. See schemas/input.json for more information.
            context: An object required by AWS Lambda. Unused.
        Raises:
            CopyRequestError: An error occurred calling copy for one or more files.
            The same dict that is returned for a successful copy will be included in the
            message, with 'success' = False for the files for which the copy failed.
    
    task(records: List[Dict[str, Any]], max_retries: int, retry_sleep_secs: float, db_queue_url: str, default_multipart_chunksize_mb: int) -> None
        Task called by the handler to perform the work.
        This task will call copy_object for each file. A copy will be tried
        up to {retries} times if it fails, waiting {retry_sleep_secs}
        between each attempt.
        Args:
            records: Passed through from the handler.
            max_retries: The number of attempts to retry a failed copy.
            retry_sleep_secs: The number of seconds
                to sleep between retry attempts.
            db_queue_url: The URL of the queue that posts status entries.
            default_multipart_chunksize_mb: The multipart_chunksize to use if not set on file.
        Raises:
            CopyRequestError: Thrown if there are errors with the input records or the copy failed.

DATA
    Any = typing.Any
    Dict = typing.Dict
    FILE_ERROR_MESSAGE_KEY = 'err_msg'
    FILE_SUCCESS_KEY = 'success'
    INPUT_FILENAME_KEY = 'filename'
    INPUT_GRANULE_ID_KEY = 'granule_id'
    INPUT_JOB_ID_KEY = 'job_id'
    INPUT_MULTIPART_CHUNKSIZE_MB = 'multipart_chunksize_mb'
    INPUT_SOURCE_BUCKET_KEY = 'source_bucket'
    INPUT_SOURCE_KEY_KEY = 'source_key'
    INPUT_TARGET_BUCKET_KEY = 'restore_destination'
    INPUT_TARGET_KEY_KEY = 'target_key'
    LOGGER = <cumulus_logger.CumulusLogger object>
    List = typing.List
    MB = 1048576
    OS_ENVIRON_DB_QUEUE_URL_KEY = 'DB_QUEUE_URL'
    Optional = typing.Optional
    Union = typing.Union
```