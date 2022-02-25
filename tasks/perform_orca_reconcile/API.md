# Table of Contents

* [perform\_orca\_reconcile](#perform_orca_reconcile)
  * [task](#perform_orca_reconcile.task)
  * [generate\_reports](#perform_orca_reconcile.generate_reports)
  * [generate\_phantom\_reports\_sql](#perform_orca_reconcile.generate_phantom_reports_sql)
  * [generate\_orphan\_reports\_sql](#perform_orca_reconcile.generate_orphan_reports_sql)
  * [generate\_mismatch\_reports](#perform_orca_reconcile.generate_mismatch_reports)
  * [get\_mismatches\_sql](#perform_orca_reconcile.get_mismatches_sql)
  * [insert\_mismatch\_sql](#perform_orca_reconcile.insert_mismatch_sql)
  * [handler](#perform_orca_reconcile.handler)

<a id="perform_orca_reconcile"></a>

# perform\_orca\_reconcile

Name: perform_orca_reconcile.py

Description: Compares entries in reconcile_s3_objects to the Orca catalog,
writing differences to reconcile_catalog_mismatch_report, reconcile_orphan_report, and reconcile_phantom_report.

<a id="perform_orca_reconcile.task"></a>

#### task

```python
def task(job_id: int, orca_archive_location: str, db_connect_info: Dict) -> Dict[str, Any]
```

Reads the record to find the location of manifest.json, then uses that information to spawn of business logic
for pulling manifest's data into sql.

**Arguments**:

- `job_id` - The id of the job containing s3 inventory info.
- `orca_archive_location` - The name of the glacier bucket the job targets.
- `db_connect_info` - See shared_db.py's get_configuration for further details.
- `Returns` - See output.json for details.

<a id="perform_orca_reconcile.generate_reports"></a>

#### generate\_reports

```python
@shared_db.retry_operational_error()
def generate_reports(job_id: int, orca_archive_location: str, engine: Engine) -> None
```

Generates and posts phantom, orphan, and mismatch reports within the same transaction.

**Arguments**:

- `job_id` - The id of the job containing s3 inventory info.
- `orca_archive_location` - The name of the bucket to generate the reports for.
- `engine` - The sqlalchemy engine to use for contacting the database.

<a id="perform_orca_reconcile.generate_phantom_reports_sql"></a>

#### generate\_phantom\_reports\_sql

```python
def generate_phantom_reports_sql(partition_name: str) -> TextClause
```

SQL for generating reports on files in the Orca catalog, but not S3.

<a id="perform_orca_reconcile.generate_orphan_reports_sql"></a>

#### generate\_orphan\_reports\_sql

```python
def generate_orphan_reports_sql(partition_name: str) -> TextClause
```

SQL for generating reports on files in S3, but not the Orca catalog.

<a id="perform_orca_reconcile.generate_mismatch_reports"></a>

#### generate\_mismatch\_reports

```python
def generate_mismatch_reports(job_id: int, orca_archive_location: str, partition_name: str, connection)
```

Generates and posts phantom, orphan, and mismatch reports within the same transaction.

**Arguments**:

- `job_id` - The id of the job containing s3 inventory info.
- `orca_archive_location` - The name of the bucket to generate the reports for.
- `partition_name` - The name of the partition to retrieve s3 information from.
- `connection` - The sqlalchemy connection to use for contacting the database.

<a id="perform_orca_reconcile.get_mismatches_sql"></a>

#### get\_mismatches\_sql

```python
def get_mismatches_sql(partition_name: str) -> TextClause
```

SQL for retrieving mismatches between entries in S3 and the Orca catalog.

<a id="perform_orca_reconcile.insert_mismatch_sql"></a>

#### insert\_mismatch\_sql

```python
def insert_mismatch_sql() -> TextClause
```

SQL for posting a mismatch to reconcile_catalog_mismatch_report.

<a id="perform_orca_reconcile.handler"></a>

#### handler

```python
def handler(event: Dict[str, Union[str, int]], context) -> Dict[str, Any]
```

Lambda handler. Receives a list of s3 events from an SQS queue, and loads the s3 inventory specified into postgres.

**Arguments**:

- `event` - See input.json for details.
- `context` - An object passed through by AWS. Used for tracking.
  Environment Vars:
  See shared_db.py's get_configuration for further details.
- `Returns` - See output.json for details.

