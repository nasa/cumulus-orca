"""
Name: copy_files_to_archive.py

Description:  Lambda function that copies files from one s3 bucket
to another s3 bucket.
"""

import json
import os
import time
import logging
import boto3
from botocore.exceptions import ClientError
from utils import requests_db

class CopyRequestError(Exception):
    """
    Exception to be raised if the copy request fails for any of the files.
    """

def task(records, bucket_map, retries, retry_sleep_secs):
    """
    Task called by the handler to perform the work.

    This task will call copy_object for each file. A copy will be tried
    up to {retries} times if it fails, waiting {retry_sleep_secs}
    between each attempt.

        Args:
            records (dict): passed through from the handler
            bucket_map (dict): Mapping of file extensions to bucket names
            retries (number): The number of attempts to retry a failed copy.
            retry_sleep_secs (number): The number of seconds
                to sleep between retry attempts.

        Returns:
            files: A list of dicts with the following keys:
                'source_key': The object key of the file that was restored
                'source_bucket': The name of the s3 bucket where the restored
                    file was temporarily sitting
                'target_bucket': The name of the archive s3 bucket
                'success' (boolean): True, if the copy was successful,
                    otherwise False.
                'err_msg' (string): when success is False, this will contain
                    the error message from the copy error

            Example:  [{'source_key': 'file1.xml', 'source_bucket': 'my-dr-fake-glacier-bucket',
                          'target_bucket': 'unittest_xml_bucket', 'success': True,
                          'err_msg': ''},
                      {'source_key': 'file2.txt', 'source_bucket': 'my-dr-fake-glacier-bucket',
                          'target_bucket': 'unittest_txt_bucket', 'success': True,
                          'err_msg': ''}]

        Raises:
            CopyRequestError: Thrown if there are errors with the input records or the copy failed.
    """
    files = get_files_from_records(records, bucket_map)
    attempt = 1
    s3 = boto3.client('s3')  # pylint: disable-msg=invalid-name
    while attempt <= retries:
        for afile in files:
            if not afile['success']:
                err_msg = copy_object(s3, afile['source_bucket'], afile['source_key'],
                                      afile['target_bucket'])
                try:
                    update_status_in_db(afile, attempt, err_msg)
                except requests_db.DatabaseError:
                    try:
                        time.sleep(30)
                        update_status_in_db(afile, attempt, err_msg)
                    except requests_db.DatabaseError:
                        continue
        attempt = attempt + 1
        if attempt <= retries:
            time.sleep(retry_sleep_secs)

    return files

def update_status_in_db(afile, attempt, err_msg):
    """
    Updates the status for the job in the database.

        Args:
            afile: An input dict with keys for:
            'attempt': The attempt number for the copy
            'err_msg' (string): None, or the error message from the copy command

        Returns:
            afile: The input dict with additional keys for:
                'success' (boolean): True, if the copy was successful,
                    otherwise False.
                'err_msg' (string): when success is False, this will contain
                    the error message from the copy error

            Example:  [{'source_key': 'file1.xml', 'source_bucket': 'my-dr-fake-glacier-bucket',
                          'target_bucket': 'unittest_xml_bucket', 'success': True,
                          'err_msg': ''},
                      {'source_key': 'file2.txt', 'source_bucket': 'my-dr-fake-glacier-bucket',
                          'target_bucket': 'unittest_txt_bucket', 'success': True,
                          'err_msg': ''}]
    """
    old_status = ""
    new_status = ""
    try:
        request_id = None
        jobs = requests_db.get_jobs_by_object_key(afile['source_key'])
        for job in jobs:
            if job["job_status"] != "complete":
                request_id = job["request_id"]
                old_status = job["job_status"]
                break
        if not request_id:
            log_msg = ("Failed to update request status in database. "
                       f"No incomplete entry found for object_key: {afile['source_key']}")
            logging.error(log_msg)
        else:
            if err_msg:
                afile['err_msg'] = err_msg
                new_status = "error"
                logging.error(f"Attempt {attempt}. Error copying file {afile['source_key']}"
                              f" from {afile['source_bucket']} to {afile['target_bucket']}."
                              f" msg: {err_msg}")
                requests_db.update_request_status_for_job(request_id, new_status, err_msg)
            else:
                afile['success'] = True
                afile['err_msg'] = ''
                new_status = "complete"
                logging.info(f"Attempt {attempt}. Success copying file "
                             f"{afile['source_key']} from {afile['source_bucket']} "
                             f"to {afile['target_bucket']}.")
                requests_db.update_request_status_for_job(request_id, new_status)
    except requests_db.DatabaseError as err:
        logging.error(f"Failed to update request status in database. "
                      f"key: {afile['source_key']} old status: {old_status} "
                      f"new status: {new_status}. Err: {str(err)}")
        raise
    return afile

def get_files_from_records(records, bucket_map):
    """
    Parses the input records and returns the files to be restored.

        Args:
            records (dict): passed through from the handler
            bucket_map (dict): Mapping of file extensions to bucket names

        Returns:
            files: A list of dicts with the following keys:
                'source_key': The object key of the file that was restored
                'source_bucket': The name of the s3 bucket where the restored
                    file was temporarily sitting
                'target_bucket': The name of the archive s3 bucket
    """
    files = []
    for record in records:
        afile = {}
        afile['success'] = False
        try:
            log_str = 'Records["s3"]["bucket"]["name"]'
            source_bucket = record["s3"]["bucket"]["name"]
            afile['source_bucket'] = source_bucket
            log_str = 'Records["s3"]["object"]["key"]'
            source_key = record["s3"]["object"]["key"]
            afile['source_key'] = source_key
            _, ext = os.path.splitext(source_key)
            try:
                afile['target_bucket'] = bucket_map[ext]
            except KeyError:
                try:
                    afile['target_bucket'] = bucket_map["other"]
                except KeyError:
                    raise CopyRequestError(f'BUCKET_MAP: {bucket_map} does not contain '
                                           f'values for "{ext}" or "other"')
            files.append(afile)
        except KeyError:
            raise CopyRequestError(f'event record: "{record}" does not contain a '
                                   f'value for {log_str}')
    return files

def copy_object(s3_cli, src_bucket_name, src_object_name,
                dest_bucket_name, dest_object_name=None):
    """Copy an Amazon S3 bucket object

        Args:
            s3_cli (object): An instance of boto3 s3 client
            src_bucket_name (string): The source S3 bucket name
            src_object_name (string): The key of the s3 object being copied
            dest_bucket_name (string): The target S3 bucket name
            dest_object_name (string, optional, default = src_object_name): The key of
                the destination object. If dest bucket/object exists, it is overwritten.

        Returns:
            err_msg: None if object was copied, otherwise contains error message.
    """

    # Construct source bucket/object parameter
    copy_source = {'Bucket': src_bucket_name, 'Key': src_object_name}
    if dest_object_name is None:
        dest_object_name = src_object_name

    # Copy the object
    try:
        response = s3_cli.copy_object(CopySource=copy_source,
                                      Bucket=dest_bucket_name,
                                      Key=dest_object_name)
        logging.info(f"Copy response: {response}")
    except ClientError as ex:
        return str(ex)
    return None

def handler(event, context):      #pylint: disable-msg=unused-argument
    """Lambda handler. Copies a file from it's temporary s3 bucket to the s3 archive.

    If the copy for a file in the request fails, the lambda
    throws an exception. Environment variables can be set to override how many
    times to retry a copy before failing, and how long to wait between retries.

        Environment Vars:
            BUCKET_MAP (dict): A dict of key:value entries, where the key is a file
                extension (including the .) ex. ".hdf", and the value is the destination
                bucket for files with that extension. One of the keys can be "other"
                to designate a bucket for any extensions that are not explicitly
                mapped.
                ex.  {".hdf": "my-great-protected-bucket",
                      ".met": "my-great-protected-bucket",
                      ".txt": "my-great-public-bucket",
                      "other": "my-great-protected-bucket"}
            COPY_RETRIES (number, optional, default = 3): The number of
                attempts to retry a copy that failed.
            COPY_RETRY_SLEEP_SECS (number, optional, default = 0): The number of seconds
                to sleep between retry attempts.
            DATABASE_HOST (string): the server where the database resides.
            DATABASE_PORT (string): the database port. The standard is 5432.
            DATABASE_NAME (string): the name of the database.
            DATABASE_USER (string): the name of the application user.
            DATABASE_PW (string): the password for the application user.

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
    """

    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s: %(asctime)s: %(message)s')
    try:
        bucket_map = json.loads(os.environ['BUCKET_MAP'])
    except KeyError:
        bucket_map = {}

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
    logging.warning(f'event: {event}')
    records = event["Records"]
    result = task(records, bucket_map, retries, retry_sleep_secs)
    for afile in result:
        #if any file failed, the function will fail
        if not afile['success']:
            logging.error(
                f'File copy failed. {result}')
            raise CopyRequestError(f'File copy failed. {result}')
    return result
