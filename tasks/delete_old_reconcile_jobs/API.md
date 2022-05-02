# Table of Contents

* [delete\_old\_reconcile\_jobs](#delete_old_reconcile_jobs)
  * [task](#delete_old_reconcile_jobs.task)
  * [get\_jobs\_older\_than\_x\_days](#delete_old_reconcile_jobs.get_jobs_older_than_x_days)
  * [delete\_jobs](#delete_old_reconcile_jobs.delete_jobs)
  * [get\_jobs\_sql](#delete_old_reconcile_jobs.get_jobs_sql)
  * [delete\_job\_sql](#delete_old_reconcile_jobs.delete_job_sql)
  * [retry\_error](#delete_old_reconcile_jobs.retry_error)
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

<a id="delete_old_reconcile_jobs.get_jobs_older_than_x_days"></a>

#### get\_jobs\_older\_than\_x\_days

```python
@shared_db.retry_operational_error()
def get_jobs_older_than_x_days(internal_reconciliation_expiration_days: int,
                               engine: Engine) -> List[int]
```

Gets all jobs older than internal_reconciliation_expiration_days days.

**Arguments**:

- `internal_reconciliation_expiration_days` - Only reports updated before this many days ago will be retrieved.
- `engine` - The sqlalchemy engine to use for contacting the database.
  
- `Returns` - A list of ids for the jobs.

<a id="delete_old_reconcile_jobs.delete_jobs"></a>

#### delete\_jobs

```python
@shared_db.retry_operational_error()
def delete_jobs(job_ids: List[int], engine: Engine) -> None
```

Deletes all records for the given job ids from the database.

**Arguments**:

- `job_ids` - The ids of the jobs containing s3 inventory info.
- `engine` - The sqlalchemy engine to use for contacting the database.

<a id="delete_old_reconcile_jobs.get_jobs_sql"></a>

#### get\_jobs\_sql

```python
def get_jobs_sql() -> TextClause
```

SQL for getting jobs older than a certain date.

<a id="delete_old_reconcile_jobs.delete_job_sql"></a>

#### delete\_job\_sql

```python
def delete_job_sql() -> TextClause
```

SQL for deleting all jobs in a given range.

<a id="delete_old_reconcile_jobs.retry_error"></a>

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

