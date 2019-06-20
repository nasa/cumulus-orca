**Lambda function dr_copy_files_to_archive **

- [Setup](#setup)
- [Development](#development)
  * [Unit Testing and Coverage](#unit-testing-and-coverage)
  * [Linting](#linting)
- [Deployment](#deployment)
  * [Deployment Validation](#deployment-validation)
- [pydoc dr_copy_files_to_archive](#pydoc)

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

(podr) λ cd C:\devpy\poswotdr\tasks\dr_copy_files_to_archive
(podr) λ nosetests --with-coverage --cover-erase --cover-package=dr_copy_files_to_archive -v
test_handler_no_bucket_map (test_dr_copy_files_to_archive.TestCopyFiles) ... ok
test_handler_no_ext_in_bucket_map (test_dr_copy_files_to_archive.TestCopyFiles) ... ok
test_handler_no_object_key_in_event (test_dr_copy_files_to_archive.TestCopyFiles) ... ok
test_handler_no_other_in_bucket_map (test_dr_copy_files_to_archive.TestCopyFiles) ... ok
test_handler_one_file_fail_3x (test_dr_copy_files_to_archive.TestCopyFiles) ... ok
test_handler_one_file_retry2_success (test_dr_copy_files_to_archive.TestCopyFiles) ... ok
test_handler_one_file_success (test_dr_copy_files_to_archive.TestCopyFiles) ... ok
test_handler_two_records_one_fail_one_success (test_dr_copy_files_to_archive.TestCopyFiles) ... ok
test_handler_two_records_success (test_dr_copy_files_to_archive.TestCopyFiles) ... ok

Name                          Stmts   Miss  Cover
-------------------------------------------------
dr_copy_files_to_archive.py      79      0   100%
----------------------------------------------------------------------
Ran 9 tests in 5.650s

```
<a name="linting"></a>
## Linting
```
Run pylint against the code:

(podr) λ cd C:\devpy\poswotdr\tasks\dr_copy_files_to_archive
(podr) λ pylint dr_copy_files_to_archive.py

--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)
```
<a name="deployment"></a>
## Deployment
```
    cd tasks\dr_copy_files_to_archive
    zip task.zip *.py
```
<a name="deployment-validation"></a>
### Deployment Validation
```
1.  Upload the files in /tasks/testfiles/ to the test glacier bucket.
    It may take overnight for the files to be moved to Glacier.
2.  Once the files are in Glacier, run the request_files lambda to restore them.
    You can use the test event in /tasks/request_files/test/testevents/restore_test_files.json
    The restore may take up to 5 hours.
3.  When the restore completes, the ObjectRestore:Post event should trigger the
    dr_copy_files_to_archive lambda. You can also test it using the
    test events in /tasks/dr_copy_files_to_archive/test/testevents. You
    can view the logs in Cloud Watch for /aws/lambda/dr_copy_files_to_archive
```
<a name="pydoc"></a>
## pydoc dr_copy_files_to_archive
```
NAME
    dr_copy_files_to_archive - Name: dr_copy_files_to_archive.py

DESCRIPTION
    Description:  Lambda function that copies files from one s3 bucket
    to another s3 bucket.

CLASSES
    builtins.Exception(builtins.BaseException)
        CopyRequestError

    class CopyRequestError(builtins.Exception)
     |  Exception to be raised if the copy request fails for any of the files.

FUNCTIONS
    handler(event, context)
        Lambda handler. Copies a file from it's temporary s3 bucket to the s3 archive.

        If the copy for a file in the request fails, the lambda
        throws an exception. Environment variables can be set to override how many
        times to retry a copy before failing, and how long to wait between retries.

            Environment Vars:
                bucket_map (dict): A dict of key:value entries, where the key is a file
                    extension (including the .) ex. ".hdf", and the value is the destination
                    bucket for files with that extension. One of the keys can be "other"
                    to designate a bucket for any extensions that are not explicitly
                    mapped.
                    ex.  {".hdf": "my-great-protected-bucket",
                          ".met": "my-great-protected-bucket",
                          ".txt": "my-great-public-bucket",
                          "other": "my-great-protected-bucket"}
                copy_retries (number, optional, default = 3): The number of
                    attempts to retry a copy that failed.
                copy_retry_sleep_secs (number, optional, default = 0): The number of seconds
                    to sleep between retry attempts.

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

                context (Object): None
```
