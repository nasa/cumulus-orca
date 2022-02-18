# Table of Contents

* [orca\_shared](#orca_shared)
* [orca\_shared.reconciliation](#orca_shared.reconciliation)
* [orca\_shared.reconciliation.shared\_reconciliation](#orca_shared.reconciliation.shared_reconciliation)
  * [OrcaStatus](#orca_shared.reconciliation.shared_reconciliation.OrcaStatus)
  * [get\_partition\_name\_from\_bucket\_name](#orca_shared.reconciliation.shared_reconciliation.get_partition_name_from_bucket_name)
* [orca\_shared.database](#orca_shared.database)
* [orca\_shared.database.shared\_db](#orca_shared.database.shared_db)
  * [get\_configuration](#orca_shared.database.shared_db.get_configuration)
  * [get\_admin\_connection](#orca_shared.database.shared_db.get_admin_connection)
  * [get\_user\_connection](#orca_shared.database.shared_db.get_user_connection)
  * [retry\_operational\_error](#orca_shared.database.shared_db.retry_operational_error)
* [orca\_shared.recovery](#orca_shared.recovery)
* [orca\_shared.recovery.shared\_recovery](#orca_shared.recovery.shared_recovery)
  * [RequestMethod](#orca_shared.recovery.shared_recovery.RequestMethod)
  * [OrcaStatus](#orca_shared.recovery.shared_recovery.OrcaStatus)
  * [get\_aws\_region](#orca_shared.recovery.shared_recovery.get_aws_region)
  * [create\_status\_for\_job](#orca_shared.recovery.shared_recovery.create_status_for_job)
  * [update\_status\_for\_file](#orca_shared.recovery.shared_recovery.update_status_for_file)
  * [post\_entry\_to\_fifo\_queue](#orca_shared.recovery.shared_recovery.post_entry_to_fifo_queue)
  * [post\_entry\_to\_standard\_queue](#orca_shared.recovery.shared_recovery.post_entry_to_standard_queue)

<a id="orca_shared"></a>

# orca\_shared

<a id="orca_shared.reconciliation"></a>

# orca\_shared.reconciliation

<a id="orca_shared.reconciliation.shared_reconciliation"></a>

# orca\_shared.reconciliation.shared\_reconciliation

Name: shared_reconciliation.py
Description: Shared library that combines common functions and classes needed for
             reconciliation operations.

<a id="orca_shared.reconciliation.shared_reconciliation.OrcaStatus"></a>

## OrcaStatus Objects

```python
class OrcaStatus(Enum)
```

An enumeration.
Defines the status value used in the ORCA Reconciliation database for use by the reconciliation functions.

<a id="orca_shared.reconciliation.shared_reconciliation.get_partition_name_from_bucket_name"></a>

#### get\_partition\_name\_from\_bucket\_name

```python
def get_partition_name_from_bucket_name(bucket_name: str)
```

Used for interacting with the reconcile_s3_object table.
Provides a valid partition name given an Orca bucket name.

bucket_name: The name of the Orca bucket in AWS.

<a id="orca_shared.database"></a>

# orca\_shared.database

<a id="orca_shared.database.shared_db"></a>

# orca\_shared.database.shared\_db

Name: shared_db.py

Description: Shared library for database objects needed by the various libraries.

<a id="orca_shared.database.shared_db.get_configuration"></a>

#### get\_configuration

```python
def get_configuration() -> Dict[str, str]
```

Create a dictionary of configuration values based on environment variables
parameter store information and other items needed to create the database.


```
Environment Variables:
    PREFIX (str): Deployment prefix used to pull the proper AWS secret.
    AWS_REGION (str): AWS reserved runtime variable used to set boto3 client region.

Parameter Store:
    <prefix>-orca-db-login-secret (string): The json string containing all the db login info.
```

**Arguments**:

  None
  

**Returns**:

- `Configuration` _Dict_ - Dictionary with all of the configuration information.
  The schema for the output is available [here](schemas/output.json).
  

**Raises**:

- `Exception` _Exception_ - When variables or secrets are not available.

<a id="orca_shared.database.shared_db.get_admin_connection"></a>

#### get\_admin\_connection

```python
def get_admin_connection(config: Dict[str, str], database: str = None) -> Engine
```

Creates a connection engine to a database as a superuser.

**Arguments**:

- `config` _Dict_ - Configuration containing connection information.
- `database` _str_ - Database for the admin user to connect to. Defaults to admin_database.
  
  Returns
- `Engine` _sqlalchemy.future.Engine_ - engine object for creating database connections.

<a id="orca_shared.database.shared_db.get_user_connection"></a>

#### get\_user\_connection

```python
def get_user_connection(config: Dict[str, str]) -> Engine
```

Creates a connection engine to the application database as the application
database user.

**Arguments**:

- `config` _Dict_ - Configuration containing connection information.
  
  Returns
- `Engine` _sqlalchemy.future.Engine_ - engine object for creating database connections.

<a id="orca_shared.database.shared_db.retry_operational_error"></a>

#### retry\_operational\_error

```python
def retry_operational_error(max_retries: int = MAX_RETRIES, backoff_in_seconds: int = INITIAL_BACKOFF_IN_SECONDS, backoff_factor: int = BACKOFF_FACTOR) -> Callable[[Callable[[], RT]], Callable[[], RT]]
```

Decorator takes arguments to adjust number of retries and backoff strategy.

**Arguments**:

- `max_retries` _int_ - number of times to retry in case of failure.
- `backoff_in_seconds` _int_ - Number of seconds to sleep the first time through.
- `backoff_factor` _int_ - Value of the factor used for backoff.

<a id="orca_shared.recovery"></a>

# orca\_shared.recovery

<a id="orca_shared.recovery.shared_recovery"></a>

# orca\_shared.recovery.shared\_recovery

Name: shared_recovery.py
Description: Shared library that combines common functions and classes needed for
             recovery operations.

<a id="orca_shared.recovery.shared_recovery.RequestMethod"></a>

## RequestMethod Objects

```python
class RequestMethod(Enum)
```

An enumeration.
Provides potential actions for the database lambda to take when posting to the SQS queue.

<a id="orca_shared.recovery.shared_recovery.OrcaStatus"></a>

## OrcaStatus Objects

```python
class OrcaStatus(Enum)
```

An enumeration.
Defines the status value used in the ORCA Recovery database for use by the recovery functions.

<a id="orca_shared.recovery.shared_recovery.get_aws_region"></a>

#### get\_aws\_region

```python
def get_aws_region() -> str
```

Gets AWS region variable from the runtime environment variable.

**Returns**:

  The AWS region variable.

**Raises**:

- `Exception` - Thrown if AWS region is empty or None.

<a id="orca_shared.recovery.shared_recovery.create_status_for_job"></a>

#### create\_status\_for\_job

```python
def create_status_for_job(job_id: str, granule_id: str, archive_destination: str, files: List[Dict[str, Any]], db_queue_url: str)
```

Creates status information for a new job and its files, and posts to queue.

**Arguments**:

- `job_id` - The unique identifier used for tracking requests.
- `granule_id` - The id of the granule being restored.
- `archive_destination` - The S3 bucket destination of where the data is archived.
- `files` - A List of Dicts with the following keys:
  'filename' (str)
  'keyPath' (str)
  'restoreDestination' (str)
  's3MultipartChunksizeMb' (int)
  'statusId' (int)
  'errorMessage' (str, Optional)
  'requestTime' (str)
  'lastUpdate' (str)
  'completionTime' (str, Optional)
- `db_queue_url` - The SQS queue URL defined by AWS.

<a id="orca_shared.recovery.shared_recovery.update_status_for_file"></a>

#### update\_status\_for\_file

```python
def update_status_for_file(job_id: str, granule_id: str, filename: str, orca_status: OrcaStatus, error_message: Optional[str], db_queue_url: str)
```

Creates update information for a file's status entry, and posts to queue.
Queue entry will be rejected by post_to_database if status for
job_id + granule_id + filename does not exist.

**Arguments**:

- `job_id` - The unique identifier used for tracking requests.
- `granule_id` - The id of the granule being restored.
- `filename` - The name of the file being copied.
- `orca_status` - Defines the status id used in the ORCA Recovery database.
- `error_message` - message displayed on error.
- `db_queue_url` - The SQS queue URL defined by AWS.

<a id="orca_shared.recovery.shared_recovery.post_entry_to_fifo_queue"></a>

#### post\_entry\_to\_fifo\_queue

```python
def post_entry_to_fifo_queue(new_data: Dict[str, Any], request_method: RequestMethod, db_queue_url: str) -> None
```

Posts messages to SQS FIFO queue.

**Arguments**:

- `new_data` - A dictionary representing the column/value pairs to write to the DB table.
- `request_method` - The action for the database lambda to take when posting to the SQS queue.
- `db_queue_url` - The SQS queue URL defined by AWS.

**Raises**:

  None

<a id="orca_shared.recovery.shared_recovery.post_entry_to_standard_queue"></a>

#### post\_entry\_to\_standard\_queue

```python
def post_entry_to_standard_queue(new_data: Dict[str, Any], recovery_queue_url: str) -> None
```

Posts messages to the recovery standard SQS queue.

**Arguments**:

- `new_data` - A dictionary representing the column/value pairs to write to the DB table.
- `recovery_queue_url` - The SQS queue URL defined by AWS.

**Raises**:

  None

