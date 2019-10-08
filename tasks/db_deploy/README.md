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
->setenv PASS %DB_PW_HERE%; docker run -p 5432:5432 -e POSTGRES_PASSWORD=$PASS --name daac_db -d postgres:11.4 
->bash
(this next command maps %GIT_WORK_DIR%/database/ddl to /data inside the container)
bash-4.2$docker run -it --rm -v %GIT_WORK_DIR%/database/ddl:/data postgres:11.4 /bin/bash
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
Port: 5432
Database:  postgres  
```
<a name="development"></a>
# Development

<a name="unit-testing-and-coverage"></a>
## Unit Testing and Coverage
```
To run the tests you'll need to define these 5 environment variables in a file
named private_config.json in the db_deploy folder. Do NOT check it into GIT. 
ex:
(podr2) λ cat private_config.json 
{"DATABASE_HOST": "%DOCKER_HOST%",
"DATABASE_PORT": "%DB_PORT%", 
"DATABASE_NAME": "%DB_NAME%",
"DATABASE_USER": "%APP_USER_NAME%",
"DATABASE_PW": "%DB_PW_HERE%",
"MASTER_USER_PW": %MASTER_USER_PW_HERE%}

λ activate podr

(podr) λ cd C:\devpy\poswotdr\tasks\db_deploy
(podr) λ nosetests --with-coverage --cover-erase --cover-package=db_deploy -v

Name           Stmts   Miss  Cover
----------------------------------
db_deploy.py     160      0   100%
----------------------------------------------------------------------
Ran 8 tests in 87.100s


Run the tests:
C:\devpy\poswotdr\tasks\db_deploy  
(podr2) λ nosetests test/test_db_deploy.py -v

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
1.  Create an empty JSON test event:
    {}

2.  Set the following environment variables
    DATABASE_HOST   Amazon RDS | Databases | choose db instance | Connectivity & Security | Endpoint value
    DATABASE_PORT   %DB_PORT%
    DATABASE_NAME   %DB_NAME%
    DATABASE_PW     %DB_PW_HERE%
    DATABASE_USER   %APP_USER_NAME%
    MASTER_USER_PW  %MASTER_USER_PW_HERE%
    DDL_DIR         ddl/
    DROP_DATABASE   True to perform DROP_DATABASE, False to keep existing database
    PLATFORM        AWS 

3.  Execute the test event.

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
                DATABASE_HOST (string): the server where the database will reside.
                DATABASE_PORT (string): the database port number
                DATABASE_NAME (string): the name of the database being created.
                DATABASE_USER (string): the name of the application user.
                DATABASE_PW (string): the password for the application user.
                MASTER_USER_PW (string): the password for the master user.
                DROP_DATABASE (bool, optional, default is False): When true, will
                    execute a DROP DATABASE command.
                PLATFORM (string): 'onprem' or 'AWS'

            Args:
                event (dict): empty
                    Example: event: {}
                context (Object): None

            Returns:
                string: status description.

            Raises:
                DatabaseError: An error occurred.
```
