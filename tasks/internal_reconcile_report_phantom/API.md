# Table of Contents

* [internal\_reconcile\_report\_phantom](#internal_reconcile_report_phantom)
  * [task](#internal_reconcile_report_phantom.task)
  * [query\_db](#internal_reconcile_report_phantom.query_db)
  * [create\_http\_error\_dict](#internal_reconcile_report_phantom.create_http_error_dict)
  * [handler](#internal_reconcile_report_phantom.handler)

<a id="internal_reconcile_report_phantom"></a>

# internal\_reconcile\_report\_phantom

<a id="internal_reconcile_report_phantom.task"></a>

#### task

```python
def task(job_id: int, page_index: int,
         db_connect_info: Dict[str, str]) -> Dict[str, Any]
```

**Arguments**:

- `job_id` - The unique ID of job/report.
- `page_index` - The 0-based index of the results page to return.
- `db_connect_info` - See requests_db.py's get_configuration for further details.

<a id="internal_reconcile_report_phantom.query_db"></a>

#### query\_db

```python
@retry_operational_error()
def query_db(engine: Engine, job_id: str,
             page_index: int) -> List[Dict[str, Any]]
```

**Arguments**:

- `engine` - The sqlalchemy engine to use for contacting the database.
- `job_id` - The unique ID of job/report.
- `page_index` - The 0-based index of the results page to return.

<a id="internal_reconcile_report_phantom.create_http_error_dict"></a>

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

<a id="internal_reconcile_report_phantom.handler"></a>

#### handler

```python
def handler(event: Dict[str, Union[str, int]],
            context: Any) -> Union[List[Dict[str, Any]], Dict[str, Any]]
```

Entry point for the internal_reconcile_report_phantom Lambda.

**Arguments**:

- `event` - See schemas/input.json
- `context` - An object provided by AWS Lambda. Used for context tracking.
  
  Environment Vars: See requests_db.py's get_configuration for further details.
  

**Returns**:

  See schemas/output.json
  Or, if an error occurs, see create_http_error_dict
  400 if input does not match schemas/input.json. 500 if an error occurs when querying the database.

