**Lambda function request_files **

- [Setup](#setup)
- [Development](#development)
  * [Unit Testing and Coverage](#unit-testing-and-coverage)
  * [Linting](#linting)
- [Deployment](#deployment)
  * [Deployment Validation](#deployment-validation)
- [pydoc request_files](#pydoc)

<a name="setup"></a>
# Setup
    See the README in the tasks folder for general development setup instructions

<a name="development"></a>
# Development

<a name="unit-testing-and-coverage"></a>
## Unit Testing and Coverage
```
There are 4 unit test files in the test folder. These have everything mocked
and are suitable for automation. The nosetests/code coverage here are using only these 4 files:

Run the unit tests with code coverage:

λ activate podr

(podr) λ cd C:\devpy\poswotdr\tasks\request_files
(podr) λ nosetests --with-coverage --cover-erase --cover-package=request_files --cover-package=request_status --cover-package=copy_files_to_archive --cover-package=requests -v
Name                       Stmts   Miss  Cover
----------------------------------------------
copy_files_to_archive.py      91      0   100%
request_files.py              98      0   100%
request_status.py             71      0   100%
requests.py                  182      0   100%
----------------------------------------------
TOTAL                        442      0   100%
----------------------------------------------------------------------
Ran 59 tests in 17.041s

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
these 4 environment variables in a file named private_config.json. Do NOT check into GIT. 
ex:
(podr2) λ cat private_config.json 
{"DATABASE_HOST": "db.host.gov_goes_here", 
"DATABASE_NAME": "dbname_goes_here", 
"DATABASE_USER": "dbusername_goes_here", 
"DATABASE_PW": "db_pw_goes_here"}

Eventually, it would be nice to move these to the test folder, but for now
to run them, you can either temporarily move them to the /test folder
Or copy the helper files to the dev_test folder:
cp test/request_helpers.py /dev_test/
cp test/copy_helpers.py /dev_test/ 

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

(podr) λ cd C:\devpy\poswotdr\tasks\request_files\test
(podr) λ pylint test_request_files.py

--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)
```
<a name="deployment"></a>
## Deployment
```
    cd tasks\request_files
    zip task.zip *.py
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
    The restore may take up to 5 hours.

Use the AWS CLI to check status of restore request:
ex> (podr) λ aws s3api head-object --bucket podaac-sndbx-cumulus-glacier --key L0A_RAD_RAW_product_0001-of-0020.iso.xml
```
<a name="pydoc"></a>
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
