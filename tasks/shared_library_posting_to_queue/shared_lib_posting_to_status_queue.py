from enum import Enum
import json
import boto3
from typing import Dict,Any, Optional
import time

class RequestMethod(Enum):
    POST = 'post'
    PUT = 'put'

class ORCA_STATUS(Enum):
    ORCA_STATUS_PENDING = 1
    ORCA_STATUS_STAGED = 2
    ORCA_STATUS_SUCCESS = 3
    ORCA_STATUS_FAILED = 4


db_queue_url = "TBD"
region= 'us-west-2'
sqs = boto3.client('sqs', region_name = region)

def post_status_for_job_to_queue(job_id: str, granule_id: str, status_id: Optional[int],
                                 request_time: Optional[str], completion_time: Optional[str],
                                 archive_destination: Optional[str],
                                 request_method: RequestMethod, db_queue_url: str,
                                 max_retries: int, retry_sleep_secs: float):
    new_data = {'job_id': job_id, 'granule_id': granule_id}
    if status_id is not None:
        new_data['status_id'] = status_id
    if request_time is not None:
        new_data['request_time'] = request_time
    if completion_time is not None:
        new_data['completion_time'] = completion_time
    if archive_destination is not None:
        new_data['archive_destination'] = archive_destination

    post_entry_to_queue('orca_recoveryjob',
                        new_data,
                        request_method, db_queue_url, max_retries, retry_sleep_secs)

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
        new_data['key_path'] = key_path
    if restore_destination is not None:
        new_data['restore_destination'] = restore_destination
    if status_id is not None:
        new_data['status_id'] = status_id
    if error_message is not None:
        new_data['error_message'] = error_message
    if request_time is not None:
        new_data['request_time'] = request_time
    if last_update is not None:
        new_data['last_update'] = last_update
    if completion_time is not None:
        new_data['completion_time'] = completion_time

    post_entry_to_queue('orca_recoverfile',
                        new_data,
                        request_method,
                        db_queue_url, max_retries, retry_sleep_secs)

def post_entry_to_queue(table_name: str, new_data: Dict[str, Any], request_method: RequestMethod, db_queue_url: str,
                        max_retries: int, retry_sleep_secs: float):
    body = json.dumps(new_data, indent=4)
    for attempt in range(1, max_retries + 1):
        try:
            sqs.send_message(
                QueueUrl=db_queue_url
            )
            sqs.send_message(
                QueueUrl=db_queue_url,
                MessageDeduplicationId=table_name + request_method.value + body,
                MessageGroupId='request_files',
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
                MessageBody=body
            )
            return
        except Exception as e:
            if attempt == max_retries + 1:
                LOGGER.error(f"Error while logging row {json.dumps(new_data, indent=4)} "
                             f"to table {table_name}: {e}")
                raise e
            time.sleep(retry_sleep_secs)
            continue