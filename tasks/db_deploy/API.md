# Table of Contents

* [db\_deploy](#db_deploy)
  * [handler](#db_deploy.handler)
  * [task](#db_deploy.task)
  * [app\_db\_exists](#db_deploy.app_db_exists)
  * [app\_schema\_exists](#db_deploy.app_schema_exists)
  * [app\_version\_table\_exists](#db_deploy.app_version_table_exists)
  * [get\_migration\_version](#db_deploy.get_migration_version)

<a name="db_deploy"></a>
# db\_deploy

Name: db_deploy.py

Description: Performs database installation and migration for the ORCA schema.

<a name="db_deploy.handler"></a>
#### handler

```python
handler(event: Dict[str, Any], context: object) -> None
```

Lambda handler for db_deploy. The handler generates the database connection
configuration information, sets logging handler information and calls the
Lambda task function. See the `shared_db.get_configuration()` function for
information on the needed environment variables and parameter store names
required by this Lambda.

**Arguments**:

- `event` _Dict_ - Event dictionary passed by AWS.
- `context` _object_ - An object required by AWS Lambda.
  

**Raises**:

- `Exception` - If environment or secrets are unavailable.

<a name="db_deploy.task"></a>
#### task

```python
task(config: Dict[str, str]) -> None
```

Checks for the ORCA database and throws an error if it does not exist.
Determines if a fresh install or a migration is needed for the ORCA
schema.

**Arguments**:

- `config` _Dict_ - Dictionary of connection information.
  

**Raises**:

- `Exception` - If database does not exist.

<a name="db_deploy.app_db_exists"></a>
#### app\_db\_exists

```python
@retry_operational_error(MAX_RETRIES)
app_db_exists(connection: Connection, db_name: str) -> bool
```

Checks to see if the ORCA application database exists.

**Arguments**:

- `connection` _sqlalchemy.future.Connection_ - Database connection object.
- `db_name` - The name of the Orca database within the RDS cluster.
  

**Returns**:

- `True/False` _bool_ - True if database exists.

<a name="db_deploy.app_schema_exists"></a>
#### app\_schema\_exists

```python
app_schema_exists(connection: Connection) -> bool
```

Checks to see if the ORCA application schema exists.

**Arguments**:

- `connection` _sqlalchemy.future.Connection_ - Database connection object.
  

**Returns**:

- `True/False` _bool_ - True if ORCA schema exists.

<a name="db_deploy.app_version_table_exists"></a>
#### app\_version\_table\_exists

```python
app_version_table_exists(connection: Connection) -> bool
```

Checks to see if the orca.schema_version table exists.

**Arguments**:

- `connection` _sqlalchemy.future.Connection_ - Database connection object.
  

**Returns**:

- `True/False` _bool_ - True if ORCA schema_version table exists.

<a name="db_deploy.get_migration_version"></a>
#### get\_migration\_version

```python
get_migration_version(connection: Connection) -> int
```

Queries the database version table and returns the latest version.

**Arguments**:

- `connection` _sqlalchemy.future.Connection_ - Database connection object.
  

**Returns**:

  Schema Version (int): Version number of the currently installed ORCA schema

