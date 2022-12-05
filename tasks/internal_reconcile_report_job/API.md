# Table of Contents

* [internal\_reconcile\_report\_job](#internal_reconcile_report_job)
  * [task](#internal_reconcile_report_job.task)
  * [query\_db](#internal_reconcile_report_job.query_db)
  * [get\_jobs\_sql](#internal_reconcile_report_job.get_jobs_sql)
  * [create\_http\_error\_dict](#internal_reconcile_report_job.create_http_error_dict)
  * [check\_env\_variable](#internal_reconcile_report_job.check_env_variable)
  * [handler](#internal_reconcile_report_job.handler)

<a id="internal_reconcile_report_job"></a>

# internal\_reconcile\_report\_job

<a id="internal_reconcile_report_job.task"></a>

#### task

```python
def task(page_index: int, db_connect_info: Dict[str, str]) -> Dict[str, Any]
```

**Arguments**:

- `page_index` - The 0-based index of the results page to return.
- `db_connect_info` - See requests_db.py's get_configuration for further details.

<a id="internal_reconcile_report_job.query_db"></a>

#### query\_db

```python
@retry_operational_error()
def query_db(engine: Engine, page_index: int) -> List[Dict[str, Any]]
```

Gets jobs for the given page, up to PAGE_SIZE + 1 results.

**Arguments**:

- `engine` - The sqlalchemy engine to use for contacting the database.
- `page_index` - The 0-based index of the results page to return.
  

**Returns**:

  A list containing dicts matching the format of "jobs" in output.json.

<a id="internal_reconcile_report_job.get_jobs_sql"></a>

#### get\_jobs\_sql

```python
def get_jobs_sql() -> text
```

SQL for getting jobs and associated metadata from Postgres.
Formats datetimes in milliseconds since 1 January 1970 UTC.

<a id="internal_reconcile_report_job.create_http_error_dict"></a>

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

<a id="internal_reconcile_report_job.check_env_variable"></a>

#### check\_env\_variable

```python
def check_env_variable(env_name: str) -> str
```

Checks for the lambda environment variable.

**Arguments**:

- `env_name` _str_ - The environment variable name set in lambda configuration.
- `Raises` - KeyError in case the environment variable is not found.

<a id="internal_reconcile_report_job.handler"></a>

#### handler

```python
@LOGGER.inject_lambda_context
def handler(
        event: Dict[str, Union[str, int]],
        context: LambdaContext) -> Union[List[Dict[str, Any]], Dict[str, Any]]
```

Entry point for the internal_reconcile_report_job Lambda.

**Arguments**:

- `event` - See schemas/input.json for details.
- `context` - This object provides information about the lambda invocation, function,
  and execution env.
  Environment Vars:
  DB_CONNECT_INFO_SECRET_ARN (string):
  Secret ARN of the AWS secretsmanager secret for connecting to the database.
  See shared_db.py's get_configuration for further details.
  

**Returns**:

  See schemas/output.json
  Or, if an error occurs, see create_http_error_dict
  400 if input does not match schemas/input.json.
  500 if an error occurs when querying the database.

