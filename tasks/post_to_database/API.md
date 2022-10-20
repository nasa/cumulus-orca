# Table of Contents

* [post\_to\_database](#post_to_database)
  * [task](#post_to_database.task)
  * [send\_record\_to\_database](#post_to_database.send_record_to_database)
  * [create\_status\_for\_job\_and\_files](#post_to_database.create_status_for_job_and_files)
  * [update\_status\_for\_file](#post_to_database.update_status_for_file)
  * [handler](#post_to_database.handler)

<a id="post_to_database"></a>

# post\_to\_database

Name: post_to_database.py

Description:  Pulls entries from a queue and posts them to a DB.

<a id="post_to_database.task"></a>

#### task

```python
def task(records: List[Dict[str, Any]], db_connect_info: Dict) -> None
```

Sends each individual record to send_record_to_database.

**Arguments**:

- `records` - A list of Dicts. See send_record_to_database for schema info.
- `db_connect_info` - See shared_db.py's get_configuration for further details.

<a id="post_to_database.send_record_to_database"></a>

#### send\_record\_to\_database

```python
def send_record_to_database(record: Dict[str, Any], engine: Engine) -> None
```

Deconstructs a record to its components and calls send_values_to_database with the result.

**Arguments**:

- `record` - Contains the following keys:
- `'body'` _str_ - A json string representing a dict.
  Contains key/value pairs of column names and values for those columns.
  Must match one of the schemas.
- `'messageAttributes'` _dict_ - Contains the following keys:
- `'RequestMethod'` _str_ - 'post' or 'put',
  depending on if row should be created or updated respectively.
- `engine` - The sqlalchemy engine to use for contacting the database.

<a id="post_to_database.create_status_for_job_and_files"></a>

#### create\_status\_for\_job\_and\_files

```python
@shared_db.retry_operational_error(
    # Retry all files due to transactional behavior of engine.begin
)
def create_status_for_job_and_files(job_id: str, granule_id: str,
                                    request_time: str,
                                    archive_destination: str,
                                    files: List[Dict[str, Any]],
                                    engine: Engine) -> None
```

Posts the entry for the job, followed by individual entries for each file.

**Arguments**:

- `job_id` - The unique identifier used for tracking requests.
- `granule_id` - The id of the granule being restored.
- `archive_destination` - The S3 bucket destination of where the data is archived.
- `request_time` - The time the restore was requested in utc and iso-format.
- `files` - A List of Dicts. See schemas/new_job_input.json's `files` array for properties.
- `engine` - The sqlalchemy engine to use for contacting the database.

<a id="post_to_database.update_status_for_file"></a>

#### update\_status\_for\_file

```python
@shared_db.retry_operational_error(
    # Retry all files due to transactional behavior of engine.begin
)
def update_status_for_file(job_id: str, granule_id: str, filename: str,
                           last_update: str, completion_time: Optional[str],
                           status_id: int, error_message: Optional[str],
                           engine: Engine) -> None
```

Updates a given file's status entry, modifying the job if all files
for that job have advanced in status.

**Arguments**:

- `job_id` - The unique identifier used for tracking requests.
- `granule_id` - The id of the granule being restored.
- `filename` - The name of the file being copied.
- `last_update` - The time this status update occurred, in UTC iso-format.
- `completion_time` - The completion time, in UTC iso-format.
- `status_id` - Defines the status id used in the ORCA Recovery database.
- `error_message` - message displayed on error.
  
- `engine` - The sqlalchemy engine to use for contacting the database.

<a id="post_to_database.handler"></a>

#### handler

```python
@LOGGER.inject_lambda_context
def handler(event: Dict[str, List], context: LambdaContext) -> None
```

Lambda handler. Receives a list of queue entries from an SQS queue,
and posts them to a database.

**Arguments**:

- `event` - A dict with the following keys:
- `'Records'` _List_ - A list of dicts with the following keys:
  'messageId' (str)
  'receiptHandle' (str)
- `'body'` _str_ - A json string representing a dict.
  See files in schemas for details.
  'attributes' (Dict)
- `'messageAttributes'` _Dict_ - A dict with the following keys
  defined in the functions that write to queue.
- `'RequestMethod'` _str_ - Matches to a shared_recovery.RequestMethod.
- `context` - This object provides information about the lambda invocation, function,
  and execution env.
  Environment Vars:
  DB_CONNECT_INFO_SECRET_ARN (string):
  Secret ARN of the AWS secretsmanager secret for connecting to the database.
  See shared_db.py's get_configuration for further details.

