# Table of Contents

* [get\_current\_archive\_list](#get_current_archive_list)
  * [task](#get_current_archive_list.task)
  * [get\_manifest](#get_current_archive_list.get_manifest)
  * [create\_job](#get_current_archive_list.create_job)
  * [truncate\_s3\_partition](#get_current_archive_list.truncate_s3_partition)
  * [update\_job\_with\_s3\_inventory\_in\_postgres](#get_current_archive_list.update_job_with_s3_inventory_in_postgres)
  * [add\_metadata\_to\_gzip](#get_current_archive_list.add_metadata_to_gzip)
  * [generate\_temporary\_s3\_column\_list](#get_current_archive_list.generate_temporary_s3_column_list)
  * [create\_temporary\_table\_sql](#get_current_archive_list.create_temporary_table_sql)
  * [trigger\_csv\_load\_from\_s3\_sql](#get_current_archive_list.trigger_csv_load_from_s3_sql)
  * [translate\_s3\_import\_to\_partitioned\_data\_sql](#get_current_archive_list.translate_s3_import_to_partitioned_data_sql)
  * [get\_s3\_credentials\_from\_secrets\_manager](#get_current_archive_list.get_s3_credentials_from_secrets_manager)
  * [MessageData](#get_current_archive_list.MessageData)
  * [get\_message\_from\_queue](#get_current_archive_list.get_message_from_queue)
  * [check\_env\_variable](#get_current_archive_list.check_env_variable)
  * [handler](#get_current_archive_list.handler)

<a id="get_current_archive_list"></a>

# get\_current\_archive\_list

Name: get_current_archive_list.py

Description: Receives a list of s3 events from an SQS queue, and loads the s3 inventory specified into postgres.

<a id="get_current_archive_list.task"></a>

#### task

```python
def task(report_bucket_region: str, report_bucket_name: str, manifest_key: str,
         s3_access_key: str, s3_secret_key: str,
         db_connect_info: Dict) -> Dict[str, Any]
```

Reads the record to find the location of manifest.json, then uses that information to spawn of business logic
for pulling manifest's data into sql.

**Arguments**:

- `report_bucket_region` - The region the report bucket resides in.
- `report_bucket_name` - The name of the report bucket.
- `manifest_key` - The key/path to the manifest within the report bucket.
- `s3_access_key` - The access key that, when paired with s3_secret_key, allows postgres to access s3.
- `s3_secret_key` - The secret key that, when paired with s3_access_key, allows postgres to access s3.
- `db_connect_info` - See shared_db.py's get_configuration for further details.
  
- `Returns` - See output.json for details.

<a id="get_current_archive_list.get_manifest"></a>

#### get\_manifest

```python
def get_manifest(manifest_key_path: str, report_bucket_name: str,
                 report_bucket_region: str) -> Dict[str, Any]
```

**Arguments**:

- `manifest_key_path` - The full path within the s3 bucket to the manifest.
- `report_bucket_name` - The name of the bucket the manifest is located in.
- `report_bucket_region` - The name of the region the report bucket resides in.
  
- `Returns` - The key of the csv specified in the manifest.

<a id="get_current_archive_list.create_job"></a>

#### create\_job

```python
@shared_db.retry_operational_error()
def create_job(orca_archive_location: str, inventory_creation_time: datetime,
               engine: Engine) -> int
```

Creates the initial status entry for a job.

**Arguments**:

- `orca_archive_location` - The name of the bucket to generate the reports for.
- `inventory_creation_time` - The time the s3 Inventory report was created.
- `engine` - The sqlalchemy engine to use for contacting the database.
  
- `Returns` - The auto-incremented job_id from the database.

<a id="get_current_archive_list.truncate_s3_partition"></a>

#### truncate\_s3\_partition

```python
@shared_db.retry_operational_error()
def truncate_s3_partition(orca_archive_location: str, engine: Engine) -> None
```

Truncates the partition for the given orca_archive_location, removing its data.

**Arguments**:

- `orca_archive_location` - The name of the bucket to generate the reports for.
- `engine` - The sqlalchemy engine to use for contacting the database.

<a id="get_current_archive_list.update_job_with_s3_inventory_in_postgres"></a>

#### update\_job\_with\_s3\_inventory\_in\_postgres

```python
@shared_db.retry_operational_error()
def update_job_with_s3_inventory_in_postgres(s3_access_key: str,
                                             s3_secret_key: str,
                                             report_bucket_name: str,
                                             report_bucket_region: str,
                                             csv_key_paths: List[str],
                                             manifest_file_schema: str,
                                             job_id: int,
                                             engine: Engine) -> None
```

Constructs a temporary table capable of holding full data from s3 inventory report, triggers load into that table,
then moves that data into the proper partition.

**Arguments**:

- `s3_access_key` - The access key that, when paired with s3_secret_key, allows postgres to access s3.
- `s3_secret_key` - The secret key that, when paired with s3_access_key, allows postgres to access s3.
- `report_bucket_name` - The name of the bucket the csv is located in.
- `report_bucket_region` - The name of the region the report bucket resides in.
- `csv_key_paths` - The paths of the csvs within the report bucket.
- `manifest_file_schema` - The string representing columns present in the csv.
- `job_id` - The id of the job to associate info with.
- `engine` - The sqlalchemy engine to use for contacting the database.

<a id="get_current_archive_list.add_metadata_to_gzip"></a>

#### add\_metadata\_to\_gzip

```python
def add_metadata_to_gzip(report_bucket_name: str, gzip_key_path: str) -> None
```

AWS does not add proper metadata to gzip files, which breaks aws_s3.table_import_from_s3
Must add manually.

**Arguments**:

- `report_bucket_name` - The name of the bucket the csv is located in.
- `gzip_key_path` - The path within the bucket to the gzip file that needs metadata updated.

<a id="get_current_archive_list.generate_temporary_s3_column_list"></a>

#### generate\_temporary\_s3\_column\_list

```python
def generate_temporary_s3_column_list(manifest_file_schema: str) -> str
```

Creates a list of columns that matches the order of columns in the manifest.
Columns used by our database are given standardized names.

**Arguments**:

- `manifest_file_schema` - An ordered CSV representing columns in the CSV the manifest points to.
  
- `Returns` - A string representing SQL columns to create.
  Columns required for import but unused by orca will be filled in with `junk` values.
  For example, 'orca_archive_location text, key_path text, size_in_bytes bigint, last_update timestamptz, etag text, storage_class text, junk7 text, junk8 text, junk9 text, junk10 text, junk11 text, junk12 text, junk13 text, junk14 text'

<a id="get_current_archive_list.create_temporary_table_sql"></a>

#### create\_temporary\_table\_sql

```python
def create_temporary_table_sql(temporary_s3_column_list: str) -> TextClause
```

Creates a temporary table to store inventory data.

**Arguments**:

- `temporary_s3_column_list` - The list of columns that need to be created to store csv data.
  Be very careful to avoid injection.

<a id="get_current_archive_list.trigger_csv_load_from_s3_sql"></a>

#### trigger\_csv\_load\_from\_s3\_sql

```python
def trigger_csv_load_from_s3_sql() -> TextClause
```

SQL for telling postgres where/how to copy in the s3 inventory data.

<a id="get_current_archive_list.translate_s3_import_to_partitioned_data_sql"></a>

#### translate\_s3\_import\_to\_partitioned\_data\_sql

```python
def translate_s3_import_to_partitioned_data_sql() -> TextClause
```

SQL for translating between the temporary table and Orca table.

<a id="get_current_archive_list.get_s3_credentials_from_secrets_manager"></a>

#### get\_s3\_credentials\_from\_secrets\_manager

```python
def get_s3_credentials_from_secrets_manager(
        s3_credentials_secret_arn: str) -> tuple
```

Gets the s3 secret from the given arn and decompiles into two strings.

**Arguments**:

- `s3_credentials_secret_arn` - The arn of the secret containing s3 credentials.
  

**Returns**:

  A tuple consisting of
  (str) An access key
  (str) A secret key

<a id="get_current_archive_list.MessageData"></a>

## MessageData Objects

```python
@dataclass(frozen=True)
class MessageData()
```

Data class that manages the message information needed to perform the task.

Contains:
    report_bucket_region: (str) The region the report bucket resides in
    report_bucket_name: (str) The name of the report bucket
    manifest_key: (str) The key/path to the manifest within the report bucket
    message_receipt: (str) The receipt handle of the message in the queue

<a id="get_current_archive_list.get_message_from_queue"></a>

#### get\_message\_from\_queue

```python
def get_message_from_queue(internal_report_queue_url: str) -> MessageData
```

Gets a message from the queue and formats it into input.json schema.

**Arguments**:

- `internal_report_queue_url` - The url of the queue containing the message.
  

**Returns**:

  A MessageData consisting of the relevant data.

<a id="get_current_archive_list.check_env_variable"></a>

#### check\_env\_variable

```python
def check_env_variable(env_name: str) -> str
```

Checks for the lambda environment variable.

**Arguments**:

- `env_name` _str_ - The environment variable name set in lambda configuration.
  
- `Raises` - KeyError in case the environment variable is not found.

<a id="get_current_archive_list.handler"></a>

#### handler

```python
def handler(event: Dict[str, List], context) -> Dict[str, Any]
```

Lambda handler. Receives a list of s3 events from an SQS queue, and loads the s3 inventory specified into postgres.

**Arguments**:

- `event` - Unused. Data is pulled in by contacting INTERNAL_REPORT_QUEUE_URL
- `context` - An object passed through by AWS. Used for tracking.
  Environment Vars:
- `INTERNAL_REPORT_QUEUE_URL` _string_ - The URL of the SQS queue the job came from.
- `S3_CREDENTIALS_SECRET_ARN` _string_ - The ARN of the secret containing s3 credentials.
- `DB_CONNECT_INFO_SECRET_ARN` _string_ - Secret ARN of the AWS secretsmanager secret for connecting to the database.
  See shared_db.py's get_configuration for further details.
  
- `Returns` - See output.json for details.

