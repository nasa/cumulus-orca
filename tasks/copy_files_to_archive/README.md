[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/copy_files_to_archive/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/copy_files_to_archive/requirements.txt)

**Lambda function copy_files_to_archive **

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro) for information on environment setup and testing.

- [Deployment](#deployment)
  * [Deployment Validation](#deployment-validation)
- [pydoc copy_files_to_archive](#pydoc-copy-files)

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
                COPY_RETRIES (number, optional, default = 2): The number of
                    attempts to retry a copy that failed.
                COPY_RETRY_SLEEP_SECS (number, optional, default = 30): The number of seconds
                    to sleep between retry attempts.
                DATABASE_PORT (string): the database port. The standard is 5432.
                DATABASE_NAME (string): the name of the database.
                DATABASE_USER (string): the name of the application user.

            Parameter Store:
                drdb-user-pass (string): the password for the application user (DATABASE_USER).
                drdb-host (string): the database host
                
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
                A list of dicts with the following keys:
                    'source_key' (string): The object key of the file that was restored.
                    'source_bucket' (string): The name of the s3 bucket where the restored
                        file was temporarily sitting.
                    'target_bucket' (string): The name of the archive s3 bucket.
                    'success' (boolean): True, if the copy was successful,
                        otherwise False.
                    'err_msg' (string): when success is False, this will contain
                        the error message from the copy error.
                    'request_id' (string): The request_id of the database entry.
                        Only guaranteed to be present if 'success' == True.

                All 'success' values will be True.
                If they were not all True, the CopyRequestError exception would be raised.

            Raises:
                CopyRequestError: An error occurred calling copy_object for one or more files.
                The same dict that is returned for a successful copy, will be included in the
                message, with 'success' = False for the files for which the copy failed.
```
