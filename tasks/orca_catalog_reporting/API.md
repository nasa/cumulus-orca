# Table of Contents

* [orca\_catalog\_reporting](#orca_catalog_reporting)
  * [task](#orca_catalog_reporting.task)
  * [query\_db](#orca_catalog_reporting.query_db)
  * [create\_http\_error\_dict](#orca_catalog_reporting.create_http_error_dict)
  * [handler](#orca_catalog_reporting.handler)

<a id="orca_catalog_reporting"></a>

# orca\_catalog\_reporting

<a id="orca_catalog_reporting.task"></a>

#### task

```python
def task(provider_id: Union[None, List[str]], collection_id: Union[None,
                                                                   List[str]],
         granule_id: Union[None, List[str]], start_timestamp: Union[None, int],
         end_timestamp: int, page_index: int,
         db_connect_info: Dict[str, str]) -> Dict[str, Any]
```

**Arguments**:

- `provider_id` - The unique ID of the provider(s) making the request.
- `collection_id` - The unique ID of collection(s) to compare.
- `granule_id` - The unique ID of granule(s) to compare.
- `start_timestamp` - Cumulus createdAt start time for date range to compare data.
- `end_timestamp` - Cumulus createdAt end-time for date range to compare data.
- `page_index` - The 0-based index of the results page to return.
- `db_connect_info` - See requests_db.py's get_configuration for further details.

<a id="orca_catalog_reporting.query_db"></a>

#### query\_db

```python
@retry_operational_error()
def query_db(engine: Engine, provider_id: Union[None, List[str]],
             collection_id: Union[None, List[str]],
             granule_id: Union[None, List[str]], start_timestamp: Union[None,
                                                                        int],
             end_timestamp: int, page_index: int) -> List[Dict[str, Any]]
```

**Arguments**:

- `engine` - The sqlalchemy engine to use for contacting the database.
- `provider_id` - The unique ID of the provider(s) making the request.
- `collection_id` - The unique ID of collection(s) to compare.
- `granule_id` - The unique ID of granule(s) to compare.
- `start_timestamp` - Cumulus createdAt start time for date range to compare data.
- `end_timestamp` - Cumulus createdAt end-time for date range to compare data.
- `page_index` - The 0-based index of the results page to return.

<a id="orca_catalog_reporting.create_http_error_dict"></a>

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

<a id="orca_catalog_reporting.handler"></a>

#### handler

```python
@LOGGER.inject_lambda_context
def handler(
        event: Dict[str, Union[str, int]],
        context: LambdaContext) -> Union[List[Dict[str, Any]], Dict[str, Any]]
```

Entry point for the orca_catalog_reporting Lambda.

**Arguments**:

- `event` - See schemas/input.json
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

