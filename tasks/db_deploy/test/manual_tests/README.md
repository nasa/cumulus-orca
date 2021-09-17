# Manual Testing for the db_deploy Lambda Code

The following document provides the steps and files needed to manually test and
verify the db_deploy application.

To run the tests provided below, run the steps in the [initial setup](#initial-setup)
section first.

It is recommended to run the tests in the following order.
- [Database Migration v1 to v4 Test](#database-migration-v1-to-v4-test)
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
   **pgclient** window in the remaining instructions. run the following commands
   in the window.
   ```bash
   cd /data/tasks/db_deploy/test/manual_tests
   psql
   ```
4. In a new terminal window run the setup script with the `python` action
   `./setup_testing.sh python`. This will put you in a bash environment that
   can use the proper version of python for the tests. This window will be
   called the **python** window in the remaining instructions.
5. In the **python** window run the following commands to load the needed
   libraries for testing and put the user in the proper testing directory.
   ```bash
   python3 -m venv venv
   . venv/bin/activate
   cd /data/tasks/db_deploy
   pip install -r requirements-dev.txt
   cd test/manual_tests
   ```


## Tear Down of Environment

Once all tests are complete perform the following:

1. Close the **python** window by typing `exit` at the command prompt.
2. Close the **pgclient** window by quitting psql via the `\q` command and then
   typing `exit` at the command prompt.
3. Shut down PostgreSQL and cleanup by running the `./setup_testing stop` command
   in the setup window.
4. Remove the defined `DATA_DIR` directory and data.

## Database Fresh Install Test

This test validates that the db_deploy scripts will perform a fresh install if
the server exists without the disaster_recovery database.

### Database Setup Fresh Install Test

In the **pgclient** window use the `psql` client to connect to the database and
validate that the *disaster_recovery* database does not exist as seen below.

```bash
root@26df0390e999:/# psql
psql (12.6 (Debian 12.6-1.pgdg100+1))
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

C:\Users\adorn\GitHub\orca\cumulus-orca\tasks\db_deploy\venv\Scripts\python.exe C:/Users/adorn/GitHub/orca/cumulus-orca/tasks/db_deploy/test/manual_tests/manual_test.py
{"message": "Beginning manual test.", "timestamp": "2021-09-15T15:32:30.320254", "level": "info"}
{"message": "Creating admin user connection object.", "timestamp": "2021-09-15T15:32:30.320254", "level": "debug"}
{"message": "Database set to postgres for the connection.", "timestamp": "2021-09-15T15:32:30.320254", "level": "debug"}
{"message": "Creating URL object to connect to the database.", "timestamp": "2021-09-15T15:32:30.320254", "level": "debug"}
{"message": "Creating admin user connection object.", "timestamp": "2021-09-15T15:32:30.351539", "level": "debug"}
{"message": "Database set to disaster_recovery for the connection.", "timestamp": "2021-09-15T15:32:30.351539", "level": "debug"}
{"message": "Creating URL object to connect to the database.", "timestamp": "2021-09-15T15:32:30.351539", "level": "debug"}
{"message": "The ORCA database disaster_recovery does not exist.", "timestamp": "2021-09-15T15:32:33.326334", "level": "info"}
{"message": "Creating admin user connection object.", "timestamp": "2021-09-15T15:32:35.184367", "level": "debug"}
{"message": "Database set to disaster_recovery for the connection.", "timestamp": "2021-09-15T15:32:35.184367", "level": "debug"}
{"message": "Creating URL object to connect to the database.", "timestamp": "2021-09-15T15:32:35.184367", "level": "debug"}
{"message": "Creating the ORCA dbo role ...", "timestamp": "2021-09-15T15:32:38.537891", "level": "debug"}
{"message": "ORCA dbo role created.", "timestamp": "2021-09-15T15:32:38.968242", "level": "info"}
{"message": "Creating the ORCA app role ...", "timestamp": "2021-09-15T15:32:38.968242", "level": "debug"}
{"message": "ORCA app role created.", "timestamp": "2021-09-15T15:32:39.187607", "level": "info"}
{"message": "Creating the ORCA schema ...", "timestamp": "2021-09-15T15:32:39.187607", "level": "debug"}
{"message": "ORCA schema created.", "timestamp": "2021-09-15T15:32:40.453552", "level": "info"}
{"message": "Creating the ORCA application user ...", "timestamp": "2021-09-15T15:32:40.453552", "level": "debug"}
{"message": "ORCA application user created.", "timestamp": "2021-09-15T15:32:40.679509", "level": "info"}
{"message": "Changing to the dbo role to create objects ...", "timestamp": "2021-09-15T15:32:40.679509", "level": "debug"}
{"message": "Setting search path to the ORCA schema to create objects ...", "timestamp": "2021-09-15T15:32:40.804050", "level": "debug"}
{"message": "Creating schema_versions table ...", "timestamp": "2021-09-15T15:32:41.045785", "level": "debug"}
{"message": "schema_versions table created.", "timestamp": "2021-09-15T15:32:41.287815", "level": "info"}
{"message": "Populating the schema_versions table with data ...", "timestamp": "2021-09-15T15:32:41.287815", "level": "debug"}
{"message": "Data added to the schema_versions table.", "timestamp": "2021-09-15T15:32:41.517232", "level": "info"}
{"message": "Creating recovery_status table ...", "timestamp": "2021-09-15T15:32:41.517232", "level": "debug"}
{"message": "recovery_status table created.", "timestamp": "2021-09-15T15:32:41.725347", "level": "info"}
{"message": "Populating the recovery_status table with data ...", "timestamp": "2021-09-15T15:32:41.725347", "level": "debug"}
{"message": "Data added to the recovery_status table.", "timestamp": "2021-09-15T15:32:41.960324", "level": "info"}
{"message": "Creating recovery_job table ...", "timestamp": "2021-09-15T15:32:41.960324", "level": "debug"}
{"message": "recovery_job table created.", "timestamp": "2021-09-15T15:32:42.180611", "level": "info"}
{"message": "Creating recovery_file table ...", "timestamp": "2021-09-15T15:32:42.180611", "level": "debug"}
{"message": "recovery_file table created.", "timestamp": "2021-09-15T15:32:42.404445", "level": "info"}
{"message": "Creating providers table ...", "timestamp": "2021-09-15T15:32:42.404445", "level": "debug"}
{"message": "providers table created.", "timestamp": "2021-09-15T15:32:42.612921", "level": "info"}
{"message": "Creating collections table ...", "timestamp": "2021-09-15T15:32:42.612921", "level": "debug"}
{"message": "collections table created.", "timestamp": "2021-09-15T15:32:42.927131", "level": "info"}
{"message": "Creating provider and collection cross reference table ...", "timestamp": "2021-09-15T15:32:42.927131", "level": "debug"}
{"message": "provider and collection cross reference table created.", "timestamp": "2021-09-15T15:32:43.164561", "level": "info"}
{"message": "Creating granules table ...", "timestamp": "2021-09-15T15:32:43.164561", "level": "debug"}
{"message": "granules table created.", "timestamp": "2021-09-15T15:32:43.445441", "level": "info"}
{"message": "Creating files table ...", "timestamp": "2021-09-15T15:32:43.445441", "level": "debug"}
{"message": "files table created.", "timestamp": "2021-09-15T15:32:43.710367", "level": "info"}
{"message": "Manual test complete.", "timestamp": "2021-09-15T15:32:44.145858", "level": "info"}

Process finished with exit code 0
```


### Fresh Install Test Validation

To validate the fresh install perform the following actions.

First, review the logs and verify that the following *info* messages were
expressed in the logs.

```bash
{"message": "Performing full install of ORCA schema.", "timestamp": "2021-09-14T13:37:47.649467", "level": "info"}
{"message": "ORCA dbo role created.", "timestamp": "2021-09-14T13:37:51.271456", "level": "info"}
{"message": "ORCA app role created.", "timestamp": "2021-09-14T13:37:51.472515", "level": "info"}
{"message": "ORCA schema created.", "timestamp": "2021-09-14T13:37:51.715371", "level": "info"}
{"message": "ORCA application user created.", "timestamp": "2021-09-14T13:37:51.912015", "level": "info"}
{"message": "schema_versions table created.", "timestamp": "2021-09-14T13:37:52.720591", "level": "info"}
{"message": "Data added to the recovery_status table.", "timestamp": "2021-09-14T13:37:53.398124", "level": "info"}
{"message": "recovery_status table created.", "timestamp": "2021-09-14T13:37:53.185110", "level": "info"}
{"message": "Data added to the recovery_status table.", "timestamp": "2021-09-14T13:37:53.398124", "level": "info"}
{"message": "recovery_job table created.", "timestamp": "2021-09-14T13:37:53.621899", "level": "info"}
{"message": "recovery_file table created.", "timestamp": "2021-09-14T13:37:53.843190", "level": "info"}
{"message": "providers table created.", "timestamp": "2021-09-14T13:37:54.056274", "level": "info"}
{"message": "collections table created.", "timestamp": "2021-09-14T13:37:54.279718", "level": "info"}
{"message": "provider and collection cross reference table created.", "timestamp": "2021-09-14T13:37:54.494315", "level": "info"}
{"message": "granules table created.", "timestamp": "2021-09-14T13:37:54.711834", "level": "info"}
{"message": "files table created.", "timestamp": "2021-09-14T13:37:54.927886", "level": "info"}

```

Next, verify that the objects were actually created with the proper data in the
PostgreSQL *disaster_recovery* database. Perform the checks below by going to the
**pgclient** window and logging into the *disaster_recovery* database as the
*postgres* user as seen below.

```bash
   root@26df0390e999:/data/test/manual_tests# psql
   psql (12.6 (Debian 12.6-1.pgdg100+1))
   Type "help" for help

   postgres=# \c disaster_recovery
   You are now connected to database "disaster_recovery" as user "postgres".
```

1. Verify that the roles/users were created and that *orcauser* is a
   part of the *orca_app* role.
   ```bash
   postgres=# \du
                                       List of roles
    Role name |                         Attributes                         | Member of
   -----------+------------------------------------------------------------+------------
    orca_app  | Cannot login                                               | {}
    orca_dbo  | Cannot login                                               | {}
    orcauser  |                                                            | {orca_app}
    postgres  | Superuser, Create role, Create DB, Replication, Bypass RLS | {}
   ```
2. Verify the ORCA schema was created.
   ```bash
   disaster_recovery=# \dn

     List of schemas
     Name  |  Owner
   --------+----------
    orca   | orca_dbo
    public | postgres
   (2 rows)
   ```
3. Verify the tables were created in the ORCA schema.
   ```bash
   disaster_recovery=# \dt orca.*

                 List of relations
    Schema |      Name                 | Type  |  Owner
   --------+---------------------------+-------+----------
    orca   | collections               | table | orca_dbo
    orca   | files                     | table | orca_dbo
    orca   | granules                  | table | orca_dbo
    orca   | providers                 | table | orca_dbo
    orca   | provider_collection_xref  | table | orca_dbo
    orca   | recovery_file             | table | orca_dbo
    orca   | recovery_job              | table | orca_dbo
    orca   | recovery_status           | table | orca_dbo
    orca   | schema_versions           | table | orca_dbo
    (9 rows)
   ```
4. Verify the static data in the *recovery_status* table.
   ```bash
   disaster_recovery=# select * from orca.recovery_status;

    id |  value
   ----+----------
     1 | pending
     2 | staged
     3 | error
     4 | complete
   (4 rows)
   ```
5. Verify the static data in the *schema_versions* table.
   ```bash
   disaster_recovery=# select * from orca.schema_versions;

    version_id |                     description                      |         install _date         | is_latest
   ------------+------------------------------------------------------+-------------------------------+-----------
             4 | Added inventory schema for v4.x of ORCA application  | 2021-04-28 23:3 9:58.63444+00 | t
   (1 row)
   ```
6. Verify the orcauser can login with the password provided in the `.env` files
   `APPLICATION_PASSWORD` environment variable.
   ```bash
   disaster_recovery=# \c "dbname=disaster_recovery user=orcauser password=<Your Password Here>"

   You are now connected to database "disaster_recovery" as user "orcauser".
   ```


### Fresh Install Test Cleanup

No cleanup is necessary if the next test run is the [Database No Migration Test](#database-no-migration-test).

The `sql/cleanup.sql` script will remove all objects including the *disaster_recovery* database. The
`sql/orca_schema_v2/remove.sql` script will remove only the objects created
in this test but leave the database intact. Both scripts must be run as the
*postgres* user.

```bash
root@26df0390e999:/data/test/manual_tests# psql
psql (12.6 (Debian 12.6-1.pgdg100+1))
Type "help" for help.

postgres=# \c disaster_recovery
You are now connected to database "disaster_recovery" as user "postgres".

disaster_recovery=# \i sql/orca_schema_v2/remove.sql

psql:sql/orca_schema_v2/remove.sql:1: NOTICE:  drop cascades to 4 other objects
DETAIL:  drop cascades to table orca.schema_versions
drop cascades to table orca.recovery_status
drop cascades to table orca.recovery_job
drop cascades to table orca.recovery_file
drop cascades to table orca.schema_versions
drop cascades to table orca.files
drop cascades to table orca.granules
drop cascades to table orca.provider_collections_xref
drop cascades to table orca.collections
drop cascades to table orca.providers
DROP SCHEMA
DROP ROLE
REVOKE
REVOKE
DROP ROLE
REVOKE
DROP ROLE
psql:sql/orca_schema_v2/remove.sql:8: WARNING:  there is no transaction in progress
COMMIT
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

## Database Migration v1 to v4 Test

This test validates that the db_deploy scripts correctly identify a v1 ORCA
schema and run the migration of objects and data to an ORCA v4 schema.

### Database Setup Migration Test

1. Verify that the *disaster_recovery* database does not exist. If it does, remove
   it using the `\i sql/cleanup.sql` command as described in the [DNE Test](#database-setup-dne-test).
2. Create the *disaster_recovery* database by using the `\i sql/create_database.sql`
   command as seen below.
   ```bash
   root@26df0390e999:/data/test/manual_tests# psql
   psql (12.6 (Debian 12.6-1.pgdg100+1))
   Type "help" for help

   postgres=# \i sql/create_database.sql
   CREATE DATABASE
   COMMENT
   ```
3. Run the `sql/orca_schema_v1/create.sql` script as seen below. This will
   populate the database with the users, schema, tables and dummy data used for
   migrating from v1 of the schema to v4.
   ```bash
   root@26df0390e999:/data/test/manual_tests# psql
   psql (12.6 (Debian 12.6-1.pgdg100+1))
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
   You are now connected to database "disaster_recovery" as user "postgres".
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
   
   # Once complete quit psql. We will login as postgres user during validation.
   disaster_recovery=> \q
   ```


### Running the Migration Test

To run the migration test, in your **python** window run the command
`python manual_test.py`. The output should look similar to below.

```bash
(venv) root@cf4b0741a628:/data/test/manual_tests# python manual_test.py

{"message": "Beginning manual test.", "timestamp": "2021-09-14T13:37:39.791395", "level": "info"}
{"message": "Creating admin user connection object.", "timestamp": "2021-09-14T13:37:39.791395", "level": "debug"}
{"message": "Database set to postgres for the connection.", "timestamp": "2021-09-14T13:37:39.791395", "level": "debug"}
{"message": "Creating URL object to connect to the database.", "timestamp": "2021-09-14T13:37:39.791395", "level": "debug"}
{"message": "Creating admin user connection object.", "timestamp": "2021-09-14T13:37:39.826098", "level": "debug"}
{"message": "Database set to disaster_recovery for the connection.", "timestamp": "2021-09-14T13:37:39.826098", "level": "debug"}
{"message": "Creating URL object to connect to the database.", "timestamp": "2021-09-14T13:37:39.826098", "level": "debug"}
{"message": "Performing full install of ORCA schema.", "timestamp": "2021-09-14T13:37:47.649467", "level": "info"}
{"message": "Creating admin user connection object.", "timestamp": "2021-09-14T13:37:47.649467", "level": "debug"}
{"message": "Database set to disaster_recovery for the connection.", "timestamp": "2021-09-14T13:37:47.649467", "level": "debug"}
{"message": "Creating URL object to connect to the database.", "timestamp": "2021-09-14T13:37:47.649467", "level": "debug"}
{"message": "Creating the ORCA dbo role ...", "timestamp": "2021-09-14T13:37:50.859040", "level": "debug"}
{"message": "ORCA dbo role created.", "timestamp": "2021-09-14T13:37:51.271456", "level": "info"}
{"message": "Creating the ORCA app role ...", "timestamp": "2021-09-14T13:37:51.271456", "level": "debug"}
{"message": "ORCA app role created.", "timestamp": "2021-09-14T13:37:51.472515", "level": "info"}
{"message": "Creating the ORCA schema ...", "timestamp": "2021-09-14T13:37:51.472515", "level": "debug"}
{"message": "ORCA schema created.", "timestamp": "2021-09-14T13:37:51.715371", "level": "info"}
{"message": "Creating the ORCA application user ...", "timestamp": "2021-09-14T13:37:51.715892", "level": "debug"}
{"message": "ORCA application user created.", "timestamp": "2021-09-14T13:37:51.912015", "level": "info"}
{"message": "Changing to the dbo role to create objects ...", "timestamp": "2021-09-14T13:37:51.912015", "level": "debug"}
{"message": "Setting search path to the ORCA schema to create objects ...", "timestamp": "2021-09-14T13:37:52.076420", "level": "debug"}
{"message": "Creating schema_versions table ...", "timestamp": "2021-09-14T13:37:52.359576", "level": "debug"}
{"message": "schema_versions table created.", "timestamp": "2021-09-14T13:37:52.720591", "level": "info"}
{"message": "Populating the schema_versions table with data ...", "timestamp": "2021-09-14T13:37:52.720591", "level": "debug"}
{"message": "Data added to the schema_versions table.", "timestamp": "2021-09-14T13:37:52.967958", "level": "info"}
{"message": "Creating recovery_status table ...", "timestamp": "2021-09-14T13:37:52.967958", "level": "debug"}
{"message": "recovery_status table created.", "timestamp": "2021-09-14T13:37:53.185110", "level": "info"}
{"message": "Populating the recovery_status table with data ...", "timestamp": "2021-09-14T13:37:53.185110", "level": "debug"}
{"message": "Data added to the recovery_status table.", "timestamp": "2021-09-14T13:37:53.398124", "level": "info"}
{"message": "Creating recovery_job table ...", "timestamp": "2021-09-14T13:37:53.398714", "level": "debug"}
{"message": "recovery_job table created.", "timestamp": "2021-09-14T13:37:53.621899", "level": "info"}
{"message": "Creating recovery_file table ...", "timestamp": "2021-09-14T13:37:53.621899", "level": "debug"}
{"message": "recovery_file table created.", "timestamp": "2021-09-14T13:37:53.843190", "level": "info"}
{"message": "Creating providers table ...", "timestamp": "2021-09-14T13:37:53.843190", "level": "debug"}
{"message": "providers table created.", "timestamp": "2021-09-14T13:37:54.056274", "level": "info"}
{"message": "Creating collections table ...", "timestamp": "2021-09-14T13:37:54.056274", "level": "debug"}
{"message": "collections table created.", "timestamp": "2021-09-14T13:37:54.279718", "level": "info"}
{"message": "Creating provider and collection cross reference table ...", "timestamp": "2021-09-14T13:37:54.279718", "level": "debug"}
{"message": "provider and collection cross reference table created.", "timestamp": "2021-09-14T13:37:54.494315", "level": "info"}
{"message": "Creating granules table ...", "timestamp": "2021-09-14T13:37:54.494315", "level": "debug"}
{"message": "granules table created.", "timestamp": "2021-09-14T13:37:54.711834", "level": "info"}
{"message": "Creating files table ...", "timestamp": "2021-09-14T13:37:54.711834", "level": "debug"}
{"message": "files table created.", "timestamp": "2021-09-14T13:37:54.927886", "level": "info"}
{"message": "Data added to the schema_versions table.", "timestamp": "2021-09-14T15:20:20.231299", "level": "info"}
{"message": "Populating the schema_versions table with data ...", "timestamp": "2021-09-14T15:20:20.199998", "level": "debug"}
{"message": "Manual test complete.", "timestamp": "2021-09-14T15:20:20.363841", "level": "info"}
```


### Migration Test Validation

To validate the migration test perform the following actions.

First, review the logs and verify that the following *info* messages were
expressed in the logs.

```bash
{"message": "Performing migration of the ORCA schema.", "timestamp": "2021-09-14T15:20:18.952832", "level": "info"}
{"message": "ORCA dbo role created.", "timestamp": "2021-09-14T15:20:19.083400", "level": "info"}
{"message": "ORCA app role created.", "timestamp": "2021-09-14T15:20:19.090386", "level": "info"}
{"message": "ORCA schema created.", "timestamp": "2021-09-14T15:20:19.122371", "level": "info"}
{"message": "ORCA application user created.", "timestamp": "2021-09-14T15:20:19.155396", "level": "info"}
{"message": "schema_versions table created.", "timestamp": "2021-09-14T15:20:19.309066", "level": "info"}
{"message": "recovery_status table created.", "timestamp": "2021-09-14T15:20:19.402883", "level": "info"}
{"message": "recovery_job table created.", "timestamp": "2021-09-14T15:20:19.495748", "level": "info"}
{"message": "recovery_file table created.", "timestamp": "2021-09-14T15:20:19.597165", "level": "info"}
{"message": "Data added to the recovery_status table.", "timestamp": "2021-09-14T15:20:19.761836", "level": "info"}
{"message": "Data migrated to recovery_job table.", "timestamp": "2021-09-14T15:20:20.007252", "level": "info"}
{"message": "Data migrated to recovery_file table.", "timestamp": "2021-09-14T15:20:20.129916", "level": "info"}
{"message": "dr.request_status table removed.", "timestamp": "2021-09-14T15:20:20.154444", "level": "info"}
{"message": "dr schema removed.", "timestamp": "2021-09-14T15:20:20.165126", "level": "info"}
{"message": "drdbo_role role removed.", "timestamp": "2021-09-14T15:20:20.172164", "level": "info"}
{"message": "dr_role role removed.", "timestamp": "2021-09-14T15:20:20.181274", "level": "info"}
{"message": "dbo user removed", "timestamp": "2021-09-14T15:20:20.188715", "level": "info"}
{"message": "druser user removed.", "timestamp": "2021-09-14T15:20:20.199778", "level": "info"}
{"message": "providers table created.", "timestamp": "2021-09-14T15:20:20.231299", "level": "info"}
{"message": "collections table created.", "timestamp": "2021-09-14T15:20:20.231299", "level": "info"}
{"message": "provider and collection cross reference table created.", "timestamp": "2021-09-14T15:20:20.231299", "level": "info"}
{"message": "granules table created.", "timestamp": "2021-09-14T15:20:20.231299", "level": "info"}
{"message": "files table created.", "timestamp": "2021-09-14T15:20:20.231299", "level": "info"}
{"message": "Data added to the schema_versions table.", "timestamp": "2021-09-14T15:20:20.231299", "level": "info"}

```

Next, verify that the objects were actually created with the proper data in the
PostgreSQL *disaster_recovery* database. Perform the checks below by going to the
**pgclient** window and logging into the *disaster_recovery* database as the
*postgres* user as seen below.

```bash
   root@26df0390e999:/data/test/manual_tests# psql
   psql (12.6 (Debian 12.6-1.pgdg100+1))
   Type "help" for help

   postgres=# \c disaster_recovery
   You are now connected to database "disaster_recovery" as user "postgres".
```

1. Verify that the roles/users were created and that *orcauser* is a
   part of the *orca_app* role. Also verify the *dbo*, *druser*, *drdbo_role*,
   and *dr_role* have been removed.
   ```bash
   postgres=# \du
                                       List of roles
    Role name |                         Attributes                         | Member of
   -----------+------------------------------------------------------------+------------
    orca_app  | Cannot login                                               | {}
    orca_dbo  | Cannot login                                               | {}
    orcauser  |                                                            | {orca_app}
    postgres  | Superuser, Create role, Create DB, Replication, Bypass RLS | {}
   ```
2. Verify the ORCA schema was created and the *dr* schema was removed.
   ```bash
   disaster_recovery=# \dn

     List of schemas
     Name  |  Owner
   --------+----------
    orca   | orca_dbo
    public | postgres
   (2 rows)
   ```
3. Verify the tables were created in the ORCA schema.
   ```bash
   disaster_recovery=# \dt orca.*

                 List of relations
    Schema |      Name                 | Type  |  Owner
   --------+---------------------------+-------+----------
    orca   | collections               | table | orca_dbo
    orca   | files                     | table | orca_dbo
    orca   | granules                  | table | orca_dbo
    orca   | providers                 | table | orca_dbo
    orca   | provider_collection_xref  | table | orca_dbo
    orca   | recovery_file             | table | orca_dbo
    orca   | recovery_job              | table | orca_dbo
    orca   | recovery_status           | table | orca_dbo
    orca   | schema_versions           | table | orca_dbo
    (9 rows)
   ```
4. Verify the static data in the *recovery_status* table.
   ```bash
   disaster_recovery=# select * from orca.recovery_status;

    id |  value
   ----+----------
     1 | pending
     2 | staged
     3 | error
     4 | complete
   (4 rows)
   ```
5. Verify the static data in the *schema_versions* table.
   ```bash
   disaster_recovery=# select * from orca.schema_versions;

    version_id |                     description                      |         install _date         | is_latest
   ------------+------------------------------------------------------+-------------------------------+-----------
             4 | Added inventory schema for v4.x of ORCA application  | 2021-09-13 23:3 9:58.63444+00 | t
   (1 row)
   ```
6. Verify the orcauser can login with the password provided in the `.env` files
   `APPLICATION_PASSWORD` environment variable.
   ```bash
   disaster_recovery=# \c "dbname=disaster_recovery user=orcauser password=<Your Password Here>"

   You are now connected to database "disaster_recovery" as user "orcauser".
   ```
7. Validate that the data was properly migrated into the recovery jobs table. The
   dummy data has a 1 job -> 1 granule -> 1 file relation.
   ```bash
   # Check the total numbers based on status value. They should match the values
   # expressed below.
   disaster_recovery=# select status_id, count(*) from recovery_job group by 1;
   
   status_id | count
   -----------+-------
            1 |   117
            3 |   110
            4 |   110
   (3 rows)

   # Check the pending data. Verify completion date is not set and arcive_destination
   # is set to myglacierarchivebucket
   disaster_recovery=# select * from recovery_job where status_id = 1 LIMIT 5;

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
    disaster_recovery=# select * from recovery_job where status_id = 4 LIMIT 5;

                  job_id                |        granule_id        |  archive_destination   | multipart_chunksize_mb | status_id |         request_time          | completion_time
   -------------------------------------+--------------------------+------------------------+-----------+-------------------------------+-------------------------------
   04c9db6d-2d09-4e75-af79-feaf54c7771e | 64e83cc5103965b83fca62ad | myarchiveglacierbucket |                        |         4 | 2021-04-19 08:10:04.855081+00 | 2021-04-29 15:10:04.855081+00
   057e1fe7-c561-48c3-b539-65193de99279 | 0a1662031cfecd9c5190bf6d | myarchiveglacierbucket |                        |         4 | 2021-04-18 20:10:04.855081+00 | 2021-04-29 15:10:04.855081+00
   0c86fa12-8773-4da6-b0e3-38104230c12e | 7b8be6c8f9076afe64f1aa62 | myarchiveglacierbucket |                        |         4 | 2021-04-16 03:10:04.855081+00 | 2021-04-29 15:10:04.855081+00
   0e377a25-e8a6-4de8-86de-42dfad803b75 | cca7d86de488a25864f18095 | myarchiveglacierbucket |                        |         4 | 2021-04-18 02:10:04.855081+00 | 2021-04-29 15:10:04.855081+00
   0eefcaf1-5dc5-47eb-a299-a9c206bf58d5 | 11790a3ddcdfcd1cbd6e341b | myarchiveglacierbucket |                        |         4 | 2021-04-19 20:10:04.855081+00 | 2021-04-29 15:10:04.855081+00
   (5 rows)

   # Check the complete data. Verify completion date is set and arcive_destination
   # is set to myglacierarchivebucket
   disaster_recovery=# select * from recovery_job where status_id = 3 LIMIT 5;

                  job_id                |        granule_id        |  archive_destination   | status_id |         request_time          | completion_time
   -------------------------------------+--------------------------+------------------------+-----------+-------------------------------+-------------------------------
   0169a025-1e3e-4a69-ab64-498634cd933b | 865a440a34c319b22ee52419 | myarchiveglacierbucket |         3 | 2021-04-24 10:10:04.855081+00 | 2021-04-29 15:10:04.855081+00
   0673403b-6c52-459f-b59a-04ab9b87b93f | 9eda38da05d01ade96a3a3e8 | myarchiveglacierbucket |         3 | 2021-04-23 20:10:04.855081+00 | 2021-04-29 15:10:04.855081+00
   072db1cb-0efd-41b7-bc09-03272f0a6ab9 | 1bbf8c9d3b4b52a44220bdfc | myarchiveglacierbucket |         3 | 2021-04-24 08:10:04.855081+00 | 2021-04-29 15:10:04.855081+00
   09ccd4bc-7904-47f6-93e3-1f4ec21ff9b6 | 5510126af9eae7e6baab940a | myarchiveglacierbucket |         3 | 2021-04-21 13:10:04.855081+00 | 2021-04-29 15:10:04.855081+00
   0b4620bd-07d3-46a7-aa7c-db3c1316b697 | ac40bb34b5d64655daca2f1d | myarchiveglacierbucket |         3 | 2021-04-22 13:10:04.855081+00 | 2021-04-29 15:10:04.855081+00
   (5 rows)
   ```
8. Validate that the data was properly migrated into the recovery files table. The
   dummy data has a 1 job -> 1 granule -> 1 file relation.
   ```bash
   # Check the total numbers based on status value. They should match the values
   # expressed below.
   disaster_recovery=# select status_id, count(*) from recovery_file group by 1;
   
    status_id | count
   -----------+-------
            1 |   117
            3 |   110
            4 |   110
   (3 rows)

   # Check the pending data. Verify completion date is not set and error_message
   # is NULL.
   disaster_recovery=# select * from recovery_file where status_id=1 LIMIT 2;
                   job_id                |        granule_id        |         filename        |         key_path         |   restore_destination    | multipart_chunksize_mb | status_id | error_message |         request_time          |          last_update          | completion_time
   --------------------------------------+--------------------------+-------------------------+--------------------------+--------------------------+-----------+---------------+-------------------------------+-------------------------------+-----------------
   3efd79f0-f7f5-4109-afd8-a16c36b7f270 | 687687b5b5441c3c3626b39e | 8dbb97f77729cd437a93232e | 8dbb97f77729cd437a93232e | 248f9d70d72f69f9d578966c |                   NULL |         1 |               | 2021-04-24 19:10:04.855081+00 | 2021-04-29 15:10:04.855081+00 |
   2766e7bd-d1da-4c7d-8161-2f01ae2f8cd1 | 8132aeb56fcd3a56155e6f23 | 6585af9ca8cd765df803c605 | 6585af9ca8cd765df803c605 | 3288d5c9a706237839db94f8 |                   NULL |         1 |               | 2021-04-24 20:10:04.855081+00 | 2021-04-29 15:10:04.855081+00 |
   (2 rows)
   
   # Check the complete data. Verify completion date is set and error_message
   # is NULL.
   disaster_recovery=# select * from recovery_file where status_id=4 LIMIT 2;

                   job_id                |        granule_id        |         filename        |         key_path         |   restore_destination    | multipart_chunksize_mb | status_id | error_message |         request_time          |          last_update          | completion_time
   --------------------------------------+--------------------------+-------------------------+--------------------------+--------------------------+-----------+------------------------+---------------+-------------------------------+-------------------------------+------------------------------
   5cad5640-ec11-48d0-9edb-a69cc0db99ef | 379f47a2f4b20801422242fa | 677c162d5e01009773a90b4e | 677c162d5e01009773a90b4e | eb9032c408f08350b1544054 |                   NULL |         4 |               | 2021-04-15 15:10:04.855081+00 | 2021-04-29 15:10:04.855081+00 | 2021-04-29 15:10:04.855081+00
   b4ccf94e-d439-4b71-b9e4-6d3ba6b867a9 | d8420b485a8a2ad194a1fdc4 | bc859b2dec647a32c8a2edc9 | bc859b2dec647a32c8a2edc9 | afd07600908d2c476ccceb72 |                   NULL |         4 |               | 2021-04-15 16:10:04.855081+00 | 2021-04-29 15:10:04.855081+00 | 2021-04-29 15:10:04.855081+00
                                         (2 rows)
   
   # Check the error data. Verify completion date is set and error_message
   # is set to "Some error occured here".
   disaster_recovery=# select * from recovery_file where status_id=3 LIMIT 2;

                   job_id                |        granule_id        |         filename        |         key_path         |   restore_destination    | multipart_chunksize_mb | status_id |      error_message      |         request_time          |          last_update          | completion_time
   --------------------------------------+--------------------------+-------------------------+--------------------------+--------------------------+-----------+------------------------+-------------------------+-------------------------------+-------------------------------+------------------------------
   bd325313-e4fb-4c8d-8941-14e27942c081 | 140f54e91f70cdf5c23ceb9f | 7237771bd8e9c8614ebdf1fe | 7237771bd8e9c8614ebdf1fe | 8752510fd8053d01a33dd002 |                   NULL |         3 | Some error occurerd here | 2021-04-20 05:10:04.855081+00 | 2021-04-29 15:10:04.855081+00 | 2021-04-29 15:10:04.855081+00
   f87f219e-b04b-4ca7-abc2-bcdec1809182 | e1f62c411040f269a5aef941 | d4a228869f83a3395c36eaf1 | d4a228869f83a3395c36eaf1 | a27b5b0a2c08a40067c409f0 |                   NULL |         3 | Some error occurred here | 2021-04-20 06:10:04.855081+00 | 2021-04-29 15:10:04.855081+00 | 2021-04-29 15:10:04.855081+00
   (2 rows)

   ```
9. Run additional queries joining the recovery_job and recovery_file tables on
   job_id and granule_id and validate that the request_time,completion_time, and
   status_id information matches in both tables for a given record.



### Migration Test Cleanup

No cleanup is necessary if the next test run is the [Database No Migration Test](#database-no-migration-test).

To clean up from this test you can use one of two scripts. The `sql/cleanup.sql`
script will remove all objects including the *disaster_recovery* database. The
`sql/orca_schema_v4/remove.sql` script will migrate v4 schema to v3 schema, update the `schema_versions` table with value of 3 and also remove the `providers`, `collections`, `provider_collection_xref`, `granules` and `files` tables. The `sql/orca_schema_v3/remove.sql` script will migrate the schema from v3 to v2, update the `schema_versions` table with value of 2. The `sql/orca_schema_v2/remove.sql` script will migrate the schema from v2 to v1, update the `schema_versions` table with value of 1. The `sql/orca_schema_v1/remove.sql` script will remove all the user and roles created.

```bash
root@26df0390e999:/data/test/manual_tests# psql
psql (12.6 (Debian 12.6-1.pgdg100+1))
Type "help" for help.

postgres=# \c disaster_recovery
You are now connected to database "disaster_recovery" as user "postgres".

disaster_recovery=# \i sql/orca_schema_v4/remove.sql

DROP TABLE 
DROP TABLE 
DROP TABLE 
DROP TABLE 
DROP TABLE 
```



## Database No Migration Test

This test validates that the db_deploy scripts correctly identify that a v4 ORCA
schema is installed and do not perform any additional action.

### Database Setup No Migration Test

The *disaster_recovery* database should be installed with the ORCA version 4
schema. This test should be ran immediately after the Fresh Install or Migration
test so that a validated v4 schema is in place.

### Running the No Migration Test

To run the no migration test, in your **python** window run the command
`python manual_test.py`. The output should look similar to below.

```bash
(venv) root@cf4b0741a628:/data/test/manual_tests# python manual_test.py

{"message": "Beginning manual test.", "timestamp": "2021-04-29T16:09:07.629433", "level": "info"}
{"message": "Creating root user connection object.", "timestamp": "2021-04-29T16:09:07.630515", "level": "debug"}
{"message": "Database set to postgres for the connection.", "timestamp": "2021-04-29T16:09:07.630696", "level": "debug"}
{"message": "Creating URL object to connect to the database.", "timestamp": "2021-04-29T16:09:07.630804", "level": "debug"}
{"message": "Creating root user connection object.", "timestamp": "2021-04-29T16:09:08.452903", "level": "debug"}
{"message": "Database set to disaster_recovery for the connection.", "timestamp": "2021-04-29T16:09:08.453245", "level": "debug"}
{"message": "Creating URL object to connect to the database.", "timestamp": "2021-04-29T16:09:08.453468", "level": "debug"}
{"message": "ORCA schema exists. Checking for schema versions ...", "timestamp": "2021-04-29T16:09:08.617406", "level": "debug"}
{"message": "Creating root user connection object.", "timestamp": "2021-04-29T16:09:08.617941", "level": "debug"}
{"message": "Database set to disaster_recovery for the connection.", "timestamp": "2021-04-29T16:09:08.618295", "level": "debug"}
{"message": "Creating URL object to connect to the database.", "timestamp": "2021-04-29T16:09:08.618446", "level": "debug"}
{"message": "Checking for schema_versions table.", "timestamp": "2021-04-29T16:09:08.815223", "level": "debug"}
{"message": "schema_versions table exists True", "timestamp": "2021-04-29T16:09:08.871903", "level": "debug"}
{"message": "Getting current schema version from table.", "timestamp": "2021-04-29T16:09:08.872287", "level": "debug"}
{"message": "Current ORCA schema version detected. No migration needed!", "timestamp": "2021-04-29T16:09:08.912127", "level": "info"}
{"message": "Manual test complete.", "timestamp": "2021-04-29T16:09:08.912344", "level": "info"}
```


### Validating the No Migration Test

Verify the following info message lines appear in the output. Note that
the time stamp value will be different.

```bash
{"message": "Current ORCA schema version detected. No migration needed!", "timestamp": "2021-04-29T16:09:08.912127", "level": "info"}
```

Perform validation tests similar to the Migration or Fresh Install tests to
verify the v4 schema objects have not changed.

### Cleaning Up the No Migration Test

From the **pgclient** window run the `sql/cleanup.sql` script as seen below.

```bash
root@26df0390e999:/data/test/manual_tests# psql
psql (12.6 (Debian 12.6-1.pgdg100+1))
Type "help" for help.

postgres=# \c disaster_recovery
You are now connected to database "disaster_recovery" as user "postgres".

disaster_recovery=# \i sql/cleanup.sql
You are now connected to database "disaster_recovery" as user "postgres".
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
psql:sql/orca_schema_v2/remove.sql:1: NOTICE:  drop cascades to 4 other objects
DETAIL:  drop cascades to table orca.schema_versions
drop cascades to table orca.recovery_status
drop cascades to table orca.recovery_job
drop cascades to table orca.recovery_file
drop cascades to table orca.schema_versions
drop cascades to table orca.files
drop cascades to table orca.granules
drop cascades to table orca.provider_collections_xref
drop cascades to table orca.collections
drop cascades to table orca.providers
DROP SCHEMA
DROP ROLE
REVOKE
REVOKE
DROP ROLE
REVOKE
DROP ROLE
psql:sql/orca_schema_v2/remove.sql:8: WARNING:  there is no transaction in progress
COMMIT
You are now connected to database "postgres" as user "postgres".
DROP DATABASE
postgres=# \q
```