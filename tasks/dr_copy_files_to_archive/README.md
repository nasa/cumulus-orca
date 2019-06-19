**Lambda function request_files **

- [Setup](#setup)
- [Development](#development)
  * [Unit Testing and Coverage](#unit-testing-and-coverage)
  * [Linting](#linting)
- [Integration Testing](#integration-testing)
- [Deployment](#deployment)
- [pydoc request_files](#pydoc-request-files)

# Setup
    See the README in the tasks folder for general development setup instructions

# Development

## Unit Testing and Coverage
```
Run the unit tests with code coverage:

λ activate podr

(podr) λ cd C:\devpy\poswotdr\tasks\dr_copy_files_to_archive
(podr) λ nosetests --with-coverage --cover-erase --cover-package=dr_copy_files_to_archive -v
test_handler_one_file_success (test_dr_copy_files_to_archive.TestCopyFiles) ... ok

Name                          Stmts   Miss  Cover
-------------------------------------------------
dr_copy_files_to_archive.py      82     18    78%
----------------------------------------------------------------------
Ran 1 test in 1.626s

```
## Linting
```
Run pylint against the code:

(podr) λ cd C:\devpy\poswotdr\tasks\dr_copy_files_to_archive
(podr) λ pylint dr_copy_files_to_archive.py

--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)
```
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

The restore request could take up to 5 hours. When it completes, the dr_copy_files_to_archive lambda
should be triggered. View the logs in Cloud Watch for /aws/lambda/dr_copy_files_to_archive

```
## Deployment
```
    cd tasks\dr_copy_files_to_archive
    zip dr_copy_files_to_archive.zip *.py
```
## pydoc dr_copy_files_to_archive
```
NAME
    dr_copy_files_to_archive - Name: dr_copy_files_to_archive.py

DESCRIPTION
    Description:  Lambda function that copies files for a granule that was
    restored from Glacier to the archive location.

CLASSES
    builtins.Exception(builtins.BaseException)
        CopyRequestError

    class CopyRequestError(builtins.Exception)
     |  Exception to be raised if the copy request fails for any of the files.

FUNCTIONS
    handler(event, context)
        Lambda handler. Copies a file from it's temporary s3 bucket to the s3 archive.

        If the copy for any file in the request fails, the entire lambda
        (workflow) fails. Environment variables can be set to override how
        many times to retry a copy, and how long to wait between retries.

            Environment Vars:
                protected_bucket (string): The name of the protected bucket where the data
                    files will be written.
                public_bucket (string): The name of the public bucket where the non-data
                    files will be written.
                copy_retries (number, optional, default = 3): The number of
                    attempts to retry a restore_request that failed to submit.
                copy_retry_sleep_secs (number, optional, default = 0): The number of seconds
                    to sleep between retry attempts.

            Args:
                event (dict): A dict with the following keys:

                    glacierBucket (string) :  The name of the glacier bucket from which the files
                        will be restored.
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