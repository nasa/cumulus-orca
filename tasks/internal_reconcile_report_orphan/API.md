# Table of Contents

* [src](#src)
* [src.adapters](#src.adapters)
* [src.adapters.storage](#src.adapters.storage)
* [src.adapters.storage.rdbms](#src.adapters.storage.rdbms)
  * [StorageAdapterRDBMS](#src.adapters.storage.rdbms.StorageAdapterRDBMS)
    * [\_\_init\_\_](#src.adapters.storage.rdbms.StorageAdapterRDBMS.__init__)
    * [get\_orphans\_page](#src.adapters.storage.rdbms.StorageAdapterRDBMS.get_orphans_page)
  * [StorageAdapterPostgres](#src.adapters.storage.rdbms.StorageAdapterPostgres)
    * [get\_orphans\_sql](#src.adapters.storage.rdbms.StorageAdapterPostgres.get_orphans_sql)
* [src.adapters.api](#src.adapters.api)
* [src.adapters.api.aws](#src.adapters.api.aws)
  * [check\_env\_variable](#src.adapters.api.aws.check_env_variable)
  * [create\_http\_error\_dict](#src.adapters.api.aws.create_http_error_dict)
  * [handler](#src.adapters.api.aws.handler)
* [src.use\_cases.get\_orphans\_page](#src.use_cases.get_orphans_page)
  * [task](#src.use_cases.get_orphans_page.task)
* [src.use\_cases](#src.use_cases)
* [src.use\_cases.adapter\_interfaces](#src.use_cases.adapter_interfaces)
* [src.use\_cases.adapter\_interfaces.storage](#src.use_cases.adapter_interfaces.storage)
  * [OrphansPageStorageInterface](#src.use_cases.adapter_interfaces.storage.OrphansPageStorageInterface)
* [src.entities](#src.entities)
* [src.entities.orphan](#src.entities.orphan)

<a id="src"></a>

# src

<a id="src.adapters"></a>

# src.adapters

<a id="src.adapters.storage"></a>

# src.adapters.storage

<a id="src.adapters.storage.rdbms"></a>

# src.adapters.storage.rdbms

<a id="src.adapters.storage.rdbms.StorageAdapterRDBMS"></a>

## StorageAdapterRDBMS Objects

```python
class StorageAdapterRDBMS(OrphansPageStorageInterface)
```

<a id="src.adapters.storage.rdbms.StorageAdapterRDBMS.__init__"></a>

#### \_\_init\_\_

```python
def __init__(connection_uri: str)
```

**Arguments**:

- `connection_uri` - The URI connection string.

<a id="src.adapters.storage.rdbms.StorageAdapterRDBMS.get_orphans_page"></a>

#### get\_orphans\_page

```python
@shared_db.retry_operational_error()
def get_orphans_page(orphan_record_filter: OrphanRecordFilter,
                     LOGGER: logging.Logger) -> OrphanRecordPage
```

Gets orphans for the given job/page, up to PAGE_SIZE + 1 results.

**Arguments**:

- `orphan_record_filter` - The filter designating which orphans to return.
- `LOGGER` - The logger to use.
  

**Returns**:

  A list containing orphan records.
  A bool indicating if there are further pages to retrieve.

<a id="src.adapters.storage.rdbms.StorageAdapterPostgres"></a>

## StorageAdapterPostgres Objects

```python
class StorageAdapterPostgres(StorageAdapterRDBMS)
```

<a id="src.adapters.storage.rdbms.StorageAdapterPostgres.get_orphans_sql"></a>

#### get\_orphans\_sql

```python
@staticmethod
def get_orphans_sql() -> text
```

SQL for getting orphan report entries for a given job_id, page_size, and page_index.
Formats datetimes in milliseconds since 1 January 1970 UTC.

<a id="src.adapters.api"></a>

# src.adapters.api

<a id="src.adapters.api.aws"></a>

# src.adapters.api.aws

<a id="src.adapters.api.aws.check_env_variable"></a>

#### check\_env\_variable

```python
def check_env_variable(env_name: str) -> str
```

Checks for the lambda environment variable.

**Arguments**:

- `env_name` _str_ - The environment variable name set in lambda configuration.
- `Raises` - KeyError in case the environment variable is not found.

<a id="src.adapters.api.aws.create_http_error_dict"></a>

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

<a id="src.adapters.api.aws.handler"></a>

#### handler

```python
@LOGGER.inject_lambda_context
def handler(
        event: Dict[str, Union[str, int]],
        context: LambdaContext) -> Union[List[Dict[str, Any]], Dict[str, Any]]
```

Entry point for the internal_reconcile_report_orphan Lambda.

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

<a id="src.use_cases.get_orphans_page"></a>

# src.use\_cases.get\_orphans\_page

<a id="src.use_cases.get_orphans_page.task"></a>

#### task

```python
def task(orphan_record_filter: OrphanRecordFilter,
         orphans_page_storage: OrphansPageStorageInterface,
         LOGGER: logging.Logger) -> OrphanRecordPage
```

**Arguments**:

- `orphan_record_filter` - The filter designating which orphans to return.
- `orphans_page_storage` - The helper class for getting the page from the DB.
- `LOGGER` - The logger to use.
  

**Returns**:

  A list containing orphan records.
  A bool indicating if there are further pages to retrieve.

<a id="src.use_cases"></a>

# src.use\_cases

<a id="src.use_cases.adapter_interfaces"></a>

# src.use\_cases.adapter\_interfaces

<a id="src.use_cases.adapter_interfaces.storage"></a>

# src.use\_cases.adapter\_interfaces.storage

<a id="src.use_cases.adapter_interfaces.storage.OrphansPageStorageInterface"></a>

## OrphansPageStorageInterface Objects

```python
class OrphansPageStorageInterface()
```

Generic storage class with method that needs to be implemented by database adapter.

<a id="src.entities"></a>

# src.entities

<a id="src.entities.orphan"></a>

# src.entities.orphan

