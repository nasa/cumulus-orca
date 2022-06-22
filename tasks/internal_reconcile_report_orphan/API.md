# Table of Contents

* [internal\_reconcile\_report\_orphan](#internal_reconcile_report_orphan)
  * [task](#internal_reconcile_report_orphan.task)
  * [query\_db](#internal_reconcile_report_orphan.query_db)
  * [get\_orphans\_sql](#internal_reconcile_report_orphan.get_orphans_sql)
  * [create\_http\_error\_dict](#internal_reconcile_report_orphan.create_http_error_dict)
  * [check\_env\_variable](#internal_reconcile_report_orphan.check_env_variable)
  * [handler](#internal_reconcile_report_orphan.handler)

<a id="internal_reconcile_report_orphan"></a>

# internal\_reconcile\_report\_orphan

<a id="internal_reconcile_report_orphan.task"></a>

#### task

```python
def task(job_id: int, page_index: int,
         db_connect_info: Dict[str, str]) -> Dict[str, Any]
```

**Arguments**:

- `job_id` - The unique ID of job/report.
- `page_index` - The 0-based index of the results page to return.
- `db_connect_info` - See requests_db.py's get_configuration for further details.

<a id="internal_reconcile_report_orphan.query_db"></a>

#### query\_db

```python
@retry_operational_error()
def query_db(engine: Engine, job_id: str,
             page_index: int) -> List[Dict[str, Any]]
```

Gets orphans for the given job/page, up to PAGE_SIZE + 1 results.

**Arguments**:

- `engine` - The sqlalchemy engine to use for contacting the database.
- `job_id` - The unique ID of job/report.
- `page_index` - The 0-based index of the results page to return.
  

**Returns**:

  A list containing dicts matching the format of "orphans" in output.json.

<a id="internal_reconcile_report_orphan.get_orphans_sql"></a>

#### get\_orphans\_sql

```python
def get_orphans_sql() -> text
```

SQL for getting orphan report entries for a given job_id, page_size, and page_index.
Formats datetimes in milliseconds since 1 January 1970 UTC.

<a id="internal_reconcile_report_orphan.create_http_error_dict"></a>

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

<a id="internal_reconcile_report_orphan.check_env_variable"></a>

#### check\_env\_variable

```python
def check_env_variable(env_name: str) -> str
```

Checks for the lambda environment variable.

**Arguments**:

- `env_name` _str_ - The environment variable name set in lambda configuration.
- `Raises` - KeyError in case the environment variable is not found.

<a id="internal_reconcile_report_orphan.handler"></a>

#### handler

```python
def handler(event: Dict[str, Union[str, int]],
            context: Any) -> Union[List[Dict[str, Any]], Dict[str, Any]]
```

Entry point for the internal_reconcile_report_orphan Lambda.

**Arguments**:

- `event` - See schemas/input.json for details.
- `context` - An object provided by AWS Lambda. Used for context tracking.
  
  Environment Vars:
- `DB_CONNECT_INFO_SECRET_ARN` _string_ - Secret ARN of the AWS secretsmanager secret for connecting to the database.
  See shared_db.py's get_configuration for further details.
  

**Returns**:

  See schemas/output.json
  Or, if an error occurs, see create_http_error_dict
  400 if input does not match schemas/input.json. 500 if an error occurs when querying the database.

