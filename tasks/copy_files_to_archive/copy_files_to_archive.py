"""
Name: copy_files_to_archive.py

Description:  Lambda function that copies files from one s3 bucket
to another s3 bucket.
"""
import json
import os
import time
import logging
from enum import Enum
from typing import Any, List, Dict, Optional

import boto3
import database
from botocore.client import BaseClient
from botocore.exceptions import ClientError
import requests_db
from cumulus_logger import CumulusLogger


class RequestMethod(Enum):
    POST = 'post'
    PUT = 'put'


OS_ENVIRON_DB_QUEUE_URL_KEY = 'DB_QUEUE_URL'

# These will determine what the output looks like.
FILE_SUCCESS_KEY = 'success'
FILE_SOURCE_KEY_KEY = 'source_key'
FILE_ERROR_MESSAGE_KEY = 'err_msg'
FILE_SOURCE_BUCKET_KEY = 'source_bucket'
FILE_TARGET_BUCKET_KEY = 'target_bucket'

# These are tied to the database schema.
JOB_REQUEST_ID_KEY = 'request_id'
JOB_ARCHIVE_BUCKET_DEST_KEY = 'archive_bucket_dest'
JOB_JOB_STATUS_KEY = 'job_status'

ORCA_STATUS_PENDING = 0
ORCA_STATUS_STAGED = 1
ORCA_STATUS_SUCCESS = 2
ORCA_STATUS_FAILED = 3

LOGGER = CumulusLogger()


class CopyRequestError(Exception):
    """
    Exception to be raised if the copy request fails for any of the files.
    """


# todo: Add params to docs and usage. Might need to be moved into records.
def task(records: List[Dict[str, Any]], max_retries: int, retry_sleep_secs: float, job_id: str, granule_id: str) \
        -> List[Dict[str, Any]]:
    """
    Task called by the handler to perform the work.

    This task will call copy_object for each file. A copy will be tried
    up to {retries} times if it fails, waiting {retry_sleep_secs}
    between each attempt.

    Args:
        records: Passed through from the handler.
        max_retries: The number of attempts to retry a failed copy.
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
                      'err_msg': '', 'request_id': '4192bff0-e1e0-43ce-a4db-912808c32493'}]
    Raises:
        CopyRequestError: Thrown if there are errors with the input records or the copy failed.
    """
    db_queue_url = str(os.environ[OS_ENVIRON_DB_QUEUE_URL_KEY])
    files = get_files_from_records(records)
    attempt = 1
    s3 = boto3.client('s3')  # pylint: disable-msg=invalid-name
    while attempt <= max_retries + 1:
        for a_file in files:
            # All files from get_files_from_records start with 'success' == False.
            if not a_file[FILE_SUCCESS_KEY]:
                key = a_file[FILE_SOURCE_KEY_KEY]

                try:
                    # todo: Pass the target bucket in through params. Previously was set at this point from status DB guesswork.
                    err_msg = copy_object(s3, a_file[FILE_SOURCE_BUCKET_KEY], a_file[FILE_SOURCE_KEY_KEY],
                                          a_file[FILE_TARGET_BUCKET_KEY])
                    a_file[FILE_ERROR_MESSAGE_KEY] = err_msg
                except requests_db.DatabaseError:
                    continue  # Move on to the next file. We'll come back to retry on next attempt

        attempt = attempt + 1
        if attempt <= max_retries + 1:
            if all(a_file[FILE_SUCCESS_KEY] for a_file in files):  # Check for early completion
                break
            time.sleep(retry_sleep_secs)

    any_error = False
    for a_file in files:
        if not a_file[FILE_SUCCESS_KEY]:
            any_error = True
            post_status_for_file_to_queue(
                job_id, granule_id, a_file[FILE_SOURCE_KEY_KEY], None,
                None,
                ORCA_STATUS_FAILED, a_file.get(FILE_ERROR_MESSAGE_KEY, None),
                None, database.get_utc_now_iso(), None, RequestMethod.PUT, db_queue_url,
                max_retries, retry_sleep_secs)

    if any_error:
        logging.error(
            f'File copy failed. {files}')
        raise CopyRequestError(f'File copy failed. {files}')

    return files


# todo: Move to shared lib
def post_status_for_file_to_queue(job_id: str, granule_id: str, filename: str, key_path: Optional[str],
                                  restore_destination: Optional[str],
                                  status_id: Optional[int], error_message: Optional[str],
                                  request_time: Optional[str], last_update: str,
                                  completion_time: Optional[str],
                                  request_method: RequestMethod,
                                  db_queue_url: str,
                                  max_retries: int, retry_sleep_secs: float):
    new_data = {'job_id': job_id,
                'granule_id': granule_id,
                'filename': filename}
    if key_path is not None:
        new_data['key_path'] = status_id
    if restore_destination is not None:
        new_data['restore_destination'] = status_id
    if status_id is not None:
        new_data['status_id'] = status_id
    if error_message is not None:
        new_data['error_message'] = status_id
    if request_time is not None:
        new_data['request_time'] = status_id
    if last_update is not None:
        new_data['last_update'] = status_id
    if completion_time is not None:
        new_data['completion_time'] = status_id

    post_entry_to_queue('orca_recoverfile',
                        new_data,
                        request_method,
                        db_queue_url, max_retries, retry_sleep_secs)


sqs = boto3.client('sqs')


def post_entry_to_queue(table_name: str, new_data: Dict[str, Any], request_method: RequestMethod, db_queue_url: str,
                        max_retries: int, retry_sleep_secs: float):
    attempt = 0
    while attempt <= max_retries + 1:
        try:
            sqs.send_message(
                QueueUrl=db_queue_url
            )
            sqs.send_message(
                QueueUrl=db_queue_url,
                DelaySeconds=0,
                MessageAttributes={
                    'RequestMethod': {
                        'DataType': 'String',
                        'StringValue': request_method.value
                    },
                    'TableName': {
                        'DataType': 'String',
                        'StringValue': table_name
                    }
                },
                MessageBody=(
                    json.dumps(new_data, indent=4)
                )
            )
        except Exception as e:
            if attempt == max_retries + 1:
                LOGGER.error(f"Error while logging row {json.dumps(new_data, indent=4)} "
                             f"to table {table_name}: {e}")
                raise e
            time.sleep(retry_sleep_secs)
            continue


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
        logging.error(ex)
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
        # todo: Rework this to pull from queue and not use guesswork.
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
                      'err_msg': '', 'request_id': '4192bff0-e1e0-43ce-a4db-912808c32493'}]

    Raises:
        CopyRequestError: An error occurred calling copy_object for one or more files.
        The same dict that is returned for a successful copy will be included in the
        message, with 'success' = False for the files for which the copy failed.
    """
    LOGGER.setMetadata(event, context)

    logging.basicConfig(level=logging.INFO,
                        format='%(levelname)s: %(asctime)s: %(message)s')
    try:
        str_env_val = os.environ['COPY_RETRIES']
        retries = int(str_env_val)
    except KeyError:
        retries = 2

    try:
        str_env_val = os.environ['COPY_RETRY_SLEEP_SECS']
        retry_sleep_secs = float(str_env_val)
    except KeyError:
        retry_sleep_secs = 30

    logging.debug(f'event: {event}')
    records = event["Records"]
    return task(records, retries, retry_sleep_secs)
