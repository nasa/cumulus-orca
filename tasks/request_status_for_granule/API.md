# Table of Contents

* [request\_status\_for\_granule](#request_status_for_granule)
  * [task](#request_status_for_granule.task)
  * [get\_most\_recent\_job\_id\_for\_granule](#request_status_for_granule.get_most_recent_job_id_for_granule)
  * [get\_job\_entry\_for\_granule](#request_status_for_granule.get_job_entry_for_granule)
  * [get\_file\_entries\_for\_granule\_in\_job](#request_status_for_granule.get_file_entries_for_granule_in_job)
  * [create\_http\_error\_dict](#request_status_for_granule.create_http_error_dict)
  * [handler](#request_status_for_granule.handler)

<a id="request_status_for_granule"></a>

# request\_status\_for\_granule

<a id="request_status_for_granule.task"></a>

#### task

```python
def task(granule_id: str,
         db_connect_info: Dict,
         request_id: str,
         job_id: str = None) -> Dict[str, Any]
```

**Arguments**:

- `granule_id` - The unique ID of the granule to retrieve status for.
- `db_connect_info` - The {database}.py defined db_connect_info.
- `request_id` - An ID provided by AWS Lambda. Used for context tracking.
- `job_id` - An optional additional filter to get a specific job's entry.
- `Returns` - See output.json
  
  Will also return a dict from create_http_error_dict with error
  NOT_FOUND if job/granule could not be found.

<a id="request_status_for_granule.get_most_recent_job_id_for_granule"></a>

#### get\_most\_recent\_job\_id\_for\_granule

```python
@shared_db.retry_operational_error()
def get_most_recent_job_id_for_granule(granule_id: str,
                                       engine: Engine) -> Union[str, None]
```

Gets the job_id for the most recent job that restores the given granule.

**Arguments**:

- `granule_id` - The unique ID of the granule.
- `engine` - The sqlalchemy engine to use for contacting the database.
  
- `Returns` - The job_id for the given granule's restore job.

<a id="request_status_for_granule.get_job_entry_for_granule"></a>

#### get\_job\_entry\_for\_granule

```python
@shared_db.retry_operational_error()
def get_job_entry_for_granule(granule_id: str, job_id: str,
                              engine: Engine) -> Union[Dict[str, Any], None]
```

Gets the recovery_file status entries for the associated granule_id.
If async_operation_id is non-None, then it will be used to filter results.
Otherwise, only the item with the most recent request_time will be returned.

**Arguments**:

- `granule_id` - The unique ID of the granule to retrieve status for.
- `job_id` - An optional additional filter to get a specific job's entry.
- `engine` - The sqlalchemy engine to use for contacting the database.
- `Returns` - A Dict with the following keys:
- `'granule_id'` _str_ - The unique ID of the granule to retrieve status for.
- `'job_id'` _str_ - The unique ID of the asyncOperation.
- `'request_time'` _int_ - The time, in milliseconds since 1 January 1970 UTC,
  when the request to restore the granule was initiated.
- `'completion_time'` _int, Null_ - The time, in milliseconds since 1 January 1970 UTC,
  when all granule_files were no longer 'pending'/'staged'.

<a id="request_status_for_granule.get_file_entries_for_granule_in_job"></a>

#### get\_file\_entries\_for\_granule\_in\_job

```python
@shared_db.retry_operational_error()
def get_file_entries_for_granule_in_job(granule_id: str, job_id: str,
                                        engine: Engine) -> List[Dict]
```

Gets the individual status entries for the files for the given job+granule.

**Arguments**:

- `granule_id` - The id of the granule to get file statuses for.
- `job_id` - The id of the job to get file statuses for.
- `engine` - The sqlalchemy engine to use for contacting the database.
  
- `Returns` - A Dict with the following keys:
- `'file_name'` _str_ - The name and extension of the file.
- `'restore_destination'` _str_ - The name of the archive bucket the file is being copied to.
- `'status'` _str_ - The status of the restoration of the file.
  May be 'pending', 'staged', 'success', or 'failed'.
- `'error_message'` _str_ - If the restoration of the file errored,
  the error will be stored here. Otherwise, None.

<a id="request_status_for_granule.create_http_error_dict"></a>

#### create\_http\_error\_dict

```python
def create_http_error_dict(error_type: str, http_status_code: int,
                           request_id: str, message: str) -> Dict[str, Any]
```

Creates a standardized dictionary for error reporting.

**Arguments**:

- `error_type` - The string representation of http_status_code.
- `http_status_code` - The integer representation of the http error.
- `request_id` - The incoming request's id.
- `message` - The message to display to the user and to record for debugging.

**Returns**:

  A dict with the following keys:
  'errorType' (str)
  'httpStatus' (int)
  'requestId' (str)
  'message' (str)

<a id="request_status_for_granule.handler"></a>

#### handler

```python
def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]
```

Entry point for the request_status_for_granule Lambda.

**Arguments**:

- `event` - A dict with the following keys:
- `granule_id` - The unique ID of the granule to retrieve status for.
- `asyncOperationId` _Optional_ - The unique ID of the asyncOperation.
  May apply to a request that covers multiple granules.
- `context` - An object provided by AWS Lambda. Used for context tracking.
  
  Environment Vars:
  DB_CONNECT_INFO_SECRET_ARN (string):
  Secret ARN of the AWS secretsmanager secret for connecting to the database.
  See shared_db.py's get_configuration for further details.
  
- `Returns` - A Dict with the following keys:
- `'granule_id'` _str_ - The unique ID of the granule to retrieve status for.
- `'asyncOperationId'` _str_ - The unique ID of the asyncOperation.
- `'files'` _List_ - Description and status of the files within the given granule.
  List of Dicts with keys:
- `'file_name'` _str_ - The name and extension of the file.
- `'restore_destination'` _str_ - The name of the archive bucket
  the file is being copied to.
- `'status'` _str_ - The status of the restoration of the file.
  May be 'pending', 'staged', 'success', or 'failed'.
- `'error_message'` _str, Optional_ - If the restoration of the file errored,
  the error will be stored here.
- `'request_time'` _DateTime_ - The time, in UTC isoformat,
  when the request to restore the granule was initiated.
- `'completion_time'` _DateTime, Optional_ - The time, in UTC isoformat,
  when all granule_files were no longer 'pending'/'staged'.
  
  Or, if an error occurs, see create_http_error_dict
  400 if granule_id is missing.
  400 if input.json schema is not matched. 500 if an error occurs when querying the database. 404 if not found.

