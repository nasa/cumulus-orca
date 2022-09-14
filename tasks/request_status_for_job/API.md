# Table of Contents

* [request\_status\_for\_job](#request_status_for_job)
  * [task](#request_status_for_job.task)
  * [get\_granule\_status\_entries\_for\_job](#request_status_for_job.get_granule_status_entries_for_job)
  * [get\_status\_totals\_for\_job](#request_status_for_job.get_status_totals_for_job)
  * [create\_http\_error\_dict](#request_status_for_job.create_http_error_dict)
  * [handler](#request_status_for_job.handler)

<a id="request_status_for_job"></a>

# request\_status\_for\_job

<a id="request_status_for_job.task"></a>

#### task

```python
def task(job_id: str, db_connect_info: Dict,
         request_id: str) -> Dict[str, Any]
```

**Arguments**:

- `job_id` - The unique asyncOperationId of the recovery job.
- `db_connect_info` - The database.py defined db_connect_info.
- `request_id` - An ID provided by AWS Lambda. Used for context tracking.

**Returns**:

  A dictionary with the following keys:
- `'asyncOperationId'` _str_ - The job_id.
- `'job_status_totals'` _Dict_ - A dictionary with the following keys:
  'pending' (int)
  'staged' (int)
  'success' (int)
  'failed' (int)
- `'granules'` _List_ - A list of dicts with the following keys:
  'granule_id' (str)
- `'status'` _str_ - pending|staged|success|failed
  
  Will also return a dict from create_http_error_dict with
  error NOT_FOUND if job could not be found.

<a id="request_status_for_job.get_granule_status_entries_for_job"></a>

#### get\_granule\_status\_entries\_for\_job

```python
@shared_db.retry_operational_error()
def get_granule_status_entries_for_job(job_id: str,
                                       engine: Engine) -> List[Dict[str, Any]]
```

Gets the recovery_job status entry for the associated job_id.

**Arguments**:

- `job_id` - The unique asyncOperationId of the recovery job to retrieve status for.
- `engine` - The sqlalchemy engine to use for contacting the database.
  
- `Returns` - A list of dicts with the following keys:
  'granule_id' (str)
- `'status'` _str_ - pending|staged|success|failed

<a id="request_status_for_job.get_status_totals_for_job"></a>

#### get\_status\_totals\_for\_job

```python
@shared_db.retry_operational_error()
def get_status_totals_for_job(job_id: str, engine: Engine) -> Dict[str, int]
```

Gets the number of recovery_job for the given job_id for each possible status value.

**Arguments**:

- `job_id` - The unique id of the recovery job to retrieve status for.
- `engine` - The sqlalchemy engine to use for contacting the database.
  
- `Returns` - A dictionary with the following keys:
  'pending' (int)
  'staged' (int)
  'success' (int)
  'failed' (int)

<a id="request_status_for_job.create_http_error_dict"></a>

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

<a id="request_status_for_job.handler"></a>

#### handler

```python
def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]
```

Entry point for the request_status_for_job Lambda.

**Arguments**:

- `event` - A dict with the following keys:
- `asyncOperationId` - The unique asyncOperationId of the recovery job.
- `context` - An object provided by AWS Lambda. Used for context tracking.
  
  Environment Vars:
  DB_CONNECT_INFO_SECRET_ARN (string):
  Secret ARN of the AWS secretsmanager secret for connecting to the database.
  See shared_db.py's get_configuration for further details.
  
- `Returns` - A Dict with the following keys:
- `asyncOperationId` _str_ - The unique ID of the asyncOperation.
- `job_status_totals` _Dict[str, int]_ - Sums of how many granules are in each
  particular restoration status.
- `pending` _int_ - The number of granules that still need to be copied.
- `staged` _int_ - Currently unimplemented.
- `success` _int_ - The number of granules that have been successfully copied.
- `failed` _int_ - The number of granules that did not copy
  and will not copy due to an error.
- `granules` _Array[Dict]_ - An array of Dicts representing each granule
  being copied as part of the job.
- `granule_id` _str_ - The unique ID of the granule.
- `status` _str_ - The status of the restoration of the file.
  May be 'pending', 'staged', 'success', or 'failed'.
  
  Or, if an error occurs, see create_http_error_dict
  400 if input.json schema is not matched.
  500 if an error occurs when querying the database.

