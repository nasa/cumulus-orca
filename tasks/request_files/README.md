[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/request_files/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/request_files/requirements.txt)

**Lambda function request_files **

- [Setup](#setup)
- [Development](#development)
  * [Unit Testing and Coverage](#unit-testing-and-coverage)
  * [Linting](#linting)
- [Deployment](#deployment)
  * [Deployment Validation](#deployment-validation)
- [pydoc request_files](#pydoc-request-files)
- [pydoc copy_files_to_archive](#pydoc-copy-files)
- [pydoc request_status](#pydoc-request-status)

<a name="setup"></a>
# Setup
    See the README in the tasks folder for general development setup instructions
    See the README in the tasks/dr_dbutils folder to install dr_dbutils

<a name="development"></a>
# Development

<a name="unit-testing-and-coverage"></a>
## Unit Testing and Coverage
```
Test files in the test folder that end with _postgres.py run
against a Postgres database in a Docker container, and allow you to 
develop against an actual database. You can create the database
using task/db_deploy. 
These postgres tests allow you to test things that the mocked tests won't catch -
such as a restore request that fails the first time and succeeds the second time. The mocked 
tests didn't catch that it was actually inserting two rows ('error' and 'inprogress'), instead
of inserting one 'error' row, then updating it to 'inprogress'.
Note that these _postgres test files could use some more assert tests.
For now they can be used as a development aid. To run them you'll need to define
these 5 environment variables in a file named private_config.json, but do NOT check it into GIT. 
ex:
(podr2) λ cat private_config.json 
{"DATABASE_HOST": "db.host.gov_goes_here",
"DATABASE_PORT": "dbport_goes_here", 
"DATABASE_NAME": "dbname_goes_here", 
"DATABASE_USER": "dbusername_goes_here", 
"DATABASE_PW": "db_pw_goes_here"}

The remaining tests have everything mocked.

### Create docker container with DB for testing

`docker run -it --rm --name some-postgres -v /Users/<user>/cumulus-orca/database/ddl/base:/docker-entrypoint-initdb.d/ -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres`

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

#### Note that you have to use the druser account, otherwise the schema path won't quite match and you may receive errors like "table doesn't exist"

Run the tests:
C:\devpy\poswotdr\tasks\request_files  
λ activate podr
All tests:
(podr) λ pytest

Individual tests (insert desired test file name):
(podr) λ pytest test/test_requests_postgres.py

Code Coverage:
(podr) λ cd C:\devpy\poswotdr\tasks\request_files
(podr) λ coverage run --source request_files -m pytest
(podr) λ coverage report

Name               Stmts   Miss  Cover
--------------------------------------
request_files.py     117      0   100%
----------------------------------------------------------------------
Ran 16 tests in 13.150s
```
<a name="linting"></a>
## Linting
```
Run pylint against the code:

(podr) λ cd C:\devpy\poswotdr\tasks\request_files
(podr) λ pylint request_files.py
--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)

(podr) λ pylint test/request_helpers.py
--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)

(podr) λ pylint test/test_request_files.py
--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)

(podr) λ pylint test/test_request_files_postgres.py
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
1.  The easiest way to test is to use the DrRecoveryWorkflowStateMachine.
    You can use the test event in tasks/extract_filepaths_for_granule/test/testevents/StepFunction.json.
    Edit the ['payload']['granules']['keys'] values as needed to be the file(s) you wish to restore.
    Edit the ['cumulus_meta']['execution_name'] to be something unique (like yyyymmdd_hhmm). Then
    copy and paste the same value to the execution name field above the input field.
    The restore may take up to 5 hours.

Use the AWS CLI to check status of restore request:
ex> (podr) λ aws s3api head-object --bucket podaac-sndbx-cumulus-glacier --key L0A_RAD_RAW_product_0001-of-0020.iso.xml
```
<a name="pydoc-request-files"></a>
## pydoc request_files
```
NAME
    request_files - Name: request_files.py

DESCRIPTION
    Description:  Lambda function that makes a restore request from glacier for each input file.

CLASSES
    builtins.Exception(builtins.BaseException)
        RestoreRequestError

    class RestoreRequestError(builtins.Exception)
     |  Exception to be raised if the restore request fails submission for any of the files.

FUNCTIONS
    handler(event, context)
        Lambda handler. Initiates a restore_object request from glacier for each file of a granule.

        Note that this function is set up to accept a list of granules, (because Cumulus sends a list),
        but at this time, only 1 granule will be accepted.
        This is due to the error handling. If the restore request for any file for a
        granule fails to submit, the entire granule (workflow) fails. If more than one granule were
        accepted, and a failure occured, at present, it would fail all of them.
        Environment variables can be set to override how many days to keep the restored files, how
        many times to retry a restore_request, and how long to wait between retries.

            Environment Vars:
                RESTORE_EXPIRE_DAYS (number, optional, default = 5): The number of days
                    the restored file will be accessible in the S3 bucket before it expires.
                RESTORE_REQUEST_RETRIES (number, optional, default = 3): The number of
                    attempts to retry a restore_request that failed to submit.
                RESTORE_RETRY_SLEEP_SECS (number, optional, default = 0): The number of seconds
                    to sleep between retry attempts.
                RESTORE_RETRIEVAL_TYPE (string, optional, default = 'Standard'): the Tier
                    for the restore request. Valid valuesare 'Standard'|'Bulk'|'Expedited'.
                DATABASE_PORT (string): the database port. The standard is 5432.
                DATABASE_NAME (string): the name of the database.
                DATABASE_USER (string): the name of the application user.

            Parameter Store:
                drdb-user-pass (string): the password for the application user (DATABASE_USER).
                drdb-host (string): the database host

            Args:
                event (dict): A dict with the following keys:

                    glacierBucket (string) :  The name of the glacier bucket from which the files
                        will be restored.
                    granules (list(dict)): A list of dict with the following keys:
                        granuleId (string): The id of the granule being restored.
                        keys (list(string)): list of keys (glacier keys) for the granule

                    Example: event: {'glacierBucket': 'some_bucket',
                                     'granules': [{'granuleId': 'granxyz',
                                                   'keys': ['path1', 'path2']}]
                               }

                context (Object): None

            Returns:
                dict: The dict returned from the task. All 'success' values will be True. If they were
                not all True, the RestoreRequestError exception would be raised.

            Raises:
                RestoreRequestError: An error occurred calling restore_object for one or more files.
                The same dict that is returned for a successful granule restore, will be included in the
                message, with 'success' = False for the files for which the restore request failed to
                submit.
```
