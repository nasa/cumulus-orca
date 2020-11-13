"""
Name: copy_files_to_archive.py

Description:  Lambda function that copies files from one s3 bucket
to another s3 bucket.
"""

import os
import time
import logging
from typing import Any, List, Dict, Optional

import boto3
from botocore.client import BaseClient
from botocore.exceptions import ClientError
import requests_db

FILE_SUCCESS_KEY = 'success'
FILE_SOURCE_KEY_KEY = 'source_key'
FILE_ERROR_MESSAGE_KEY = 'err_msg'
FILE_REQUEST_ID_KEY = 'request_id'
FILE_SOURCE_BUCKET_KEY = 'source_bucket'
FILE_TARGET_BUCKET_KEY = 'target_bucket'


class CopyRequestError(Exception):
    """
    Exception to be raised if the copy request fails for any of the files.
    """


def task(records: List[Dict[str, Any]], retries: int, retry_sleep_secs: float) -> List[Dict[str, Any]]:
    """
    Task called by the handler to perform the work.

    This task will call copy_object for each file. A copy will be tried
    up to {retries} times if it fails, waiting {retry_sleep_secs}
    between each attempt.

        Args:
            records: Passed through from the handler.
            retries: The number of attempts to retry a failed copy.
            retry_sleep_secs: The number of seconds
                to sleep between retry attempts.

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

            Example:  [{'source_key': 'file1.xml', 'source_bucket': 'my-dr-fake-glacier-bucket',
                          'target_bucket': 'unittest_xml_bucket', 'success': True,
                          'err_msg': ''},
                      {'source_key': 'file2.txt', 'source_bucket': 'my-dr-fake-glacier-bucket',
                          'target_bucket': 'unittest_txt_bucket', 'success': True,
                          'err_msg': ''}]
        # TODO: Do we not want to expose request_id? It's not even in the Example above.
        Raises:
            CopyRequestError: Thrown if there are errors with the input records or the copy failed.
    """
    files = get_files_from_records(records)
    attempt = 1
    s3 = boto3.client('s3')  # pylint: disable-msg=invalid-name
    while attempt <= retries:
        for a_file in files:
            # All files from get_files_from_records start with 'success' == False.
            if not a_file[FILE_SUCCESS_KEY]:
                key = a_file[FILE_SOURCE_KEY_KEY]
                try:
                    try:
                        a_file[FILE_REQUEST_ID_KEY]
                    except KeyError:  # Lazily get/set the request_id
                        job = find_job_in_db(key)
                        if job:
                            a_file[FILE_REQUEST_ID_KEY] = job['request_id']
                            a_file[FILE_TARGET_BUCKET_KEY] = job['archive_bucket_dest']
                        else:
                            continue
                    err_msg = copy_object(s3, a_file[FILE_SOURCE_BUCKET_KEY], a_file[FILE_SOURCE_KEY_KEY],
                                          a_file[FILE_TARGET_BUCKET_KEY])
                except requests_db.DatabaseError:
                    continue

                try:
                    # todo: Bit disingenuous to have nested retries...
                    update_status_in_db(a_file, attempt, err_msg)
                except requests_db.DatabaseError:
                    try:
                        time.sleep(
                            30)  # todo: Some room for optimization here. Why are there two sleeps?
                        update_status_in_db(a_file, attempt, err_msg)
                    except requests_db.DatabaseError:
                        continue

        attempt = attempt + 1
        if attempt <= retries:
            if all(a_file[FILE_SUCCESS_KEY] for a_file in files):  # Check for early completion
                return files
            time.sleep(retry_sleep_secs)

    return files


def find_job_in_db(key: str) -> Optional[Dict[str, Any]]:
    """
    Finds the active job for the file in the database.

        Args:
            key: The object key for the file to find in the db.

        Returns:
            None if no in-progress job found for the given {key}.
            Otherwise, the job related to the restore request. Contains the following keys:
                'request_id' (string): The request_id of the database entry.
                'archive_bucket_dest' (string): The name of the archive s3 bucket.

        Raises:
            requests_db.DatabaseError: Thrown if the request cannot be read from database.
    """
    try:
        jobs = requests_db.get_jobs_by_object_key(key)
    except requests_db.DatabaseError as err:
        logging.error(f"Failed to read request from database. "
                      f"key: {key} "
                      f"Err: {str(err)}")
        raise

    for job in jobs:
        if job["job_status"] != "complete":
            return job

    log_msg = ("Failed to update request status in database. "
               f"No incomplete entry found for object_key: {key}")
    logging.error(log_msg)
    return None


def update_status_in_db(a_file: Dict[str, Any], attempt: int, err_msg: str) -> None:
    """
    Updates the status for the job in the database.

        Args:
            a_file: An input dict with keys for:
                'request_id' (string): The request_id of the database entry to update.
                'source_key' (string): The filename of the restored file.
                'source_bucket' (string): The location of the restored file.
                'target_bucket' (string): the archive bucket the file was copied to.
            attempt: The attempt number for the copy (1 based).
            err_msg: None, or the error message from the copy command.

        Returns:
            None: {a_file} will be modified with additional keys for:
                'success' (boolean): True if the copy was successful,
                    otherwise False.
                'err_msg' (string): When 'success' is False, this will contain
                    the error message from the copy error

            Example:  [{'request_id': '', 'source_key': 'file1.xml',
                          'source_bucket': 'my-dr-fake-glacier-bucket',
                          'target_bucket': 'unittest_xml_bucket', 'success': True,
                          'err_msg': ''},
                      {'request_id': '', 'source_key': 'file2.txt',
                          'source_bucket': 'my-dr-fake-glacier-bucket',
                          'target_bucket': 'unittest_txt_bucket', 'success': True,
                          'err_msg': ''}]

        Raises:
            requests_db.DatabaseError: Thrown if the update operation fails.
    """
    old_status = ""  # todo: Unused
    new_status = ""
    try:
        if err_msg:
            a_file[FILE_ERROR_MESSAGE_KEY] = err_msg
            new_status = "error"
            logging.error(f"Attempt {attempt}. Error copying file {a_file[FILE_SOURCE_KEY_KEY]}"
                          f" from {a_file[FILE_SOURCE_BUCKET_KEY]} to {a_file[FILE_TARGET_BUCKET_KEY]}."
                          f" msg: {err_msg}")
            requests_db.update_request_status_for_job(a_file[FILE_REQUEST_ID_KEY], new_status, err_msg)
        else:
            a_file[FILE_SUCCESS_KEY] = True
            a_file[FILE_ERROR_MESSAGE_KEY] = ''
            new_status = "complete"
            logging.info(f"Attempt {attempt}. Success copying file "
                         f"{a_file[FILE_SOURCE_KEY_KEY]} from {a_file[FILE_SOURCE_BUCKET_KEY]} "
                         f"to {a_file[FILE_TARGET_BUCKET_KEY]}.")
            requests_db.update_request_status_for_job(a_file[FILE_REQUEST_ID_KEY], new_status)
    except requests_db.DatabaseError as err:
        logging.error(f"Failed to update request status in database. "
                      f"key: {a_file[FILE_SOURCE_KEY_KEY]} old status: {old_status} "
                      f"new status: {new_status}. Err: {str(err)}")
        raise
    return


def get_files_from_records(records: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    Parses the input records and returns the files to be restored.

        Args:
            records: passed through from the handler.

        Returns:
            files: A list of dicts with the following keys:
                'source_key': The object key of the file that was restored.
                'source_bucket': The name of the s3 bucket where the restored
                    file was temporarily sitting.

        Raises:
            KeyError: Thrown if the event record does not contain a value for the given bucket or object.
                Bucket will be checked/raised first, then object.
    """
    files = []
    for record in records:
        a_file = {FILE_SUCCESS_KEY: False}
        log_str = 'Records["s3"]["bucket"]["name"]'
        try:
            source_bucket = record["s3"]["bucket"]["name"]
            a_file[FILE_SOURCE_BUCKET_KEY] = source_bucket
            log_str = 'Records["s3"]["object"]["key"]'  # Use the same var to make except handling easier.
            source_key = record["s3"]["object"]["key"]
            a_file[FILE_SOURCE_KEY_KEY] = source_key
            files.append(a_file)
        except KeyError:
            raise CopyRequestError(f'event record: "{record}" does not contain a '
                                   f'value for {log_str}')
    return files


def copy_object(s3_cli: BaseClient, src_bucket_name: str, src_object_name: str,
                dest_bucket_name: str, dest_object_name: str = None) -> Optional[str]:
    """Copy an Amazon S3 bucket object

        Args:
            s3_cli: An instance of boto3 s3 client.
            src_bucket_name: The source S3 bucket name.
            src_object_name: The key of the s3 object being copied.
            dest_bucket_name: The target S3 bucket name.
            dest_object_name: Optional; The key of the destination object.
                If an object with the same name exists in the given bucket, the object is overwritten.
                Defaults to {src_object_name}.

        Returns:
            None if object was copied, otherwise contains error message.
    """

    if dest_object_name is None:
        dest_object_name = src_object_name
    # Construct source bucket/object parameter
    copy_source = {'Bucket': src_bucket_name, 'Key': src_object_name}

    # Copy the object
    try:
        response = s3_cli.copy_object(CopySource=copy_source,
                                      Bucket=dest_bucket_name,
                                      Key=dest_object_name)
        logging.debug(f"Copy response: {response}")
    except ClientError as ex:
        return str(ex)
    return None


def handler(event: Dict[str, Any], context: object) -> List[Dict[str, Any]]:  # pylint: disable-msg=unused-argument
    """Lambda handler. Copies a file from its temporary s3 bucket to the s3 archive.

    If the copy for a file in the request fails, the lambda
    throws an exception. Environment variables can be set to override how many
    times to retry a copy before failing, and how long to wait between retries.

        Environment Vars:
            COPY_RETRIES (number, optional, default = 3): The number of
                attempts to retry a copy that failed.
            COPY_RETRY_SLEEP_SECS (number, optional, default = 0): The number of seconds
                to sleep between retry attempts.
            DATABASE_PORT (string): the database port. The standard is 5432.
            DATABASE_NAME (string): the name of the database.
            DATABASE_USER (string): the name of the application user.

        Parameter Store:
                drdb-user-pass (string): the password for the application user (DATABASE_USER).
                drdb-host (string): the database host

        Args:
            event: A dict with the following keys:

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

            context: An object required by AWS Lambda. Unused.

        Returns:
            The list of dicts returned from the task. All 'success' values will be True. If they were
            not all True, the CopyRequestError exception would be raised.
            Dicts have the following keys:
                'source_key' (string): The object key of the file that was restored.
                'source_bucket' (string): The name of the s3 bucket where the restored
                    file was temporarily sitting.
                'target_bucket' (string): The name of the archive s3 bucket
                'success' (boolean): True, if the copy was successful,
                    otherwise False.
                'err_msg' (string): when success is False, this will contain
                    the error message from the copy error.
                'request_id' (string): The request_id of the database entry.
                    Only guaranteed to be present if 'success' == True.

            Example:  [{'source_key': 'file1.xml', 'source_bucket': 'my-dr-fake-glacier-bucket',
                          'target_bucket': 'unittest_xml_bucket', 'success': True,
                          'err_msg': ''},
                      {'source_key': 'file2.txt', 'source_bucket': 'my-dr-fake-glacier-bucket',
                          'target_bucket': 'unittest_txt_bucket', 'success': True,
                          'err_msg': ''}]
            # TODO: Do we not want to expose request_id? It's not even in the Example above.

        Raises:
            CopyRequestError: An error occurred calling copy_object for one or more files.
            The same dict that is returned for a successful copy will be included in the
            message, with 'success' = False for the files for which the copy failed.
    """

    logging.basicConfig(level=logging.INFO,
                        format='%(levelname)s: %(asctime)s: %(message)s')
    try:
        str_env_val = os.environ['COPY_RETRIES']
        retries = int(str_env_val)
    except KeyError:
        retries = 3

    try:
        str_env_val = os.environ['COPY_RETRY_SLEEP_SECS']
        retry_sleep_secs = float(str_env_val)
    except KeyError:
        retry_sleep_secs = 0

    logging.debug(f'event: {event}')
    records = event["Records"]
    result = task(records, retries, retry_sleep_secs)
    for a_file in result:
        # if any file failed, the function will fail
        if not a_file[FILE_SUCCESS_KEY]:
            logging.error(
                f'File copy failed. {result}')
            raise CopyRequestError(f'File copy failed. {result}')
    return result
