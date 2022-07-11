# Table of Contents

* [perform\_orca\_reconcile](#perform_orca_reconcile)
  * [task](#perform_orca_reconcile.task)
  * [generate\_reports](#perform_orca_reconcile.generate_reports)
  * [generate\_phantom\_reports\_sql](#perform_orca_reconcile.generate_phantom_reports_sql)
  * [generate\_orphan\_reports\_sql](#perform_orca_reconcile.generate_orphan_reports_sql)
  * [generate\_mismatch\_reports\_sql](#perform_orca_reconcile.generate_mismatch_reports_sql)
  * [retry\_error](#perform_orca_reconcile.retry_error)
  * [remove\_job\_from\_queue](#perform_orca_reconcile.remove_job_from_queue)
  * [handler](#perform_orca_reconcile.handler)

<a id="perform_orca_reconcile"></a>

# perform\_orca\_reconcile

Name: perform_orca_reconcile.py

Description: Compares entries in reconcile_s3_objects to the Orca catalog,
writing differences to reconcile_catalog_mismatch_report, reconcile_orphan_report, and reconcile_phantom_report.

<a id="perform_orca_reconcile.task"></a>

#### task

```python
def task(job_id: int, orca_archive_location: str,
         internal_report_queue_url: str, message_receipt_handle: str,
         db_connect_info: Dict) -> Dict[str, Any]
```

Reads the record to find the location of manifest.json, then uses that information to spawn of business logic
for pulling manifest's data into sql.

**Arguments**:

- `job_id` - The id of the job containing s3 inventory info.
- `orca_archive_location` - The name of the glacier bucket the job targets.
- `internal_report_queue_url` - The url of the queue containing the message.
- `message_receipt_handle` - The ReceiptHandle for the event in the queue.
- `db_connect_info` - See shared_db.py's get_configuration for further details.
- `Returns` - See output.json for details.

<a id="perform_orca_reconcile.generate_reports"></a>

#### generate\_reports

```python
@shared_db.retry_operational_error()
def generate_reports(job_id: int, orca_archive_location: str,
                     engine: Engine) -> None
```

Generates and posts phantom, orphan, and mismatch reports within the same transaction.

**Arguments**:

- `job_id` - The id of the job containing s3 inventory info.
- `orca_archive_location` - The name of the bucket to generate the reports for.
- `engine` - The sqlalchemy engine to use for contacting the database.

<a id="perform_orca_reconcile.generate_phantom_reports_sql"></a>

#### generate\_phantom\_reports\_sql

```python
def generate_phantom_reports_sql() -> text
```

SQL for generating reports on files in the Orca catalog, but not S3.

<a id="perform_orca_reconcile.generate_orphan_reports_sql"></a>

#### generate\_orphan\_reports\_sql

```python
def generate_orphan_reports_sql() -> text
```

SQL for generating reports on files in S3, but not the Orca catalog.

<a id="perform_orca_reconcile.generate_mismatch_reports_sql"></a>

#### generate\_mismatch\_reports\_sql

```python
def generate_mismatch_reports_sql() -> text
```

SQL for retrieving mismatches between entries in S3 and the Orca catalog.

<a id="perform_orca_reconcile.retry_error"></a>

#### retry\_error

```python
def retry_error(max_retries: int = 3,
                backoff_in_seconds: int = 1,
                backoff_factor: int = 2
                ) -> Callable[[Callable[[], RT]], Callable[[], RT]]
```

Decorator takes arguments to adjust number of retries and backoff strategy.

**Arguments**:

- `max_retries` _int_ - number of times to retry in case of failure.
- `backoff_in_seconds` _int_ - Number of seconds to sleep the first time through.
- `backoff_factor` _int_ - Value of the factor used for backoff.

<a id="perform_orca_reconcile.remove_job_from_queue"></a>

#### remove\_job\_from\_queue

```python
@retry_error()
def remove_job_from_queue(internal_report_queue_url: str,
                          message_receipt_handle: str)
```

Removes the completed job from the queue, preventing it from going to the dead-letter queue.

**Arguments**:

- `internal_report_queue_url` - The url of the queue containing the message.
- `message_receipt_handle` - message_receipt_handle: The ReceiptHandle for the event in the queue.

<a id="perform_orca_reconcile.handler"></a>

#### handler

```python
def handler(event: Dict[str, Dict[str, Union[str, int]]],
            context) -> Dict[str, Any]
```

Lambda handler. Receives a list of s3 events from an SQS queue, and loads the s3 inventory specified into postgres.

**Arguments**:

- `event` - See input.json for details.
- `context` - An object passed through by AWS. Used for tracking.
  Environment Vars:
- `INTERNAL_REPORT_QUEUE_URL` _string_ - The URL of the SQS queue the job came from.
- `DB_CONNECT_INFO_SECRET_ARN` _string_ - Secret ARN of the AWS secretsmanager secret for connecting to the database.
  See shared_db.py's get_configuration for further details.
- `Returns` - See output.json for details.
