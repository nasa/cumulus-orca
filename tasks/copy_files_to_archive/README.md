**Lambda function copy_files_to_archive **

- [Setup](#setup)
- [Development](#development)
  * [Unit Testing and Coverage](#unit-testing-and-coverage)
  * [Linting](#linting)
- [Deployment](#deployment)
  * [Deployment Validation](#deployment-validation)
- [pydoc copy_files_to_archive](#pydoc-copy-files)

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

Run the tests:
C:\devpy\poswotdr\tasks\copy_files_to_archive  
λ activate podr
All tests:
(podr) λ nosetests -v

Individual tests (insert desired test file name):
(podr) λ nosetests test/test_copy_files_to_archive.py -v

Code Coverage:
(podr) λ cd C:\devpy\poswotdr\tasks\copy_files_to_archive
(podr) λ nosetests --with-coverage --cover-erase --cover-package=copy_files_to_archive -v

Name                       Stmts   Miss  Cover
----------------------------------------------
copy_files_to_archive.py     119      0   100%
----------------------------------------------------------------------
Ran 15 tests in 22.936s
```
<a name="linting"></a>
## Linting
```
Run pylint against the code:

(podr) λ cd C:\devpy\poswotdr\tasks\copy_files_to_archive
(podr) λ pylint copy_files_to_archive.py
--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)

(podr) λ pylint test/test_copy_files_to_archive.py
--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)

(podr) λ pylint test/test_copy_files_to_archive_postgres.py
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
1.  Paste the contents of test/testevents/copy_exp_event_1.json into
    a test event and execute it.
2.  Neither the source_key or the source_bucket should exist, so the copy will fail
    and the database update will fail.

```
<a name="pydoc-copy-files"></a>
## pydoc copy_files_to_archive
```
NAME
    copy_files_to_archive - Name: copy_files_to_archive.py

DESCRIPTION
    Description:  Lambda function that copies files from one s3 bucket
    to another s3 bucket.

CLASSES
    builtins.Exception(builtins.BaseException)
        CopyRequestError

    class CopyRequestError(builtins.Exception)
        Exception to be raised if the copy request fails for any of the files.

FUNCTIONS
    handler(event, context)
        Lambda handler. Copies a file from it's temporary s3 bucket to the s3 archive.

        If the copy for a file in the request fails, the lambda
        throws an exception. Environment variables can be set to override how many
        times to retry a copy before failing, and how long to wait between retries.

            Environment Vars:
                COPY_RETRIES (number, optional, default = 3): The number of
                    attempts to retry a copy that failed.
                COPY_RETRY_SLEEP_SECS (number, optional, default = 0): The number of seconds
                    to sleep between retry attempts.
                DATABASE_HOST (string): the server where the database resides.
                DATABASE_PORT (string): the database port. The standard is 5432.
                DATABASE_NAME (string): the name of the database.
                DATABASE_USER (string): the name of the application user.
                DATABASE_PW (string): the password for the application user.

            Args:
                event (dict): A dict with the following keys:

                    Records (list(dict)): A list of dict with the following keys:
                        s3 (dict): A dict with the following keys:
                            bucket (dict):  A dict with the following keys:
                                name (string): The name of the s3 bucket holding the restored file
                            object (dict):  A dict with the following keys:
                                key (string): The key of the restored file

                    Example: event: {"Records": [{"eventVersion": "2.1",
                                          "eventSource": "aws:s3",
                                          "awsRegion": "us-west-2",
                                          "eventTime": "2019-06-17T18:54:06.686Z",
                                          "eventName": "ObjectRestore:Post",
                                          "userIdentity": {
                                          "principalId": "AWS:AROAJWMHUPO:request_files"},
                                          "requestParameters": {"sourceIPAddress": "1.001.001.001"},
                                          "responseElements": {"x-amz-request-id": "0364DB32C0",
                                                               "x-amz-id-2":
                                             "4TpisFevIyonOLD/z1OGUE/Ee3w/Et+pr7c5F2RbnAnU="},
                                          "s3": {"s3SchemaVersion": "1.0",
                                                "configurationId": "dr_restore_complete",
                                                "bucket": {"name": exp_src_bucket,
                                                           "ownerIdentity":
                                                           {"principalId": "A1BCXDGCJ9"},
                                                   "arn": "arn:aws:s3:::my-dr-fake-glacier-bucket"},
                                                "object": {"key": exp_file_key1,
                                                           "size": 645,
                                                           "sequencer": "005C54A126FB"}}}]}

                context (Object): None

            Returns:
                dict: The dict returned from the task. All 'success' values will be True. If they were
                not all True, the CopyRequestError exception would be raised.

            Raises:
                CopyRequestError: An error occurred calling copy_object for one or more files.
                The same dict that is returned for a successful copy, will be included in the
                message, with 'success' = False for the files for which the copy failed.
```
