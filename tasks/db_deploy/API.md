# Table of Contents

* [db\_deploy](#db_deploy)
  * [handler](#db_deploy.handler)
  * [task](#db_deploy.task)
  * [app\_db\_exists](#db_deploy.app_db_exists)
  * [app\_schema\_exists](#db_deploy.app_schema_exists)
  * [app\_version\_table\_exists](#db_deploy.app_version_table_exists)
  * [get\_migration\_version](#db_deploy.get_migration_version)
* [install/create\_db](#install/create_db)
  * [create\_fresh\_orca\_install](#install/create_db.create_fresh_orca_install)
  * [create\_database](#install/create_db.create_database)
  * [create\_app\_schema\_role\_users](#install/create_db.create_app_schema_role_users)
  * [set\_search\_path\_and\_role](#install/create_db.set_search_path_and_role)
  * [create\_metadata\_objects](#install/create_db.create_metadata_objects)
  * [create\_recovery\_objects](#install/create_db.create_recovery_objects)
  * [create\_inventory\_objects](#install/create_db.create_inventory_objects)
  * [create\_internal\_reconciliation\_objects](#install/create_db.create_internal_reconciliation_objects)
* [install/orca\_sql](#install/orca_sql)
  * [commit\_sql](#install/orca_sql.commit_sql)
  * [app\_database\_sql](#install/orca_sql.app_database_sql)
  * [app\_database\_comment\_sql](#install/orca_sql.app_database_comment_sql)
  * [dbo\_role\_sql](#install/orca_sql.dbo_role_sql)
  * [app\_role\_sql](#install/orca_sql.app_role_sql)
  * [orca\_schema\_sql](#install/orca_sql.orca_schema_sql)
  * [app\_user\_sql](#install/orca_sql.app_user_sql)
  * [create\_extension](#install/orca_sql.create_extension)
  * [schema\_versions\_table\_sql](#install/orca_sql.schema_versions_table_sql)
  * [schema\_versions\_data\_sql](#install/orca_sql.schema_versions_data_sql)
  * [recovery\_status\_table\_sql](#install/orca_sql.recovery_status_table_sql)
  * [recovery\_status\_data\_sql](#install/orca_sql.recovery_status_data_sql)
  * [recovery\_job\_table\_sql](#install/orca_sql.recovery_job_table_sql)
  * [recovery\_file\_table\_sql](#install/orca_sql.recovery_file_table_sql)
  * [providers\_table\_sql](#install/orca_sql.providers_table_sql)
  * [collections\_table\_sql](#install/orca_sql.collections_table_sql)
  * [granules\_table\_sql](#install/orca_sql.granules_table_sql)
  * [files\_table\_sql](#install/orca_sql.files_table_sql)
  * [reconcile\_status\_table\_sql](#install/orca_sql.reconcile_status_table_sql)
  * [reconcile\_job\_table\_sql](#install/orca_sql.reconcile_job_table_sql)
  * [reconcile\_s3\_object\_table\_sql](#install/orca_sql.reconcile_s3_object_table_sql)
  * [reconcile\_s3\_object\_partition\_sql](#install/orca_sql.reconcile_s3_object_partition_sql)
  * [reconcile\_catalog\_mismatch\_report\_table\_sql](#install/orca_sql.reconcile_catalog_mismatch_report_table_sql)
  * [reconcile\_orphan\_report\_table\_sql](#install/orca_sql.reconcile_orphan_report_table_sql)
  * [reconcile\_phantom\_report\_table\_sql](#install/orca_sql.reconcile_phantom_report_table_sql)
* [migrations/migrate\_db](#migrations/migrate_db)
  * [perform\_migration](#migrations/migrate_db.perform_migration)
* [migrations/migrate\_versions\_1\_to\_2/migrate](#migrations/migrate_versions_1_to_2/migrate)
  * [migrate\_versions\_1\_to\_2](#migrations/migrate_versions_1_to_2/migrate.migrate_versions_1_to_2)
* [migrations/migrate\_versions\_1\_to\_2/migrate\_sql](#migrations/migrate_versions_1_to_2/migrate_sql)
  * [dbo\_role\_sql](#migrations/migrate_versions_1_to_2/migrate_sql.dbo_role_sql)
  * [app\_role\_sql](#migrations/migrate_versions_1_to_2/migrate_sql.app_role_sql)
  * [orca\_schema\_sql](#migrations/migrate_versions_1_to_2/migrate_sql.orca_schema_sql)
  * [app\_user\_sql](#migrations/migrate_versions_1_to_2/migrate_sql.app_user_sql)
  * [schema\_versions\_table\_sql](#migrations/migrate_versions_1_to_2/migrate_sql.schema_versions_table_sql)
  * [schema\_versions\_data\_sql](#migrations/migrate_versions_1_to_2/migrate_sql.schema_versions_data_sql)
  * [recovery\_status\_table\_sql](#migrations/migrate_versions_1_to_2/migrate_sql.recovery_status_table_sql)
  * [recovery\_status\_data\_sql](#migrations/migrate_versions_1_to_2/migrate_sql.recovery_status_data_sql)
  * [recovery\_job\_table\_sql](#migrations/migrate_versions_1_to_2/migrate_sql.recovery_job_table_sql)
  * [recovery\_file\_table\_sql](#migrations/migrate_versions_1_to_2/migrate_sql.recovery_file_table_sql)
  * [migrate\_recovery\_job\_data\_sql](#migrations/migrate_versions_1_to_2/migrate_sql.migrate_recovery_job_data_sql)
  * [migrate\_recovery\_file\_data\_sql](#migrations/migrate_versions_1_to_2/migrate_sql.migrate_recovery_file_data_sql)
  * [drop\_request\_status\_table\_sql](#migrations/migrate_versions_1_to_2/migrate_sql.drop_request_status_table_sql)
  * [drop\_dr\_schema\_sql](#migrations/migrate_versions_1_to_2/migrate_sql.drop_dr_schema_sql)
  * [drop\_druser\_user\_sql](#migrations/migrate_versions_1_to_2/migrate_sql.drop_druser_user_sql)
  * [drop\_dbo\_user\_sql](#migrations/migrate_versions_1_to_2/migrate_sql.drop_dbo_user_sql)
  * [drop\_dr\_role\_sql](#migrations/migrate_versions_1_to_2/migrate_sql.drop_dr_role_sql)
  * [drop\_drdbo\_role\_sql](#migrations/migrate_versions_1_to_2/migrate_sql.drop_drdbo_role_sql)
* [migrations/migrate\_versions\_2\_to\_3/migrate](#migrations/migrate_versions_2_to_3/migrate)
  * [migrate\_versions\_2\_to\_3](#migrations/migrate_versions_2_to_3/migrate.migrate_versions_2_to_3)
* [migrations/migrate\_versions\_2\_to\_3/migrate\_sql](#migrations/migrate_versions_2_to_3/migrate_sql)
  * [add\_multipart\_chunksize\_sql](#migrations/migrate_versions_2_to_3/migrate_sql.add_multipart_chunksize_sql)
  * [schema\_versions\_data\_sql](#migrations/migrate_versions_2_to_3/migrate_sql.schema_versions_data_sql)
* [migrations/migrate\_versions\_3\_to\_4/migrate](#migrations/migrate_versions_3_to_4/migrate)
  * [migrate\_versions\_3\_to\_4](#migrations/migrate_versions_3_to_4/migrate.migrate_versions_3_to_4)
* [migrations/migrate\_versions\_3\_to\_4/migrate\_sql](#migrations/migrate_versions_3_to_4/migrate_sql)
  * [providers\_table\_sql](#migrations/migrate_versions_3_to_4/migrate_sql.providers_table_sql)
  * [collections\_table\_sql](#migrations/migrate_versions_3_to_4/migrate_sql.collections_table_sql)
  * [granules\_table\_sql](#migrations/migrate_versions_3_to_4/migrate_sql.granules_table_sql)
  * [files\_table\_sql](#migrations/migrate_versions_3_to_4/migrate_sql.files_table_sql)
  * [schema\_versions\_data\_sql](#migrations/migrate_versions_3_to_4/migrate_sql.schema_versions_data_sql)
* [migrations/migrate\_versions\_4\_to\_5/migrate](#migrations/migrate_versions_4_to_5/migrate)
  * [migrate\_versions\_4\_to\_5](#migrations/migrate_versions_4_to_5/migrate.migrate_versions_4_to_5)
* [migrations/migrate\_versions\_4\_to\_5/migrate\_sql](#migrations/migrate_versions_4_to_5/migrate_sql)
  * [schema\_versions\_data\_sql](#migrations/migrate_versions_4_to_5/migrate_sql.schema_versions_data_sql)
  * [create\_extension](#migrations/migrate_versions_4_to_5/migrate_sql.create_extension)
  * [reconcile\_status\_table\_sql](#migrations/migrate_versions_4_to_5/migrate_sql.reconcile_status_table_sql)
  * [reconcile\_job\_table\_sql](#migrations/migrate_versions_4_to_5/migrate_sql.reconcile_job_table_sql)
  * [reconcile\_s3\_object\_table\_sql](#migrations/migrate_versions_4_to_5/migrate_sql.reconcile_s3_object_table_sql)
  * [reconcile\_s3\_object\_partition\_sql](#migrations/migrate_versions_4_to_5/migrate_sql.reconcile_s3_object_partition_sql)
  * [reconcile\_catalog\_mismatch\_report\_table\_sql](#migrations/migrate_versions_4_to_5/migrate_sql.reconcile_catalog_mismatch_report_table_sql)
  * [reconcile\_orphan\_report\_table\_sql](#migrations/migrate_versions_4_to_5/migrate_sql.reconcile_orphan_report_table_sql)
  * [reconcile\_phantom\_report\_table\_sql](#migrations/migrate_versions_4_to_5/migrate_sql.reconcile_phantom_report_table_sql)

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
task(config: Dict[str, str], orca_buckets: List[str]) -> None
```

Checks for the ORCA database and throws an error if it does not exist.
Determines if a fresh install or a migration is needed for the ORCA
schema.

**Arguments**:

- `config` _Dict_ - Dictionary of connection information.
- `orca_buckets` - List[str]): List of ORCA buckets needed to create partitioned tables.
  

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

<a name="install/create_db"></a>
# install/create\_db

Name: create_db.py

Description: Creates the current version on the ORCA database.

<a name="install/create_db.create_fresh_orca_install"></a>
#### create\_fresh\_orca\_install

```python
create_fresh_orca_install(config: Dict[str, str], orca_buckets: List[str]) -> None
```

This task will create the ORCA roles, users, schema, and tables needed
by the ORCA application as a fresh install.

**Arguments**:

- `config` _Dict_ - Dictionary with database connection information
- `orca_buckets` - List[str]): List of ORCA buckets needed to create
  partitioned tables for reporting.
  

**Returns**:

  None

<a name="install/create_db.create_database"></a>
#### create\_database

```python
create_database(config: Dict[str, str]) -> None
```

Creates the orca database

<a name="install/create_db.create_app_schema_role_users"></a>
#### create\_app\_schema\_role\_users

```python
create_app_schema_role_users(connection: Connection, app_username: str, app_password: str, db_name: str) -> None
```

Creates the ORCA application database schema, users and roles.

**Arguments**:

- `connection` _sqlalchemy.future.Connection_ - Database connection.
- `app_username` - The name for the created scoped user.
- `app_password` - The password for the created scoped user.
- `db_name` - The name of the Orca database within the RDS cluster.
  

**Returns**:

  None

<a name="install/create_db.set_search_path_and_role"></a>
#### set\_search\_path\_and\_role

```python
set_search_path_and_role(connection: Connection) -> None
```

Sets the role to the dbo role to create/modify ORCA objects and sets the
search_path to make the orca schema first. This must be run before any
creations or modifications to ORCA objects in the ORCA schema.

**Arguments**:

- `connection` _sqlalchemy.future.Connection_ - Database connection.
  

**Returns**:

  None

<a name="install/create_db.create_metadata_objects"></a>
#### create\_metadata\_objects

```python
create_metadata_objects(connection: Connection) -> None
```

Create the ORCA application metadata tables used to manage application
versions and other ORCA internal information in the proper order.
- schema_versions

**Arguments**:

- `connection` _sqlalchemy.future.Connection_ - Database connection.
  

**Returns**:

  None

<a name="install/create_db.create_recovery_objects"></a>
#### create\_recovery\_objects

```python
create_recovery_objects(connection: Connection) -> None
```

Creates the ORCA recovery tables in the proper order.
- recovery_status
- recovery_job
- recovery_table

**Arguments**:

- `connection` _sqlalchemy.future.Connection_ - Database connection.
  

**Returns**:

  None

<a name="install/create_db.create_inventory_objects"></a>
#### create\_inventory\_objects

```python
create_inventory_objects(connection: Connection) -> None
```

Creates the ORCA catalog metadata tables used for reconciliation with
Cumulus in the proper order.
- providers
- collections
- provider_collection_xref
- granules
- files

**Arguments**:

- `connection` _sqlalchemy.future.Connection_ - Database connection.
  

**Returns**:

  None

<a name="install/create_db.create_internal_reconciliation_objects"></a>
#### create\_internal\_reconciliation\_objects

```python
create_internal_reconciliation_objects(connection: Connection, orca_buckets: List[str]) -> None
```

Creates the ORCA internal reconciliation tables in the proper order.
- reconcile_status
- reconcile_job
- reconcile_s3_object
- reconcile_catalog_mismatch_report
- reconcile_orphan_report
- reconcile_phantom_report

**Arguments**:

- `connection` _sqlalchemy.future.Connection_ - Database connection.
- `orca_buckets` - List[str]): List of ORCA buckets needed to create
  partitioned tables for reporting.
  

**Returns**:

  None

<a name="install/orca_sql"></a>
# install/orca\_sql

Name: orca_sql.py

Description: All of the SQL used for creating and migrating the ORCA schema.

<a name="install/orca_sql.commit_sql"></a>
#### commit\_sql

```python
commit_sql() -> TextClause
```

SQL for a simple 'commit' to exit the current transaction.

<a name="install/orca_sql.app_database_sql"></a>
#### app\_database\_sql

```python
app_database_sql(db_name: str) -> TextClause
```

Full SQL for creating the ORCA application database.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating database.

<a name="install/orca_sql.app_database_comment_sql"></a>
#### app\_database\_comment\_sql

```python
app_database_comment_sql(db_name: str) -> TextClause
```

SQL for adding a documentation comment to the database.
Cannot be merged with DB creation due to SQLAlchemy limitations.

<a name="install/orca_sql.dbo_role_sql"></a>
#### dbo\_role\_sql

```python
dbo_role_sql(db_name: str) -> TextClause
```

Full SQL for creating the ORCA dbo role that owns the ORCA schema and
objects.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating orca_dbo role.

<a name="install/orca_sql.app_role_sql"></a>
#### app\_role\_sql

```python
app_role_sql(db_name: str) -> TextClause
```

Full SQL for creating the ORCA application role that has all the privileges
to interact with the ORCA schema.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating orca_app role.

<a name="install/orca_sql.orca_schema_sql"></a>
#### orca\_schema\_sql

```python
orca_schema_sql() -> TextClause
```

Full SQL for creating the ORCA application schema that contains all the
ORCA tables and objects. This SQL must be used after the dbo_role_sql and
before the app_user_sql and ORCA objects.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating orca schema.

<a name="install/orca_sql.app_user_sql"></a>
#### app\_user\_sql

```python
app_user_sql(user_name: str, user_password: str) -> TextClause
```

Full SQL for creating the ORCA application database user. Must be created
after the app_role_sql and orca_schema_sql.

**Arguments**:

- `user_password` _str_ - Password for the application user
  

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating PREFIX_orcauser user.

<a name="install/orca_sql.create_extension"></a>
#### create\_extension

```python
create_extension() -> TextClause
```

Full SQL for creating the aws_s3 extension used for COPYING S3 reporting data
from a CSV file in an AWS bucket into the database.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating extension for the database.

<a name="install/orca_sql.schema_versions_table_sql"></a>
#### schema\_versions\_table\_sql

```python
schema_versions_table_sql() -> TextClause
```

Full SQL for creating the schema_versions table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating schema_versions table.

<a name="install/orca_sql.schema_versions_data_sql"></a>
#### schema\_versions\_data\_sql

```python
schema_versions_data_sql() -> TextClause
```

Data for the schema_versions table. Inserts the current schema
version into the table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for populating schema_versions table.

<a name="install/orca_sql.recovery_status_table_sql"></a>
#### recovery\_status\_table\_sql

```python
recovery_status_table_sql() -> TextClause
```

Full SQL for creating the recovery_status table. This SQL must be run
before any of the other recovery table sql.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating recovery_status table.

<a name="install/orca_sql.recovery_status_data_sql"></a>
#### recovery\_status\_data\_sql

```python
recovery_status_data_sql() -> TextClause
```

Data for the recovery_status table. Inserts the current status values into
the table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for populating recovery_status table.

<a name="install/orca_sql.recovery_job_table_sql"></a>
#### recovery\_job\_table\_sql

```python
recovery_job_table_sql() -> TextClause
```

Full SQL for creating the recovery_job table. This SQL must be run
before the other recovery_file table sql and after the recovery_status
table sql to maintain key dependencies.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating recovery_job table.

<a name="install/orca_sql.recovery_file_table_sql"></a>
#### recovery\_file\_table\_sql

```python
recovery_file_table_sql() -> TextClause
```

Full SQL for creating the recovery_file table. This SQL must be run
after the recovery_job table sql to maintain key dependencies.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating recovery_file table.

<a name="install/orca_sql.providers_table_sql"></a>
#### providers\_table\_sql

```python
providers_table_sql() -> TextClause
```

Full SQL for creating the providers table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating providers table.

<a name="install/orca_sql.collections_table_sql"></a>
#### collections\_table\_sql

```python
collections_table_sql() -> TextClause
```

Full SQL for creating the collections table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating collections table.

<a name="install/orca_sql.granules_table_sql"></a>
#### granules\_table\_sql

```python
granules_table_sql() -> TextClause
```

Full SQL for creating the catalog granules table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating granules table.

<a name="install/orca_sql.files_table_sql"></a>
#### files\_table\_sql

```python
files_table_sql() -> TextClause
```

Full SQL for creating the catalog files table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating files table.

<a name="install/orca_sql.reconcile_status_table_sql"></a>
#### reconcile\_status\_table\_sql

```python
reconcile_status_table_sql() -> TextClause
```

Full SQL for creating the reconcile_status table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating reconcile_status table.

<a name="install/orca_sql.reconcile_job_table_sql"></a>
#### reconcile\_job\_table\_sql

```python
reconcile_job_table_sql() -> TextClause
```

Full SQL for creating the reconcile_job table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating reconcile_job table.

<a name="install/orca_sql.reconcile_s3_object_table_sql"></a>
#### reconcile\_s3\_object\_table\_sql

```python
reconcile_s3_object_table_sql() -> TextClause
```

Full SQL for creating the reconcile_s3_object table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating reconcile_s3_object table.

<a name="install/orca_sql.reconcile_s3_object_partition_sql"></a>
#### reconcile\_s3\_object\_partition\_sql

```python
reconcile_s3_object_partition_sql(partition_name: str) -> TextClause
```

Full SQL for creating the reconcile_s3_object partition table. Requires the
user to pass the orca_archive_location value for the partition in the form
of `{"bucket_name": value}` when executing the SQL via the driver.

**Arguments**:

- `partition_name(str)` - Name of the partition table.
  

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating reconcile_s3_object partition table.

<a name="install/orca_sql.reconcile_catalog_mismatch_report_table_sql"></a>
#### reconcile\_catalog\_mismatch\_report\_table\_sql

```python
reconcile_catalog_mismatch_report_table_sql() -> TextClause
```

Full SQL for creating the reconcile_catalog_mismatch_report table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating reconcile_catalog_mismatch_report.

<a name="install/orca_sql.reconcile_orphan_report_table_sql"></a>
#### reconcile\_orphan\_report\_table\_sql

```python
reconcile_orphan_report_table_sql() -> TextClause
```

Full SQL for creating the reconcile_orphan_report table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating reconcile_orphan_report table.

<a name="install/orca_sql.reconcile_phantom_report_table_sql"></a>
#### reconcile\_phantom\_report\_table\_sql

```python
reconcile_phantom_report_table_sql() -> TextClause
```

Full SQL for creating the reconcile_phantom_report table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating reconcile_phantom_report table.

<a name="migrations/migrate_db"></a>
# migrations/migrate\_db

Name: migrate_db.py

Description: Migrates the current ORCA schema version to the latest version.

<a name="migrations/migrate_db.perform_migration"></a>
#### perform\_migration

```python
perform_migration(current_schema_version: int, config: Dict[str, str], orca_buckets: List[str]) -> None
```

Performs a migration of the ORCA database. Determines the order and
migrations to run.

**Arguments**:

- `current_schema_version` _int_ - Current version of the ORCA schema
- `config` _Dict_ - Dictionary containing database connection information
- `orca_buckets` - List[str]): List of ORCA bucket names used to create partition tables for v5.
  

**Returns**:

  None

<a name="migrations/migrate_versions_1_to_2/migrate"></a>
# migrations/migrate\_versions\_1\_to\_2/migrate

Name: migrate_db_v2.py

Description: Migrates the ORCA schema from version 1 to version 2.

<a name="migrations/migrate_versions_1_to_2/migrate.migrate_versions_1_to_2"></a>
#### migrate\_versions\_1\_to\_2

```python
migrate_versions_1_to_2(config: Dict[str, str], is_latest_version: bool) -> None
```

Performs the migration of the ORCA schema from version 1 to version 2 of
the ORCA schema.

**Arguments**:

- `config` _Dict_ - Connection information for the database.
- `is_latest_version` _bool_ - Flag to determine if version 2 is the latest schema version.
  

**Returns**:

  None

<a name="migrations/migrate_versions_1_to_2/migrate_sql"></a>
# migrations/migrate\_versions\_1\_to\_2/migrate\_sql

Name: orca_sql_v2.py

Description: All of the SQL used for creating and migrating the ORCA schema to version 2.

<a name="migrations/migrate_versions_1_to_2/migrate_sql.dbo_role_sql"></a>
#### dbo\_role\_sql

```python
dbo_role_sql(db_name: str) -> TextClause
```

Full SQL for creating the ORCA dbo role that owns the ORCA schema and
objects.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating orca_dbo role.

<a name="migrations/migrate_versions_1_to_2/migrate_sql.app_role_sql"></a>
#### app\_role\_sql

```python
app_role_sql(db_name: str) -> TextClause
```

Full SQL for creating the ORCA application role that has all the privileges
to interact with the ORCA schema.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating orca_app role.

<a name="migrations/migrate_versions_1_to_2/migrate_sql.orca_schema_sql"></a>
#### orca\_schema\_sql

```python
orca_schema_sql() -> TextClause
```

Full SQL for creating the ORCA application schema that contains all the
ORCA tables and objects. This SQL must be used after the dbo_role_sql and
before the app_user_sql and ORCA objects.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating orca schema.

<a name="migrations/migrate_versions_1_to_2/migrate_sql.app_user_sql"></a>
#### app\_user\_sql

```python
app_user_sql(user_name: str, user_password: str) -> TextClause
```

Full SQL for creating the ORCA application database user. Must be created
after the app_role_sql and orca_schema_sql.

**Arguments**:

- `user_password` _str_ - Password for the application user
  

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating PREFIX_orcauser user.

<a name="migrations/migrate_versions_1_to_2/migrate_sql.schema_versions_table_sql"></a>
#### schema\_versions\_table\_sql

```python
schema_versions_table_sql() -> TextClause
```

Full SQL for creating the schema_versions table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating schema_versions table.

<a name="migrations/migrate_versions_1_to_2/migrate_sql.schema_versions_data_sql"></a>
#### schema\_versions\_data\_sql

```python
schema_versions_data_sql() -> TextClause
```

Data for the schema_versions table. Inserts the current schema
version into the table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for populating schema_versions table.

<a name="migrations/migrate_versions_1_to_2/migrate_sql.recovery_status_table_sql"></a>
#### recovery\_status\_table\_sql

```python
recovery_status_table_sql() -> TextClause
```

Full SQL for creating the recovery_status table. This SQL must be run
before any of the other recovery table sql.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating recovery_status table.

<a name="migrations/migrate_versions_1_to_2/migrate_sql.recovery_status_data_sql"></a>
#### recovery\_status\_data\_sql

```python
recovery_status_data_sql() -> TextClause
```

Data for the recovery_status table. Inserts the current status values into
the table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for populating recovery_status table.

<a name="migrations/migrate_versions_1_to_2/migrate_sql.recovery_job_table_sql"></a>
#### recovery\_job\_table\_sql

```python
recovery_job_table_sql() -> TextClause
```

Full SQL for creating the recovery_job table. This SQL must be run
before the other recovery_file table sql and after the recovery_status
table sql to maintain key dependencies.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating recovery_job table.

<a name="migrations/migrate_versions_1_to_2/migrate_sql.recovery_file_table_sql"></a>
#### recovery\_file\_table\_sql

```python
recovery_file_table_sql() -> TextClause
```

Full SQL for creating the recovery_file table. This SQL must be run
after the recovery_job table sql to maintain key dependencies.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating recovery_file table.

<a name="migrations/migrate_versions_1_to_2/migrate_sql.migrate_recovery_job_data_sql"></a>
#### migrate\_recovery\_job\_data\_sql

```python
migrate_recovery_job_data_sql() -> TextClause
```

SQL that migrates data from the old dr.request_status table to the new
orca.recovery_job table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for populating recovery_job table.

<a name="migrations/migrate_versions_1_to_2/migrate_sql.migrate_recovery_file_data_sql"></a>
#### migrate\_recovery\_file\_data\_sql

```python
migrate_recovery_file_data_sql() -> TextClause
```

SQL that migrates data from the old dr.request_status table to the new
orca.recovery_file table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for populating recovery_file table.

<a name="migrations/migrate_versions_1_to_2/migrate_sql.drop_request_status_table_sql"></a>
#### drop\_request\_status\_table\_sql

```python
drop_request_status_table_sql() -> TextClause
```

SQL that removes the dr.request_status table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for dropping request_status table.

<a name="migrations/migrate_versions_1_to_2/migrate_sql.drop_dr_schema_sql"></a>
#### drop\_dr\_schema\_sql

```python
drop_dr_schema_sql() -> TextClause
```

SQL that removes the dr schema.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for dropping dr schema.

<a name="migrations/migrate_versions_1_to_2/migrate_sql.drop_druser_user_sql"></a>
#### drop\_druser\_user\_sql

```python
drop_druser_user_sql() -> TextClause
```

SQL that removes the druser user.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for dropping druser user.

<a name="migrations/migrate_versions_1_to_2/migrate_sql.drop_dbo_user_sql"></a>
#### drop\_dbo\_user\_sql

```python
drop_dbo_user_sql(db_name: str) -> TextClause
```

SQL that removes the dbo user.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for dropping dbo user.

<a name="migrations/migrate_versions_1_to_2/migrate_sql.drop_dr_role_sql"></a>
#### drop\_dr\_role\_sql

```python
drop_dr_role_sql(db_name: str) -> TextClause
```

SQL that removes the dr_role role.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for dropping dr_role role.

<a name="migrations/migrate_versions_1_to_2/migrate_sql.drop_drdbo_role_sql"></a>
#### drop\_drdbo\_role\_sql

```python
drop_drdbo_role_sql(db_name: str) -> TextClause
```

SQL that removes the drdbo_role role.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for dropping drdbo_role role.
  f

<a name="migrations/migrate_versions_2_to_3/migrate"></a>
# migrations/migrate\_versions\_2\_to\_3/migrate

Name: migrate_db_v3.py

Description: Migrates the ORCA schema from version 2 to version 3.

<a name="migrations/migrate_versions_2_to_3/migrate.migrate_versions_2_to_3"></a>
#### migrate\_versions\_2\_to\_3

```python
migrate_versions_2_to_3(config: Dict[str, str], is_latest_version: bool) -> None
```

Performs the migration of the ORCA schema from version 2 to version 3 of
the ORCA schema.

**Arguments**:

- `config` _Dict_ - Connection information for the database.
- `is_latest_version` _bool_ - Flag to determine if version 3 is the latest schema version.

<a name="migrations/migrate_versions_2_to_3/migrate_sql"></a>
# migrations/migrate\_versions\_2\_to\_3/migrate\_sql

Name: orca_sql_v3.py

Description: All of the SQL used for creating and migrating the ORCA schema to version 3.

<a name="migrations/migrate_versions_2_to_3/migrate_sql.add_multipart_chunksize_sql"></a>
#### add\_multipart\_chunksize\_sql

```python
add_multipart_chunksize_sql() -> TextClause
```

SQL that adds the multipart_chunksize_mb column to recovery_file.

Returns: SQL for adding multipart_chunksize_mb.

<a name="migrations/migrate_versions_2_to_3/migrate_sql.schema_versions_data_sql"></a>
#### schema\_versions\_data\_sql

```python
schema_versions_data_sql() -> TextClause
```

Data for the schema_versions table. Inserts the current schema
version into the table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for populating schema_versions table.

<a name="migrations/migrate_versions_3_to_4/migrate"></a>
# migrations/migrate\_versions\_3\_to\_4/migrate

Name: migrate.py

Description: Migrates the ORCA schema from version 3 to version 4.

<a name="migrations/migrate_versions_3_to_4/migrate.migrate_versions_3_to_4"></a>
#### migrate\_versions\_3\_to\_4

```python
migrate_versions_3_to_4(config: Dict[str, str], is_latest_version: bool) -> None
```

Performs the migration of the ORCA schema from version 3 to version 4 of
the ORCA schema.

**Arguments**:

- `config` _Dict_ - Connection information for the database.
- `is_latest_version` _bool_ - Flag to determine if version 4 is the latest schema version.

**Returns**:

  None

<a name="migrations/migrate_versions_3_to_4/migrate_sql"></a>
# migrations/migrate\_versions\_3\_to\_4/migrate\_sql

Name: migrate_sql.py

Description: All of the SQL used for creating and migrating the ORCA schema to version 4.

<a name="migrations/migrate_versions_3_to_4/migrate_sql.providers_table_sql"></a>
#### providers\_table\_sql

```python
providers_table_sql() -> TextClause
```

Full SQL for creating the providers table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating providers table.

<a name="migrations/migrate_versions_3_to_4/migrate_sql.collections_table_sql"></a>
#### collections\_table\_sql

```python
collections_table_sql() -> TextClause
```

Full SQL for creating the collections table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating collections table.

<a name="migrations/migrate_versions_3_to_4/migrate_sql.granules_table_sql"></a>
#### granules\_table\_sql

```python
granules_table_sql() -> TextClause
```

Full SQL for creating the catalog granules table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating granules table.

<a name="migrations/migrate_versions_3_to_4/migrate_sql.files_table_sql"></a>
#### files\_table\_sql

```python
files_table_sql() -> TextClause
```

Full SQL for creating the catalog files table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating files table.

<a name="migrations/migrate_versions_3_to_4/migrate_sql.schema_versions_data_sql"></a>
#### schema\_versions\_data\_sql

```python
schema_versions_data_sql() -> TextClause
```

Data for the schema_versions table. Inserts the current schema
version into the table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for populating schema_versions table.

<a name="migrations/migrate_versions_4_to_5/migrate"></a>
# migrations/migrate\_versions\_4\_to\_5/migrate

Name: migrate.py

Description: Migrates the ORCA schema from version 4 to version 5.

<a name="migrations/migrate_versions_4_to_5/migrate.migrate_versions_4_to_5"></a>
#### migrate\_versions\_4\_to\_5

```python
migrate_versions_4_to_5(config: Dict[str, str], is_latest_version: bool, orca_buckets: List[str]) -> None
```

Performs the migration of the ORCA schema from version 4 to version 5 of
the ORCA schema. This includes adding the aws s3 extension and adding the
following tables:
- reconcile_status
- reconcile_job
- reconcile_s3_object (and partitions)
- reconcile_catalog_mismatch_report
- reconcile_phantom_report
- reconcile_orphan_report

**Arguments**:

- `config` _Dict_ - Connection information for the database.
- `is_latest_version` _bool_ - Flag to determine if version 5 is the latest
  schema version.
- `orca_buckets` - List[str]): List of ORCA buckets names needed to create
  partition tables for v5.

**Returns**:

  None

<a name="migrations/migrate_versions_4_to_5/migrate_sql"></a>
# migrations/migrate\_versions\_4\_to\_5/migrate\_sql

Name: migrate_sql.py

Description: All of the SQL used for creating and migrating the ORCA schema to version 5.

<a name="migrations/migrate_versions_4_to_5/migrate_sql.schema_versions_data_sql"></a>
#### schema\_versions\_data\_sql

```python
schema_versions_data_sql() -> TextClause
```

Data for the schema_versions table. Inserts the current schema
version into the table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for populating schema_versions table.

<a name="migrations/migrate_versions_4_to_5/migrate_sql.create_extension"></a>
#### create\_extension

```python
create_extension() -> TextClause
```

Full SQL for creating the aws_s3 extension used for COPYING S3 reporting data
from a CSV file in an AWS bucket into the database.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating extension for the database.

<a name="migrations/migrate_versions_4_to_5/migrate_sql.reconcile_status_table_sql"></a>
#### reconcile\_status\_table\_sql

```python
reconcile_status_table_sql() -> TextClause
```

Full SQL for creating the reconcile_status table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating reconcile_status table.

<a name="migrations/migrate_versions_4_to_5/migrate_sql.reconcile_job_table_sql"></a>
#### reconcile\_job\_table\_sql

```python
reconcile_job_table_sql() -> TextClause
```

Full SQL for creating the reconcile_job table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating reconcile_job table.

<a name="migrations/migrate_versions_4_to_5/migrate_sql.reconcile_s3_object_table_sql"></a>
#### reconcile\_s3\_object\_table\_sql

```python
reconcile_s3_object_table_sql() -> TextClause
```

Full SQL for creating the reconcile_s3_object table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating reconcile_s3_object table.

<a name="migrations/migrate_versions_4_to_5/migrate_sql.reconcile_s3_object_partition_sql"></a>
#### reconcile\_s3\_object\_partition\_sql

```python
reconcile_s3_object_partition_sql(partition_name: str) -> TextClause
```

Full SQL for creating the reconcile_s3_object partition table. Requires the
user to pass the orca_archive_location value for the partition in the form
of `{"bucket_name": value}` when executing the SQL via the driver.

**Arguments**:

- `partition_name(str)` - Name of the partition table.
  

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating reconcile_s3_object partition table.

<a name="migrations/migrate_versions_4_to_5/migrate_sql.reconcile_catalog_mismatch_report_table_sql"></a>
#### reconcile\_catalog\_mismatch\_report\_table\_sql

```python
reconcile_catalog_mismatch_report_table_sql() -> TextClause
```

Full SQL for creating the reconcile_catalog_mismatch_report table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating reconcile_catalog_mismatch_report.

<a name="migrations/migrate_versions_4_to_5/migrate_sql.reconcile_orphan_report_table_sql"></a>
#### reconcile\_orphan\_report\_table\_sql

```python
reconcile_orphan_report_table_sql() -> TextClause
```

Full SQL for creating the reconcile_orphan_report table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating reconcile_orphan_report table.

<a name="migrations/migrate_versions_4_to_5/migrate_sql.reconcile_phantom_report_table_sql"></a>
#### reconcile\_phantom\_report\_table\_sql

```python
reconcile_phantom_report_table_sql() -> TextClause
```

Full SQL for creating the reconcile_phantom_report table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating reconcile_phantom_report table.

