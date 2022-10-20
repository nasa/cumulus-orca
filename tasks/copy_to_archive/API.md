# Table of Contents

* [copy\_to\_archive](#copy_to_archive)
  * [should\_exclude\_files\_type](#copy_to_archive.should_exclude_files_type)
  * [copy\_granule\_between\_buckets](#copy_to_archive.copy_granule_between_buckets)
  * [task](#copy_to_archive.task)
  * [get\_destination\_bucket\_name](#copy_to_archive.get_destination_bucket_name)
  * [get\_storage\_class](#copy_to_archive.get_storage_class)
  * [handler](#copy_to_archive.handler)
* [sqs\_library](#sqs_library)
  * [retry\_error](#sqs_library.retry_error)
  * [get\_aws\_region](#sqs_library.get_aws_region)
  * [post\_to\_metadata\_queue](#sqs_library.post_to_metadata_queue)

<a id="copy_to_archive"></a>

# copy\_to\_archive

Name: copy_to_archive.py
Description: Lambda function that takes a Cumulus message, extracts a list of files,
and copies those files from their current storage location into a staging/archive location.

<a id="copy_to_archive.should_exclude_files_type"></a>

#### should\_exclude\_files\_type

```python
def should_exclude_files_type(file_key: str,
                              exclude_file_types: List[str]) -> bool
```

Tests whether file is included in {excludedFileExtensions}.

**Arguments**:

- `file_key` - The key of the file within the s3 bucket.
- `exclude_file_types` - List of extensions to exclude in the backup.

**Returns**:

  True if file should be excluded from copy, False otherwise.

<a id="copy_to_archive.copy_granule_between_buckets"></a>

#### copy\_granule\_between\_buckets

```python
def copy_granule_between_buckets(source_bucket_name: str, source_key: str,
                                 destination_bucket: str, destination_key: str,
                                 multipart_chunksize_mb: int,
                                 storage_class: str) -> Dict[str, str]
```

Copies granule from source bucket to destination.
Also queries the destination_bucket to get additional metadata file info.

**Arguments**:

- `source_bucket_name` - The name of the bucket in which the granule is currently located.
- `source_key` - source Granule path excluding s3://[bucket]/
- `destination_bucket` - The name of the bucket the granule is to be copied to.
- `destination_key` - Destination granule path excluding s3://[bucket]/
- `multipart_chunksize_mb` - The maximum size of chunks to use when copying.
- `storage_class` - The storage class to store in.

**Returns**:

  A dictionary containing all the file metadata needed
  for reconciliation with Cumulus with the following keys:
  "cumulusArchiveLocation" (str):
  Cumulus bucket the file is stored in.
  "orcaArchiveLocation" (str):
  ORCA archive bucket the file object is stored in.
  "keyPath" (str):
  Full AWS key path including file name of the file
  where the file resides in ORCA.
  "sizeInBytes" (str):
  Size of the object in bytes
  "version" (str):
  Latest version of the file in the archive bucket
  "ingestTime" (str):
  Date and time the file was originally ingested into ORCA.
  "etag" (str):
  etag of the file object in the archive bucket.

<a id="copy_to_archive.task"></a>

#### task

```python
def task(event: Dict[str, Union[List[str], Dict]],
         context: object) -> Dict[str, Any]
```

Copies the files in {event}['input']
to the ORCA archive bucket defined in ORCA_DEFAULT_BUCKET.

Environment Variables:
ORCA_DEFAULT_BUCKET (string, required):
Name of the default archive bucket.
Overridden by bucket specified in config.
DEFAULT_MULTIPART_CHUNKSIZE_MB (int, optional):
The default maximum size of chunks to use when copying.
Can be overridden by collection config.
METADATA_DB_QUEUE_URL (string, required):
SQS URL of the metadata queue.

**Arguments**:

- `event` - Passed through from {handler}
- `context` - An object required by AWS Lambda. Unused.
  

**Returns**:

  A dict representing input and copied files. See schemas/output.json for more information.

<a id="copy_to_archive.get_destination_bucket_name"></a>

#### get\_destination\_bucket\_name

```python
def get_destination_bucket_name(config: Dict[str, Any]) -> str
```

Returns the bucket to copy to.
Uses the collection value in config if present,
otherwise the default.

Environment Vars:
ORCA_DEFAULT_BUCKET (str): Name of the default archive
bucket files should be
archived to.

**Arguments**:

- `config` - See schemas/config.json for more information.
  

**Returns**:

  The name of the bucket to use.

<a id="copy_to_archive.get_storage_class"></a>

#### get\_storage\_class

```python
def get_storage_class(config: Dict[str, Any]) -> str
```

Returns the storage class to use on ingest.
Uses the collection value in config if present,
otherwise the default.

Environment Vars:
DEFAULT_STORAGE_CLASS (str):
The class of storage to use when ingesting files.
Can be overridden by collection config.
Must match value in storage_class table.

**Arguments**:

- `config` - See schemas/config.json for more information.
  

**Returns**:

  The name of the storage class to use.

<a id="copy_to_archive.handler"></a>

#### handler

```python
def handler(event: Dict[str, Union[List[str], Dict]], context: object) -> Any
```

Lambda handler. Runs a cumulus task that
Copies the files in {event}['input']
to the default ORCA bucket. Environment variables must be set to
provide a default ORCA bucket to store the files in.

Environment Vars:
DEFAULT_MULTIPART_CHUNKSIZE_MB (int):
The default maximum size of chunks to use when copying.
Can be overridden by collection config.
DEFAULT_STORAGE_CLASS (str):
The class of storage to use when ingesting files.
Can be overridden by collection config.
Must match value in storage_class table.
ORCA_DEFAULT_BUCKET (str):
Name of the default
archive bucket that files should be archived to.
METADATA_DB_QUEUE_URL (string, required): SQS URL of the metadata queue.

**Arguments**:

- `event` - Event passed into the step from the aws workflow.
  See schemas/input.json and schemas/config.json for more information.
  
  
- `context` - An object required by AWS Lambda. Unused.
  

**Returns**:

  The result of the cumulus task. See schemas/output.json for more information.

<a id="sqs_library"></a>

# sqs\_library

Name: sqs_library.py
Description: library for copy_to_archive lambda function for posting to metadata SQS queue.

<a id="sqs_library.retry_error"></a>

#### retry\_error

```python
def retry_error(
    max_retries: int = MAX_RETRIES,
    backoff_in_seconds: int = INITIAL_BACKOFF_IN_SECONDS,
    backoff_factor: int = BACKOFF_FACTOR
) -> Callable[[Callable[[], RT]], Callable[[], RT]]
```

Decorator takes arguments to adjust number of retries and backoff strategy.

**Arguments**:

- `max_retries` _int_ - number of times to retry in case of failure.
- `backoff_in_seconds` _int_ - Number of seconds to sleep the first time through.
- `backoff_factor` _int_ - Value of the factor used for backoff.

<a id="sqs_library.get_aws_region"></a>

#### get\_aws\_region

```python
def get_aws_region() -> str
```

Gets AWS region variable from the runtime environment variable.

**Returns**:

  The AWS region variable.

**Raises**:

- `Exception` - Thrown if AWS region is empty or None.

<a id="sqs_library.post_to_metadata_queue"></a>

#### post\_to\_metadata\_queue

```python
@retry_error()
def post_to_metadata_queue(sqs_body: Dict[str, Any],
                           metadata_queue_url: str) -> None
```

Posts metadata information to the metadata SQS queue.

**Arguments**:

- `sqs_body` - A dictionary containing the metadata objects that will be sent to SQS.
- `metadata_queue_url` - The metadata SQS queue URL defined by AWS.

**Raises**:

  None

