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

<a name="development"></a>
# Development

<a name="unit-testing-and-coverage"></a>
## Unit Testing and Coverage
```
There are 4 unit test files in the test folder. These have everything mocked
and are suitable for automation. The nosetests/code coverage here are using only these 4 files.
Note that you might need to temporarily move the 3 test files from the dev_test folder to 
somewhere that the tests won't pick them up (see 'Postgres Tests' below). 

λ activate podr

(podr) λ cd C:\devpy\poswotdr\tasks\request_files
(podr) λ nosetests --with-coverage --cover-erase --cover-package=request_files --cover-package=request_status --cover-package=copy_files_to_archive --cover-package=requests -v

Name                       Stmts   Miss  Cover
----------------------------------------------
copy_files_to_archive.py      97      0   100%
request_files.py             104      0   100%
request_status.py             67      0   100%
requests.py                  182      0   100%
----------------------------------------------
TOTAL                        450      0   100%
----------------------------------------------------------------------
Ran 59 tests in 16.982s

Postgres Tests:
There are 3 additional test files in the dev_test folder.
These run against a Postgres database in a Docker container, and allow you to 
develop against an actual database. The tests run successfully when run alone. However if
moved to the 'test' folder and included in the nosetests/code coverage
they introduce a lot of failures and poor coverage. I didn't take the time
to figure it out (maybe duplicate test function names among the files?). 
They do however allow you to test things that the mocked tests won't catch -
such as a restore request that fails the first time and succeeds the second time. The mocked 
tests didn't catch that it was actually inserting two rows ('error' and 'inprogress'), instead
of inserting one 'error' row, then updating it to 'inprogress'.
These 3 test files would need some work to be able to rely on them, such as more assert tests.
For now they can be used as a development aid. To run them you'll need to define
these 4 environment variables in a file named private_config.json, but do NOT check it into GIT. 
ex:
(podr2) λ cat private_config.json 
{"DATABASE_HOST": "db.host.gov_goes_here",
"DATABASE_PORT": "dbport_goes_here", 
"DATABASE_NAME": "dbname_goes_here", 
"DATABASE_USER": "dbusername_goes_here", 
"DATABASE_PW": "db_pw_goes_here"}

Eventually, it would be nice to move these to the test folder, but for now
to run them, you can either temporarily move them to the /test folder
Or copy the helper files to the dev_test folder:
cp test/request_helpers.py dev_test/
cp test/copy_helpers.py dev_test/ 

Run the tests:
C:\devpy\poswotdr\tasks\request_files (PCESA-1229 -> origin) 
(podr2) λ nosetests dev_test/test_requests_postgres.py -v
(podr2) λ nosetests dev_test/test_request_files_postgres.py -v
(podr2) λ nosetests dev_test/test_copy_files_to_archive_postgres.py -v

```
<a name="linting"></a>
## Linting
```
Run pylint against the code:

(podr) λ cd C:\devpy\poswotdr\tasks\request_files
(podr) λ pylint request_files.py
--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)

(podr) λ pylint copy_files_to_archive.py
--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)

(podr) λ pylint request_status.py
--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)

(podr) λ pylint requests.py
 --------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)

(podr) λ pylint utils/database.py
************* Module utils.database
utils\database.py:19:1: W0511: TODO develop tests for database.py later. in those mock psycopg2.cursor, etc (fixme)
------------------------------------------------------------------
Your code has been rated at 9.89/10 (previous run: 9.89/10, +0.00)

(podr) λ pylint test/copy_helpers.py
--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)

(podr) λ pylint test/request_helpers.py
--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)

(podr) λ pylint test/test_request_files.py
--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)

(podr) λ pylint test/test_copy_files_to_archive.py
--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)

(podr) λ pylint test/test_request_status.py
--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)

(podr) λ pylint test/test_requests.py
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
1.  Upload the files in /tasks/testfiles/ to the test glacier bucket.
    It may take overnight for the files to be moved to Glacier.
2.  I haven't figured out how to write an input event that populates the 'config' part, but you
    can use the test event in /tasks/request_files/test/testevents/RestoreTestFiles.json, and expect
    an error ending with 'does not contain a config value for glacier-bucket'
2.  Once the files are in Glacier, use the CumulusDrRecoveryWorkflowStateMachine to restore them.
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
                DATABASE_HOST (string): the server where the database resides.
                DATABASE_PORT (string): the database port. The standard is 5432.
                DATABASE_NAME (string): the name of the database.
                DATABASE_USER (string): the name of the application user.
                DATABASE_PW (string): the password for the application user.

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
                BUCKET_MAP (dict): A dict of key:value entries, where the key is a file
                    extension (including the .) ex. ".hdf", and the value is the destination
                    bucket for files with that extension. One of the keys can be "other"
                    to designate a bucket for any extensions that are not explicitly
                    mapped.
                    ex.  {".hdf": "my-great-protected-bucket",
                          ".met": "my-great-protected-bucket",
                          ".txt": "my-great-public-bucket",
                          "other": "my-great-protected-bucket"}
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
<a name="pydoc-request-status"></a>
## pydoc request_status
```
NAME
    request_status - Name: request_status.py

DESCRIPTION
    Description:  Queries the request_status table.

CLASSES
    builtins.Exception(builtins.BaseException)
        BadRequestError

    class BadRequestError(builtins.Exception)
        Exception to be raised if there is a problem with the request.

FUNCTIONS
    handler(event, context)
        Lambda handler. Retrieves job(s) from the database.

        Environment Vars:
            DATABASE_HOST (string): the server where the database resides.
            DATABASE_PORT (string): the database port. The standard is 5432.
            DATABASE_NAME (string): the name of the database.
            DATABASE_USER (string): the name of the application user.
            DATABASE_PW (string): the password for the application user.

        Args:
            event (dict): A dict with zero or one of the following keys:

                granule_id (string): A granule_id to retrieve
                request_id (string): A request_id (uuid) to retrieve
                job_id (string): A job_id to retrieve

                Example: event: {'granuleId': 'granxyz'
                                }

            context (Object): None

        Returns:
            (list(dict)): A list of dict with the following keys:
                'job_id' (number): Sequential id, uniquely identifying a table entry.
                'request_id' (string): The request_id the job belongs to.
                'granule_id' (string): The id of a granule.
                'object_key' (string): The name of the file that was requested.
                'job_type' (string): The type of job. "restore" or "regenerate"
                'restore_bucket_dest' (string): The bucket where the restored file will be put.
                'job_status' (string): The current status of the job
                'request_time' (string): UTC time that the request was initiated.
                'last_update_time' (string): UTC time of the last update to job_status.
                'err_msg' (string): Description of the error if the job_status is 'error'.

            Example:
                [
                    {
                        "job_id": 1,
                        "request_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
                        "granule_id": "granxyz",
                        "object_key": "my_test_filename",
                        "job_type": "restore",
                        "restore_bucket_dest": "my_test_bucket",
                        "job_status": "inprogress",
                        "request_time": "2019-09-30 18:24:38.370252+00:00",
                        "last_update_time": "2019-09-30 18:24:38.370252+00:00",
                        "err_msg": null
                    }
                ]

        Raises:
            BadRequestError: An error occurred parsing the input.
```
