[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/copy_files_to_archive/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/copy_files_to_archive/requirements.txt)

**Lambda function request_status_for_granule **

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro) for information on environment setup and testing.

- [Input/Output Schemas and Examples](#input-output-schemas)
- [pydoc request_status_for_granule](#pydoc)

<a name="input-output-schemas"></a>
## Input/Output Schemas and Examples
Fully defined json schemas written in the schema of https://json-schema.org/ can be found in the [schemas folder](schemas).

### Example Input
Input with granule_id and asyncOperationId.
```json
{
  "granule_id": "6c8d0c8b-4f9a-4d87-ab7c-480b185a0250",
  "asyncOperationId": "43c9751b-9498-4733-90d8-56b1458e0f85"
}
```
Input with no asyncOperationId. Only the most recent operation for the granule will be queried.
```json
{
  "granule_id": "6c8d0c8b-4f9a-4d87-ab7c-480b185a0250"
}
```

### Example Output
```json
{
  "granule_id": "6c8d0c8b-4f9a-4d87-ab7c-480b185a0250",
  "asyncOperationId": "43c9751b-9498-4733-90d8-56b1458e0f85",
  "files": [
    {
      "file_name": "f1.doc",
      "status": "pending"
    },
    {
      "file_name": "f2.pdf",
      "status": "failed",
      "error_message": "Access Denied"
    },
    {
      "file_name": "f3.txt",
      "status": "success"
    }
  ],
  "restore_destination": "bucket_name",
  "request_time": "2019-07-17T17:36:38.494918",
  "completion_time": "2019-07-18T17:36:38.494918"
}
```
<a name="pydoc"></a>
## pydoc request_status_for_granule
```
NAME
    request_status_for_granule

FUNCTIONS
    create_http_error_dict(error_type: str, http_status_code: int, request_id: str, message: str) -> Dict[str, Any]
    
    get_file_entries_for_granule_in_job(granule_id: str, job_id: str, db_connect_info: Dict) -> List[Dict]
        Gets the individual status entries for the files for the given job+granule.
        
        Args:
        
        Returns: A Dict with the following keys:
            'file_name' (str): The name and extension of the file.
            'status' (str): The status of the restoration of the file. May be 'pending', 'success', or 'failed'.
            'error_message' (str): If the restoration of the file errored, the error will be stored here. Otherwise, None.
    
    get_job_entry_for_granule(granule_id: str, job_id: str, db_connect_info: Dict) -> Dict[str, Any]
        Gets the orca_recoverfile status entries for the associated granule_id.
        If async_operation_id is non-None, then it will be used to filter results.
        Otherwise, only the item with the most recent request_time will be returned.
        
        Args:
            granule_id: The unique ID of the granule to retrieve status for.
            job_id: An optional additional filter to get a specific job's entry.
            db_connect_info: The {database}.py defined db_connect_info.
        Returns: A Dict with the following keys:
            'granule_id' (str): The unique ID of the granule to retrieve status for.
            'job_id' (str): The unique ID of the asyncOperation.
            'restore_destination' (str): The name of the glacier bucket the granule is being copied to.
            'request_time' (DateTime): The time, in UTC isoformat, when the request to restore the granule was initiated.
            'completion_time' (DateTime, Optional):
                The time, in UTC isoformat, when all granule_files were no longer 'pending'.
    
    get_most_recent_job_id_for_granule(granule_id: str, db_connect_info: Dict[str, <built-in function any>]) -> str
    
    handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]
        Entry point for the request_status_for_granule Lambda.
        Args:
            event: A dict with the following keys:
                granule_id: The unique ID of the granule to retrieve status for.
                asyncOperationId (Optional): The unique ID of the asyncOperation.
                    May apply to a request that covers multiple granules.
            context: An object required by AWS Lambda. Unused.
        
        Returns: A Dict with the following keys:
            'granule_id' (str): The unique ID of the granule to retrieve status for.
            'asyncOperationId' (str): The unique ID of the asyncOperation.
            'files' (List): Description and status of the files within the given granule. List of Dicts with keys:
                'file_name' (str): The name and extension of the file.
                'status' (str): The status of the restoration of the file. May be 'pending', 'success', or 'failed'.
                'error_message' (str, Optional): If the restoration of the file errored, the error will be stored here.
            'restore_destination' (str): The name of the glacier bucket the granule is being copied to.
            'request_time' (DateTime): The time, in UTC isoformat, when the request to restore the granule was initiated.
            'completion_time' (DateTime, Optional):
                The time, in UTC isoformat, when all granule_files were no longer 'pending'.
                
            Or, if an error occurs, see create_http_error_dict
                400 if granule_id is missing. 500 if an error occurs when querying the database.
    
    task(granule_id: str, db_connect_info: Dict, job_id: str = None) -> Dict[str, Any]
        todo: Remember to fix datetime bugs in dists.
        Args:
            granule_id: The unique ID of the granule to retrieve status for.
            db_connect_info: The {database}.py defined db_connect_info.
            job_id: An optional additional filter to get a specific job's entry.
        Returns: A Dict with the following keys:
            'granule_id' (str): The unique ID of the granule to retrieve status for.
            'asyncOperationId' (str): The unique ID of the asyncOperation.
            'files' (List): Description and status of the files within the given granule. List of Dicts with keys:
                'file_name' (str): The name and extension of the file.
                'status' (str): The status of the restoration of the file. May be 'pending', 'success', or 'failed'.
                'error_message' (str, Optional): If the restoration of the file errored, the error will be stored here.
            'restore_destination' (str): The name of the glacier bucket the granule is being copied to.
            'request_time' (DateTime): The time, in UTC isoformat, when the request to restore the granule was initiated.
            'completion_time' (DateTime, Optional):
                The time, in UTC isoformat, when all granule_files were no longer 'pending'.

DATA
    Any = typing.Any
    Dict = typing.Dict
    INPUT_GRANULE_ID_KEY = 'granule_id'
    INPUT_JOB_ID_KEY = 'asyncOperationId'
    LOGGER = <cumulus_logger.CumulusLogger object>
    List = typing.List
    OUTPUT_COMPLETION_TIME_KEY = 'completion_time'
    OUTPUT_ERROR_MESSAGE_KEY = 'error_message'
    OUTPUT_FILENAME_KEY = 'file_name'
    OUTPUT_FILES_KEY = 'files'
    OUTPUT_GRANULE_ID_KEY = 'granule_id'
    OUTPUT_JOB_ID_KEY = 'asyncOperationId'
    OUTPUT_REQUEST_TIME_KEY = 'request_time'
    OUTPUT_RESTORE_DESTINATION_KEY = 'restore_destination'
    OUTPUT_STATUS_KEY = 'status'
```