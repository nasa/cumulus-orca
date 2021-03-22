"""
Name: post_copy_request_to_queue.py

Description:  Posts to a queue that notifies copy_files_to_archive that a file is ready for copy.
"""
import json
import time
from enum import Enum
from typing import Any, List, Dict, Optional

import boto3 as boto3
import requests_db
from cumulus_logger import CumulusLogger

#ORCA_STATUS_PENDING = 0
ORCA_STATUS_STAGED = 1
ORCA_STATUS_SUCCESS = 2
#ORCA_STATUS_FAILED = 3


class RequestMethod(Enum):
    POST = 'post'
    PUT = 'put'


LOGGER = CumulusLogger()


def task(db_connect_info: Dict[str, Any]):
    # todo: Get all entries from orca_recoverfile table that match the given file and are 'PENDING'.
    # todo: Update entry to be STAGED, and post back to table.
    # todo: For each orca_recoverfile, add instructions for copy_files_to_archive to the queue.
    pass


# todo: Move to shared lib
def post_status_for_job_to_queue(job_id: str, granule_id: str, status_id: Optional[int],
                                 request_time: Optional[str], completion_time: Optional[str],
                                 archive_destination: Optional[str],
                                 request_method: RequestMethod, db_queue_url: str,
                                 max_retries: int, retry_sleep_secs: float):
    new_data = {'job_id': job_id, 'granule_id': granule_id}
    if status_id is not None:
        new_data['status_id'] = status_id
    if request_time is not None:
        new_data['request_time'] = status_id
    if completion_time is not None:
        new_data['completion_time'] = status_id
    if archive_destination is not None:
        new_data['archive_destination'] = status_id

    post_entry_to_queue('orca_recoveryjob',
                        new_data,
                        request_method, db_queue_url, max_retries, retry_sleep_secs)


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


def handler(event: Dict[str, List], context):
    """
    Lambda handler.
    Receives input from copy operation, adds details from status DB, and stores in queue for copy_files_to_archive.

    Args:
        event: todo: use relevant properties from https://bugs.earthdata.nasa.gov/browse/ORCA-149
        context: An object passed through by AWS. Used for tracking.
    Environment Vars: See requests_db.py's get_dbconnect_info for further details.
        'DATABASE_PORT' (int): Defaults to 5432
        'DATABASE_NAME' (str)
        'DATABASE_USER' (str)
        'PREFIX' (str)
        '{prefix}-drdb-host' (str, secretsmanager)
        '{prefix}-drdb-user-pass' (str, secretsmanager)
    """
    LOGGER.setMetadata(event, context)

    db_connect_info = requests_db.get_dbconnect_info()

    task(db_connect_info)
