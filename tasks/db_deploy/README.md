[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/db_deploy/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/db_deploy/requirements.txt)

**Lambda function db_deploy **

- [Setup](#setup)
- [Deployment](#deployment)
  * [Deployment Validation](#deployment-validation)
- [pydoc db_deploy](#pydoc)

<a name="setup"></a>
# Setup
    See the README in the tasks folder for general development setup instructions
    See the README in the tasks/dr_dbutils folder to install dr_dbutils

# Development

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
