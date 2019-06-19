**Lambda function request_files **

- [Setup](#setup)
- [Development](#development)
  * [Unit Testing and Coverage](#unit-testing-and-coverage)
  * [Linting](#linting)
- [Integration Testing](#integration-testing)
- [Deployment](#deployment)
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
(podr) λ nosetests --with-coverage --cover-erase --cover-package=request_files -v
test_handler_client_error_2_times (test_request_files.TestRequestFiles) ... ok
test_handler_client_error_3_times (test_request_files.TestRequestFiles) ... ok
test_handler_client_error_one_file (test_request_files.TestRequestFiles) ... ok
test_handler_no_bucket (test_request_files.TestRequestFiles) ... ok
test_handler_no_expire_days_env_var (test_request_files.TestRequestFiles) ... ok
test_handler_no_retries_env_var (test_request_files.TestRequestFiles) ... ok
test_handler_one_granule_4_files_success (test_request_files.TestRequestFiles) ... ok
test_handler_two_granules (test_request_files.TestRequestFiles) ... ok

Name               Stmts   Miss  Cover
--------------------------------------
request_files.py      65      0   100%
----------------------------------------------------------------------
Ran 8 tests in 1.641s

```
<a name="linting"></a>
## Linting
```
Run pylint against the code:

(podr) λ cd C:\devpy\poswotdr\tasks\request_files
(podr) λ pylint request_files.py

--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)
```
<a name="integration-testing"></a>
## Integration Testing
```
Create an S3 bucket, for example, my-dr-fake-glacier-bucket
Create a folder in the bucket, for example, dr-glacier
Upload some small dummy test files to the folder.
Make a restore request:

input:
{
  "glacierBucket": "my-dr-fake-glacier-bucket",
  "granules": [
    {
      "granuleId": "MOD09GQ.A0219114.N5aUCG.006.0656338553321",
      "filepaths": [
        "dr-glacier/MOD09GQ.A0219115.N5aUCG.006.0656338553321.hdf.txt"
      ]
    }
  ]
}

check status of restore request
(podr) λ aws s3api head-object --bucket my-dr-fake-glacier-bucket --key dr-glacier/MOD09GQ.A0219115.N5aUCG.006.0656338553321.hdf.txt

```
<a name="deployment"></a>
## Deployment
```
    cd tasks\request_files
    zip request_files.zip *.py
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
                restore_expire_days (number, optional, default = 5): The number of days
                    the restored file will be accessible in the S3 bucket before it expires.
                restore_request_retries (number, optional, default = 3): The number of
                    attempts to retry a restore_request that failed to submit.
                restore_retry_sleep_secs (number, optional, default = 0): The number of seconds
                    to sleep between retry attempts.

            Args:
                event (dict): A dict with the following keys:

                    glacierBucket (string) :  The name of the glacier bucket from which the files
                        will be restored.
                    granules (list(dict)): A list of dict with the following keys:
                        granuleId (string): The id of the granule being restored.
                        filepaths (list(string)): list of filepaths (glacier keys) for the granule

                    Example: event: {'glacierBucket': 'some_bucket',
                                'granules': [{'granuleId': 'granxyz',
                                            'filepaths': ['path1', 'path2']}]
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