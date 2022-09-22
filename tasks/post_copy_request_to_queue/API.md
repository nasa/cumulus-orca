# Table of Contents

* [post\_copy\_request\_to\_queue](#post_copy_request_to_queue)
  * [task](#post_copy_request_to_queue.task)
  * [exponential\_delay](#post_copy_request_to_queue.exponential_delay)
  * [query\_db](#post_copy_request_to_queue.query_db)
  * [get\_metadata\_sql](#post_copy_request_to_queue.get_metadata_sql)
  * [handler](#post_copy_request_to_queue.handler)

<a id="post_copy_request_to_queue"></a>

# post\_copy\_request\_to\_queue

Name: post_copy_request_to_queue.py
Description:  lambda function that queries the db for file metadata, updates the status
of recovered file to staged,
and sends the staged file info to staged_recovery queue for further processing.

<a id="post_copy_request_to_queue.task"></a>

#### task

```python
def task(key_path: str, bucket_name: str, status_update_queue_url: str,
         recovery_queue_url: str, max_retries: int, retry_sleep_secs: int,
         retry_backoff: int, db_connect_info_secret_arn: str) -> None
```

Task called by the handler to perform the work.
This task queries all entries from orca_recoverfile table
that match the given filename and whose status_id is 'PENDING'.
The result is then sent to the staged-recovery-queue SQS and status-update-queue SQS.

**Arguments**:

  key_path:
  Full AWS key path including file name of the file where the file resides.
- `bucket_name` - Name of the source S3 bucket.
- `status_update_queue_url` - The SQS URL of status_update_queue
- `recovery_queue_url` - The SQS URL of staged_recovery_queue
- `max_retries` - Number of times the code will retry in case of failure.
- `retry_sleep_secs` - Number of seconds to wait between recovery failure retries.
- `retry_backoff` - The multiplier by which the retry interval increases during each attempt.
- `db_connect_info_secret_arn` - Secret ARN of the secretsmanager secret to connect to the DB.

**Returns**:

  None

**Raises**:

- `Exception` - If unable to retrieve key_path or db parameters, convert db result to json,
  or post to queue.

<a id="post_copy_request_to_queue.exponential_delay"></a>

#### exponential\_delay

```python
def exponential_delay(base_delay: int, exponential_backoff: int = 2) -> int
```

Exponential delay function. This function is used for retries during failure.

**Arguments**:

- `base_delay` - Number of seconds to wait between recovery failure retries.
- `exponential_backoff` - The multiplier by which the retry interval increases during each attempt.

**Returns**:

  An integer which is multiplication of base_delay and exponential_backoff.

**Raises**:

  None

<a id="post_copy_request_to_queue.query_db"></a>

#### query\_db

```python
@retry_operational_error()
def query_db(key_path: str, bucket_name: str,
             db_connect_info_secret_arn: str) -> List[Dict[str, str]]
```

Connect and query the recover_file status table return needed metadata for posting to the recovery status SQS Queue.

**Arguments**:

  key_path:
  Full AWS key path including file name of the file where the file resides.
- `bucket_name` - Name of the source S3 bucket.
- `db_connect_info_secret_arn` - Secret ARN of the secretsmanager secret to connect to the DB.

**Returns**:

  A list of dict containing the following keys, matching the input format from copy_from_archive:
  "jobId" (str):
  "granuleId"(str):
  "filename" (str):
  "restoreDestination" (str):
  "s3MultipartChunksizeMb" (str):
  "sourceKey" (str):
  "targetKey" (str):
  "sourceBucket" (str):

**Raises**:

- `Exception` - If unable to retrieve the metadata by querying the DB.

<a id="post_copy_request_to_queue.get_metadata_sql"></a>

#### get\_metadata\_sql

```python
def get_metadata_sql(key_path: str) -> text
```

Query for finding metadata based on key_path and PENDING status.

**Arguments**:

- `key_path` _str_ - s3 key for the file less the bucket name

**Returns**:

- `(sqlalchemy.text)` - SQL statement

<a id="post_copy_request_to_queue.handler"></a>

#### handler

```python
def handler(event: Dict[str, Any], context) -> None
```

Lambda handler. This lambda calls the task function to perform db queries
and send message to SQS.

Environment Vars:
RECOVERY_QUEUE_URL (string): the SQS URL for staged_recovery_queue
DB_QUEUE_URL (string): the SQS URL for status-update-queue
MAX_RETRIES (string): Number of times the code will retry in case of failure.
RETRY_SLEEP_SECS (string): Number of seconds to wait between recovery failure retries.
RETRY_BACKOFF (string): The multiplier by which the retry interval increases during each attempt.
DB_CONNECT_INFO_SECRET_ARN (string): Secret ARN of the AWS secretsmanager secret for connecting to the database.

**Arguments**:

  event:
  A dictionary from the S3 bucket. See schemas/input.json for more information.
- `context` - An object required by AWS Lambda. Unused.

**Returns**:

  None

**Raises**:

- `Exception` - If unable to retrieve the SQS URLs or exponential retry fields from env variables.

