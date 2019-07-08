"""
Name: request_files.py

Description:  Lambda function that makes a restore request from glacier for each input file.
"""

import os
import time
import boto3
from botocore.exceptions import ClientError

from run_cumulus_task import run_cumulus_task
from cumulus_logger import CumulusLogger

LOGGER = CumulusLogger()

class RestoreRequestError(Exception):
    """
    Exception to be raised if the restore request fails submission for any of the files.
    """

def task(event, context):              #pylint: disable-msg=unused-argument
    """
    Task called by the handler to perform the work.

    This task will call the restore_request for each file. Restored files will be kept
    for {exp_days} days before they expire. A restore request will be tried up to {retries} times
    if it fails, waiting {retry_sleep_secs} between each attempt.

        Args:
            event (dict): passed through from the handler
            exp_days (number): The number of days the restored file will be accessible
                in the S3 bucket before it expires
            retries (number): The number of attempts to retry a restore_request that
                failed to submit.
            retry_sleep_secs (number): The number of seconds to sleep between retry attempts.

        Returns:
            dict: A dict with the following keys:

                'granuleId' (string): The id of the granule being restored.
                'files' (list(dict)): A list of dicts with the following keys:
                    'filepath': The glacier key (filepath) of the file to restore
                    'success' (boolean): True, indicating the restore request was submitted
                        successfully, otherwise False.
                    'err_msg' (string): when success is False, this will contain
                        the error message from the restore error

                Example:  {'granuleId': 'granxyz',
                      'files': [{'filepath': 'path1', 'success': True},
                                {'filepath': 'path2', 'success': False, 'err_msg': 'because'}]}

        Raises:
            RestoreRequestError: Thrown if there are errors with the input request.
    """
    try:
        exp_days = int(os.environ['RESTORE_EXPIRE_DAYS'])
    except KeyError:
        exp_days = 5

    try:
        glacier_bucket = event['config']['glacier-bucket']
    except KeyError:
        raise RestoreRequestError(
            f'request: {event} does not contain a config value for glacier-bucket')

    gran = {}
    granules = event['input']['granules']
    if len(granules) > 1:
        raise RestoreRequestError(f'request_files can only accept 1 granule in the list. '
                                  f'This input contains {len(granules)}')
    s3 = boto3.client('s3')  # pylint: disable-msg=invalid-name

    for granule in granules:
        gran['granuleId'] = granule['granuleId']
        files = []
        for file_key in granule['filepaths']:
            if object_exists(s3, glacier_bucket, file_key):
                LOGGER.info("Added {} to the list of files we'll attempt to recover.", file_key)
                afile = {}
                afile['filepath'] = file_key
                afile['success'] = False
                afile['err_msg'] = ''
                files.append(afile)
        gran['files'] = files

    process_granules(s3, gran, glacier_bucket, exp_days)

    return gran

def process_granules(s3, gran, glacier_bucket, exp_days):        # pylint: disable-msg=invalid-name
    """Call restore_object for the files in the granule_list

        Args:
            gran (list):
            s3 (object): An instance of boto3 s3 client
            glacier_bucket (string): The S3 glacier bucket name
            file_key (string): The key of the Glacier object

        Returns:
            gran: updated granules list, indicating if the restore request for each file
                  was successful, including an error message for any that were not.
    """
    try:
        retries = int(os.environ['RESTORE_REQUEST_RETRIES'])
    except KeyError:
        retries = 3

    try:
        retry_sleep_secs = float(os.environ['RESTORE_RETRY_SLEEP_SECS'])
    except KeyError:
        retry_sleep_secs = 0

    attempt = 1
    while attempt <= retries:
        for afile in gran['files']:
            if not afile['success']:
                try:
                    restore_object(s3, glacier_bucket, afile['filepath'], exp_days)
                    afile['success'] = True
                    afile['err_msg'] = ''
                    LOGGER.info("restore {} from {} attempt {} successful.",
                                afile["filepath"], glacier_bucket, attempt)
                except ClientError as err:
                    afile['err_msg'] = str(err)

        attempt = attempt + 1
        if attempt <= retries:
            time.sleep(retry_sleep_secs)

    for afile in gran['files']:
        # if any file failed, the whole granule will fail
        if not afile['success']:
            LOGGER.error("One or more files failed to be requested from {}. {}",
                         glacier_bucket, gran)
            raise RestoreRequestError(f'One or more files failed to be requested. {gran}')
    return gran

def object_exists(s3_cli, glacier_bucket, file_key):
    """Check to see if an object exists in S3 Glacier.

        Args:
            s3_cli (object): An instance of boto3 s3 client
            glacier_bucket (string): The S3 glacier bucket name
            file_key (string): The key of the Glacier object

        Returns:
            boolean: True if the object exists, otherwise False.
        """
    try:
        # head_object will fail with a thrown 404 if the object doesn't exist
        s3_cli.head_object(Bucket=glacier_bucket, Key=file_key)
        return True
    except ClientError as err:              #pylint: disable-msg=unused-variable
        return False

def restore_object(s3_cli, bucket_name, object_name, days, retrieval_type='Standard'):
    """Restore an archived S3 Glacier object in an Amazon S3 bucket.

        Args:
            s3_cli (object): An instance of boto3 s3 client
            bucket_name (string): The S3 bucket name
            object_name (string): The key of the Glacier object being restored
            days (number): The number of days the restored file will be accessible in the S3 bucket
                before it expires
            retrieval_type (string, optional, default=Standard): Glacier Tier.
                Valid values are 'Standard'|'Bulk'|'Expedited'.

        Returns:
            string: None if restore request was submitted, otherwise contains error message.
    """
    request = {'Days': days,
               'GlacierJobParameters': {'Tier': retrieval_type}}

    # Submit the request
    try:
        s3_cli.restore_object(Bucket=bucket_name, Key=object_name, RestoreRequest=request)
    except ClientError as err:
        # NoSuchBucket, NoSuchKey, or InvalidObjectState error == the object's
        # storage class was not GLACIER
        LOGGER.error("{}. bucket: {} file: {}", err, bucket_name, object_name)
        raise err

def handler(event, context):      #pylint: disable-msg=unused-argument
    """Lambda handler. Initiates a restore_object request from glacier for each file of a granule.

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
    """
    LOGGER.setMetadata(event, context)
    return run_cumulus_task(task, event, context)
