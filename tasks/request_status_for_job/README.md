[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/copy_files_to_archive/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/copy_files_to_archive/requirements.txt)

**Lambda function request_status_for_job **

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro) for information on environment setup and testing.

- [Input/Output Schemas and Examples](#input-output-schemas)
- [pydoc request_status_for_job](#pydoc)

<a name="input-output-schemas"></a>
## Input/Output Schemas and Examples
Fully defined json schemas written in the schema of https://json-schema.org/ can be found in the [schemas folder](schemas).

### Example Input
```json
{
  "asyncOperationId": "43c9751b-9498-4733-90d8-56b1458e0f85"
}
```

### Example Output
```json
{
  "asyncOperationId": "43c9751b-9498-4733-90d8-56b1458e0f85",
  "jobStatusTotals": {
    "pending": 1,
    "success": 1,
    "failed": 1
  },
  "granules": [
    {
      "granuleId": "6c8d0c8b-4f9a-4d87-ab7c-480b185a0250",
      "status": "failed"
    },
    {
      "granuleId": "b5681dc1-48ba-4dc3-877d-1b5ad97e8276",
      "status": "pending"
    },
    {
      "granuleId": "7a75767d-abe3-4c1d-b55f-9009de1838f8",
      "status": "success"
    }
  ]
}
```
<a name="pydoc"></a>
## pydoc request_status_for_job
```
Help on module request_status_for_job:

NAME
    request_status_for_job

FUNCTIONS
    create_http_error_dict(error_type: str, http_status_code: int, request_id: str, message: str) -> Dict[str, Any]
        Creates a standardized dictionary for error reporting.
        Args:
            error_type: The string representation of http_status_code.
            http_status_code: The integer representation of the http error.
            request_id: The incoming request's id.
            message: The message to display to the user and to record for debugging.
        Returns:
            A dict with the following keys:
                'errorType' (str)
                'httpStatus' (int)
                'requestId' (str)
                'message' (str)
    
    get_granule_status_entries_for_job(job_id: str, engine: sqlalchemy.future.engine.Engine) -> List[Dict[str, Any]]
        Gets the recovery_job status entry for the associated job_id.
        
        Args:
            job_id: The unique asyncOperationId of the recovery job to retrieve status for.
            engine: The sqlalchemy engine to use for contacting the database.
        
        Returns: A list of dicts with the following keys:
            'granule_id' (str)
            'status' (str): pending|staged|success|failed
    
    get_granule_status_entries_for_job_sql() -> <function text at 0x10a89a710>
    
    get_status_totals_for_job(job_id: str, engine: sqlalchemy.future.engine.Engine) -> Dict[str, int]
        Gets the number of recovery_job for the given job_id for each possible status value.
        
        Args:
            job_id: The unique id of the recovery job to retrieve status for.
            engine: The sqlalchemy engine to use for contacting the database.
        
        Returns: A dictionary with the following keys:
            'pending' (int)
            'staged' (int)
            'success' (int)
            'failed' (int)
    
    get_status_totals_for_job_sql() -> <function text at 0x10a89a710>
    
    handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]
        Entry point for the request_status_for_job Lambda.
        Args:
            event: A dict with the following keys:
                asyncOperationId: The unique asyncOperationId of the recovery job.
            context: An object provided by AWS Lambda. Used for context tracking.
        
        Environment Vars: See shared_db.py's get_configuration for further details.
        
        Returns: A Dict with the following keys:
            asyncOperationId (str): The unique ID of the asyncOperation.
            job_status_totals (Dict[str, int]): Sums of how many granules are in each particular restoration status.
                pending (int): The number of granules that still need to be copied.
                staged (int): Currently unimplemented.
                success (int): The number of granules that have been successfully copied.
                failed (int): The number of granules that did not copy and will not copy due to an error.
            granules (Array[Dict]): An array of Dicts representing each granule being copied as part of the job.
                granule_id (str): The unique ID of the granule.
                status (str): The status of the restoration of the file. May be 'pending', 'staged', 'success', or 'failed'.
        
            Or, if an error occurs, see create_http_error_dict
                400 if asyncOperationId is missing. 500 if an error occurs when querying the database.
    
    task(job_id: str, db_connect_info: Dict, request_id: str) -> Dict[str, Any]
        Args:
            job_id: The unique asyncOperationId of the recovery job.
            db_connect_info: The database.py defined db_connect_info.
            request_id: An ID provided by AWS Lambda. Used for context tracking.
        Returns:
            A dictionary with the following keys:
                'asyncOperationId' (str): The job_id.
                'job_status_totals' (Dict): A dictionary with the following keys:
                    'pending' (int)
                    'staged' (int)
                    'success' (int)
                    'failed' (int)
                'granules' (List): A list of dicts with the following keys:
                    'granule_id' (str)
                    'status' (str): pending|staged|success|failed
        
            Will also return a dict from create_http_error_dict with error NOT_FOUND if job could not be found.

DATA
    Any = typing.Any
    Dict = typing.Dict
    INPUT_JOB_ID_KEY = 'asyncOperationId'
    LOGGER = <cumulus_logger.CumulusLogger object>
    List = typing.List
    OUTPUT_GRANULES_KEY = 'granules'
    OUTPUT_GRANULE_ID_KEY = 'granuleId'
    OUTPUT_JOB_ID_KEY = 'asyncOperationId'
    OUTPUT_JOB_STATUS_TOTALS_KEY = 'jobStatusTotals'
    OUTPUT_STATUS_KEY = 'status'
```