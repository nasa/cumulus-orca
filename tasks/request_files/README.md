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
Run the unit tests with code coverage:

λ activate podr

(podr) λ cd C:\devpy\poswotdr\tasks\request_files
(podr) λ nosetests --with-coverage --cover-erase --cover-package=request_files --cover-package=request_status --cover-package=copy_files_to_archive --cover-package=requests -v
Tests the handler ... {"message": "request: {'input': {'granules': [{'granuleId': 'MOD09GQ.A0219114.N5aUCG.006.0656338553321', 'keys': ['L0A_LR_RAW_product_0010-of-0092.h5']}]}, 'config': {}} does not contain a config value for glacier-bucket", "level": "error", "executions": ["DrRecovery54"], "timestamp": "2019-07-09T09:34:15.167271", "sender": "request_files", "version": 1}
ok
Test two files, first successful, second has two errors, then success. ... ok
Test four files, first 3 successful, fourth errors on all retries and fails. ... ok
Test retries for restore error for one file. ... ok
Test a file that is not in glacier. ... ok
Test environment var RESTORE_EXPIRE_DAYS not set - use default. ... ok
Test for missing glacier-bucket in config. ... ok
Test environment var RESTORE_REQUEST_RETRIES not set - use default. ... ok
Test four files for one granule - successful ... ok
Test two granules with one file each - successful. ... ok

Name               Stmts   Miss  Cover
--------------------------------------
request_files.py      80      0   100%
----------------------------------------------------------------------
Ran 10 tests in 1.741s

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
