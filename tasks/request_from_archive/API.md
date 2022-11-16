# Table of Contents

* [request\_from\_archive](#request_from_archive)
  * [RestoreRequestError](#request_from_archive.RestoreRequestError)
  * [task](#request_from_archive.task)
  * [get\_archive\_recovery\_type](#request_from_archive.get_archive_recovery_type)
  * [inner\_task](#request_from_archive.inner_task)
  * [process\_granule](#request_from_archive.process_granule)
  * [get\_s3\_object\_information](#request_from_archive.get_s3_object_information)
  * [restore\_object](#request_from_archive.restore_object)
  * [post\_to\_archive\_queue](#request_from_archive.post_to_archive_queue)
  * [set\_optional\_event\_property](#request_from_archive.set_optional_event_property)
  * [handler](#request_from_archive.handler)

<a id="request_from_archive"></a>

# request\_from\_archive

Name: request_from_archive.py
Description:  Lambda function that makes a restore request from archive bucket for each input file.

<a id="request_from_archive.RestoreRequestError"></a>

## RestoreRequestError Objects

```python
class RestoreRequestError(Exception)
```

Exception to be raised if the restore request fails submission for any of the files.

<a id="request_from_archive.task"></a>

#### task

```python
def task(event: Dict) -> Dict[str, Any]
```

Pulls information from os.environ, utilizing defaults if needed,
then calls inner_task.

**Arguments**:

  Note that because we are using CumulusMessageAdapter,
  this may not directly correspond to Lambda input.
- `event` - A dict with the following keys:
- `'config'` _dict_ - See schemas/config.json for details.
- `'input'` _dict_ - See schemas/input.json for details.
  Environment Vars:
  See docs in handler for details.

**Returns**:

  See schemas/output.json for details.

**Raises**:

- `RestoreRequestError` - Thrown if there are errors with the input request.

<a id="request_from_archive.get_archive_recovery_type"></a>

#### get\_archive\_recovery\_type

```python
def get_archive_recovery_type(config: Dict[str, Any]) -> str
```

Returns the archive recovery type from either config or environment variable.
Must be either 'Bulk', 'Expedited', or 'Standard'.

**Arguments**:

- `config` - The config dictionary from lambda event.
  

**Raises**:

  KeyError if recovery type is not set.
  ValueError if recovery type value is invalid.

<a id="request_from_archive.inner_task"></a>

#### inner\_task

```python
def inner_task(event: Dict, max_retries: int, retry_sleep_secs: float,
               recovery_type: str, restore_expire_days: int,
               status_update_queue_url: str) -> Dict[str, Any]
```

Task called by the handler to perform the work.
This task will call the restore_request for each file. Restored files will be kept
for {exp_days} days before they expire. A restore request will be tried up to {retries} times
if it fails, waiting {retry_sleep_secs} between each attempt.

**Arguments**:

  Note that because we are using CumulusMessageAdapter,
  this may not directly correspond to Lambda input.
- `event` - A dict with the following keys:
- `'config'` _dict_ - A dict with the following keys:
- `'defaultBucketOverride'` _str_ - The name of the archive bucket
  from which the files will be restored.
- `'asyncOperationId'` _str_ - The unique identifier used for tracking requests.
- `'input'` _dict_ - A dict with the following keys:
  'granules' (list(dict)): A list of dicts with the following keys:
- `'granuleId'` _str_ - The id of the granule being restored.
  'keys' (list(dict)): A list of dicts with the following keys:
- `'key'` _str_ - Key to the file within the granule.
- `'destBucket'` _str_ - The bucket the restored file will be moved
  to after the restore completes.
- `max_retries` - The maximum number of retries for network operations.
- `retry_sleep_secs` - The number of time to sleep between retries.
- `recovery_type` - The Tier for the restore request.
  Valid values are 'Standard'|'Bulk'|'Expedited'.
- `restore_expire_days` - The number of days the restored file will be accessible
  in the S3 bucket before it expires.
- `status_update_queue_url` - The URL of the SQS queue to post status to.

**Returns**:

  See schemas/output.json

**Raises**:

- `RestoreRequestError` - Thrown if there are errors with the input request.

<a id="request_from_archive.process_granule"></a>

#### process\_granule

```python
def process_granule(s3: BaseClient, granule: Dict[str, Union[str, List[Dict]]],
                    archive_bucket_name: str, restore_expire_days: int,
                    max_retries: int, retry_sleep_secs: float,
                    recovery_type: str, job_id: str,
                    status_update_queue_url: str) -> None
```

Call restore_object for the files in the granule_list. Modifies granule for output.

**Arguments**:

- `s3` - An instance of boto3 s3 client
- `granule` - A dict with the following keys:
- `'granuleId'` _str_ - The id of the granule being restored.
  'recover_files' (list(dict)): A list of dicts with the following keys:
- `'keyPath'` _str_ - Key to the file within the granule.
- `'success'` _bool_ - Should enter this method set to False.
  Modified to 'True' by method end.
- `'errorMessage'` _str_ - Will be modified if error occurs.
  
  
- `archive_bucket_name` - The S3 archive bucket name.
  restore_expire_days:
  The number of days the restored file will be accessible in the S3 bucket
  before it expires.
- `max_retries` - The number of attempts to retry a restore_request that failed to submit.
- `retry_sleep_secs` - The number of seconds to sleep between retry attempts.
- `recovery_type` - The Tier for the restore request. Valid values are
  'Standard'|'Bulk'|'Expedited'.
- `job_id` - The unique identifier used for tracking requests.
- `status_update_queue_url` - The URL of the SQS queue to post status to.
  
- `Raises` - RestoreRequestError if any file restore could not be initiated.

<a id="request_from_archive.get_s3_object_information"></a>

#### get\_s3\_object\_information

```python
def get_s3_object_information(s3_cli: BaseClient, archive_bucket_name: str,
                              file_key: str) -> Optional[Dict[str, Any]]
```

Perform a head request to get information about a file in S3.

**Arguments**:

- `s3_cli` - An instance of boto3 s3 client
- `archive_bucket_name` - The S3 bucket name
- `file_key` - The key of the archived object

**Returns**:

  None if the object does not exist.
  Otherwise, the dictionary specified in
  https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3
  .Client.head_object

<a id="request_from_archive.restore_object"></a>

#### restore\_object

```python
def restore_object(s3_cli: BaseClient, key: str, days: int,
                   db_archive_bucket_key: str, attempt: int, job_id: str,
                   recovery_type: str) -> None
```

Restore an archived S3 object in an Amazon S3 bucket.
Posts to archive recovery queue if object is already recovered from archive bucket.

**Arguments**:

- `s3_cli` - An instance of boto3 s3 client.
- `key` - The key of the archived object being restored.
- `days` - How many days the restored file will be accessible in the
  S3 bucket before it expires.
- `db_archive_bucket_key` - The S3 bucket name.
- `attempt` - The attempt number for logging purposes.
- `job_id` - The unique id of the job. Used for logging.
- `recovery_type` - Valid values are
  'Standard'|'Bulk'|'Expedited'.

**Raises**:

  None

<a id="request_from_archive.post_to_archive_queue"></a>

#### post\_to\_archive\_queue

```python
def post_to_archive_queue(archive_recovery_queue_url: str, key,
                          bucket_name: str) -> None
```

Posts to archive SQS queue with the correct message format.

**Arguments**:

- `archive_recovery_queue_url` - URL of archive SQS.
- `key` - file name to recover.
- `bucket_name` - name of archvie bucket.

**Returns**:

  None

<a id="request_from_archive.set_optional_event_property"></a>

#### set\_optional\_event\_property

```python
def set_optional_event_property(event: Dict[str,
                                            Any], target_path_cursor: Dict,
                                target_path_segments: List) -> None
```

Sets the optional variable value from event if present, otherwise sets to None.

**Arguments**:

- `event` - See schemas/input.json.
- `target_path_cursor` - Cursor of the current section to check.
- `target_path_segments` - The path to the current cursor.

**Returns**:

  None

<a id="request_from_archive.handler"></a>

#### handler

```python
@LOGGER.inject_lambda_context
def handler(event: Dict[str, Any], context: LambdaContext)
```

Lambda handler. Initiates a restore_object request from archive for each file of a granule.
Note that this function is set up to accept a list of granules, (because Cumulus sends a list),
but at this time, only 1 granule will be accepted.
This is due to the error handling. If the restore request for any file for a
granule fails to submit, the entire granule (workflow) fails. If more than one granule were
accepted, and a failure occurred, at present, it would fail all of them.
Environment variables can be set to override how many days to keep the restored files, how
many times to retry a restore_request, and how long to wait between retries.
Environment Vars:
RESTORE_EXPIRE_DAYS (int, optional, default = 5): The number of days
the restored file will be accessible in the S3 bucket before it expires.
RESTORE_REQUEST_RETRIES (int, optional, default = 3): The number of
attempts to retry a restore_request that failed to submit.
RESTORE_RETRY_SLEEP_SECS (int, optional, default = 0): The number of seconds
to sleep between retry attempts.
RESTORE_RECOVERY_TYPE (str, optional, default = 'Standard'): the Tier
for the restore request. Valid values are 'Standard'|'Bulk'|'Expedited'.
STATUS_UPDATE_QUEUE_URL
The URL of the SQS queue to post status to.
ORCA_DEFAULT_BUCKET
The bucket to use if destBucket is not set.

**Arguments**:

- `event` - See schemas/input.json.
- `context` - This object provides information about the lambda invocation, function,
  and execution env.

**Returns**:

  A dict matching schemas/output.json

**Raises**:

- `RestoreRequestError` - An error occurred calling restore_object for one or more files.
  The same dict that is returned for a successful granule restore,
  will be included in the message, with 'success' = False for
  the files for which the restore request failed to submit.

