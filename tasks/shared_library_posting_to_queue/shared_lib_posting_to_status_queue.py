from enum import Enum
import json
import boto3
from typing import Dict,Any, Optional

class RequestMethod(Enum):
    POST = 'post'
    PUT = 'put'

class OrcaStatus(Enum):
    """
    Defines the status of ORCA DB?
    """
    PENDING = 1
    STAGED  = 2
    SUCCESS = 3
    FAILED  = 4

def post_status_for_job_to_queue(job_id: str, granule_id: str, status_id: OrcaStatus,
                                 request_time: Optional[str], completion_time: Optional[str],
                                 archive_destination: Optional[str],
                                 request_method: RequestMethod, db_queue_url: str):
    new_data = {'job_id': job_id, 'granule_id': granule_id}
    if request_time is not None:
        new_data['request_time'] = request_time
    if completion_time is not None:
        new_data['completion_time'] = completion_time
    if archive_destination is not None:
        new_data['archive_destination'] = archive_destination

    post_entry_to_queue('orca_recoveryjob',
                        new_data,
                        request_method, db_queue_url)

def post_status_for_file_to_queue(job_id: str, granule_id: str, filename: str, key_path: Optional[str],
                                  restore_destination: Optional[str],
                                  status_id: OrcaStatus, error_message: Optional[str],
                                  request_time: Optional[str], last_update: str,
                                  completion_time: Optional[str],
                                  request_method: RequestMethod,
                                  db_queue_url: str):
    new_data = {'job_id': job_id,
                'granule_id': granule_id,
                'filename': filename}
    if key_path is not None:
        new_data['key_path'] = key_path
    if restore_destination is not None:
        new_data['restore_destination'] = restore_destination
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
                        db_queue_url)


sqs = boto3.client('sqs')

def post_entry_to_queue(table_name: str, new_data: Dict[str, Any], request_method: RequestMethod, db_queue_url: str):
    body = json.dumps(new_data, indent=4)
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