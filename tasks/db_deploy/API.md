# Table of Contents

* [migrations/migrate\_versions\_2\_to\_3/migrate\_db\_v3](#migrations/migrate_versions_2_to_3/migrate_db_v3)
  * [migrate\_versions\_2\_to\_3](#migrations/migrate_versions_2_to_3/migrate_db_v3.migrate_versions_2_to_3)
* [migrations/migrate\_versions\_2\_to\_3/migrate\_sql\_v3](#migrations/migrate_versions_2_to_3/migrate_sql_v3)
  * [add\_multipart\_chunksize\_sql](#migrations/migrate_versions_2_to_3/migrate_sql_v3.add_multipart_chunksize_sql)
  * [schema\_versions\_data\_sql](#migrations/migrate_versions_2_to_3/migrate_sql_v3.schema_versions_data_sql)
* [migrations/migrate\_versions\_3\_to\_4/migrate\_sql\_v4](#migrations/migrate_versions_3_to_4/migrate_sql_v4)
  * [providers\_table\_sql](#migrations/migrate_versions_3_to_4/migrate_sql_v4.providers_table_sql)
  * [collections\_table\_sql](#migrations/migrate_versions_3_to_4/migrate_sql_v4.collections_table_sql)
  * [granules\_table\_sql](#migrations/migrate_versions_3_to_4/migrate_sql_v4.granules_table_sql)
  * [files\_table\_sql](#migrations/migrate_versions_3_to_4/migrate_sql_v4.files_table_sql)
  * [schema\_versions\_data\_sql](#migrations/migrate_versions_3_to_4/migrate_sql_v4.schema_versions_data_sql)
* [migrations/migrate\_versions\_3\_to\_4/migrate\_db\_v4](#migrations/migrate_versions_3_to_4/migrate_db_v4)
  * [migrate\_versions\_3\_to\_4](#migrations/migrate_versions_3_to_4/migrate_db_v4.migrate_versions_3_to_4)
* [migrations/migrate\_db](#migrations/migrate_db)
  * [perform\_migration](#migrations/migrate_db.perform_migration)
* [migrations/migrate\_versions\_1\_to\_2/migrate\_db\_v2](#migrations/migrate_versions_1_to_2/migrate_db_v2)
  * [migrate\_versions\_1\_to\_2](#migrations/migrate_versions_1_to_2/migrate_db_v2.migrate_versions_1_to_2)
* [migrations/migrate\_versions\_1\_to\_2/migrate\_sql\_v2](#migrations/migrate_versions_1_to_2/migrate_sql_v2)
  * [dbo\_role\_sql](#migrations/migrate_versions_1_to_2/migrate_sql_v2.dbo_role_sql)
  * [app\_role\_sql](#migrations/migrate_versions_1_to_2/migrate_sql_v2.app_role_sql)
  * [orca\_schema\_sql](#migrations/migrate_versions_1_to_2/migrate_sql_v2.orca_schema_sql)
  * [app\_user\_sql](#migrations/migrate_versions_1_to_2/migrate_sql_v2.app_user_sql)
  * [schema\_versions\_table\_sql](#migrations/migrate_versions_1_to_2/migrate_sql_v2.schema_versions_table_sql)
  * [schema\_versions\_data\_sql](#migrations/migrate_versions_1_to_2/migrate_sql_v2.schema_versions_data_sql)
  * [recovery\_status\_table\_sql](#migrations/migrate_versions_1_to_2/migrate_sql_v2.recovery_status_table_sql)
  * [recovery\_status\_data\_sql](#migrations/migrate_versions_1_to_2/migrate_sql_v2.recovery_status_data_sql)
  * [recovery\_job\_table\_sql](#migrations/migrate_versions_1_to_2/migrate_sql_v2.recovery_job_table_sql)
  * [recovery\_file\_table\_sql](#migrations/migrate_versions_1_to_2/migrate_sql_v2.recovery_file_table_sql)
  * [migrate\_recovery\_job\_data\_sql](#migrations/migrate_versions_1_to_2/migrate_sql_v2.migrate_recovery_job_data_sql)
  * [migrate\_recovery\_file\_data\_sql](#migrations/migrate_versions_1_to_2/migrate_sql_v2.migrate_recovery_file_data_sql)
  * [drop\_request\_status\_table\_sql](#migrations/migrate_versions_1_to_2/migrate_sql_v2.drop_request_status_table_sql)
  * [drop\_dr\_schema\_sql](#migrations/migrate_versions_1_to_2/migrate_sql_v2.drop_dr_schema_sql)
  * [drop\_druser\_user\_sql](#migrations/migrate_versions_1_to_2/migrate_sql_v2.drop_druser_user_sql)
  * [drop\_dbo\_user\_sql](#migrations/migrate_versions_1_to_2/migrate_sql_v2.drop_dbo_user_sql)
  * [drop\_dr\_role\_sql](#migrations/migrate_versions_1_to_2/migrate_sql_v2.drop_dr_role_sql)
  * [drop\_drdbo\_role\_sql](#migrations/migrate_versions_1_to_2/migrate_sql_v2.drop_drdbo_role_sql)
* [install/orca\_reconcile\_sql](#install/orca_reconcile_sql)
  * [reconcile\_status\_table\_sql](#install/orca_reconcile_sql.reconcile_status_table_sql)
  * [reconcile\_job\_table\_sql](#install/orca_reconcile_sql.reconcile_job_table_sql)
  * [reconcile\_s3\_object\_table\_sql](#install/orca_reconcile_sql.reconcile_s3_object_table_sql)
  * [reconcile\_catalog\_mismatch\_report\_table\_sql](#install/orca_reconcile_sql.reconcile_catalog_mismatch_report_table_sql)
  * [reconcile\_orphan\_report\_table\_sql](#install/orca_reconcile_sql.reconcile_orphan_report_table_sql)
  * [reconcile\_phantom\_report\_table\_sql](#install/orca_reconcile_sql.reconcile_phantom_report_table_sql)
  * [orca\_archive\_location\_bucket](#install/orca_reconcile_sql.orca_archive_location_bucket)
  * [create\_extension](#install/orca_reconcile_sql.create_extension)
  * [drop\_extension](#install/orca_reconcile_sql.drop_extension)
* [install/orca\_sql](#install/orca_sql)
  * [commit\_sql](#install/orca_sql.commit_sql)
  * [app\_database\_sql](#install/orca_sql.app_database_sql)
  * [app\_database\_comment\_sql](#install/orca_sql.app_database_comment_sql)
  * [dbo\_role\_sql](#install/orca_sql.dbo_role_sql)
  * [app\_role\_sql](#install/orca_sql.app_role_sql)
  * [orca\_schema\_sql](#install/orca_sql.orca_schema_sql)
  * [app\_user\_sql](#install/orca_sql.app_user_sql)
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
* [install/create\_db](#install/create_db)
  * [create\_fresh\_orca\_install](#install/create_db.create_fresh_orca_install)
  * [create\_database](#install/create_db.create_database)
  * [create\_app\_schema\_role\_users](#install/create_db.create_app_schema_role_users)
  * [set\_search\_path\_and\_role](#install/create_db.set_search_path_and_role)
  * [create\_metadata\_objects](#install/create_db.create_metadata_objects)
  * [create\_recovery\_objects](#install/create_db.create_recovery_objects)
  * [create\_inventory\_objects](#install/create_db.create_inventory_objects)
  * [create\_internal\_reconciliation\_objects](#install/create_db.create_internal_reconciliation_objects)
* [test/unit\_tests/test\_migrate\_sql\_v3](#test/unit_tests/test_migrate_sql_v3)
  * [TestOrcaSqlLogic](#test/unit_tests/test_migrate_sql_v3.TestOrcaSqlLogic)
    * [test\_all\_functions\_return\_text](#test/unit_tests/test_migrate_sql_v3.TestOrcaSqlLogic.test_all_functions_return_text)
* [test/unit\_tests/test\_db\_deploy](#test/unit_tests/test_db_deploy)
  * [TestDbDeployFunctions](#test/unit_tests/test_db_deploy.TestDbDeployFunctions)
    * [setUp](#test/unit_tests/test_db_deploy.TestDbDeployFunctions.setUp)
    * [tearDown](#test/unit_tests/test_db_deploy.TestDbDeployFunctions.tearDown)
    * [test\_handler\_happy\_path](#test/unit_tests/test_db_deploy.TestDbDeployFunctions.test_handler_happy_path)
    * [test\_task\_no\_database](#test/unit_tests/test_db_deploy.TestDbDeployFunctions.test_task_no_database)
    * [test\_task\_no\_schema](#test/unit_tests/test_db_deploy.TestDbDeployFunctions.test_task_no_schema)
    * [test\_task\_schmea\_old\_version](#test/unit_tests/test_db_deploy.TestDbDeployFunctions.test_task_schmea_old_version)
    * [test\_task\_schema\_current\_version](#test/unit_tests/test_db_deploy.TestDbDeployFunctions.test_task_schema_current_version)
    * [test\_app\_db\_exists\_happy\_path](#test/unit_tests/test_db_deploy.TestDbDeployFunctions.test_app_db_exists_happy_path)
    * [test\_app\_schema\_exists\_happy\_path](#test/unit_tests/test_db_deploy.TestDbDeployFunctions.test_app_schema_exists_happy_path)
    * [test\_app\_versions\_table\_exists\_happy\_path](#test/unit_tests/test_db_deploy.TestDbDeployFunctions.test_app_versions_table_exists_happy_path)
    * [test\_get\_migration\_version\_happy\_path](#test/unit_tests/test_db_deploy.TestDbDeployFunctions.test_get_migration_version_happy_path)
* [test/unit\_tests/test\_migrate\_sql\_v2](#test/unit_tests/test_migrate_sql_v2)
  * [TestOrcaSqlLogic](#test/unit_tests/test_migrate_sql_v2.TestOrcaSqlLogic)
    * [test\_app\_user\_sql\_happy\_path](#test/unit_tests/test_migrate_sql_v2.TestOrcaSqlLogic.test_app_user_sql_happy_path)
    * [test\_app\_user\_sql\_exceptions](#test/unit_tests/test_migrate_sql_v2.TestOrcaSqlLogic.test_app_user_sql_exceptions)
    * [test\_all\_functions\_return\_text](#test/unit_tests/test_migrate_sql_v2.TestOrcaSqlLogic.test_all_functions_return_text)
* [test/unit\_tests/test\_create\_db](#test/unit_tests/test_create_db)
  * [TestCreateDatabaseLibraries](#test/unit_tests/test_create_db.TestCreateDatabaseLibraries)
    * [setUp](#test/unit_tests/test_create_db.TestCreateDatabaseLibraries.setUp)
    * [tearDown](#test/unit_tests/test_create_db.TestCreateDatabaseLibraries.tearDown)
    * [test\_create\_fresh\_orca\_install\_happy\_path](#test/unit_tests/test_create_db.TestCreateDatabaseLibraries.test_create_fresh_orca_install_happy_path)
    * [test\_create\_database\_happy\_path](#test/unit_tests/test_create_db.TestCreateDatabaseLibraries.test_create_database_happy_path)
    * [test\_create\_app\_schema\_user\_role\_users\_happy\_path](#test/unit_tests/test_create_db.TestCreateDatabaseLibraries.test_create_app_schema_user_role_users_happy_path)
    * [test\_set\_search\_path\_and\_role](#test/unit_tests/test_create_db.TestCreateDatabaseLibraries.test_set_search_path_and_role)
    * [test\_create\_metadata\_objects](#test/unit_tests/test_create_db.TestCreateDatabaseLibraries.test_create_metadata_objects)
    * [test\_create\_recovery\_objects](#test/unit_tests/test_create_db.TestCreateDatabaseLibraries.test_create_recovery_objects)
    * [test\_create\_inventory\_objects](#test/unit_tests/test_create_db.TestCreateDatabaseLibraries.test_create_inventory_objects)
* [test/unit\_tests/test\_migrate\_db\_v4](#test/unit_tests/test_migrate_db_v4)
  * [TestMigrateDatabaseLibraries](#test/unit_tests/test_migrate_db_v4.TestMigrateDatabaseLibraries)
    * [setUp](#test/unit_tests/test_migrate_db_v4.TestMigrateDatabaseLibraries.setUp)
    * [tearDown](#test/unit_tests/test_migrate_db_v4.TestMigrateDatabaseLibraries.tearDown)
    * [test\_migrate\_versions\_3\_to\_4\_happy\_path](#test/unit_tests/test_migrate_db_v4.TestMigrateDatabaseLibraries.test_migrate_versions_3_to_4_happy_path)
* [test/unit\_tests/test\_migrate\_db\_v3](#test/unit_tests/test_migrate_db_v3)
  * [TestMigrateDatabaseLibraries](#test/unit_tests/test_migrate_db_v3.TestMigrateDatabaseLibraries)
    * [setUp](#test/unit_tests/test_migrate_db_v3.TestMigrateDatabaseLibraries.setUp)
    * [tearDown](#test/unit_tests/test_migrate_db_v3.TestMigrateDatabaseLibraries.tearDown)
    * [test\_migrate\_versions\_2\_to\_3\_happy\_path](#test/unit_tests/test_migrate_db_v3.TestMigrateDatabaseLibraries.test_migrate_versions_2_to_3_happy_path)
* [test/unit\_tests/test\_migrate\_db\_v2](#test/unit_tests/test_migrate_db_v2)
  * [TestMigrateDatabaseLibraries](#test/unit_tests/test_migrate_db_v2.TestMigrateDatabaseLibraries)
    * [setUp](#test/unit_tests/test_migrate_db_v2.TestMigrateDatabaseLibraries.setUp)
    * [tearDown](#test/unit_tests/test_migrate_db_v2.TestMigrateDatabaseLibraries.tearDown)
    * [test\_migrate\_versions\_1\_to\_2\_happy\_path](#test/unit_tests/test_migrate_db_v2.TestMigrateDatabaseLibraries.test_migrate_versions_1_to_2_happy_path)
* [test/unit\_tests/test\_migrate\_db](#test/unit_tests/test_migrate_db)
  * [TestMigrateDatabaseLibraries](#test/unit_tests/test_migrate_db.TestMigrateDatabaseLibraries)
    * [setUp](#test/unit_tests/test_migrate_db.TestMigrateDatabaseLibraries.setUp)
    * [tearDown](#test/unit_tests/test_migrate_db.TestMigrateDatabaseLibraries.tearDown)
    * [test\_perform\_migration\_happy\_path](#test/unit_tests/test_migrate_db.TestMigrateDatabaseLibraries.test_perform_migration_happy_path)
* [test/unit\_tests/test\_orca\_reconcile\_sql](#test/unit_tests/test_orca_reconcile_sql)
  * [TestOrcaSqlLogic](#test/unit_tests/test_orca_reconcile_sql.TestOrcaSqlLogic)
    * [test\_all\_functions\_return\_text](#test/unit_tests/test_orca_reconcile_sql.TestOrcaSqlLogic.test_all_functions_return_text)
* [test/unit\_tests/test\_orca\_sql](#test/unit_tests/test_orca_sql)
  * [TestOrcaSqlLogic](#test/unit_tests/test_orca_sql.TestOrcaSqlLogic)
    * [test\_app\_user\_sql\_happy\_path](#test/unit_tests/test_orca_sql.TestOrcaSqlLogic.test_app_user_sql_happy_path)
    * [test\_app\_user\_sql\_exceptions](#test/unit_tests/test_orca_sql.TestOrcaSqlLogic.test_app_user_sql_exceptions)
    * [test\_all\_functions\_return\_text](#test/unit_tests/test_orca_sql.TestOrcaSqlLogic.test_all_functions_return_text)
* [test/unit\_tests/test\_migrate\_sql\_v4](#test/unit_tests/test_migrate_sql_v4)
  * [TestOrcaSqlLogic](#test/unit_tests/test_migrate_sql_v4.TestOrcaSqlLogic)
    * [test\_all\_functions\_return\_text](#test/unit_tests/test_migrate_sql_v4.TestOrcaSqlLogic.test_all_functions_return_text)
* [test/manual\_tests/manual\_test](#test/manual_tests/manual_test)
  * [set\_search\_path](#test/manual_tests/manual_test.set_search_path)
  * [get\_configuration](#test/manual_tests/manual_test.get_configuration)
* [db\_deploy](#db_deploy)
  * [handler](#db_deploy.handler)
  * [task](#db_deploy.task)
  * [app\_db\_exists](#db_deploy.app_db_exists)
  * [app\_schema\_exists](#db_deploy.app_schema_exists)
  * [app\_version\_table\_exists](#db_deploy.app_version_table_exists)
  * [get\_migration\_version](#db_deploy.get_migration_version)

<a name="migrations/migrate_versions_2_to_3/migrate_db_v3"></a>
# migrations/migrate\_versions\_2\_to\_3/migrate\_db\_v3

Name: migrate_db_v3.py

Description: Migrates the ORCA schema from version 2 to version 3.

<a name="migrations/migrate_versions_2_to_3/migrate_db_v3.migrate_versions_2_to_3"></a>
#### migrate\_versions\_2\_to\_3

```python
migrate_versions_2_to_3(config: Dict[str, str], is_latest_version: bool) -> None
```

Performs the migration of the ORCA schema from version 2 to version 3 of
the ORCA schema.

**Arguments**:

- `config` _Dict_ - Connection information for the database.
- `is_latest_version` _bool_ - Flag to determine if version 3 is the latest schema version.

<a name="migrations/migrate_versions_2_to_3/migrate_sql_v3"></a>
# migrations/migrate\_versions\_2\_to\_3/migrate\_sql\_v3

Name: orca_sql_v3.py

Description: All of the SQL used for creating and migrating the ORCA schema to version 3.

<a name="migrations/migrate_versions_2_to_3/migrate_sql_v3.add_multipart_chunksize_sql"></a>
#### add\_multipart\_chunksize\_sql

```python
add_multipart_chunksize_sql() -> TextClause
```

SQL that adds the multipart_chunksize_mb column to recovery_file.

Returns: SQL for adding multipart_chunksize_mb.

<a name="migrations/migrate_versions_2_to_3/migrate_sql_v3.schema_versions_data_sql"></a>
#### schema\_versions\_data\_sql

```python
schema_versions_data_sql() -> TextClause
```

Data for the schema_versions table. Inserts the current schema
version into the table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for populating schema_versions table.

<a name="migrations/migrate_versions_3_to_4/migrate_sql_v4"></a>
# migrations/migrate\_versions\_3\_to\_4/migrate\_sql\_v4

Name: orca_sql_v4.py

Description: All of the SQL used for creating and migrating the ORCA schema to version 4.

<a name="migrations/migrate_versions_3_to_4/migrate_sql_v4.providers_table_sql"></a>
#### providers\_table\_sql

```python
providers_table_sql() -> TextClause
```

Full SQL for creating the providers table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating providers table.

<a name="migrations/migrate_versions_3_to_4/migrate_sql_v4.collections_table_sql"></a>
#### collections\_table\_sql

```python
collections_table_sql() -> TextClause
```

Full SQL for creating the collections table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating collections table.

<a name="migrations/migrate_versions_3_to_4/migrate_sql_v4.granules_table_sql"></a>
#### granules\_table\_sql

```python
granules_table_sql() -> TextClause
```

Full SQL for creating the catalog granules table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating granules table.

<a name="migrations/migrate_versions_3_to_4/migrate_sql_v4.files_table_sql"></a>
#### files\_table\_sql

```python
files_table_sql() -> TextClause
```

Full SQL for creating the catalog files table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating files table.

<a name="migrations/migrate_versions_3_to_4/migrate_sql_v4.schema_versions_data_sql"></a>
#### schema\_versions\_data\_sql

```python
schema_versions_data_sql() -> TextClause
```

Data for the schema_versions table. Inserts the current schema
version into the table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for populating schema_versions table.

<a name="migrations/migrate_versions_3_to_4/migrate_db_v4"></a>
# migrations/migrate\_versions\_3\_to\_4/migrate\_db\_v4

Name: migrate_db_v4.py

Description: Migrates the ORCA schema from version 3 to version 4.

<a name="migrations/migrate_versions_3_to_4/migrate_db_v4.migrate_versions_3_to_4"></a>
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

<a name="migrations/migrate_db"></a>
# migrations/migrate\_db

Name: migrate_db.py

Description: Migrates the current ORCA schema version to the latest version.

<a name="migrations/migrate_db.perform_migration"></a>
#### perform\_migration

```python
perform_migration(current_schema_version: int, config: Dict[str, str]) -> None
```

Performs a migration of the ORCA database. Determines the order and
migrations to run.

**Arguments**:

- `current_schema_version` _int_ - Current version of the ORCA schema
- `config` _Dict_ - Dictionary containing database connection information
  

**Returns**:

  None

<a name="migrations/migrate_versions_1_to_2/migrate_db_v2"></a>
# migrations/migrate\_versions\_1\_to\_2/migrate\_db\_v2

Name: migrate_db_v2.py

Description: Migrates the ORCA schema from version 1 to version 2.

<a name="migrations/migrate_versions_1_to_2/migrate_db_v2.migrate_versions_1_to_2"></a>
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

<a name="migrations/migrate_versions_1_to_2/migrate_sql_v2"></a>
# migrations/migrate\_versions\_1\_to\_2/migrate\_sql\_v2

Name: orca_sql_v2.py

Description: All of the SQL used for creating and migrating the ORCA schema to version 2.

<a name="migrations/migrate_versions_1_to_2/migrate_sql_v2.dbo_role_sql"></a>
#### dbo\_role\_sql

```python
dbo_role_sql(db_name: str) -> TextClause
```

Full SQL for creating the ORCA dbo role that owns the ORCA schema and
objects.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating orca_dbo role.

<a name="migrations/migrate_versions_1_to_2/migrate_sql_v2.app_role_sql"></a>
#### app\_role\_sql

```python
app_role_sql(db_name: str) -> TextClause
```

Full SQL for creating the ORCA application role that has all the privileges
to interact with the ORCA schema.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating orca_app role.

<a name="migrations/migrate_versions_1_to_2/migrate_sql_v2.orca_schema_sql"></a>
#### orca\_schema\_sql

```python
orca_schema_sql() -> TextClause
```

Full SQL for creating the ORCA application schema that contains all the
ORCA tables and objects. This SQL must be used after the dbo_role_sql and
before the app_user_sql and ORCA objects.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating orca schema.

<a name="migrations/migrate_versions_1_to_2/migrate_sql_v2.app_user_sql"></a>
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

<a name="migrations/migrate_versions_1_to_2/migrate_sql_v2.schema_versions_table_sql"></a>
#### schema\_versions\_table\_sql

```python
schema_versions_table_sql() -> TextClause
```

Full SQL for creating the schema_versions table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating schema_versions table.

<a name="migrations/migrate_versions_1_to_2/migrate_sql_v2.schema_versions_data_sql"></a>
#### schema\_versions\_data\_sql

```python
schema_versions_data_sql() -> TextClause
```

Data for the schema_versions table. Inserts the current schema
version into the table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for populating schema_versions table.

<a name="migrations/migrate_versions_1_to_2/migrate_sql_v2.recovery_status_table_sql"></a>
#### recovery\_status\_table\_sql

```python
recovery_status_table_sql() -> TextClause
```

Full SQL for creating the recovery_status table. This SQL must be run
before any of the other recovery table sql.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating recovery_status table.

<a name="migrations/migrate_versions_1_to_2/migrate_sql_v2.recovery_status_data_sql"></a>
#### recovery\_status\_data\_sql

```python
recovery_status_data_sql() -> TextClause
```

Data for the recovery_status table. Inserts the current status values into
the table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for populating recovery_status table.

<a name="migrations/migrate_versions_1_to_2/migrate_sql_v2.recovery_job_table_sql"></a>
#### recovery\_job\_table\_sql

```python
recovery_job_table_sql() -> TextClause
```

Full SQL for creating the recovery_job table. This SQL must be run
before the other recovery_file table sql and after the recovery_status
table sql to maintain key dependencies.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating recovery_job table.

<a name="migrations/migrate_versions_1_to_2/migrate_sql_v2.recovery_file_table_sql"></a>
#### recovery\_file\_table\_sql

```python
recovery_file_table_sql() -> TextClause
```

Full SQL for creating the recovery_file table. This SQL must be run
after the recovery_job table sql to maintain key dependencies.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating recovery_file table.

<a name="migrations/migrate_versions_1_to_2/migrate_sql_v2.migrate_recovery_job_data_sql"></a>
#### migrate\_recovery\_job\_data\_sql

```python
migrate_recovery_job_data_sql() -> TextClause
```

SQL that migrates data from the old dr.request_status table to the new
orca.recovery_job table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for populating recovery_job table.

<a name="migrations/migrate_versions_1_to_2/migrate_sql_v2.migrate_recovery_file_data_sql"></a>
#### migrate\_recovery\_file\_data\_sql

```python
migrate_recovery_file_data_sql() -> TextClause
```

SQL that migrates data from the old dr.request_status table to the new
orca.recovery_file table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for populating recovery_file table.

<a name="migrations/migrate_versions_1_to_2/migrate_sql_v2.drop_request_status_table_sql"></a>
#### drop\_request\_status\_table\_sql

```python
drop_request_status_table_sql() -> TextClause
```

SQL that removes the dr.request_status table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for dropping request_status table.

<a name="migrations/migrate_versions_1_to_2/migrate_sql_v2.drop_dr_schema_sql"></a>
#### drop\_dr\_schema\_sql

```python
drop_dr_schema_sql() -> TextClause
```

SQL that removes the dr schema.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for dropping dr schema.

<a name="migrations/migrate_versions_1_to_2/migrate_sql_v2.drop_druser_user_sql"></a>
#### drop\_druser\_user\_sql

```python
drop_druser_user_sql() -> TextClause
```

SQL that removes the druser user.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for dropping druser user.

<a name="migrations/migrate_versions_1_to_2/migrate_sql_v2.drop_dbo_user_sql"></a>
#### drop\_dbo\_user\_sql

```python
drop_dbo_user_sql(db_name: str) -> TextClause
```

SQL that removes the dbo user.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for dropping dbo user.

<a name="migrations/migrate_versions_1_to_2/migrate_sql_v2.drop_dr_role_sql"></a>
#### drop\_dr\_role\_sql

```python
drop_dr_role_sql(db_name: str) -> TextClause
```

SQL that removes the dr_role role.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for dropping dr_role role.

<a name="migrations/migrate_versions_1_to_2/migrate_sql_v2.drop_drdbo_role_sql"></a>
#### drop\_drdbo\_role\_sql

```python
drop_drdbo_role_sql(db_name: str) -> TextClause
```

SQL that removes the drdbo_role role.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for dropping drdbo_role role.
  f

<a name="install/orca_reconcile_sql"></a>
# install/orca\_reconcile\_sql

Name: orca_reconcile_sql.py

Description: All of the SQL used for creating the internal reconciliation tables.

<a name="install/orca_reconcile_sql.reconcile_status_table_sql"></a>
#### reconcile\_status\_table\_sql

```python
reconcile_status_table_sql() -> TextClause
```

Full SQL for creating the reconcile_status table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating reconcile_status table.

<a name="install/orca_reconcile_sql.reconcile_job_table_sql"></a>
#### reconcile\_job\_table\_sql

```python
reconcile_job_table_sql() -> TextClause
```

Full SQL for creating the reconcile_job table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating reconcile_job table.

<a name="install/orca_reconcile_sql.reconcile_s3_object_table_sql"></a>
#### reconcile\_s3\_object\_table\_sql

```python
reconcile_s3_object_table_sql() -> TextClause
```

Full SQL for creating the reconcile_s3_object table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating reconcile_s3_object table.

<a name="install/orca_reconcile_sql.reconcile_catalog_mismatch_report_table_sql"></a>
#### reconcile\_catalog\_mismatch\_report\_table\_sql

```python
reconcile_catalog_mismatch_report_table_sql() -> TextClause
```

Full SQL for creating the reconcile_catalog_mismatch_report table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating reconcile_catalog_mismatch_report table.

<a name="install/orca_reconcile_sql.reconcile_orphan_report_table_sql"></a>
#### reconcile\_orphan\_report\_table\_sql

```python
reconcile_orphan_report_table_sql() -> TextClause
```

Full SQL for creating the reconcile_orphan_report table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating reconcile_orphan_report table.

<a name="install/orca_reconcile_sql.reconcile_phantom_report_table_sql"></a>
#### reconcile\_phantom\_report\_table\_sql

```python
reconcile_phantom_report_table_sql() -> TextClause
```

Full SQL for creating the reconcile_phantom_report table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating reconcile_phantom_report table.

<a name="install/orca_reconcile_sql.orca_archive_location_bucket"></a>
#### orca\_archive\_location\_bucket

```python
orca_archive_location_bucket() -> TextClause
```

Full SQL for creating the orca_archive_location_bucket table.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating orca_archive_location_bucket table.

<a name="install/orca_reconcile_sql.create_extension"></a>
#### create\_extension

```python
create_extension() -> TextClause
```

Full SQL for creating the extension.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for creating extension for the database.

<a name="install/orca_reconcile_sql.drop_extension"></a>
#### drop\_extension

```python
drop_extension() -> TextClause
```

Full SQL for dropping the extension.

**Returns**:

- `(sqlalchemy.sql.element.TextClause)` - SQL for dropping extension for the database.

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

<a name="install/create_db"></a>
# install/create\_db

Name: create_db.py

Description: Creates the current version on the ORCA database.

<a name="install/create_db.create_fresh_orca_install"></a>
#### create\_fresh\_orca\_install

```python
create_fresh_orca_install(config: Dict[str, str]) -> None
```

This task will create the ORCA roles, users, schema, and tables needed
by the ORCA application as a fresh install.

**Arguments**:

- `config` _Dict_ - Dictionary with database connection information
  

**Returns**:

  None

<a name="install/create_db.create_database"></a>
#### create\_database

```python
create_database(config: Dict[str,str]) -> None
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

Creates the ORCA catalog metadata tables used for reconciliation with Cumulus in the proper order.
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
create_internal_reconciliation_objects(connection: Connection) -> None
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
  

**Returns**:

  None

<a name="test/unit_tests/test_migrate_sql_v3"></a>
# test/unit\_tests/test\_migrate\_sql\_v3

Name: test_migrate_sql_v3.py

Description: Testing library for the migrations/migrate_versions_2_to_3/migrate_sql_v3.py.

<a name="test/unit_tests/test_migrate_sql_v3.TestOrcaSqlLogic"></a>
## TestOrcaSqlLogic Objects

```python
class TestOrcaSqlLogic(unittest.TestCase)
```

Note that currently all of the function calls in the migrate_sql_v3.py
return a SQL text string. The tests below
validate the logic in the function.

<a name="test/unit_tests/test_migrate_sql_v3.TestOrcaSqlLogic.test_all_functions_return_text"></a>
#### test\_all\_functions\_return\_text

```python
 | test_all_functions_return_text() -> None
```

Validates that all functions return a type TextClause

<a name="test/unit_tests/test_db_deploy"></a>
# test/unit\_tests/test\_db\_deploy

Name: test_db_deploy.py

Description:  Unit tests for db_deploy.py.

<a name="test/unit_tests/test_db_deploy.TestDbDeployFunctions"></a>
## TestDbDeployFunctions Objects

```python
class TestDbDeployFunctions(unittest.TestCase)
```

Tests the db_deploy functions.

<a name="test/unit_tests/test_db_deploy.TestDbDeployFunctions.setUp"></a>
#### setUp

```python
 | setUp()
```

Perform initial setup for test.

<a name="test/unit_tests/test_db_deploy.TestDbDeployFunctions.tearDown"></a>
#### tearDown

```python
 | tearDown()
```

Perform tear down actions

<a name="test/unit_tests/test_db_deploy.TestDbDeployFunctions.test_handler_happy_path"></a>
#### test\_handler\_happy\_path

```python
 | @patch.dict(
 |         os.environ,
 |         {
 |             "PREFIX": "orcatest",
 |             "AWS_REGION": "us-west-2",
 |         },
 |         clear=True,
 |     )
 | @patch("db_deploy.task")
 | test_handler_happy_path(mock_task: MagicMock)
```

Does a happy path test. No real logic here as it just sets up the
Cumulus Logger and the database configuration which are tested in
other test cases.

<a name="test/unit_tests/test_db_deploy.TestDbDeployFunctions.test_task_no_database"></a>
#### test\_task\_no\_database

```python
 | @patch("db_deploy.create_fresh_orca_install")
 | @patch("db_deploy.create_database")
 | @patch("db_deploy.get_admin_connection")
 | @patch("db_deploy.app_db_exists")
 | test_task_no_database(mock_app_db_exists: MagicMock, mock_connection: MagicMock, mock_create_database: MagicMock, mock_create_fresh_orca_install: MagicMock)
```

Validates if the ORCA database does not exist, then it is created.

<a name="test/unit_tests/test_db_deploy.TestDbDeployFunctions.test_task_no_schema"></a>
#### test\_task\_no\_schema

```python
 | @patch("db_deploy.get_admin_connection")
 | @patch("db_deploy.create_fresh_orca_install")
 | @patch("db_deploy.app_schema_exists")
 | @patch("db_deploy.app_db_exists")
 | test_task_no_schema(mock_db_exists: MagicMock, mock_schema_exists: MagicMock, mock_fresh_install: MagicMock, mock_connection: MagicMock)
```

Validates that `create_fresh_orca_install` is called if no ORCA schema
are present.

<a name="test/unit_tests/test_db_deploy.TestDbDeployFunctions.test_task_schmea_old_version"></a>
#### test\_task\_schmea\_old\_version

```python
 | @patch("db_deploy.get_admin_connection")
 | @patch("db_deploy.perform_migration")
 | @patch("db_deploy.get_migration_version")
 | @patch("db_deploy.app_schema_exists")
 | @patch("db_deploy.app_db_exists")
 | test_task_schmea_old_version(mock_db_exists: MagicMock, mock_schema_exists: MagicMock, mock_migration_version: MagicMock, mock_perform_migration: MagicMock, mock_connection: MagicMock)
```

Validates that `perform_migration` is called if the current schema
version is older than the latest version.

<a name="test/unit_tests/test_db_deploy.TestDbDeployFunctions.test_task_schema_current_version"></a>
#### test\_task\_schema\_current\_version

```python
 | @patch("db_deploy.get_admin_connection")
 | @patch("db_deploy.logger.info")
 | @patch("db_deploy.get_migration_version")
 | @patch("db_deploy.app_schema_exists")
 | @patch("db_deploy.app_db_exists")
 | test_task_schema_current_version(mock_db_exists: MagicMock, mock_schema_exists: MagicMock, mock_migration_version: MagicMock, mock_logger_info: MagicMock, mock_connection: MagicMock)
```

validates that no action is taken if the current and latest versions
are the same.

<a name="test/unit_tests/test_db_deploy.TestDbDeployFunctions.test_app_db_exists_happy_path"></a>
#### test\_app\_db\_exists\_happy\_path

```python
 | test_app_db_exists_happy_path()
```

Does a happy path test for the function. No real logic to test.

<a name="test/unit_tests/test_db_deploy.TestDbDeployFunctions.test_app_schema_exists_happy_path"></a>
#### test\_app\_schema\_exists\_happy\_path

```python
 | test_app_schema_exists_happy_path()
```

Does a happy path test for the function. No real logic to test.

<a name="test/unit_tests/test_db_deploy.TestDbDeployFunctions.test_app_versions_table_exists_happy_path"></a>
#### test\_app\_versions\_table\_exists\_happy\_path

```python
 | test_app_versions_table_exists_happy_path()
```

Does a happy path test for the function. No real logic to test.

<a name="test/unit_tests/test_db_deploy.TestDbDeployFunctions.test_get_migration_version_happy_path"></a>
#### test\_get\_migration\_version\_happy\_path

```python
 | @patch("db_deploy.app_version_table_exists")
 | test_get_migration_version_happy_path(mock_table_exists)
```

Does a happy path test for the function. No real logic to test.

<a name="test/unit_tests/test_migrate_sql_v2"></a>
# test/unit\_tests/test\_migrate\_sql\_v2

Name: test_migrate_sql_v2.py

Description: Unit tests for the migrations/migrate_versions_1_to_2/migrate_sql_v2.py.

<a name="test/unit_tests/test_migrate_sql_v2.TestOrcaSqlLogic"></a>
## TestOrcaSqlLogic Objects

```python
class TestOrcaSqlLogic(unittest.TestCase)
```

Note that currently all of the function calls in the migrate_sql_v2.py
return a SQL text string and have no logic except for the app_user_sql
function that requires a string for the user password. The tests below
validate the logic in the function.

<a name="test/unit_tests/test_migrate_sql_v2.TestOrcaSqlLogic.test_app_user_sql_happy_path"></a>
#### test\_app\_user\_sql\_happy\_path

```python
 | test_app_user_sql_happy_path() -> None
```

Tests the happy path for the app_user_sql function and validates the
user password is a part of the SQL.

<a name="test/unit_tests/test_migrate_sql_v2.TestOrcaSqlLogic.test_app_user_sql_exceptions"></a>
#### test\_app\_user\_sql\_exceptions

```python
 | test_app_user_sql_exceptions() -> None
```

Tests that an exception is thrown if the password is not set or is not
a minimum of 12 characters,
or if user_name is not set or is over 64 characters.

<a name="test/unit_tests/test_migrate_sql_v2.TestOrcaSqlLogic.test_all_functions_return_text"></a>
#### test\_all\_functions\_return\_text

```python
 | test_all_functions_return_text() -> None
```

Validates that all functions return a type TextClause

<a name="test/unit_tests/test_create_db"></a>
# test/unit\_tests/test\_create\_db

Name: test_create_db.py

Description: Runs unit tests for the create_db.py library.

<a name="test/unit_tests/test_create_db.TestCreateDatabaseLibraries"></a>
## TestCreateDatabaseLibraries Objects

```python
class TestCreateDatabaseLibraries(unittest.TestCase)
```

Test the various functions in the create_db library.

<a name="test/unit_tests/test_create_db.TestCreateDatabaseLibraries.setUp"></a>
#### setUp

```python
 | setUp()
```

Set up test.

<a name="test/unit_tests/test_create_db.TestCreateDatabaseLibraries.tearDown"></a>
#### tearDown

```python
 | tearDown()
```

Tear down test

<a name="test/unit_tests/test_create_db.TestCreateDatabaseLibraries.test_create_fresh_orca_install_happy_path"></a>
#### test\_create\_fresh\_orca\_install\_happy\_path

```python
 | @patch("install.create_db.create_recovery_objects")
 | @patch("install.create_db.create_metadata_objects")
 | @patch("install.create_db.create_inventory_objects")
 | @patch("install.create_db.create_internal_reconciliation_objects")
 | @patch("install.create_db.set_search_path_and_role")
 | @patch("install.create_db.create_app_schema_role_users")
 | @patch("install.create_db.get_admin_connection")
 | test_create_fresh_orca_install_happy_path(mock_connection: MagicMock, mock_create_app_schema_roles: MagicMock, mock_set_search_path_role: MagicMock, mock_create_internal_reconciliation_objects: MagicMock, mock_create_inventory_objects: MagicMock, mock_create_metadata: MagicMock, mock_create_recovery: MagicMock)
```

Tests normal happy path of create_fresh_orca_install function.

<a name="test/unit_tests/test_create_db.TestCreateDatabaseLibraries.test_create_database_happy_path"></a>
#### test\_create\_database\_happy\_path

```python
 | @patch("install.orca_sql.app_database_comment_sql")
 | @patch("install.orca_sql.app_database_sql")
 | @patch("install.orca_sql.commit_sql")
 | @patch("install.create_db.get_admin_connection")
 | test_create_database_happy_path(mock_connection: MagicMock, mock_commit_sql: MagicMock, mock_app_database_sql: MagicMock, mock_app_database_comment_sql: MagicMock)
```

Tests normal happy path of create_database function.

<a name="test/unit_tests/test_create_db.TestCreateDatabaseLibraries.test_create_app_schema_user_role_users_happy_path"></a>
#### test\_create\_app\_schema\_user\_role\_users\_happy\_path

```python
 | @patch("install.create_db.sql.app_user_sql")
 | @patch("install.create_db.sql.orca_schema_sql")
 | @patch("install.create_db.sql.app_role_sql")
 | @patch("install.create_db.sql.dbo_role_sql")
 | test_create_app_schema_user_role_users_happy_path(mock_dbo_role_sql: MagicMock, mock_app_role_sql: MagicMock, mock_schema_sql: MagicMock, mock_user_sql: MagicMock)
```

Tests happy path of create_app_schema_role_users function.

<a name="test/unit_tests/test_create_db.TestCreateDatabaseLibraries.test_set_search_path_and_role"></a>
#### test\_set\_search\_path\_and\_role

```python
 | @patch("install.create_db.sql.text")
 | test_set_search_path_and_role(mock_text: MagicMock)
```

Tests happy path of set_search_path_and_role function.

<a name="test/unit_tests/test_create_db.TestCreateDatabaseLibraries.test_create_metadata_objects"></a>
#### test\_create\_metadata\_objects

```python
 | @patch("install.create_db.sql.schema_versions_data_sql")
 | @patch("install.create_db.sql.schema_versions_table_sql")
 | test_create_metadata_objects(mock_schema_versions_table: MagicMock, mock_schema_versions_data: MagicMock)
```

Tests happy path of create_metadata_objects function

<a name="test/unit_tests/test_create_db.TestCreateDatabaseLibraries.test_create_recovery_objects"></a>
#### test\_create\_recovery\_objects

```python
 | @patch("install.create_db.sql.recovery_file_table_sql")
 | @patch("install.create_db.sql.recovery_job_table_sql")
 | @patch("install.create_db.sql.recovery_status_data_sql")
 | @patch("install.create_db.sql.recovery_status_table_sql")
 | test_create_recovery_objects(mock_recovery_status_table: MagicMock, mock_recovery_status_data: MagicMock, mock_recovery_job_table: MagicMock, mock_recovery_file_table: MagicMock)
```

Tests happy path of the create_recovery_objects function

<a name="test/unit_tests/test_create_db.TestCreateDatabaseLibraries.test_create_inventory_objects"></a>
#### test\_create\_inventory\_objects

```python
 | @patch("install.create_db.sql.providers_table_sql")
 | @patch("install.create_db.sql.collections_table_sql")
 | @patch("install.create_db.sql.granules_table_sql")
 | @patch("install.create_db.sql.files_table_sql")
 | test_create_inventory_objects(mock_files_table: MagicMock, mock_granules_table: MagicMock, mock_collections_table: MagicMock, mock_providers_table: MagicMock)
```

Tests happy path of the create_inventory_objects function

<a name="test/unit_tests/test_migrate_db_v4"></a>
# test/unit\_tests/test\_migrate\_db\_v4

Name: test_migrate_db_v4.py

Description: Runs unit tests for the migrations/migrate_versions_3_to_4/migrate_db_v4.py

<a name="test/unit_tests/test_migrate_db_v4.TestMigrateDatabaseLibraries"></a>
## TestMigrateDatabaseLibraries Objects

```python
class TestMigrateDatabaseLibraries(unittest.TestCase)
```

Runs unit tests on the migrate_db functions.

<a name="test/unit_tests/test_migrate_db_v4.TestMigrateDatabaseLibraries.setUp"></a>
#### setUp

```python
 | setUp()
```

Set up test.

<a name="test/unit_tests/test_migrate_db_v4.TestMigrateDatabaseLibraries.tearDown"></a>
#### tearDown

```python
 | tearDown()
```

Tear down test

<a name="test/unit_tests/test_migrate_db_v4.TestMigrateDatabaseLibraries.test_migrate_versions_3_to_4_happy_path"></a>
#### test\_migrate\_versions\_3\_to\_4\_happy\_path

```python
 | @patch("migrations.migrate_versions_3_to_4.migrate_db_v4.sql.schema_versions_data_sql")
 | @patch("migrations.migrate_versions_3_to_4.migrate_db_v4.sql.providers_table_sql")
 | @patch("migrations.migrate_versions_3_to_4.migrate_db_v4.sql.collections_table_sql")
 | @patch("migrations.migrate_versions_3_to_4.migrate_db_v4.sql.granules_table_sql")
 | @patch("migrations.migrate_versions_3_to_4.migrate_db_v4.sql.files_table_sql")
 | @patch("migrations.migrate_versions_3_to_4.migrate_db_v4.get_admin_connection")
 | @patch("migrations.migrate_versions_3_to_4.migrate_db_v4.sql.text")
 | test_migrate_versions_3_to_4_happy_path(mock_text: MagicMock, mock_connection: MagicMock, mock_files_table: MagicMock, mock_granules_table: MagicMock, mock_collections_table: MagicMock, mock_providers_table: MagicMock, mock_schema_versions_data: MagicMock)
```

Tests the migrate_versions_3_to_4 function happy path

<a name="test/unit_tests/test_migrate_db_v3"></a>
# test/unit\_tests/test\_migrate\_db\_v3

Name: test_migrate_db_v3.py

Description: Runs unit tests for the migrations/migrate_versions_2_to_3/migrate_db_v3.py

<a name="test/unit_tests/test_migrate_db_v3.TestMigrateDatabaseLibraries"></a>
## TestMigrateDatabaseLibraries Objects

```python
class TestMigrateDatabaseLibraries(unittest.TestCase)
```

Runs unit tests on the migrate_db functions.

<a name="test/unit_tests/test_migrate_db_v3.TestMigrateDatabaseLibraries.setUp"></a>
#### setUp

```python
 | setUp()
```

Set up test.

<a name="test/unit_tests/test_migrate_db_v3.TestMigrateDatabaseLibraries.tearDown"></a>
#### tearDown

```python
 | tearDown()
```

Tear down test

<a name="test/unit_tests/test_migrate_db_v3.TestMigrateDatabaseLibraries.test_migrate_versions_2_to_3_happy_path"></a>
#### test\_migrate\_versions\_2\_to\_3\_happy\_path

```python
 | @patch("migrations.migrate_versions_2_to_3.migrate_db_v3.sql.text")
 | @patch("migrations.migrate_versions_2_to_3.migrate_db_v3.sql.schema_versions_data_sql")
 | @patch("migrations.migrate_versions_2_to_3.migrate_db_v3.sql.add_multipart_chunksize_sql")
 | @patch("migrations.migrate_versions_2_to_3.migrate_db_v3.get_admin_connection")
 | test_migrate_versions_2_to_3_happy_path(mock_connection: MagicMock, mock_add_multipart_chunksize_sql: MagicMock, mock_schema_versions_data: MagicMock, mock_text: MagicMock)
```

Tests the migrate_versions_2_to_3 function happy path

<a name="test/unit_tests/test_migrate_db_v2"></a>
# test/unit\_tests/test\_migrate\_db\_v2

Name: test_migrate_db_v2.py

Description: Runs unit tests for the migrations/migrate_versions_1_to_2/migrate_db_v2.py

<a name="test/unit_tests/test_migrate_db_v2.TestMigrateDatabaseLibraries"></a>
## TestMigrateDatabaseLibraries Objects

```python
class TestMigrateDatabaseLibraries(unittest.TestCase)
```

Runs unit tests on the migrate_db functions.

<a name="test/unit_tests/test_migrate_db_v2.TestMigrateDatabaseLibraries.setUp"></a>
#### setUp

```python
 | setUp()
```

Set up test.

<a name="test/unit_tests/test_migrate_db_v2.TestMigrateDatabaseLibraries.tearDown"></a>
#### tearDown

```python
 | tearDown()
```

Tear down test

<a name="test/unit_tests/test_migrate_db_v2.TestMigrateDatabaseLibraries.test_migrate_versions_1_to_2_happy_path"></a>
#### test\_migrate\_versions\_1\_to\_2\_happy\_path

```python
 | @patch("migrations.migrate_versions_1_to_2.migrate_db_v2.sql.schema_versions_data_sql")
 | @patch("migrations.migrate_versions_1_to_2.migrate_db_v2.sql.drop_druser_user_sql")
 | @patch("migrations.migrate_versions_1_to_2.migrate_db_v2.sql.drop_dbo_user_sql")
 | @patch("migrations.migrate_versions_1_to_2.migrate_db_v2.sql.drop_dr_role_sql")
 | @patch("migrations.migrate_versions_1_to_2.migrate_db_v2.sql.drop_drdbo_role_sql")
 | @patch("migrations.migrate_versions_1_to_2.migrate_db_v2.sql.drop_dr_schema_sql")
 | @patch("migrations.migrate_versions_1_to_2.migrate_db_v2.sql.drop_request_status_table_sql")
 | @patch("migrations.migrate_versions_1_to_2.migrate_db_v2.sql.migrate_recovery_file_data_sql")
 | @patch("migrations.migrate_versions_1_to_2.migrate_db_v2.sql.migrate_recovery_job_data_sql")
 | @patch("migrations.migrate_versions_1_to_2.migrate_db_v2.sql.recovery_status_data_sql")
 | @patch("migrations.migrate_versions_1_to_2.migrate_db_v2.sql.recovery_file_table_sql")
 | @patch("migrations.migrate_versions_1_to_2.migrate_db_v2.sql.recovery_job_table_sql")
 | @patch("migrations.migrate_versions_1_to_2.migrate_db_v2.sql.recovery_status_table_sql")
 | @patch("migrations.migrate_versions_1_to_2.migrate_db_v2.sql.schema_versions_table_sql")
 | @patch("migrations.migrate_versions_1_to_2.migrate_db_v2.sql.text")
 | @patch("migrations.migrate_versions_1_to_2.migrate_db_v2.sql.app_user_sql")
 | @patch("migrations.migrate_versions_1_to_2.migrate_db_v2.sql.orca_schema_sql")
 | @patch("migrations.migrate_versions_1_to_2.migrate_db_v2.sql.app_role_sql")
 | @patch("migrations.migrate_versions_1_to_2.migrate_db_v2.sql.dbo_role_sql")
 | @patch("migrations.migrate_versions_1_to_2.migrate_db_v2.get_admin_connection")
 | test_migrate_versions_1_to_2_happy_path(mock_connection: MagicMock, mock_dbo_role_sql: MagicMock, mock_app_role_sql: MagicMock, mock_orca_schema_sql: MagicMock, mock_app_user_sql: MagicMock, mock_text: MagicMock, mock_schema_versions_table: MagicMock, mock_recovery_status_table: MagicMock, mock_recovery_job_table: MagicMock, mock_recovery_file_table: MagicMock, mock_recovery_status_data: MagicMock, mock_recovery_job_data: MagicMock, mock_recovery_file_data: MagicMock, mock_drop_request_status_table: MagicMock, mock_drop_dr_schema: MagicMock, mock_drop_drdbo_role: MagicMock, mock_drop_dr_role: MagicMock, mock_drop_dbo_user: MagicMock, mock_drop_druser_user: MagicMock, mock_schema_versions_data: MagicMock)
```

Tests the migrate_versions_1_to_2 function happy path

<a name="test/unit_tests/test_migrate_db"></a>
# test/unit\_tests/test\_migrate\_db

Name: test_migrate_db.py

Description: Runs unit tests for the migrations/migrate_db.py library.

<a name="test/unit_tests/test_migrate_db.TestMigrateDatabaseLibraries"></a>
## TestMigrateDatabaseLibraries Objects

```python
class TestMigrateDatabaseLibraries(unittest.TestCase)
```

Runs unit tests on the migrate_db functions.

<a name="test/unit_tests/test_migrate_db.TestMigrateDatabaseLibraries.setUp"></a>
#### setUp

```python
 | setUp()
```

Set up test.

<a name="test/unit_tests/test_migrate_db.TestMigrateDatabaseLibraries.tearDown"></a>
#### tearDown

```python
 | tearDown()
```

Tear down test

<a name="test/unit_tests/test_migrate_db.TestMigrateDatabaseLibraries.test_perform_migration_happy_path"></a>
#### test\_perform\_migration\_happy\_path

```python
 | @patch("migrations.migrate_db.migrate_versions_1_to_2")
 | @patch("migrations.migrate_db.migrate_versions_2_to_3")
 | @patch("migrations.migrate_db.migrate_versions_3_to_4")
 | test_perform_migration_happy_path(mock_migrate_v3_to_v4: MagicMock, mock_migrate_v2_to_v3: MagicMock, mock_migrate_v1_to_v2: MagicMock)
```

Tests the perform_migration function happy paths

<a name="test/unit_tests/test_orca_reconcile_sql"></a>
# test/unit\_tests/test\_orca\_reconcile\_sql

Name: test_orca_reconcile_sql.py

Description: Testing library for the orca_reconcile_sql.py.

<a name="test/unit_tests/test_orca_reconcile_sql.TestOrcaSqlLogic"></a>
## TestOrcaSqlLogic Objects

```python
class TestOrcaSqlLogic(unittest.TestCase)
```

Note that currently all of the function calls in the orca_reconcile_sql.py
return a SQL text string. The tests below
validate the logic in the function.

<a name="test/unit_tests/test_orca_reconcile_sql.TestOrcaSqlLogic.test_all_functions_return_text"></a>
#### test\_all\_functions\_return\_text

```python
 | test_all_functions_return_text() -> None
```

Validates that all functions return a type TextClause

<a name="test/unit_tests/test_orca_sql"></a>
# test/unit\_tests/test\_orca\_sql

Name: test_orca_sql.py

Description: Testing library for the orca_sql.py library.

<a name="test/unit_tests/test_orca_sql.TestOrcaSqlLogic"></a>
## TestOrcaSqlLogic Objects

```python
class TestOrcaSqlLogic(unittest.TestCase)
```

Note that currently all of the function calls in the orca_sql library
return a SQL text string and have no logic except for the app_user_sql
function that requires a string for the user password. The tests below
validate the logic in the function.

<a name="test/unit_tests/test_orca_sql.TestOrcaSqlLogic.test_app_user_sql_happy_path"></a>
#### test\_app\_user\_sql\_happy\_path

```python
 | test_app_user_sql_happy_path() -> None
```

Tests the happy path for the app_user_sql function and validates the
user password is a part of the SQL.

<a name="test/unit_tests/test_orca_sql.TestOrcaSqlLogic.test_app_user_sql_exceptions"></a>
#### test\_app\_user\_sql\_exceptions

```python
 | test_app_user_sql_exceptions() -> None
```

Tests that an exception is thrown if the password is not set or is not
a minimum of 12 characters,
or if user_name is not set or is over 64 characters.

<a name="test/unit_tests/test_orca_sql.TestOrcaSqlLogic.test_all_functions_return_text"></a>
#### test\_all\_functions\_return\_text

```python
 | test_all_functions_return_text() -> None
```

Validates that all functions return a type TextClause

<a name="test/unit_tests/test_migrate_sql_v4"></a>
# test/unit\_tests/test\_migrate\_sql\_v4

Name: test_migrate_sql_v4.py

Description: Testing library for the migrations/migrate_versions_3_to_4/migrate_sql_v4.py.

<a name="test/unit_tests/test_migrate_sql_v4.TestOrcaSqlLogic"></a>
## TestOrcaSqlLogic Objects

```python
class TestOrcaSqlLogic(unittest.TestCase)
```

Note that currently all of the function calls in the migrate_sql_v4.py
return a SQL text string. The tests below
validate the logic in the function.

<a name="test/unit_tests/test_migrate_sql_v4.TestOrcaSqlLogic.test_all_functions_return_text"></a>
#### test\_all\_functions\_return\_text

```python
 | test_all_functions_return_text() -> None
```

Validates that all functions return a type TextClause

<a name="test/manual_tests/manual_test"></a>
# test/manual\_tests/manual\_test

Name: manual_test.py

Description: Runs the db_deploy Lambda code to perform manual tests.

<a name="test/manual_tests/manual_test.set_search_path"></a>
#### set\_search\_path

```python
set_search_path()
```

Some silliness we have to do to import the modules.

<a name="test/manual_tests/manual_test.get_configuration"></a>
#### get\_configuration

```python
get_configuration()
```

Sets a static configuration so testing is easy. Only HOST and PASSWORDS
are variable per user. Username is variable for the non-admin user.

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

