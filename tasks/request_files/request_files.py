"""
Name: request_files.py

Description:  Lambda function that makes a restore request from glacier for each input file.
"""

import json
import os
import logging
import boto3
from botocore.exceptions import ClientError

class RestoreRequestError(Exception):
    """
    Exception to be raised if the restore request fails submission for any of the files.
    """

def task(event, context):               #pylint: disable-msg=unused-argument
    """
    Task called by the handler to perform the work.

    This task will call the restore_request for each file. Restored files will be kept for 5 days
    before they expire. A restore request will be tried up to 3 times if it fails.  Environment
    variables can be set to override how many days to keep the restored files, and how many times
    to retry a restore_request.

        Environment Vars:
            restore_expire_days (number, optional, default = 5): The number of days
            the restored file will be accessible in the S3 bucket before it expires
            restore_request_retries (number, optional, default = 3): The number of
            attempts to retry a restore_request that failed to submit

        Args:
            event (dict): passed through from the handler
            context (Object): passed through from the handler

        Returns:
            dict: A dict with the following keys:

                'granuleId' (string): The id of the granule being restored.
                'files' (list(dict)): A list of dicts with the following keys:
                    'filepath': The glacier key (filepath) of the file to restore
                    'success' (boolean): True, indicating the restore request was submitted
                        successfully, otherwise False.

                Example:  {'granuleId': 'granxyz',
                      'files': [{'filepath': 'path1', 'success': True},
                                {'filepath': 'path2', 'success': False}]}

        Raises:
            RestoreRequestError: Thrown if there are errors with the input request.
    """
    try:
        glacier_bucket = event["glacierBucket"]
    except KeyError:
        raise RestoreRequestError(f'request: {event} does not contain a value for glacierBucket')
    try:
        exp_days = int(os.environ['restore_expire_days'])
    except KeyError:
        exp_days = 5

    try:
        retries = int(os.environ['restore_request_retries'])
    except KeyError:
        retries = 3


    gran = {}
    granules = event['granules']
    if len(granules) > 1:
        raise RestoreRequestError(f'request_files can only accept 1 granule in the list. '
                                  f'This input contains {len(granules)}')
    for granule in granules:
        gran['granuleId'] = granule['granuleId']
        files = []
        for file_key in granule['filepaths']:
            afile = {}
            afile['filepath'] = file_key
            afile['success'] = False
            files.append(afile)
        gran['files'] = files

    attempt = 1
    retry = True
    while retry:
        for afile in gran['files']:
            if not afile['success']:
                success = restore_object(glacier_bucket, afile['filepath'], exp_days)
                afile['success'] = success
                logging.info(f'Attempt {attempt} success status of submit request to restore '
                             f'{afile["filepath"]} from {glacier_bucket} = {success}')
        attempt = attempt + 1
        if attempt > retries:
            retry = False

    return gran

def restore_object(bucket_name, object_name, days, retrieval_type='Standard'):
    """Restore an archived S3 Glacier object in an Amazon S3 bucket.

        Args:
            bucket_name (string): The S3 bucket name
            object_name (string): The key of the Glacier object being restored
            days (number): The number of days the restored file will be accessible in the S3 bucket
                before it expires
            retrieval_type (string, optional, default=Standard): Glacier Tier.
                Valid values are 'Standard'|'Bulk'|'Expedited'.

        Returns:
            boolean: True if a request to restore archived object was submitted, otherwise False.
    """
    request = {'Days': days,
               'GlacierJobParameters': {'Tier': retrieval_type}}

    # Submit the request
    s3 = boto3.client('s3')                  #pylint: disable-msg=invalid-name
    try:
        s3.restore_object(Bucket=bucket_name, Key=object_name, RestoreRequest=request)
    except ClientError as err:
        # NoSuchBucket, NoSuchKey, or InvalidObjectState error == the object's
        # storage class was not GLACIER
        logging.error(err)
        return False
    return True

def handler(event, context):
    """Lambda handler. Initiates a restore_object request from glacier for each file of a granule.

    Note that this function is set up to accept a list of granules, (because Cumulus sends a list),
    but at this time, only 1 granule will be accepted.
    This is due to the error handling. If the restore request for any file for a
    granule fails to submit, the entire granule (workflow) fails. If more than one granule were
    accepted, and a failure occured, at present, it would fail all of them.

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
        The dict that is returned for a successful granule restore, will be included in the message,
        with 'success' = False for the files for which the restore request failed to submit.
    """

    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s: %(asctime)s: %(message)s')
    result = task(event, context)
    for afile in result['files']:
        #if any file failed, the whole granule will fail
        if not afile['success']:
            logging.error(
                f'One or more files failed to be requested from {event["glacierBucket"]}. {result}')
            raise RestoreRequestError(f'One or more files failed to be requested. {result}')
    return json.dumps(result)
