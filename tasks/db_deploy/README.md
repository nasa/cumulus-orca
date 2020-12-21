[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/db_deploy/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/db_deploy/requirements.txt)

**Lambda function db_deploy **

- [Setup](#setup)
  * [Docker Database Setup](#docker-db-setup)
- [Development](#development)
  * [Unit Testing and Coverage](#unit-testing-and-coverage)
  * [Linting](#linting)
- [Deployment](#deployment)
  * [Deployment Validation](#deployment-validation)
- [pydoc db_deploy](#pydoc)

<a name="setup"></a>
# Setup
    See the README in the tasks folder for general development setup instructions
    See the README in the tasks/dr_dbutils folder to install dr_dbutils

<a name="docker-db-setup"></a>
## Docker Database Setup
```
The unit tests run against a Docker instance of Postgres. No methods are mocked.

Setup the Database instance in Docker:
Substitute actual values for these placeholders throughout this README:
    %DB_PW_HERE%    the actual password for the app users database login
    %MASTER_USER_PW_HERE% the actual password for the master user
    %GIT_WORK_DIR%  the directory where you cloned the repo to (ex. '/home/myuser/dr-podaac-swot'
    %DOCKER_HOST%   the Docker hostname
    %DB_PORT%       the datbase port. The standard is 5432.
    %DB_NAME%       from database/ddl/base/database/database_create.sql
    %APP_USER_NAME% from database/ddl/base/users/appuser.sql

On a Docker server:
->setenv PASS %DB_PW_HERE%; docker run -p 5432:%DB_PORT% -e POSTGRES_PASSWORD=$PASS --name daac_db -d postgres:11.4 
->bash
(this next command maps %GIT_WORK_DIR%/database to /data inside the container)
bash-4.2$docker run -it --rm -v %GIT_WORK_DIR%/database:/data postgres:11.4 /bin/bash
root@883bc270c77f:/# cd /data/base
root@883bc270c77f:/data/base# psql -h %DOCKER_HOST% -U postgres postgres
Password for user postgres:  %DB_PW_HERE%

To list the databases:
postgres-# \l
                                     List of databases
       Name        |  Owner   | Encoding |  Collate   |   Ctype    |   Access privileges
-------------------+----------+----------+------------+------------+------------------------
 postgres          | postgres | UTF8     | en_US.utf8 | en_US.utf8 |
 template0         | postgres | UTF8     | en_US.utf8 | en_US.utf8 | =c/postgres           +
                   |          |          |            |            | postgres=CTc/postgres
 template1         | postgres | UTF8     | en_US.utf8 | en_US.utf8 | =c/postgres           +
                   |          |          |            |            | postgres=CTc/postgres

To change the password for the appuser:
postgres=# \password %APP_USER_NAME%
Enter new password:
Enter it again:

To exit psql:
postgres=# \q

Connect to the DB in AquaData Studio:
Right click on ‘PostgreSQL Servers’ and click ‘Register Server’
Choose PostgreSQL on the left.
Name:  dr docker - postgres
Login Name:  postgres       
Password:    %MASTER_USER_PW_HERE%
Host:   %DOCKER_HOST%
Port: %DB_PORT%
Database:  postgres  
```
<a name="development"></a>
# Development

<a name="unit-testing-and-coverage"></a>
## Unit Testing and Coverage
```
To run the tests you'll need to define these 5 environment variables in a file
named `private_config.json` in the db_deploy/test folder. Do NOT check it into GIT. 
ex:
(podr2) λ cat private_config.json 
{"DATABASE_HOST": "%DOCKER_HOST%",
"DATABASE_PORT": "%DB_PORT%", 
"DATABASE_NAME": "%DB_NAME%",
"DATABASE_USER": "%APP_USER_NAME%",
"DATABASE_PW": "%DB_PW_HERE%",
"MASTER_USER_PW": %MASTER_USER_PW_HERE%}

## Create docker container with DB for testing

`docker run -it --rm --name some-postgres -v /Users/jmcampbell/cumulus-orca/database/ddl/base:/docker-entrypoint-initdb.d/ -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres`

*In another terminal:*

`docker run -it --rm --network host -e POSTGRES_PASSWORD=<new_password> postgres psql -h localhost -U postgres`

```
psql=# ALTER USER druser WITH PASSWORD 'new_password';
```

Once you've made these changes, update your `private_config.json` file with:

```json
{
    "DATABASE_USER": "druser",
    "DATABASE_PW": "<the value you added"
}

### Note that you have to use the druser account, otherwise the schema path won't quite match and you may receive errors like "table doesn't exist"

λ activate podr

(podr) λ cd C:\devpy\poswotdr\tasks\db_deploy
(podr) λ coverage run --source db_deploy -m pytest
(podr) λ coverage report

Name           Stmts   Miss  Cover
----------------------------------
db_deploy.py     159      0   100%
----------------------------------------------------------------------
Ran 8 tests in 0.987s

```
<a name="linting"></a>
## Linting
```
Run pylint against the code:

(podr) λ cd C:\devpy\poswotdr\tasks\db_deploy
(podr) λ pylint db_deploy.py
--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)

(podr) λ pylint utils/database.py
************* Module utils.database
utils\database.py:22:1: W0511: TODO develop tests for database.py later. in those mock psycopg2.cursor, etc (fixme)
------------------------------------------------------------------
Your code has been rated at 9.77/10 (previous run: 9.77/10, +0.00)

(podr) λ pylint test/test_db_deploy.py
--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)

```
<a name="deployment"></a>
## Deployment
```
    see /bin/build_tasks.sh to build the zip file. Upload the zip file to AWS.
```
<a name="deployment-validation"></a>
### Deployment Validation
```
1.  When deploying the complete Disaster Recovery Solution, this lambda is 
    excuted as part of the deployment and should create the disaster_recovery
    database. Use the request_status lambda to query it.
    
    If you are in a sandbox environment, and want to re-create the database,
    set the DROP_DATABASE environment variable to True. To update the tables in 
    an existing database set it to False.

2.  Set the following environment variables
    DATABASE_PORT   %DB_PORT%
    DATABASE_NAME   %DB_NAME%
    DATABASE_USER   %APP_USER_NAME%
    DDL_DIR         ddl/
    DROP_DATABASE   True to perform DROP_DATABASE, False to keep existing database
    PLATFORM        AWS 

3.  create an empty JSON test event:
    {}
    Execute the test event.

4.  Use the request_status lambda to verify the database.
```
<a name="pydoc"></a>
## pydoc db_deploy
```
NAME
    db_deploy - Name: db_deploy.py

DESCRIPTION
    Description:  Deploys a database, roles, users, schema, and tables.

CLASSES
    builtins.Exception(builtins.BaseException)
        DatabaseError

    class DatabaseError(builtins.Exception)
     |  Exception to be raised when there's a database error.

FUNCTIONS
    handler(event, context)
    
        This task will create the database, roles, users, schema, and tables.

            Environment Vars:
                DATABASE_PORT (string): the database port. The standard is 5432.
                DATABASE_NAME (string): the name of the database being created.
                DATABASE_USER (string): the name of the application user.
                DROP_DATABASE (bool, optional, default is False): When true, will
                    execute a DROP DATABASE command.
                PLATFORM (string): 'onprem' or 'AWS'

            Parameter Store:
                drdb-user-pass (string): the password for the application user (DATABASE_USER).
                drdb-host (string): the database host
                drdb-admin-pass: the password for the admin user

            Args:
                event (dict): empty
                    Example: event: {}
                context (Object): None

            Returns:
                string: status description.

            Raises:
                DatabaseError: An error occurred.
```
