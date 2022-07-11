# Manual Testing for the db_deploy Lambda Code

The following document provides the steps and files needed to manually test and
verify the db_deploy application.

To run the tests provided below, run the steps in the [initial setup](#initial-setup)
section first.

It is recommended to run the tests in the following order.
- [Database Migration v1 to v5 Test](#database-migration-v1-to-v5-test)
- [Database No Migration Test](#database-no-migration-test)
- [Database Fresh Install Test](#database-fresh-install-test)
- [Database Exists Install Test](#database-exists-install-test)


## Initial Setup

The initial setup goes over setting up a python virtual environment to test the
code and a PostgreSQL database. All testing is done with Docker, and it is required
to have the latest Docker and Docker Compose application code installed.

It is recommended to have three terminal windows up and available. The windows
needed are:
- Interactive Docker shell to the python environment
- Interactive Docker shell to the postgres client
- Interactive OS shell for logs and troubleshooting

In addition, a GUI based database explorer like Aqua Data Studio or pgAdmin is
helpful for visually inspecting the database users, groups, schema, objects, and
data.

To setup the testing environment perform the following steps.

1. Copy the `env_template` file to a `.env` file and add values to environment
   variables within the new `.env` file.
2. Run the setup script with the `setup` action `./setup_testing.sh setup`. This
   will create the ORCA test database.
3. In a new terminal window run the setup script with the `pgclient` action
   `./setup_testing.sh pgclient`. This will put you in a bash environment
   that can use the psql PostgreSQL client. This window will be called the
   **pgclient** window in the remaining instructions. Run the following commands
   in the **pgclient** window.
   ```bash
   cd /data/tasks/db_deploy/test/manual_tests
   psql
   ```
4. In a new terminal window run the setup script with the `python` action
   `./setup_testing.sh python`. This will put you in a bash environment that
   can use the proper version of python for the tests. This window will be
   called the **python** window in the remaining instructions. In the **python**
   window run the following commands to load the needed libraries for testing
   and put the user in the proper testing directory.
   ```bash
   python3 -m venv venv
   . venv/bin/activate
   cd /data/tasks/db_deploy
   pip install -U pip --trusted-host pypi.org --trusted-host files.pythonhosted.org
   pip install -r requirements-dev.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org
   cd test/manual_tests
   ```


## Tear Down of Environment

Once all tests are complete perform the following:

1. Close the **python** window by typing `exit` at the command prompt.
2. Close the **pgclient** window by quitting psql via the `\q` command and then
   typing `exit` at the command prompt.
3. Shut down PostgreSQL and cleanup by running the `./setup_testing stop` command
   in the setup window. This will also remove the `DATA_DIR` defined in the `.env`
   file.

## Database Fresh Install Test

This test validates that the db_deploy scripts will perform a fresh install if
the server exists without the orca database.

### Database Setup Fresh Install Test

In the **pgclient** window use the `psql` client to connect to the database and
validate that the *orca* database does not exist as seen below.

```bash
root@26df0390e999:/# psql
psql (10.14 (Debian 10.14-1.pgdg90+1))
Type "help" for help.

postgres=# \l
                                 List of databases
   Name    |  Owner   | Encoding |  Collate   |   Ctype    |   Access privileges
-----------+----------+----------+------------+------------+-----------------------
 postgres  | postgres | UTF8     | en_US.utf8 | en_US.utf8 |
 template0 | postgres | UTF8     | en_US.utf8 | en_US.utf8 | =c/postgres          +
           |          |          |            |            | postgres=CTc/postgres
 template1 | postgres | UTF8     | en_US.utf8 | en_US.utf8 | =c/postgres          +
           |          |          |            |            | postgres=CTc/postgres
(3 rows)
```

If the database exists, remove it with the command `\i sql/cleanup.sql`
at the psql prompt.

Verify that only the default users, groups and schemas are present in the postgres
   database.

```bash
postgres=# \dn

  List of schemas
  Name  |  Owner
--------+----------
 public | postgres
(1 row)

postgres=# \dg
                                  List of roles
 Role name |                         Attributes                         | Member of
-----------+------------------------------------------------------------+-----------
 postgres  | Superuser, Create role, Create DB, Replication, Bypass RLS | {}

postgres=# \du
                                  List of roles
 Role name |                         Attributes                         | Member of
-----------+------------------------------------------------------------+-----------
 postgres  | Superuser, Create role, Create DB, Replication, Bypass RLS | {}
```

### Running the Fresh Install Test

To run the fresh install test, in your **python** window run the command
`python manual_test.py`. The output should look similar to below.

```bash
(venv) root@cf4b0741a628:/data/test/manual_tests# python manual_test.py

{"message": "Beginning manual test.", "timestamp": "2022-02-16T20:56:17.479345", "level": "info"}
{"message": "Creating admin user connection object.", "timestamp": "2022-02-16T20:56:17.479536", "level": "debug"}
{"message": "Database set to postgres for the connection.", "timestamp": "2022-02-16T20:56:17.479606", "level": "debug"}
{"message": "Creating URL object to connect to the database.", "timestamp": "2022-02-16T20:56:17.479670", "level": "debug"}
{"message": "Creating admin user connection object.", "timestamp": "2022-02-16T20:56:17.557451", "level": "debug"}
{"message": "Database set to orca for the connection.", "timestamp": "2022-02-16T20:56:17.557579", "level": "debug"}
{"message": "Creating URL object to connect to the database.", "timestamp": "2022-02-16T20:56:17.557651", "level": "debug"}
{"message": "The ORCA database orca does not exist, or the server could not be connected to.", "timestamp": "2022-02-16T20:56:17.675049", "level": "info"}
{"message": "Creating admin user connection object.", "timestamp": "2022-02-16T20:56:17.675189", "level": "debug"}
{"message": "Database set to postgres for the connection.", "timestamp": "2022-02-16T20:56:17.675268", "level": "debug"}
{"message": "Creating URL object to connect to the database.", "timestamp": "2022-02-16T20:56:17.675319", "level": "debug"}
{"message": "Database created.", "timestamp": "2022-02-16T20:56:19.168475", "level": "info"}
{"message": "Creating admin user connection object.", "timestamp": "2022-02-16T20:56:19.169761", "level": "debug"}
{"message": "Database set to orca for the connection.", "timestamp": "2022-02-16T20:56:19.169873", "level": "debug"}
{"message": "Creating URL object to connect to the database.", "timestamp": "2022-02-16T20:56:19.169953", "level": "debug"}
{"message": "Creating the ORCA dbo role ...", "timestamp": "2022-02-16T20:56:19.268274", "level": "debug"}
{"message": "ORCA dbo role created.", "timestamp": "2022-02-16T20:56:19.296273", "level": "info"}
{"message": "Creating the ORCA app role ...", "timestamp": "2022-02-16T20:56:19.296414", "level": "debug"}
{"message": "ORCA app role created.", "timestamp": "2022-02-16T20:56:19.298239", "level": "info"}
{"message": "Creating the ORCA schema ...", "timestamp": "2022-02-16T20:56:19.298338", "level": "debug"}
{"message": "ORCA schema created.", "timestamp": "2022-02-16T20:56:19.321700", "level": "info"}
{"message": "Creating the ORCA application user ...", "timestamp": "2022-02-16T20:56:19.321842", "level": "debug"}
{"message": "ORCA application user created.", "timestamp": "2022-02-16T20:56:19.331646", "level": "info"}
{"message": "Creating extension aws_s3 ...", "timestamp": "2022-02-16T20:56:19.331799", "level": "debug"}
{"message": "extension aws_s3 created.", "timestamp": "2022-02-16T20:56:19.373998", "level": "info"}
{"message": "Changing to the dbo role to create objects ...", "timestamp": "2022-02-16T20:56:19.374137", "level": "debug"}
{"message": "Setting search path to the ORCA schema to create objects ...", "timestamp": "2022-02-16T20:56:19.375289", "level": "debug"}
{"message": "Creating schema_versions table ...", "timestamp": "2022-02-16T20:56:19.376594", "level": "debug"}
{"message": "schema_versions table created.", "timestamp": "2022-02-16T20:56:19.425741", "level": "info"}
{"message": "Populating the schema_versions table with data ...", "timestamp": "2022-02-16T20:56:19.425882", "level": "debug"}
{"message": "Data added to the schema_versions table.", "timestamp": "2022-02-16T20:56:19.436505", "level": "info"}
{"message": "Creating recovery_status table ...", "timestamp": "2022-02-16T20:56:19.436697", "level": "debug"}
{"message": "recovery_status table created.", "timestamp": "2022-02-16T20:56:19.456536", "level": "info"}
{"message": "Populating the recovery_status table with data ...", "timestamp": "2022-02-16T20:56:19.456714", "level": "debug"}
{"message": "Data added to the recovery_status table.", "timestamp": "2022-02-16T20:56:19.466350", "level": "info"}
{"message": "Creating recovery_job table ...", "timestamp": "2022-02-16T20:56:19.466503", "level": "debug"}
{"message": "recovery_job table created.", "timestamp": "2022-02-16T20:56:19.497855", "level": "info"}
{"message": "Creating recovery_file table ...", "timestamp": "2022-02-16T20:56:19.498001", "level": "debug"}
{"message": "recovery_file table created.", "timestamp": "2022-02-16T20:56:19.516014", "level": "info"}
{"message": "Creating providers table ...", "timestamp": "2022-02-16T20:56:19.516186", "level": "debug"}
{"message": "providers table created.", "timestamp": "2022-02-16T20:56:19.541131", "level": "info"}
{"message": "Creating collections table ...", "timestamp": "2022-02-16T20:56:19.541290", "level": "debug"}
{"message": "collections table created.", "timestamp": "2022-02-16T20:56:19.558049", "level": "info"}
{"message": "Creating granules table ...", "timestamp": "2022-02-16T20:56:19.558192", "level": "debug"}
{"message": "granules table created.", "timestamp": "2022-02-16T20:56:19.597460", "level": "info"}
{"message": "Creating files table ...", "timestamp": "2022-02-16T20:56:19.597637", "level": "debug"}
{"message": "files table created.", "timestamp": "2022-02-16T20:56:19.629592", "level": "info"}
{"message": "Creating reconcile_status table ...", "timestamp": "2022-02-16T20:56:19.629741", "level": "debug"}
{"message": "reconcile_status table created.", "timestamp": "2022-02-16T20:56:19.660336", "level": "info"}
{"message": "Creating reconcile_job table ...", "timestamp": "2022-02-16T20:56:19.660494", "level": "debug"}
{"message": "reconcile_job table created.", "timestamp": "2022-02-16T20:56:19.684379", "level": "info"}
{"message": "Creating reconcile_s3_object table ...", "timestamp": "2022-02-16T20:56:19.684545", "level": "debug"}
{"message": "reconcile_s3_object table created.", "timestamp": "2022-02-16T20:56:19.700339", "level": "info"}
{"message": "Creating partition table reconcile_s3_object_orca_versioned_backup for reconcile_s3_object ...", "timestamp": "2022-02-16T20:56:19.700488", "level": "debug"}
{"message": "Partition table reconcile_s3_object_orca_versioned_backup for reconcile_s3_object created.", "timestamp": "2022-02-16T20:56:19.725877", "level": "info"}
{"message": "Creating partition table reconcile_s3_object_orca_worm_backup for reconcile_s3_object ...", "timestamp": "2022-02-16T20:56:19.726033", "level": "debug"}
{"message": "Partition table reconcile_s3_object_orca_worm_backup for reconcile_s3_object created.", "timestamp": "2022-02-16T20:56:19.746750", "level": "info"}
{"message": "Creating partition table reconcile_s3_object_orca_special_backup for reconcile_s3_object ...", "timestamp": "2022-02-16T20:56:19.746896", "level": "debug"}
{"message": "Partition table reconcile_s3_object_orca_special_backup for reconcile_s3_object created.", "timestamp": "2022-02-16T20:56:19.767221", "level": "info"}
{"message": "Creating reconcile_catalog_mismatch_report table ...", "timestamp": "2022-02-16T20:56:19.767364", "level": "debug"}
{"message": "reconcile_catalog_mismatch_report table created.", "timestamp": "2022-02-16T20:56:19.792888", "level": "info"}
{"message": "Creating reconcile_orphan_report table ...", "timestamp": "2022-02-16T20:56:19.793046", "level": "debug"}
{"message": "reconcile_orphan_report table created.", "timestamp": "2022-02-16T20:56:19.811829", "level": "info"}
{"message": "Creating reconcile_phantom_report table ...", "timestamp": "2022-02-16T20:56:19.811984", "level": "debug"}
{"message": "reconcile_phantom_report table created.", "timestamp": "2022-02-16T20:56:19.832392", "level": "info"}
{"message": "Manual test complete.", "timestamp": "2022-02-16T20:56:19.842243", "level": "info"}
```


### Fresh Install Test Validation

To validate the fresh install perform the following actions.

First, review the logs and verify that the following *info* messages were
expressed in the logs.

```bash
{"message": "Beginning manual test.", "timestamp": "2022-02-16T20:56:17.479345", "level": "info"}
{"message": "The ORCA database orca does not exist, or the server could not be connected to.", "timestamp": "2022-02-16T20:56:17.675049", "level": "info"}
{"message": "Database created.", "timestamp": "2022-02-16T20:56:19.168475", "level": "info"}
{"message": "ORCA dbo role created.", "timestamp": "2022-02-16T20:56:19.296273", "level": "info"}
{"message": "ORCA app role created.", "timestamp": "2022-02-16T20:56:19.298239", "level": "info"}
{"message": "ORCA schema created.", "timestamp": "2022-02-16T20:56:19.321700", "level": "info"}
{"message": "ORCA application user created.", "timestamp": "2022-02-16T20:56:19.331646", "level": "info"}
{"message": "extension aws_s3 created.", "timestamp": "2022-02-16T20:56:19.373998", "level": "info"}
{"message": "schema_versions table created.", "timestamp": "2022-02-16T20:56:19.425741", "level": "info"}
{"message": "Data added to the schema_versions table.", "timestamp": "2022-02-16T20:56:19.436505", "level": "info"}
{"message": "recovery_status table created.", "timestamp": "2022-02-16T20:56:19.456536", "level": "info"}
{"message": "Data added to the recovery_status table.", "timestamp": "2022-02-16T20:56:19.466350", "level": "info"}
{"message": "recovery_job table created.", "timestamp": "2022-02-16T20:56:19.497855", "level": "info"}
{"message": "recovery_file table created.", "timestamp": "2022-02-16T20:56:19.516014", "level": "info"}
{"message": "providers table created.", "timestamp": "2022-02-16T20:56:19.541131", "level": "info"}
{"message": "collections table created.", "timestamp": "2022-02-16T20:56:19.558049", "level": "info"}
{"message": "granules table created.", "timestamp": "2022-02-16T20:56:19.597460", "level": "info"}
{"message": "files table created.", "timestamp": "2022-02-16T20:56:19.629592", "level": "info"}
{"message": "reconcile_status table created.", "timestamp": "2022-02-16T20:56:19.660336", "level": "info"}
{"message": "reconcile_job table created.", "timestamp": "2022-02-16T20:56:19.684379", "level": "info"}
{"message": "reconcile_s3_object table created.", "timestamp": "2022-02-16T20:56:19.700339", "level": "info"}
{"message": "Partition table reconcile_s3_object_orca_versioned_backup for reconcile_s3_object created.", "timestamp": "2022-02-16T20:56:19.725877", "level": "info"}
{"message": "Partition table reconcile_s3_object_orca_worm_backup for reconcile_s3_object created.", "timestamp": "2022-02-16T20:56:19.746750", "level": "info"}
{"message": "Partition table reconcile_s3_object_orca_special_backup for reconcile_s3_object created.", "timestamp": "2022-02-16T20:56:19.767221", "level": "info"}
{"message": "reconcile_catalog_mismatch_report table created.", "timestamp": "2022-02-16T20:56:19.792888", "level": "info"}
{"message": "reconcile_orphan_report table created.", "timestamp": "2022-02-16T20:56:19.811829", "level": "info"}
{"message": "reconcile_phantom_report table created.", "timestamp": "2022-02-16T20:56:19.832392", "level": "info"}
{"message": "Manual test complete.", "timestamp": "2022-02-16T20:56:19.842243", "level": "info"}
```

Next, verify that the objects were actually created with the proper data in the
PostgreSQL *orca* database. Perform the checks below by going to the
**pgclient** window and logging into the *orca* database as the
*postgres* user as seen below.

```bash
   root@26df0390e999:/data/test/manual_tests# psql
   psql (12.6 (Debian 12.6-1.pgdg100+1))
   Type "help" for help

   postgres=# \c orca
   You are now connected to database "orca" as user "postgres".
```

1. Verify the *aws_s3* PostgreSQL extension was loaded.
   ```bash
   orca=# \dx
                                            List of installed extensions
       Name    | Version |   Schema   |                                   Description
   ------------+---------+------------+---------------------------------------------------------------------------------
    aws_s3     | 0.0.1   | public     | Custom AWS extension that allows for data COPY from and to an S3 bucket object.
    plpgsql    | 1.0     | pg_catalog | PL/pgSQL procedural language
    plpython3u | 1.0     | pg_catalog | PL/Python3U untrusted procedural language
   (3 rows)
   ```
2. Verify that the roles/users were created and that *orcauser* is a
   part of the *orca_app* role.
   ```bash
   orca=# \du
                                       List of roles
    Role name |                         Attributes                         | Member of
   -----------+------------------------------------------------------------+------------
    orca_app  | Cannot login                                               | {}
    orca_dbo  | Cannot login                                               | {}
    orcauser  |                                                            | {orca_app}
    postgres  | Superuser, Create role, Create DB, Replication, Bypass RLS | {orca_dbo}
   ```
3. Verify the ORCA schema was created.
   ```bash
   orca=# \dn

     List of schemas
        Name    |  Owner
   -------------+----------
    aws_commons | postgres
    aws_s3      | postgres
    orca        | orca_dbo
    public      | postgres
   (4 rows)
   ```
4. Verify the tables were created in the ORCA schema.
   ```bash
   orca=# \dt orca.*

                                 List of relations
    Schema |                      Name                 | Type  |  Owner
   --------+-------------------------------------------+-------+----------
    orca   | collections                               | table | orca_dbo
    orca   | files                                     | table | orca_dbo
    orca   | granules                                  | table | orca_dbo
    orca   | providers                                 | table | orca_dbo
    orca   | reconcile_catalog_mismatch_report         | table | orca_dbo
    orca   | reconcile_job                             | table | orca_dbo
    orca   | reconcile_orphan_report                   | table | orca_dbo
    orca   | reconcile_phantom_report                  | table | orca_dbo
    orca   | reconcile_s3_object                       | table | orca_dbo
    orca   | reconcile_s3_object_orca_special_backup   | table | orca_dbo
    orca   | reconcile_s3_object_orca_versioned_backup | table | orca_dbo
    orca   | reconcile_s3_object_orca_worm_backup      | table | orca_dbo
    orca   | reconcile_status                          | table | orca_dbo
    orca   | recovery_file                             | table | orca_dbo
    orca   | recovery_job                              | table | orca_dbo
    orca   | recovery_status                           | table | orca_dbo
    orca   | schema_versions                           | table | orca_dbo
    (17 rows)
   ```
5. Check that the partition table was created properly.
   ```bash
   ## Check the primary table
   orca=# \d+ orca.reconcile_s3_object

                                                                                         Table "orca.reconcile_s3_object"
           Column         |           Type           | Collation | Nullable | Default | Storage  | Stats target |                                         Description
   -----------------------+--------------------------+-----------+----------+---------+----------+--------------+----------------------------------------------------------------------------------------------
    job_id                | bigint                   |           | not null |         | plain    |              | Job the S3 listing is a part of for the comparison.
    orca_archive_location | text                     |           | not null |         | extended |              | ORCA S3 Glacier bucket name where the file is stored.
    key_path              | text                     |           | not null |         | extended |              | Full path and file name of the object in the S3 bucket.
    etag                  | text                     |           | not null |         | extended |              | AWS etag value from the s3 inventory report.
    last_update           | timestamp with time zone |           | not null |         | plain    |              | AWS Last Update from the s3 inventory report.
    size_in_bytes         | bigint                   |           | not null |         | plain    |              | AWS size of the file in bytes from the s3 inventory report.
    storage_class         | text                     |           | not null |         | extended |              | AWS storage class the object is in from the s3 inventory report.
    delete_marker         | boolean                  |           | not null | false   | plain    |              | Set to True if object is marked as deleted.
   Partition key: LIST (orca_archive_location)
   Partitions: orca.reconcile_s3_object_orca_special_backup FOR VALUES IN ('orca_special_backup'),
               orca.reconcile_s3_object_orca_versioned_backup FOR VALUES IN ('orca_versioned_backup'),
               orca.reconcile_s3_object_orca_worm_backup FOR VALUES IN ('orca_worm_backup')


   ## Check a partition table
   orca=# \d+ orca.orca.reconcile_s3_object_orca_worm_backup

                                        Table "orca.reconcile_s3_object_orca_worm_backup"
           Column         |           Type           | Collation | Nullable | Default | Storage  | Stats target | Description
   -----------------------+--------------------------+-----------+----------+---------+----------+--------------+-------------
    job_id                | bigint                   |           | not null |         | plain    |              |
    orca_archive_location | text                     |           | not null |         | extended |              |
    key_path              | text                     |           | not null |         | extended |              |
    etag                  | text                     |           | not null |         | extended |              |
    last_update           | timestamp with time zone |           | not null |         | plain    |              |
    size_in_bytes         | bigint                   |           | not null |         | plain    |              |
    storage_class         | text                     |           | not null |         | extended |              |
    delete_marker         | boolean                  |           | not null | false   | plain    |              |
   Partition of: orca.reconcile_s3_object FOR VALUES IN ('orca_worm_backup')
   Partition constraint: ((orca_archive_location IS NOT NULL) AND (orca_archive_location = 'orca_worm_backup'::text))
   Indexes:
       "pk_reconcile_s3_object_orca_worm_backup" PRIMARY KEY, btree (key_path)
   Foreign-key constraints:
       "fk_reconcile_job_reconcile_s3_object_orca_worm_backup" FOREIGN KEY (job_id) REFERENCES orca.reconcile_job(id)
   ```

6. Verify the static data in the *recovery_status* table.
   ```bash
   orca=# select * from orca.recovery_status;

    id |  value
   ----+----------
     1 | pending
     2 | staged
     3 | error
     4 | complete
   (4 rows)
   ```
7. Verify the static data in the *reconcile_status* table.
   ```bash
   orca=# select * from orca.reconcile_status;

    id |       value
   ----+--------------------
     1 | getting S3 list
     2 | staged
     3 | generating reports
     4 | error
     5 | success
   (5 rows)
   ```
8. Verify the static data in the *schema_versions* table.
   ```bash
   orca=# select * from orca.schema_versions;

    version_id |                     description                                    |        install _date        | is_latest
   ------------+--------------------------------------------------------------------+-----------------------------+-----------
             5 | Added internal reconciliation schema for v5.x of ORCA application  | 2022-02-16 20:56:19.2691+00 | t
   (1 row)
   ```
9. Verify the orcauser can login with the password provided in the `.env` files
   `APPLICATION_PASSWORD` environment variable.
   ```bash
   orca=# \c "dbname=orca user=orcauser password=<Your Password Here>"

   You are now connected to database "orca" as user "orcauser".

   orca=# \q
   ```


### Fresh Install Test Cleanup

No cleanup is necessary if the next test run is the [Database No Migration Test](#database-no-migration-test).

The `sql/cleanup.sql` script will remove all objects including the *orca* database.

```bash
root@56a9df92a881:/data/tasks/db_deploy/test/manual_tests# psql
psql (10.14 (Debian 10.14-1.pgdg90+1), server 10.20 (Debian 10.20-1.pgdg90+1))
Type "help" for help.

postgres=# \c orca
You are now connected to database "orca" as user "postgres".

orca=# \i sql/cleanup.sql

DROP EXTENSION
DROP TABLE
DROP TABLE
DROP TABLE
DROP TABLE
DROP TABLE
DROP TABLE
DROP TABLE
DROP TABLE
DROP TABLE
DELETE 1
INSERT 0 1
psql:sql/orca_schema_v5/remove.sql:18: WARNING:  there is no transaction in progress
COMMIT
DROP TABLE
DROP TABLE
DROP TABLE
DROP TABLE
DELETE 1
INSERT 0 1
psql:sql/orca_schema_v4/remove.sql:12: WARNING:  there is no transaction in progress
COMMIT
ALTER TABLE
DELETE 1
INSERT 0 1
psql:sql/orca_schema_v3/remove.sql:14: WARNING:  there is no transaction in progress
COMMIT
psql:sql/orca_schema_v2/remove.sql:1: NOTICE:  drop cascades to 4 other objects
DETAIL:  drop cascades to table orca.schema_versions
drop cascades to table orca.recovery_status
drop cascades to table orca.recovery_job
drop cascades to table orca.recovery_file
DROP SCHEMA
DROP ROLE
REVOKE
REVOKE
DROP ROLE
REVOKE
DROP ROLE
psql:sql/orca_schema_v2/remove.sql:8: WARNING:  there is no transaction in progress
COMMIT
psql:sql/orca_schema_v1/remove.sql:1: NOTICE:  schema "dr" does not exist, skipping
DROP SCHEMA
psql:sql/orca_schema_v1/remove.sql:2: NOTICE:  role "druser" does not exist, skipping
DROP ROLE
psql:sql/orca_schema_v1/remove.sql:3: ERROR:  role "dbo" does not exist
psql:sql/orca_schema_v1/remove.sql:4: NOTICE:  role "dbo" does not exist, skipping
DROP ROLE
psql:sql/orca_schema_v1/remove.sql:5: ERROR:  role "drdbo_role" does not exist
psql:sql/orca_schema_v1/remove.sql:6: ERROR:  role "drdbo_role" does not exist
psql:sql/orca_schema_v1/remove.sql:7: NOTICE:  role "drdbo_role" does not exist, skipping
DROP ROLE
psql:sql/orca_schema_v1/remove.sql:8: ERROR:  role "dr_role" does not exist
psql:sql/orca_schema_v1/remove.sql:9: NOTICE:  role "dr_role" does not exist, skipping
DROP ROLE
psql:sql/orca_schema_v1/remove.sql:10: WARNING:  there is no transaction in progress
COMMIT
psql (10.14 (Debian 10.14-1.pgdg90+1), server 10.20 (Debian 10.20-1.pgdg90+1))
You are now connected to database "postgres" as user "postgres".
```

## Database Exists Install Test

This is a modification of [Database Fresh Install Test](#database-fresh-install-test) 
where the disaster-recovery database already exists.

### Database Exists Test Setup

1. If the database exists, remove it with the command `\i sql/cleanup.sql`
   at the psql prompt.

2. Run `\i sql/create_database.sql` at the psql prompt.

### Running the Database Exists Test

Follow [Running the Fresh Install Test](#running-the-fresh-install-test),
noting that messages regarding database creation should be skipped.

### Database Exists Test Validation

Follow [Fresh Install Test Validation](#fresh-install-test-validation).

### Database Exists Test Cleanup

Follow [Fresh Install Test Cleanup](#fresh-install-test-cleanup).

## Database Migration v1 to v5 Test

This test validates that the db_deploy scripts correctly identify a v1 ORCA
schema and run the migration of objects and data to an ORCA v5 schema.

### Database Setup Migration Test

1. Verify that the *orca* database does not exist. If it does, remove
   it using the `\i sql/cleanup.sql` command as described in the cleanup section.
2. Create the *orca* database by using the `\i sql/create_database.sql`
   command as seen below.
   ```bash
   root@56a9df92a881:/data/tasks/db_deploy/test/manual_tests# psql
   psql (10.14 (Debian 10.14-1.pgdg90+1), server 10.20 (Debian 10.20-1.pgdg90+1))
   Type "help" for help.

   postgres=# \i sql/create_database.sql
   CREATE DATABASE
   COMMENT
   ```
3. Run the `sql/orca_schema_v1/create.sql` script as seen below. This will
   populate the database with the users, schema, tables and dummy data used for
   migrating from v1 of the schema to v5.
   ```bash
   root@56a9df92a881:/data/tasks/db_deploy/test/manual_tests# psql
   psql (10.14 (Debian 10.14-1.pgdg90+1), server 10.20 (Debian 10.20-1.pgdg90+1))
   Type "help" for help.

   postgres=# \i sql/orca_schema_v1/create.sql

   You are now connected to database "postgres" as user "postgres".
   DO
   psql:sql/orca_schema_v1/roles/appdbo_role.sql:24: WARNING:  there is no transaction in progress
   COMMIT
   DO
   DO
   psql:sql/orca_schema_v1/roles/appuser.sql:29: NOTICE:  role "druser" does not exist, skipping
   DO
   psql:sql/orca_schema_v1/create.sql:4: WARNING:  there is no transaction in progress
   COMMIT
   You are now connected to database "orca" as user "postgres".
   CREATE EXTENSION
   CREATE SCHEMA
   COMMENT
   GRANT
   ALTER DEFAULT PRIVILEGES
   ALTER DEFAULT PRIVILEGES
   ALTER DEFAULT PRIVILEGES
   ALTER DEFAULT PRIVILEGES
   ALTER DEFAULT PRIVILEGES
   ALTER DEFAULT PRIVILEGES
   ALTER DEFAULT PRIVILEGES
   ALTER DEFAULT PRIVILEGES
   ALTER DEFAULT PRIVILEGES
   ALTER DEFAULT PRIVILEGES
   ALTER DEFAULT PRIVILEGES
   psql:sql/orca_schema_v1/create.sql:10: WARNING:  there is no transaction in progress
   COMMIT
   SET
   BEGIN
   SAVEPOINT
   SET
   CREATE TABLE
   COMMENT
   COMMENT
   COMMENT
   COMMENT
   COMMENT
   COMMENT
   COMMENT
   COMMENT
   COMMENT
   COMMENT
   COMMENT
   COMMENT
   CREATE INDEX
   CREATE INDEX
   CREATE INDEX
   COMMIT
   INSERT 0 337
   UPDATE 110
   UPDATE 110
   psql:sql/orca_schema_v1/tables/populate_dummy_data.sql:41: WARNING:  there is no transaction in progress
   COMMIT
   psql:sql/orca_schema_v1/create.sql:15: WARNING:  there is no transaction in progress
   COMMIT
   
   # Once complete quit psql. We will login as admin user during validation.
   orca=> \q
   ```


### Running the Migration Test

To run the migration test, in your **python** window run the command
`python manual_test.py`. The output should look similar to below.

```bash
(venv) root@cf4b0741a628:/data/test/manual_tests# python manual_test.py

{"message": "Beginning manual test.", "timestamp": "2022-02-16T22:01:20.232974", "level": "info"}
{"message": "Creating admin user connection object.", "timestamp": "2022-02-16T22:01:20.233132", "level": "debug"}
{"message": "Database set to postgres for the connection.", "timestamp": "2022-02-16T22:01:20.233214", "level": "debug"}
{"message": "Creating URL object to connect to the database.", "timestamp": "2022-02-16T22:01:20.233292", "level": "debug"}
{"message": "Creating admin user connection object.", "timestamp": "2022-02-16T22:01:20.312853", "level": "debug"}
{"message": "Database set to orca for the connection.", "timestamp": "2022-02-16T22:01:20.312972", "level": "debug"}
{"message": "Creating URL object to connect to the database.", "timestamp": "2022-02-16T22:01:20.313049", "level": "debug"}
{"message": "ORCA schema exists. Checking for schema versions.", "timestamp": "2022-02-16T22:01:20.441059", "level": "debug"}
{"message": "Checking for schema_versions table.", "timestamp": "2022-02-16T22:01:20.441240", "level": "debug"}
{"message": "schema_versions table exists False", "timestamp": "2022-02-16T22:01:20.473383", "level": "debug"}
{"message": "Performing migration of the ORCA schema.", "timestamp": "2022-02-16T22:01:20.473563", "level": "info"}
{"message": "Creating admin user connection object.", "timestamp": "2022-02-16T22:01:20.473652", "level": "debug"}
{"message": "Database set to orca for the connection.", "timestamp": "2022-02-16T22:01:20.473729", "level": "debug"}
{"message": "Creating URL object to connect to the database.", "timestamp": "2022-02-16T22:01:20.473802", "level": "debug"}
{"message": "Creating the ORCA dbo role ...", "timestamp": "2022-02-16T22:01:20.498205", "level": "debug"}
{"message": "ORCA dbo role created.", "timestamp": "2022-02-16T22:01:20.570020", "level": "info"}
{"message": "Creating the ORCA app role ...", "timestamp": "2022-02-16T22:01:20.570171", "level": "debug"}
{"message": "ORCA app role created.", "timestamp": "2022-02-16T22:01:20.572014", "level": "info"}
{"message": "Creating the ORCA schema ...", "timestamp": "2022-02-16T22:01:20.572152", "level": "debug"}
{"message": "ORCA schema created.", "timestamp": "2022-02-16T22:01:20.585032", "level": "info"}
{"message": "Creating the ORCA application user ...", "timestamp": "2022-02-16T22:01:20.585178", "level": "debug"}
{"message": "ORCA application user created.", "timestamp": "2022-02-16T22:01:20.595125", "level": "info"}
{"message": "Changing to the dbo role to create objects ...", "timestamp": "2022-02-16T22:01:20.595271", "level": "debug"}
{"message": "Setting search path to the ORCA schema to create objects ...", "timestamp": "2022-02-16T22:01:20.596610", "level": "debug"}
{"message": "Creating schema_versions table ...", "timestamp": "2022-02-16T22:01:20.597905", "level": "debug"}
{"message": "schema_versions table created.", "timestamp": "2022-02-16T22:01:20.651689", "level": "info"}
{"message": "Creating recovery_status table ...", "timestamp": "2022-02-16T22:01:20.651836", "level": "debug"}
{"message": "recovery_status table created.", "timestamp": "2022-02-16T22:01:20.679471", "level": "info"}
{"message": "Creating recovery_job table ...", "timestamp": "2022-02-16T22:01:20.679625", "level": "debug"}
{"message": "recovery_job table created.", "timestamp": "2022-02-16T22:01:20.724418", "level": "info"}
{"message": "Creating recovery_file table ...", "timestamp": "2022-02-16T22:01:20.724599", "level": "debug"}
{"message": "recovery_file table created.", "timestamp": "2022-02-16T22:01:20.749111", "level": "info"}
{"message": "Changing to the admin role ...", "timestamp": "2022-02-16T22:01:20.753621", "level": "debug"}
{"message": "Setting search path to the ORCA and dr schema ...", "timestamp": "2022-02-16T22:01:20.755699", "level": "debug"}
{"message": "Populating the recovery_status table with data ...", "timestamp": "2022-02-16T22:01:20.756844", "level": "debug"}
{"message": "Data added to the recovery_status table.", "timestamp": "2022-02-16T22:01:20.772545", "level": "info"}
{"message": "Migrating data from request_status to recovery_job ...", "timestamp": "2022-02-16T22:01:20.772695", "level": "debug"}
{"message": "Data migrated to recovery_job table.", "timestamp": "2022-02-16T22:01:20.823087", "level": "info"}
{"message": "Migrating data from request_status to recovery_file ...", "timestamp": "2022-02-16T22:01:20.823235", "level": "debug"}
{"message": "Data migrated to recovery_file table.", "timestamp": "2022-02-16T22:01:20.861497", "level": "info"}
{"message": "Dropping dr.request_status table ...", "timestamp": "2022-02-16T22:01:20.861652", "level": "debug"}
{"message": "dr.request_status table removed.", "timestamp": "2022-02-16T22:01:20.878175", "level": "info"}
{"message": "Changing to the dbo role ...", "timestamp": "2022-02-16T22:01:20.878311", "level": "debug"}
{"message": "Dropping dr schema ...", "timestamp": "2022-02-16T22:01:20.879903", "level": "debug"}
{"message": "dr schema removed.", "timestamp": "2022-02-16T22:01:20.881228", "level": "info"}
{"message": "Changing to the admin role ...", "timestamp": "2022-02-16T22:01:20.881340", "level": "debug"}
{"message": "Dropping drdbo_role role ...", "timestamp": "2022-02-16T22:01:20.882405", "level": "debug"}
{"message": "drdbo_role role removed.", "timestamp": "2022-02-16T22:01:20.883609", "level": "info"}
{"message": "Dropping dr_role role ...", "timestamp": "2022-02-16T22:01:20.883712", "level": "debug"}
{"message": "dr_role role removed.", "timestamp": "2022-02-16T22:01:20.884780", "level": "info"}
{"message": "Dropping dbo user ...", "timestamp": "2022-02-16T22:01:20.884878", "level": "debug"}
{"message": "dbo user removed", "timestamp": "2022-02-16T22:01:20.886090", "level": "info"}
{"message": "Dropping druser user ...", "timestamp": "2022-02-16T22:01:20.886185", "level": "debug"}
{"message": "druser user removed.", "timestamp": "2022-02-16T22:01:20.887123", "level": "info"}
{"message": "Creating admin user connection object.", "timestamp": "2022-02-16T22:01:20.925431", "level": "debug"}
{"message": "Database set to orca for the connection.", "timestamp": "2022-02-16T22:01:20.925606", "level": "debug"}
{"message": "Creating URL object to connect to the database.", "timestamp": "2022-02-16T22:01:20.925704", "level": "debug"}
{"message": "Changing to the dbo role to modify objects ...", "timestamp": "2022-02-16T22:01:20.947317", "level": "debug"}
{"message": "Setting search path to the ORCA schema to modify objects ...", "timestamp": "2022-02-16T22:01:20.950171", "level": "debug"}
{"message": "Adding multipart_chunksize_mb column...", "timestamp": "2022-02-16T22:01:20.951764", "level": "debug"}
{"message": "multipart_chunksize_mb column added.", "timestamp": "2022-02-16T22:01:20.953789", "level": "info"}
{"message": "Creating admin user connection object.", "timestamp": "2022-02-16T22:01:20.956426", "level": "debug"}
{"message": "Database set to orca for the connection.", "timestamp": "2022-02-16T22:01:20.956582", "level": "debug"}
{"message": "Creating URL object to connect to the database.", "timestamp": "2022-02-16T22:01:20.956666", "level": "debug"}
{"message": "Changing to the dbo role to create objects ...", "timestamp": "2022-02-16T22:01:20.978347", "level": "debug"}
{"message": "Setting search path to the ORCA schema to create objects ...", "timestamp": "2022-02-16T22:01:20.980394", "level": "debug"}
{"message": "Creating providers table ...", "timestamp": "2022-02-16T22:01:20.981518", "level": "debug"}
{"message": "providers table created.", "timestamp": "2022-02-16T22:01:21.006541", "level": "info"}
{"message": "Creating collections table ...", "timestamp": "2022-02-16T22:01:21.006883", "level": "debug"}
{"message": "collections table created.", "timestamp": "2022-02-16T22:01:21.025011", "level": "info"}
{"message": "Creating granules table ...", "timestamp": "2022-02-16T22:01:21.025153", "level": "debug"}
{"message": "granules table created.", "timestamp": "2022-02-16T22:01:21.081774", "level": "info"}
{"message": "Creating storage_class table ...", "timestamp": "2022-02-16T22:01:21.081917", "level": "debug"}
{"message": "Populating storage_class table ...", "timestamp": "2022-02-16T22:01:21.081917", "level": "debug"}
{"message": "storage_class table created.", "timestamp": "2022-02-16T22:01:21.081917", "level": "debug"}
{"message": "Creating files table ...", "timestamp": "2022-02-16T22:01:21.081917", "level": "debug"}
{"message": "files table created.", "timestamp": "2022-02-16T22:01:21.129938", "level": "info"}
{"message": "Creating admin user connection object.", "timestamp": "2022-02-16T22:01:21.134615", "level": "debug"}
{"message": "Database set to orca for the connection.", "timestamp": "2022-02-16T22:01:21.135035", "level": "debug"}
{"message": "Creating URL object to connect to the database.", "timestamp": "2022-02-16T22:01:21.135158", "level": "debug"}
{"message": "Creating extension aws_s3 ...", "timestamp": "2022-02-16T22:01:21.161258", "level": "debug"}
{"message": "extension aws_s3 created.", "timestamp": "2022-02-16T22:01:21.184853", "level": "info"}
{"message": "Changing to the dbo role to create objects ...", "timestamp": "2022-02-16T22:01:21.185036", "level": "debug"}
{"message": "Setting search path to the ORCA schema to create objects ...", "timestamp": "2022-02-16T22:01:21.186355", "level": "debug"}
{"message": "Creating reconcile_status table ...", "timestamp": "2022-02-16T22:01:21.187569", "level": "debug"}
{"message": "reconcile_status table created.", "timestamp": "2022-02-16T22:01:21.232049", "level": "info"}
{"message": "Creating reconcile_job table ...", "timestamp": "2022-02-16T22:01:21.232212", "level": "debug"}
{"message": "reconcile_job table created.", "timestamp": "2022-02-16T22:01:21.272316", "level": "info"}
{"message": "Creating reconcile_s3_object table ...", "timestamp": "2022-02-16T22:01:21.272460", "level": "debug"}
{"message": "reconcile_s3_object table created.", "timestamp": "2022-02-16T22:01:21.289093", "level": "info"}
{"message": "Creating partition table reconcile_s3_object_orca_versioned_backup for reconcile_s3_object ...", "timestamp": "2022-02-16T22:01:21.289245", "level": "debug"}
{"message": "Partition table reconcile_s3_object_orca_versioned_backup for reconcile_s3_object created.", "timestamp": "2022-02-16T22:01:21.320566", "level": "info"}
{"message": "Creating partition table reconcile_s3_object_orca_worm_backup for reconcile_s3_object ...", "timestamp": "2022-02-16T22:01:21.320720", "level": "debug"}
{"message": "Partition table reconcile_s3_object_orca_worm_backup for reconcile_s3_object created.", "timestamp": "2022-02-16T22:01:21.339289", "level": "info"}
{"message": "Creating partition table reconcile_s3_object_orca_special_backup for reconcile_s3_object ...", "timestamp": "2022-02-16T22:01:21.339446", "level": "debug"}
{"message": "Partition table reconcile_s3_object_orca_special_backup for reconcile_s3_object created.", "timestamp": "2022-02-16T22:01:21.360865", "level": "info"}
{"message": "Creating reconcile_catalog_mismatch_report table ...", "timestamp": "2022-02-16T22:01:21.361009", "level": "debug"}
{"message": "reconcile_catalog_mismatch_report table created.", "timestamp": "2022-02-16T22:01:21.378214", "level": "info"}
{"message": "Creating reconcile_orphan_report table ...", "timestamp": "2022-02-16T22:01:21.378355", "level": "debug"}
{"message": "reconcile_orphan_report table created.", "timestamp": "2022-02-16T22:01:21.396433", "level": "info"}
{"message": "Creating reconcile_phantom_report table ...", "timestamp": "2022-02-16T22:01:21.396665", "level": "debug"}
{"message": "reconcile_phantom_report table created.", "timestamp": "2022-02-16T22:01:21.425628", "level": "info"}
{"message": "Populating the schema_versions table with data ...", "timestamp": "2022-02-16T22:01:21.425846", "level": "debug"}
{"message": "Data added to the schema_versions table.", "timestamp": "2022-02-16T22:01:21.434793", "level": "info"}
{"message": "Manual test complete.", "timestamp": "2022-02-16T22:01:21.439033", "level": "info"}
```


### Migration Test Validation

To validate the migration test perform the following actions.

First, review the logs and verify that the following *info* messages were
expressed in the logs.

```bash
{"message": "Performing migration of the ORCA schema.", "timestamp": "2022-02-16T22:01:20.473563", "level": "info"}
{"message": "ORCA dbo role created.", "timestamp": "2022-02-16T22:01:20.570020", "level": "info"}
{"message": "ORCA app role created.", "timestamp": "2022-02-16T22:01:20.572014", "level": "info"}
{"message": "ORCA schema created.", "timestamp": "2022-02-16T22:01:20.585032", "level": "info"}
{"message": "ORCA application user created.", "timestamp": "2022-02-16T22:01:20.595125", "level": "info"}
{"message": "schema_versions table created.", "timestamp": "2022-02-16T22:01:20.651689", "level": "info"}
{"message": "recovery_status table created.", "timestamp": "2022-02-16T22:01:20.679471", "level": "info"}
{"message": "recovery_job table created.", "timestamp": "2022-02-16T22:01:20.724418", "level": "info"}
{"message": "recovery_file table created.", "timestamp": "2022-02-16T22:01:20.749111", "level": "info"}
{"message": "Data added to the recovery_status table.", "timestamp": "2022-02-16T22:01:20.772545", "level": "info"}
{"message": "Data migrated to recovery_job table.", "timestamp": "2022-02-16T22:01:20.823087", "level": "info"}
{"message": "Data migrated to recovery_file table.", "timestamp": "2022-02-16T22:01:20.861497", "level": "info"}
{"message": "dr.request_status table removed.", "timestamp": "2022-02-16T22:01:20.878175", "level": "info"}
{"message": "dr schema removed.", "timestamp": "2022-02-16T22:01:20.881228", "level": "info"}
{"message": "drdbo_role role removed.", "timestamp": "2022-02-16T22:01:20.883609", "level": "info"}
{"message": "dr_role role removed.", "timestamp": "2022-02-16T22:01:20.884780", "level": "info"}
{"message": "dbo user removed", "timestamp": "2022-02-16T22:01:20.886090", "level": "info"}
{"message": "druser user removed.", "timestamp": "2022-02-16T22:01:20.887123", "level": "info"}
{"message": "multipart_chunksize_mb column added.", "timestamp": "2022-02-16T22:01:20.953789", "level": "info"}
{"message": "providers table created.", "timestamp": "2022-02-16T22:01:21.006541", "level": "info"}
{"message": "collections table created.", "timestamp": "2022-02-16T22:01:21.025011", "level": "info"}
{"message": "granules table created.", "timestamp": "2022-02-16T22:01:21.081774", "level": "info"}
{"message": "storage_class table created.", "timestamp": "2022-02-16T22:01:21.081917", "level": "debug"}
{"message": "files table created.", "timestamp": "2022-02-16T22:01:21.129938", "level": "info"}
{"message": "extension aws_s3 created.", "timestamp": "2022-02-16T22:01:21.184853", "level": "info"}
{"message": "reconcile_status table created.", "timestamp": "2022-02-16T22:01:21.232049", "level": "info"}
{"message": "reconcile_job table created.", "timestamp": "2022-02-16T22:01:21.272316", "level": "info"}
{"message": "reconcile_s3_object table created.", "timestamp": "2022-02-16T22:01:21.289093", "level": "info"}
{"message": "Partition table reconcile_s3_object_orca_versioned_backup for reconcile_s3_object created.", "timestamp": "2022-02-16T22:01:21.320566", "level": "info"}
{"message": "Partition table reconcile_s3_object_orca_worm_backup for reconcile_s3_object created.", "timestamp": "2022-02-16T22:01:21.339289", "level": "info"}
{"message": "Partition table reconcile_s3_object_orca_special_backup for reconcile_s3_object created.", "timestamp": "2022-02-16T22:01:21.360865", "level": "info"}
{"message": "reconcile_catalog_mismatch_report table created.", "timestamp": "2022-02-16T22:01:21.378214", "level": "info"}
{"message": "reconcile_orphan_report table created.", "timestamp": "2022-02-16T22:01:21.396433", "level": "info"}
{"message": "reconcile_phantom_report table created.", "timestamp": "2022-02-16T22:01:21.425628", "level": "info"}
{"message": "Data added to the schema_versions table.", "timestamp": "2022-02-16T22:01:21.434793", "level": "info"}
```

Next, verify that the objects were actually created with the proper data in the
PostgreSQL *orca* database. Perform the checks below by going to the
**pgclient** window and logging into the *orca* database as the
*postgres* user as seen below.

```bash
   root@56a9df92a881:/data/tasks/db_deploy/test/manual_tests# psql
   psql (10.14 (Debian 10.14-1.pgdg90+1), server 10.20 (Debian 10.20-1.pgdg90+1))
   Type "help" for help.

   postgres=# \c orca
   You are now connected to database "orca" as user "postgres".
```

1. Verify the *aws_s3* PostgreSQL extension was loaded.
   ```bash
   orca=# \dx
                                            List of installed extensions
       Name    | Version |   Schema   |                                   Description
   ------------+---------+------------+---------------------------------------------------------------------------------
    aws_s3     | 0.0.1   | public     | Custom AWS extension that allows for data COPY from and to an S3 bucket object.
    plpgsql    | 1.0     | pg_catalog | PL/pgSQL procedural language
    plpython3u | 1.0     | pg_catalog | PL/Python3U untrusted procedural language
   (3 rows)
   ```
2. Verify that the roles/users were created and that *orcauser* is a
   part of the *orca_app* role. Also verify the *dbo*, *druser*, *drdbo_role*,
   and *dr_role* have been removed.
   ```bash
   orca=# \du
                                       List of roles
    Role name |                         Attributes                         | Member of
   -----------+------------------------------------------------------------+------------
    orca_app  | Cannot login                                               | {}
    orca_dbo  | Cannot login                                               | {}
    orcauser  |                                                            | {orca_app}
    postgres  | Superuser, Create role, Create DB, Replication, Bypass RLS | {orca_dbo}
   ```
3. Verify the *orca* schema was created and the *dr* schema was removed.
   ```bash
   orca=# \dn

     List of schemas
        Name    |  Owner
   -------------+----------
    aws_commons | postgres
    aws_s3      | postgres
    orca        | orca_dbo
    public      | postgres
   (4 rows)
   ```
4. Verify the tables were created in the ORCA schema. It is assumed that the partition table in schema version 5+ is named `orca_archive_location_test_bucket`
   ```bash
   orca=# \dt orca.*

                                 List of relations
    Schema |                      Name                 | Type  |  Owner
   --------+-------------------------------------------+-------+----------
    orca   | collections                               | table | orca_dbo
    orca   | files                                     | table | orca_dbo
    orca   | granules                                  | table | orca_dbo
    orca   | providers                                 | table | orca_dbo
    orca   | reconcile_catalog_mismatch_report         | table | orca_dbo
    orca   | reconcile_job                             | table | orca_dbo
    orca   | reconcile_orphan_report                   | table | orca_dbo
    orca   | reconcile_phantom_report                  | table | orca_dbo
    orca   | reconcile_s3_object                       | table | orca_dbo
    orca   | reconcile_s3_object_orca_special_backup   | table | orca_dbo
    orca   | reconcile_s3_object_orca_versioned_backup | table | orca_dbo
    orca   | reconcile_s3_object_orca_worm_backup      | table | orca_dbo
    orca   | reconcile_status                          | table | orca_dbo
    orca   | recovery_file                             | table | orca_dbo
    orca   | recovery_job                              | table | orca_dbo
    orca   | recovery_status                           | table | orca_dbo
    orca   | schema_versions                           | table | orca_dbo
    orca   | storage_class                             | table | orca_dbo
    (17 rows)
   ```
5. Check that the partition table was created properly.
   ```bash
   ## Check the primary table
   orca=# \d+ orca.reconcile_s3_object

                                                                                         Table "orca.reconcile_s3_object"
           Column         |           Type           | Collation | Nullable | Default | Storage  | Stats target |                                         Description
   -----------------------+--------------------------+-----------+----------+---------+----------+--------------+----------------------------------------------------------------------------------------------
    job_id                | bigint                   |           | not null |         | plain    |              | Job the S3 listing is a part of for the comparison.
    orca_archive_location | text                     |           | not null |         | extended |              | ORCA S3 Glacier bucket name where the file is stored.
    key_path              | text                     |           | not null |         | extended |              | Full path and file name of the object in the S3 bucket.
    etag                  | text                     |           | not null |         | extended |              | AWS etag value from the s3 inventory report.
    last_update           | timestamp with time zone |           | not null |         | plain    |              | AWS Last Update from the s3 inventory report.
    size_in_bytes         | bigint                   |           | not null |         | plain    |              | AWS size of the file in bytes from the s3 inventory report.
    storage_class         | text                     |           | not null |         | extended |              | AWS storage class the object is in from the s3 inventory report.
    delete_marker         | boolean                  |           | not null | false   | plain    |              | Set to True if object is marked as deleted.
   Partition key: LIST (orca_archive_location)
   Partitions: orca.reconcile_s3_object_orca_special_backup FOR VALUES IN ('orca_special_backup'),
               orca.reconcile_s3_object_orca_versioned_backup FOR VALUES IN ('orca_versioned_backup'),
               orca.reconcile_s3_object_orca_worm_backup FOR VALUES IN ('orca_worm_backup')


   ## Check a partition table
   orca=# \d+ orca.orca.reconcile_s3_object_orca_worm_backup

                                        Table "orca.reconcile_s3_object_orca_worm_backup"
           Column         |           Type           | Collation | Nullable | Default | Storage  | Stats target | Description
   -----------------------+--------------------------+-----------+----------+---------+----------+--------------+-------------
    job_id                | bigint                   |           | not null |         | plain    |              |
    orca_archive_location | text                     |           | not null |         | extended |              |
    key_path              | text                     |           | not null |         | extended |              |
    etag                  | text                     |           | not null |         | extended |              |
    last_update           | timestamp with time zone |           | not null |         | plain    |              |
    size_in_bytes         | bigint                   |           | not null |         | plain    |              |
    storage_class         | text                     |           | not null |         | extended |              |
    delete_marker         | boolean                  |           | not null | false   | plain    |              |
   Partition of: orca.reconcile_s3_object FOR VALUES IN ('orca_worm_backup')
   Partition constraint: ((orca_archive_location IS NOT NULL) AND (orca_archive_location = 'orca_worm_backup'::text))
   Indexes:
       "pk_reconcile_s3_object_orca_worm_backup" PRIMARY KEY, btree (key_path)
   Foreign-key constraints:
       "fk_reconcile_job_reconcile_s3_object_orca_worm_backup" FOREIGN KEY (job_id) REFERENCES orca.reconcile_job(id)
   ```

6. Verify the static data in the *recovery_status* table.
   ```bash
   orca=# select * from orca.recovery_status;

    id |  value
   ----+----------
     1 | pending
     2 | staged
     3 | error
     4 | complete
   (4 rows)
   ```
7. Verify the static data in the *reconcile_status* table.
   ```bash
   orca=# select * from orca.reconcile_status;

    id |       value
   ----+--------------------
     1 | getting S3 list
     2 | staged
     3 | generating reports
     4 | error
     5 | success
   (5 rows)
   ```
8. Verify the static data in the *schema_versions* table.
   ```bash
   orca=# select * from orca.schema_versions;

    version_id |                     description                                    |        install _date        | is_latest
   ------------+--------------------------------------------------------------------+-----------------------------+-----------
             5 | Added internal reconciliation schema for v5.x of ORCA application  | 2022-02-16 20:56:19.2691+00 | t
   (1 row)
   ```
9. Verify the orcauser can login with the password provided in the `.env` files
   `APPLICATION_PASSWORD` environment variable.
   ```bash
   orca=# \c "dbname=orca user=orcauser password=<Your Password Here>"

   You are now connected to database "orca" as user "orcauser".
   ```
10. Validate that the data was properly migrated into the recovery jobs table. The
    dummy data has a 1 job -> 1 granule -> 1 file relation.
    ```bash
    # Check the total numbers based on status value. They should match the values
    # expressed below.
    orca=# select status_id, count(*) from recovery_job group by 1;

    status_id | count
    -----------+-------
             1 |   117
             3 |   110
             4 |   110
    (3 rows)

    # Check the pending data. Verify completion date is not set and arcive_destination
    # is set to myglacierarchivebucket
    orca=# select * from recovery_job where status_id = 1 LIMIT 5;

                   job_id                |        granule_id        |  archive_destination   | status_id |         request_time          | completion_time
    -------------------------------------+--------------------------+------------------------+-----------+-------------------------------+-----------------
    01782f43-5431-4a7a-9bdd-14f4462d93b1 | 47da62669dc4fcddfa332308 | myarchiveglacierbucket |         1 | 2021-04-29 08:10:04.855081+00 |
    01dacee7-d511-4211-b010-07d8caf4318a | db913643165b26063aa3e5c6 | myarchiveglacierbucket |         1 | 2021-04-25 00:10:04.855081+00 |
    01e20106-3673-412a-ba58-57084b63796a | bcd7c80976d5405aeff27711 | myarchiveglacierbucket |         1 | 2021-04-25 01:10:04.855081+00 |
    026e568c-41f2-4902-a0b3-f7eaab1e5a91 | 33ddbc2f4682d452031f901e | myarchiveglacierbucket |         1 | 2021-04-27 11:10:04.855081+00 |
    028717f6-b359-490c-bceb-fc3cab70b82c | fd6ef1dc3804e1f05e550364 | myarchiveglacierbucket |         1 | 2021-04-25 21:10:04.855081+00 |
    (5 rows)

    # Check the complete data. Verify completion date is set and arcive_destination
    # is set to myglacierarchivebucket
    orca=# select * from recovery_job where status_id = 4 LIMIT 5;

                   job_id                |        granule_id        |  archive_destination   | multipart_chunksize_mb | status_id |         request_time          | completion_time
    -------------------------------------+--------------------------+------------------------+-----------+-------------------------------+-------------------------------
    04c9db6d-2d09-4e75-af79-feaf54c7771e | 64e83cc5103965b83fca62ad | myarchiveglacierbucket |                   NULL |         4 | 2021-04-19 08:10:04.855081+00 | 2021-04-29 15:10:04.855081+00
    057e1fe7-c561-48c3-b539-65193de99279 | 0a1662031cfecd9c5190bf6d | myarchiveglacierbucket |                   NULL |         4 | 2021-04-18 20:10:04.855081+00 | 2021-04-29 15:10:04.855081+00
    0c86fa12-8773-4da6-b0e3-38104230c12e | 7b8be6c8f9076afe64f1aa62 | myarchiveglacierbucket |                   NULL |         4 | 2021-04-16 03:10:04.855081+00 | 2021-04-29 15:10:04.855081+00
    0e377a25-e8a6-4de8-86de-42dfad803b75 | cca7d86de488a25864f18095 | myarchiveglacierbucket |                   NULL |         4 | 2021-04-18 02:10:04.855081+00 | 2021-04-29 15:10:04.855081+00
    0eefcaf1-5dc5-47eb-a299-a9c206bf58d5 | 11790a3ddcdfcd1cbd6e341b | myarchiveglacierbucket |                   NULL |         4 | 2021-04-19 20:10:04.855081+00 | 2021-04-29 15:10:04.855081+00
    (5 rows)

    # Check the complete data. Verify completion date is set and arcive_destination
    # is set to myglacierarchivebucket
    orca=# select * from recovery_job where status_id = 3 LIMIT 5;

                   job_id                |        granule_id        |  archive_destination   | status_id |         request_time          | completion_time
    -------------------------------------+--------------------------+------------------------+-----------+-------------------------------+-------------------------------
    0169a025-1e3e-4a69-ab64-498634cd933b | 865a440a34c319b22ee52419 | myarchiveglacierbucket |         3 | 2021-04-24 10:10:04.855081+00 | 2021-04-29 15:10:04.855081+00
    0673403b-6c52-459f-b59a-04ab9b87b93f | 9eda38da05d01ade96a3a3e8 | myarchiveglacierbucket |         3 | 2021-04-23 20:10:04.855081+00 | 2021-04-29 15:10:04.855081+00
    072db1cb-0efd-41b7-bc09-03272f0a6ab9 | 1bbf8c9d3b4b52a44220bdfc | myarchiveglacierbucket |         3 | 2021-04-24 08:10:04.855081+00 | 2021-04-29 15:10:04.855081+00
    09ccd4bc-7904-47f6-93e3-1f4ec21ff9b6 | 5510126af9eae7e6baab940a | myarchiveglacierbucket |         3 | 2021-04-21 13:10:04.855081+00 | 2021-04-29 15:10:04.855081+00
    0b4620bd-07d3-46a7-aa7c-db3c1316b697 | ac40bb34b5d64655daca2f1d | myarchiveglacierbucket |         3 | 2021-04-22 13:10:04.855081+00 | 2021-04-29 15:10:04.855081+00
    (5 rows)
    ```
11. Validate that the data was properly migrated into the recovery files table. The
    dummy data has a 1 job -> 1 granule -> 1 file relation.
    ```bash
    # Check the total numbers based on status value. They should match the values
    # expressed below.
    orca=# select status_id, count(*) from recovery_file group by 1;

     status_id | count
    -----------+-------
             1 |   117
             3 |   110
             4 |   110
    (3 rows)

    # Check the pending data. Verify completion date is not set and error_message
    # is NULL.
    orca=# select * from recovery_file where status_id=1 LIMIT 2;
                    job_id                |        granule_id        |         filename        |         key_path         |   restore_destination    | multipart_chunksize_mb | status_id | error_message |         request_time          |          last_update          | completion_time
    --------------------------------------+--------------------------+-------------------------+--------------------------+--------------------------+-----------+---------------+-------------------------------+-------------------------------+-----------------
    3efd79f0-f7f5-4109-afd8-a16c36b7f270 | 687687b5b5441c3c3626b39e | 8dbb97f77729cd437a93232e | 8dbb97f77729cd437a93232e | 248f9d70d72f69f9d578966c |                   NULL |         1 |               | 2021-04-24 19:10:04.855081+00 | 2021-04-29 15:10:04.855081+00 |
    2766e7bd-d1da-4c7d-8161-2f01ae2f8cd1 | 8132aeb56fcd3a56155e6f23 | 6585af9ca8cd765df803c605 | 6585af9ca8cd765df803c605 | 3288d5c9a706237839db94f8 |                   NULL |         1 |               | 2021-04-24 20:10:04.855081+00 | 2021-04-29 15:10:04.855081+00 |
    (2 rows)

    # Check the complete data. Verify completion date is set and error_message
    # is NULL.
    orca=# select * from recovery_file where status_id=4 LIMIT 2;

                    job_id                |        granule_id        |         filename        |         key_path         |   restore_destination    | multipart_chunksize_mb | status_id | error_message |         request_time          |          last_update          | completion_time
    --------------------------------------+--------------------------+-------------------------+--------------------------+--------------------------+-----------+------------------------+---------------+-------------------------------+-------------------------------+------------------------------
    5cad5640-ec11-48d0-9edb-a69cc0db99ef | 379f47a2f4b20801422242fa | 677c162d5e01009773a90b4e | 677c162d5e01009773a90b4e | eb9032c408f08350b1544054 |                   NULL |         4 |               | 2021-04-15 15:10:04.855081+00 | 2021-04-29 15:10:04.855081+00 | 2021-04-29 15:10:04.855081+00
    b4ccf94e-d439-4b71-b9e4-6d3ba6b867a9 | d8420b485a8a2ad194a1fdc4 | bc859b2dec647a32c8a2edc9 | bc859b2dec647a32c8a2edc9 | afd07600908d2c476ccceb72 |                   NULL |         4 |               | 2021-04-15 16:10:04.855081+00 | 2021-04-29 15:10:04.855081+00 | 2021-04-29 15:10:04.855081+00
                                          (2 rows)

    # Check the error data. Verify completion date is set and error_message
    # is set to "Some error occured here".
    orca=# select * from recovery_file where status_id=3 LIMIT 2;

                    job_id                |        granule_id        |         filename        |         key_path         |   restore_destination    | multipart_chunksize_mb | status_id |      error_message      |         request_time          |          last_update          | completion_time
    --------------------------------------+--------------------------+-------------------------+--------------------------+--------------------------+-----------+------------------------+-------------------------+-------------------------------+-------------------------------+------------------------------
    bd325313-e4fb-4c8d-8941-14e27942c081 | 140f54e91f70cdf5c23ceb9f | 7237771bd8e9c8614ebdf1fe | 7237771bd8e9c8614ebdf1fe | 8752510fd8053d01a33dd002 |                   NULL |         3 | Some error occurerd here | 2021-04-20 05:10:04.855081+00 | 2021-04-29 15:10:04.855081+00 | 2021-04-29 15:10:04.855081+00
    f87f219e-b04b-4ca7-abc2-bcdec1809182 | e1f62c411040f269a5aef941 | d4a228869f83a3395c36eaf1 | d4a228869f83a3395c36eaf1 | a27b5b0a2c08a40067c409f0 |                   NULL |         3 | Some error occurred here | 2021-04-20 06:10:04.855081+00 | 2021-04-29 15:10:04.855081+00 | 2021-04-29 15:10:04.855081+00
    (2 rows)

    ```
12. Run additional queries joining the recovery_job and recovery_file tables on
    job_id and granule_id and validate that the request_time,completion_time, and
    status_id information matches in both tables for a given record.


### Running and Verifying Specific Version Migrations

All of ORCA's database migrations logic is cumulative which means regadless of
the schema starting version, the `db_deploy` code will always migrate the user to
the latest schema version. On occasion, a developer may want to test a specific
migration path like from the previous version to the current version. This can
be done by using the version rollback scripts. The table below provides guidance
on the order the scripts need to be called in order to roll back to the specific
schema version.

<table>
  <thead>
    <tr>
      <th>From Latest To Version</th>
      <th>Order of Rollback Scripts</th>
      <th>What is Changed?</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>4</td>
      <td>
        <ol>
          <li>sql/orca_schema_v5/remove.sql</li>
        </ol>
      </td>
      <td>
        <ul>
          <li>reconcile_catalog_mismatch_report table removed</li>
          <li>reconcile_job table removed</li>
          <li>reconcile_orphan_report table removed</li>
          <li>reconcile_phantom_report table removed</li>
          <li>reconcile_s3_object table removed</li>
          <li>reconcile_s3_object_orca_special_backup table removed</li>
          <li>reconcile_s3_object_orca_versioned_backup table removed</li>
          <li>reconcile_s3_object_orca_worm_backup table removed</li>
          <li>reconcile_status table removed</li>
          <li>aws_s3 extension removed</li>
        </ul>
      </td>
    </tr>
    <tr>
      <td>3</td>
      <td>
        <ol>
          <li>sql/orca_schema_v5/remove.sql</li>
          <li>sql/orca_schema_v4/remove.sql</li>
        </ol>
      </td>
      <td>
        <ul>
          <li>collections table removed</li>
          <li>files table removed</li>
          <li>granules table removed</li>
          <li>providers table removed</li>
        </ul>
      </td>
    </tr>
      <td>2</td>
      <td>
        <ol>
          <li>sql/orca_schema_v5/remove.sql</li>
          <li>sql/orca_schema_v4/remove.sql</li>
          <li>sql/orca_schema_v3/remove.sql</li>
        </ol>
      </td>
      <td>
        <ul>
          <li>recovery_job.multipart_chunksize_mb column removed</li>
        </ul>
      </td>
    </tr>
      <td>1</td>
      <td>
        <ol>
          <li>sql/orca_schema_v5/remove.sql</li>
          <li>sql/orca_schema_v4/remove.sql</li>
          <li>sql/orca_schema_v3/remove.sql</li>
          <li>sql/orca_schema_v2/remove.sql</li>
          <li>sql/orca_schema_v1/create.sql</li>
        </ol>
      </td>
      <td>
        <ul>
          <li>recovery_file table removed</li>
          <li>recovery_job table removed</li>
          <li>recovery_status table removed</li>
          <li>schema_versions table removed</li>
          <li>app_role and dbo_role groups are removed</li>
          <li>orcauser is removed</li>
          <li>orca schema is removed</li>
        </ul>
      </td>
    </tr>
  </tbody>
</table>

Run the scripts one at a time in the proper order as denoted in the table above.
To run the scripts, log into postgres via the **pgclient** window and run the
commands below. Substitute `<SQL script file>` with the proper file name from
the table above. The `\i <SQL script file>;` line will be run once for each file.

```bash
root@56a9df92a881:/data/tasks/db_deploy/test/manual_tests# psql
psql (10.14 (Debian 10.14-1.pgdg90+1), server 10.20 (Debian 10.20-1.pgdg90+1))
Type "help" for help.

postgres=# \c orca
You are now connected to database "orca" as user "postgres".

orca=# \i <SQL script file>;
```

Once the schema is rolled back to the proper version, running the
`python manual_test.py` command in the **python** window will start the migration.
Validating the migration follows the same steps as the migration test validation
above with the only diffrence being the amount of information emitted in the log
will be a subset of total migration from version 1 to latest logs.


### Migration Test Cleanup

No cleanup is necessary if the next test run is the [Database No Migration Test](#database-no-migration-test).

To clean up from this test run he `sql/cleanup.sql` script. This will remove all
objects including the *orca* database.

```bash
root@56a9df92a881:/data/tasks/db_deploy/test/manual_tests# psql
psql (10.14 (Debian 10.14-1.pgdg90+1), server 10.20 (Debian 10.20-1.pgdg90+1))
Type "help" for help.

postgres=# \c orca
You are now connected to database "orca" as user "postgres".

orca=# \i sql/cleanup.sql

postgres=# \q
```



## Database No Migration Test

This test validates that the db_deploy scripts correctly identify that the latest
ORCA schema is installed and does not perform any additional actions.

### Database Setup No Migration Test

The *orca* database should be installed with the latest ORCA schema version. This
test should be ran immediately after the Fresh Install or Migration test so that
the latest version of the schema is installed and validated.

### Running the No Migration Test

To run the no migration test, in your **python** window run the command
`python manual_test.py`. The output should look similar to below.

```bash
(venv) root@cf4b0741a628:/data/test/manual_tests# python manual_test.py

{"message": "Beginning manual test.", "timestamp": "2022-02-16T22:42:05.435474", "level": "info"}
{"message": "Creating admin user connection object.", "timestamp": "2022-02-16T22:42:05.435659", "level": "debug"}
{"message": "Database set to postgres for the connection.", "timestamp": "2022-02-16T22:42:05.435745", "level": "debug"}
{"message": "Creating URL object to connect to the database.", "timestamp": "2022-02-16T22:42:05.435821", "level": "debug"}
{"message": "Creating admin user connection object.", "timestamp": "2022-02-16T22:42:05.551283", "level": "debug"}
{"message": "Database set to orca for the connection.", "timestamp": "2022-02-16T22:42:05.551413", "level": "debug"}
{"message": "Creating URL object to connect to the database.", "timestamp": "2022-02-16T22:42:05.551470", "level": "debug"}
{"message": "ORCA schema exists. Checking for schema versions.", "timestamp": "2022-02-16T22:42:05.758473", "level": "debug"}
{"message": "Checking for schema_versions table.", "timestamp": "2022-02-16T22:42:05.758659", "level": "debug"}
{"message": "schema_versions table exists True", "timestamp": "2022-02-16T22:42:05.766004", "level": "debug"}
{"message": "Getting current schema version from table.", "timestamp": "2022-02-16T22:42:05.766144", "level": "debug"}
{"message": "Current ORCA schema version detected. No migration needed!", "timestamp": "2022-02-16T22:42:05.770799", "level": "info"}
{"message": "Manual test complete.", "timestamp": "2022-02-16T22:42:05.771868", "level": "info"}
```


### Validating the No Migration Test

Verify the following info message lines appear in the output. Note that
the time stamp value will be different.

```bash
{"message": "Current ORCA schema version detected. No migration needed!", "timestamp": "2022-02-16T22:42:05.770799", "level": "info"}
```

Perform validation tests similar to the Migration or Fresh Install tests to
verify the schema objects have not changed.

### Cleaning Up the No Migration Test

From the **pgclient** window run the `sql/cleanup.sql` script as seen below.

```bash
root@56a9df92a881:/data/tasks/db_deploy/test/manual_tests# psql
psql (10.14 (Debian 10.14-1.pgdg90+1), server 10.20 (Debian 10.20-1.pgdg90+1))
Type "help" for help.

postgres=# \c orca
You are now connected to database "orca" as user "postgres".

orca=# \i sql/cleanup.sql

DROP EXTENSION
DROP TABLE
DROP TABLE
DROP TABLE
DROP TABLE
DROP TABLE
DROP TABLE
DROP TABLE
DROP TABLE
DROP TABLE
DELETE 1
INSERT 0 1
psql:sql/orca_schema_v5/remove.sql:18: WARNING:  there is no transaction in progress
COMMIT
DROP TABLE
DROP TABLE
DROP TABLE
DROP TABLE
DELETE 1
INSERT 0 1
psql:sql/orca_schema_v4/remove.sql:12: WARNING:  there is no transaction in progress
COMMIT
ALTER TABLE
DELETE 1
INSERT 0 1
psql:sql/orca_schema_v3/remove.sql:14: WARNING:  there is no transaction in progress
COMMIT
psql:sql/orca_schema_v2/remove.sql:1: NOTICE:  drop cascades to 4 other objects
DETAIL:  drop cascades to table orca.schema_versions
drop cascades to table orca.recovery_status
drop cascades to table orca.recovery_job
drop cascades to table orca.recovery_file
DROP SCHEMA
DROP ROLE
REVOKE
REVOKE
DROP ROLE
REVOKE
DROP ROLE
psql:sql/orca_schema_v2/remove.sql:8: WARNING:  there is no transaction in progress
COMMIT
psql:sql/orca_schema_v1/remove.sql:1: NOTICE:  schema "dr" does not exist, skipping
DROP SCHEMA
psql:sql/orca_schema_v1/remove.sql:2: NOTICE:  role "druser" does not exist, skipping
DROP ROLE
psql:sql/orca_schema_v1/remove.sql:3: ERROR:  role "dbo" does not exist
psql:sql/orca_schema_v1/remove.sql:4: NOTICE:  role "dbo" does not exist, skipping
DROP ROLE
psql:sql/orca_schema_v1/remove.sql:5: ERROR:  role "drdbo_role" does not exist
psql:sql/orca_schema_v1/remove.sql:6: ERROR:  role "drdbo_role" does not exist
psql:sql/orca_schema_v1/remove.sql:7: NOTICE:  role "drdbo_role" does not exist, skipping
DROP ROLE
psql:sql/orca_schema_v1/remove.sql:8: ERROR:  role "dr_role" does not exist
psql:sql/orca_schema_v1/remove.sql:9: NOTICE:  role "dr_role" does not exist, skipping
DROP ROLE
psql:sql/orca_schema_v1/remove.sql:10: WARNING:  there is no transaction in progress
COMMIT
You are now connected to database "postgres" as user "postgres".
DROP DATABASE

postgres=# \q
```