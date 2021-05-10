[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/post_to_database/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/shared_libraries/recovery/requirements-dev.txt)

**Lambda function post_to_database **

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro) for information on environment setup and testing.

- [Deployment](#deployment)
- [pydoc recovery](#pydoc)

<a name="deployment"></a>
## Deployment
```
    see /bin/build_tasks.sh to build the zip file. Upload the zip file to AWS.
```
<a name="pydoc"></a>
## pydoc recovery
```
Help on module shared_recovery:

NAME
    shared_recovery

DESCRIPTION
    Name: shared_recovery.py
    Description: Shared library that combines common functions and classes needed for recovery operations.

CLASSES
    enum.Enum(builtins.object)
        OrcaStatus
        RequestMethod
    
    class OrcaStatus(enum.Enum)
     |  OrcaStatus(value, names=None, *, module=None, qualname=None, type=None, start=1)
     |  
     |  An enumeration.
     |  Defines the status value used in the ORCA Recovery database for use by the recovery functions.
     |  
     |  Method resolution order:
     |      OrcaStatus
     |      enum.Enum
     |      builtins.object
     |  
     |  Data and other attributes defined here:
     |  
     |  FAILED = <OrcaStatus.FAILED: 3>
     |  
     |  PENDING = <OrcaStatus.PENDING: 1>
     |  
     |  STAGED = <OrcaStatus.STAGED: 2>
     |  
     |  SUCCESS = <OrcaStatus.SUCCESS: 4>
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
    
    class RequestMethod(enum.Enum)
     |  RequestMethod(value, names=None, *, module=None, qualname=None, type=None, start=1)
     |  
     |  An enumeration.
     |  Provides potential actions for the database lambda to take when posting to the SQS queue.
     |  
     |  Method resolution order:
     |      RequestMethod
     |      enum.Enum
     |      builtins.object
     |  
     |  Data and other attributes defined here:
     |  
     |  NEW_JOB = <RequestMethod.NEW_JOB: 'new_job'>
     |  
     |  UPDATE_FILE = <RequestMethod.UPDATE_FILE: 'update_file'>
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

FUNCTIONS
    create_status_for_job(job_id: str, granule_id: str, archive_destination: str, files: List[Dict[str, Any]], db_queue_url: str)
        Creates status information for a new job and its files, and posts to queue.
        
        Args:
            job_id: The unique identifier used for tracking requests.
            granule_id: The id of the granule being restored.
            archive_destination: The S3 bucket destination of where the data is archived.
            files: A List of Dicts with the following keys:
                'filename' (str)
                'key_path' (str)
                'restore_destination' (str)
                'status_id' (int)
                'error_message' (str, Optional)
                'request_time' (str)
                'last_update' (str)
                'completion_time' (str, Optional)
            db_queue_url: The SQS queue URL defined by AWS.
    
    post_entry_to_queue(new_data: Dict[str, Any], request_method: shared_recovery.RequestMethod, db_queue_url: str) -> None
        Posts messages to an SQS queue.
        
        Args:
            new_data: A dictionary representing the column/value pairs to write to the DB table.
            request_method: The method action for the database lambda to take when posting to the SQS queue.
            db_queue_url: The SQS queue URL defined by AWS.
        
        Raises:
            None
    
    update_status_for_file(job_id: str, granule_id: str, filename: str, orca_status: shared_recovery.OrcaStatus, error_message: Union[str, NoneType], db_queue_url: str)
        Creates update information for a file's status entry, and posts to queue.
        Queue entry will be rejected by post_to_database if status for job_id + granule_id + filename does not exist.
        
        Args:
            job_id: The unique identifier used for tracking requests.
            granule_id: The id of the granule being restored.
            filename: The name of the file being copied.
            orca_status: Defines the status id used in the ORCA Recovery database.
            error_message: message displayed on error.
            db_queue_url: The SQS queue URL defined by AWS.

DATA
    Any = typing.Any
    Dict = typing.Dict
    List = typing.List
    Optional = typing.Optional
```