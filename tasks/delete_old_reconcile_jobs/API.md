# Table of Contents

* [delete\_old\_reconcile\_jobs](#delete_old_reconcile_jobs)
  * [task](#delete_old_reconcile_jobs.task)
  * [delete\_jobs\_older\_than\_x\_days](#delete_old_reconcile_jobs.delete_jobs_older_than_x_days)
  * [delete\_catalog\_mismatches\_older\_than\_x\_days\_sql](#delete_old_reconcile_jobs.delete_catalog_mismatches_older_than_x_days_sql)
  * [delete\_catalog\_orphans\_older\_than\_x\_days\_sql](#delete_old_reconcile_jobs.delete_catalog_orphans_older_than_x_days_sql)
  * [delete\_catalog\_phantoms\_older\_than\_x\_days\_sql](#delete_old_reconcile_jobs.delete_catalog_phantoms_older_than_x_days_sql)
  * [delete\_catalog\_s3\_objects\_older\_than\_x\_days\_sql](#delete_old_reconcile_jobs.delete_catalog_s3_objects_older_than_x_days_sql)
  * [delete\_jobs\_older\_than\_x\_days\_sql](#delete_old_reconcile_jobs.delete_jobs_older_than_x_days_sql)
  * [handler](#delete_old_reconcile_jobs.handler)

<a id="delete_old_reconcile_jobs"></a>

# delete\_old\_reconcile\_jobs

Name: delete_old_reconcile_jobs.py

Description: Deletes old internal reconciliation reports, reducing DB size.

<a id="delete_old_reconcile_jobs.task"></a>

#### task

```python
def task(internal_reconciliation_expiration_days: int,
         db_connect_info: Dict) -> None
```

Gets all jobs older than internal_reconciliation_expiration_days days, then deletes their records in Postgres.

**Arguments**:

- `internal_reconciliation_expiration_days` - Only reports updated before this many days ago will be deleted.
- `db_connect_info` - See shared_db.py's get_configuration for further details.

<a id="delete_old_reconcile_jobs.delete_jobs_older_than_x_days"></a>

#### delete\_jobs\_older\_than\_x\_days

```python
@shared_db.retry_operational_error()
def delete_jobs_older_than_x_days(internal_reconciliation_expiration_days: int,
                                  engine: Engine) -> None
```

Deletes all records for the given job older than internal_reconciliation_expiration_days days.

**Arguments**:

- `internal_reconciliation_expiration_days` - Only reports updated before this many days ago will be retrieved.
- `engine` - The sqlalchemy engine to use for contacting the database.

<a id="delete_old_reconcile_jobs.delete_catalog_mismatches_older_than_x_days_sql"></a>

#### delete\_catalog\_mismatches\_older\_than\_x\_days\_sql

```python
def delete_catalog_mismatches_older_than_x_days_sql() -> text
```

SQL for deleting from reconcile_catalog_mismatch_report entries older than a certain date.

<a id="delete_old_reconcile_jobs.delete_catalog_orphans_older_than_x_days_sql"></a>

#### delete\_catalog\_orphans\_older\_than\_x\_days\_sql

```python
def delete_catalog_orphans_older_than_x_days_sql() -> text
```

SQL for deleting from reconcile_orphan_report entries older than a certain date.

<a id="delete_old_reconcile_jobs.delete_catalog_phantoms_older_than_x_days_sql"></a>

#### delete\_catalog\_phantoms\_older\_than\_x\_days\_sql

```python
def delete_catalog_phantoms_older_than_x_days_sql() -> text
```

SQL for deleting from reconcile_phantom_report entries older than a certain date.

<a id="delete_old_reconcile_jobs.delete_catalog_s3_objects_older_than_x_days_sql"></a>

#### delete\_catalog\_s3\_objects\_older\_than\_x\_days\_sql

```python
def delete_catalog_s3_objects_older_than_x_days_sql() -> text
```

SQL for deleting from reconcile_s3_object entries older than a certain date.

<a id="delete_old_reconcile_jobs.delete_jobs_older_than_x_days_sql"></a>

#### delete\_jobs\_older\_than\_x\_days\_sql

```python
def delete_jobs_older_than_x_days_sql() -> text
```

SQL for deleting from reconcile_job entries older than a certain date.

<a id="delete_old_reconcile_jobs.handler"></a>

#### handler

```python
def handler(event: Dict[str, Dict[str, Dict[str, Union[str, int]]]],
            context) -> None
```

Lambda handler. Deletes old internal reconciliation reports, reducing DB size.

**Arguments**:

- `event` - An object passed through by AWS. Unused.
- `context` - An object passed through by AWS. Used for tracking.
  Environment Vars:
- `DB_CONNECT_INFO_SECRET_ARN` _string_ - Secret ARN of the AWS secretsmanager secret for connecting to the database.
  See shared_db.py's get_configuration for further details.
- `INTERNAL_RECONCILIATION_EXPIRATION_DAYS` _int_ - Only reports updated before this many days ago will be deleted.

