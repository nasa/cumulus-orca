"""
Name: request_files.py
Description:  Lambda function that makes a restore request from glacier for each input file.
"""

import os
import time
from typing import Dict, Any, Union, List

# noinspection PyPackageRequirements
import boto3
import requests_db
# noinspection PyPackageRequirements
from botocore.client import BaseClient
# noinspection PyPackageRequirements
from botocore.exceptions import ClientError
from cumulus_logger import CumulusLogger
from run_cumulus_task import run_cumulus_task

OS_ENVIRON_RESTORE_EXPIRE_DAYS_KEY = 'RESTORE_EXPIRE_DAYS'
OS_ENVIRON_RESTORE_REQUEST_RETRIES_KEY = 'RESTORE_REQUEST_RETRIES'
OS_ENVIRON_RESTORE_RETRY_SLEEP_SECS_KEY = 'RESTORE_RETRY_SLEEP_SECS'
OS_ENVIRON_RESTORE_RETRIEVAL_TYPE_KEY = 'RESTORE_RETRIEVAL_TYPE'

# noinspection SpellCheckingInspection
REQUESTS_DB_DEST_BUCKET_KEY = 'dest_bucket'
REQUESTS_DB_GLACIER_BUCKET_KEY = 'glacier_bucket'
REQUESTS_DB_REQUEST_GROUP_ID_KEY = 'request_group_id'
REQUESTS_DB_GRANULE_ID_KEY = 'granule_id'
REQUESTS_DB_REQUEST_ID_KEY = 'request_id'

REQUESTS_DB_ERROR_MESSAGE_KEY = 'err_msg'
REQUESTS_DB_JOB_STATUS_KEY = 'job_status'

EVENT_CONFIG_KEY = 'config'
EVENT_INPUT_KEY = 'input'

INPUT_GRANULES_KEY = 'granules'

CONFIG_GLACIER_BUCKET_KEY = 'glacier-bucket'

GRANULE_GRANULE_ID_KEY = 'granuleId'
GRANULE_KEYS_KEY = 'keys'
GRANULE_RECOVER_FILES_KEY = 'recover_files'

# noinspection SpellCheckingInspection
FILE_DEST_BUCKET_KEY = 'dest_bucket'
FILE_KEY_KEY = 'key'
FILE_SUCCESS_KEY = 'success'
FILE_ERROR_MESSAGE_KEY = 'err_msg'

LOGGER = CumulusLogger()


class RestoreRequestError(Exception):
    """
    Exception to be raised if the restore request fails submission for any of the files.
    """


def task(event: Dict, context: object) -> Dict[str, Any]:  # pylint: disable-msg=unused-argument
    """
    Task called by the handler to perform the work.
    This task will call the restore_request for each file. Restored files will be kept
    for {exp_days} days before they expire. A restore request will be tried up to {retries} times
    if it fails, waiting {retry_sleep_secs} between each attempt.
        Args:
            event: Passed through from the handler.
            context: Passed through from the handler. Unused, but required by framework.
        Environment Vars:
            RESTORE_EXPIRE_DAYS (int, optional, default = 5): The number of days
                the restored file will be accessible in the S3 bucket before it expires.
            RESTORE_REQUEST_RETRIES (int, optional, default = 3): The number of
                attempts to retry a restore_request that failed to submit.
            RESTORE_RETRY_SLEEP_SECS (int, optional, default = 0): The number of seconds
                to sleep between retry attempts.
            RESTORE_RETRIEVAL_TYPE (str, optional, default = 'Standard'): the Tier
                for the restore request. Valid values are 'Standard'|'Bulk'|'Expedited'.
            DATABASE_PORT (str): the database port. The default is 5432
                Hidden requirement for requests_db.get_dbconnect_info.
            DATABASE_NAME (str): the name of the database.
                Hidden requirement for requests_db.get_dbconnect_info.
            DATABASE_USER (str): the name of the application user.
                Hidden requirement for requests_db.get_dbconnect_info.
        Parameter Store:
            drdb-user-pass (str): the password for the application user (DATABASE_USER).
                Hidden requirement for requests_db.get_dbconnect_info.
            drdb-host (str): the database host.
                Hidden requirement for requests_db.get_dbconnect_info.
        Returns:
            A dict with the following keys:
                'granules' (List): A list of dicts, each with the following keys:
                    'granuleId' (string): The id of the granule being restored.
                    'recover_files' (list(dict)): A list of dicts with the following keys:
                        'key' (str): Name of the file within the granule.
                        'dest_bucket' (str): The bucket the restored file will be moved
                            to after the restore completes.
                        'success' (boolean): True, indicating the restore request was submitted successfully,
                            otherwise False.
                        'err_msg' (string): when success is False, this will contain
                            the error message from the restore error.
                    'keys': Same as recover_files, but without 'success' and 'err_msg'.
            Example:
                {'granules': [
                    {
                        'granuleId': 'granxyz',
                        'recover_files': [
                            {'key': 'path1', 'dest_bucket': 'bucket_name', 'success': True},
                            {'key': 'path2', 'success': False, 'err_msg': 'because'}
                        ]
                    }]}
        Raises:
            RestoreRequestError: Thrown if there are errors with the input request.
    """
    try:
        max_retries = int(os.environ[OS_ENVIRON_RESTORE_REQUEST_RETRIES_KEY])
    except KeyError:
        max_retries = 2

    try:
        retry_sleep_secs = float(os.environ[OS_ENVIRON_RESTORE_RETRY_SLEEP_SECS_KEY])
    except KeyError:
        retry_sleep_secs = 0

    try:
        retrieval_type = os.environ[OS_ENVIRON_RESTORE_RETRIEVAL_TYPE_KEY]
        if retrieval_type not in ('Standard', 'Bulk', 'Expedited'):
            msg = (f"Invalid RESTORE_RETRIEVAL_TYPE: '{retrieval_type}'"
                   " defaulting to 'Standard'")
            LOGGER.info(msg)
            retrieval_type = 'Standard'
    except KeyError:
        retrieval_type = 'Standard'

    try:
        exp_days = int(os.environ[OS_ENVIRON_RESTORE_EXPIRE_DAYS_KEY])
    except KeyError:
        exp_days = 5

    return inner_task(event, max_retries, retry_sleep_secs, retrieval_type, exp_days)


def inner_task(event: Dict, max_retries: int, retry_sleep_secs: float, retrieval_type: str, restore_expire_days: int):
    try:
        glacier_bucket = event[EVENT_CONFIG_KEY][CONFIG_GLACIER_BUCKET_KEY]
    except KeyError:
        raise RestoreRequestError(
            f'request: {event} does not contain a config value for glacier-bucket')

    granules = event[EVENT_INPUT_KEY][INPUT_GRANULES_KEY]
    if len(granules) > 1:
        # todo: This is either a lie, or the loop below should be removed.
        raise RestoreRequestError(f'request_files can only accept 1 granule in the list. '
                                  f'This input contains {len(granules)}')
    s3 = boto3.client('s3')  # pylint: disable-msg=invalid-name

    copied_granule = {}
    for granule in granules:
        files = []
        for keys in granule[GRANULE_KEYS_KEY]:
            file_key = keys[FILE_KEY_KEY]
            destination_bucket_name = keys[FILE_DEST_BUCKET_KEY]
            if object_exists(s3, glacier_bucket, file_key):
                LOGGER.info(f"Added {file_key} to the list of files we'll attempt to recover.")
                a_file = {
                    FILE_KEY_KEY: file_key,
                    FILE_DEST_BUCKET_KEY: destination_bucket_name,
                    FILE_SUCCESS_KEY: False,
                    FILE_ERROR_MESSAGE_KEY: ''
                }
                files.append(a_file)
        copied_granule = granule.copy()
        copied_granule[GRANULE_RECOVER_FILES_KEY] = files

    # todo: Looks like this line is why multiple granules are not supported.
    # todo: Using the default value {} for copied_granule will cause this function to raise errors every time.
    process_granule(
        s3, copied_granule, glacier_bucket, restore_expire_days, max_retries, retry_sleep_secs, retrieval_type)

    # Cumulus expects response (payload.granules) to be a list of granule objects.
    return {INPUT_GRANULES_KEY: [copied_granule]}


def process_granule(s3: BaseClient, granule: Dict[str, Union[str, List[Dict]]], glacier_bucket: str,
                    restore_expire_days: int,
                    max_retries: int, retry_sleep_secs: float, retrieval_type: str):  # pylint: disable-msg=invalid-name
    f"""Call restore_object for the files in the granule_list. Modifies {granule} for output.
        Args:
            s3: An instance of boto3 s3 client
            granule: A dict with the following keys:
                'granuleId' (str): The id of the granule being restored.
                'recover_files' (list(dict)): A list of dicts with the following keys:
                    'key' (str): Name of the file within the granule.
                    'dest_bucket' (str): The bucket the restored file will be moved
                        to after the restore completes
                    'success' (bool): Should enter this method set to False. Modified to 'True' if no error occurs.
                    'err_msg' (str): Will be modified if error occurs.


            glacier_bucket: The S3 glacier bucket name
            restore_expire_days:
                The number of days the restored file will be accessible in the S3 bucket before it expires.
            max_retries: todo
            retry_sleep_secs: todo
            retrieval_type: todo
    """
    attempt = 1
    request_group_id = requests_db.request_id_generator()
    granule_id = granule[GRANULE_GRANULE_ID_KEY]
    while attempt <= max_retries + 1:
        for a_file in granule[GRANULE_RECOVER_FILES_KEY]:
            if not a_file[FILE_SUCCESS_KEY]:
                obj = {
                    REQUESTS_DB_REQUEST_GROUP_ID_KEY: request_group_id,
                    REQUESTS_DB_GRANULE_ID_KEY: granule_id,
                    REQUESTS_DB_GLACIER_BUCKET_KEY: glacier_bucket,
                    'key': a_file[FILE_KEY_KEY],  # This property isn't from anything besides this code.
                    REQUESTS_DB_DEST_BUCKET_KEY: a_file[FILE_DEST_BUCKET_KEY],
                    'days': restore_expire_days  # This property isn't from anything besides this code.
                }
                try:
                    restore_object(s3, obj, attempt, max_retries, retrieval_type)
                    a_file[FILE_SUCCESS_KEY] = True
                    a_file[FILE_ERROR_MESSAGE_KEY] = ''
                except ClientError as err:
                    a_file[FILE_ERROR_MESSAGE_KEY] = str(err)

        attempt = attempt + 1
        if attempt <= max_retries + 1:
            # Check for early completion.
            if all(a_file[FILE_SUCCESS_KEY] for a_file in granule[GRANULE_RECOVER_FILES_KEY]):
                break
            time.sleep(retry_sleep_secs)

    for a_file in granule[GRANULE_RECOVER_FILES_KEY]:
        # if any file failed, the whole granule will fail
        if not a_file[FILE_SUCCESS_KEY]:
            LOGGER.error(f"One or more files failed to be requested from {glacier_bucket}. {granule}")
            raise RestoreRequestError(f'One or more files failed to be requested. {granule}')


def object_exists(s3_cli: BaseClient, glacier_bucket: str, file_key: str) -> bool:
    """Check to see if an object exists in S3 Glacier.
        Args:
            s3_cli: An instance of boto3 s3 client
            glacier_bucket: The S3 glacier bucket name
            file_key: The key of the Glacier object
        Returns:
            True if the object exists, otherwise False.
        """
    try:
        # head_object will fail with a thrown 404 if the object doesn't exist
        # todo: The above case was not covered, and should be considered untested.
        s3_cli.head_object(Bucket=glacier_bucket, Key=file_key)
        return True
    except ClientError as err:
        LOGGER.error(err)
        code = err.response['Error']['Code']
        if code == 'NoSuchKey' or code == 'NotFound':  # Unit tests say 'NotFound', some online docs say 'NoSuchKey'
            return False
        raise
        # todo: Online docs suggest we could catch 'S3.Client.exceptions.NoSuchKey instead of deconstructing ClientError


def restore_object(s3_cli: BaseClient, obj: Dict[str, Any], attempt: int, max_retries: int,
                   retrieval_type: str = 'Standard'
                   ) -> None:
    f"""Restore an archived S3 Glacier object in an Amazon S3 bucket.
        Args:
            s3_cli: An instance of boto3 s3 client.
            obj: A dictionary containing:
                request_group_id (string): A uuid identifying all objects in.
                    a granule restore request.
                granule_id (string): The granule_id to which the object_name being restored belongs.
                glacier_bucket (string): The S3 bucket name.
                key (string): The key of the Glacier object being restored.
                dest_bucket (string): The bucket the restored file will be moved.
                    to after the restore completes.
                days (int): How many days the restored file will be accessible in the S3 bucket
                    before it expires.
            attempt: The attempt number for retry purposes.
            max_retries: The number of retries that will be attempted.
            retrieval_type: Glacier Tier. Valid values are 'Standard'|'Bulk'|'Expedited'. Defaults to 'Standard'.
        Raises:
            ClientError: Raises ClientErrors from restore_object.
    """
    data = requests_db.create_data(obj, 'restore', 'inprogress', None, None)
    request_id = data[REQUESTS_DB_REQUEST_ID_KEY]
    request = {'Days': obj['days'],
               'GlacierJobParameters': {'Tier': retrieval_type}}
    # Submit the request
    try:
        s3_cli.restore_object(Bucket=obj[REQUESTS_DB_GLACIER_BUCKET_KEY],
                              Key=obj['key'],
                              RestoreRequest=request)
    except ClientError as c_err:
        # NoSuchBucket, NoSuchKey, or InvalidObjectState error == the object's
        # storage class was not GLACIER
        LOGGER.error(f"{c_err}. bucket: {obj[REQUESTS_DB_GLACIER_BUCKET_KEY]} file: {obj['key']}")
        if attempt == max_retries + 1:
            #  If on last attempt, post the error message to DB.
            try:
                data[REQUESTS_DB_ERROR_MESSAGE_KEY] = str(c_err)
                data[REQUESTS_DB_JOB_STATUS_KEY] = 'error'
                requests_db.submit_request(data)
                LOGGER.info(f"Job {request_id} created.")
            except requests_db.DatabaseError as err:
                LOGGER.error(f"Failed to log error message in database. Error {str(err)}. Request: {data}")
        raise c_err

    try:
        requests_db.submit_request(data)
        LOGGER.info(
            f"Restore {obj['key']} from {obj[REQUESTS_DB_GLACIER_BUCKET_KEY]} "
            f"attempt {attempt} successful. Job: {request_id}")
    except requests_db.DatabaseError as err:
        LOGGER.error(f"Failed to log request in database. Error {str(err)}. Request: {data}")


def handler(event: Dict[str, Any], context):  # pylint: disable-msg=unused-argument
    """Lambda handler. Initiates a restore_object request from glacier for each file of a granule.
    Note that this function is set up to accept a list of granules, (because Cumulus sends a list),
    but at this time, only 1 granule will be accepted.
    This is due to the error handling. If the restore request for any file for a
    granule fails to submit, the entire granule (workflow) fails. If more than one granule were
    accepted, and a failure occured, at present, it would fail all of them.
    Environment variables can be set to override how many days to keep the restored files, how
    many times to retry a restore_request, and how long to wait between retries.
        Environment Vars:
            RESTORE_EXPIRE_DAYS (int, optional, default = 5): The number of days
                the restored file will be accessible in the S3 bucket before it expires.
            RESTORE_REQUEST_RETRIES (int, optional, default = 3): The number of
                attempts to retry a restore_request that failed to submit.
            RESTORE_RETRY_SLEEP_SECS (int, optional, default = 0): The number of seconds
                to sleep between retry attempts.
            RESTORE_RETRIEVAL_TYPE (str, optional, default = 'Standard'): the Tier
                for the restore request. Valid values are 'Standard'|'Bulk'|'Expedited'.
            DATABASE_PORT (str): the database port. The default is 5432
                Hidden requirement for requests_db.get_dbconnect_info.
            DATABASE_NAME (str): the name of the database.
                Hidden requirement for requests_db.get_dbconnect_info.
            DATABASE_USER (str): the name of the application user.
                Hidden requirement for requests_db.get_dbconnect_info.
        Parameter Store:
            drdb-user-pass (str): the password for the application user (DATABASE_USER).
                Hidden requirement for requests_db.get_dbconnect_info.
            drdb-host (str): the database host.
                Hidden requirement for requests_db.get_dbconnect_info.
        Args:
            event (dict): A dict with the following keys:
                'config' (dict): A dict with the following keys:
                    'glacier_bucket' (str): The name of the glacier bucket from which the files
                    will be restored.
                'input' (dict): A dict with the following keys:
                    'granules' (list(dict)): A list of dicts with the following keys:
                        'granuleId' (str): The id of the granule being restored.
                        'keys' (list(dict)): A list of dicts with the following keys:  # TODO: rename.
                            'key' (str): Name of the file within the granule.
                            'dest_bucket' (str): The bucket the restored file will be moved
                                to after the restore completes.
                Example: {
                    'config': {'glacierBucket': 'some_bucket'}
                    'input': {
                        'granules':
                        [
                            {
                                'granuleId': 'granxyz',
                                'keys': [
                                    {'key': 'path1', 'dest_bucket': 'some_bucket'},
                                    {'key': 'path2', 'dest_bucket': 'some_other_bucket'}
                                ]
                            }
                        ]
                    }
            context: An object required by AWS Lambda. Unused.
        Returns:
            dict: The dict returned from the task. All 'success' values will be True. If they were
            not all True, the RestoreRequestError exception would be raised.
        Raises:
            RestoreRequestError: An error occurred calling restore_object for one or more files.
            The same dict that is returned for a successful granule restore, will be included in the
            message, with 'success' = False for the files for which the restore request failed to
            submit.
    """
    LOGGER.setMetadata(event, context)
    return run_cumulus_task(task, event, context)
