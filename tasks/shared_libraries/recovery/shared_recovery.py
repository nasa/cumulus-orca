"""
Name: shared_recovery.py
Description: Shared library that combines common functions and classes needed for recovery operations.
"""
from enum import Enum
import json
import boto3
from typing import Dict, Any, Optional

class RequestMethod(Enum):
    """
    An enumeration.
    Provides potential actions for the database lambda to take when posting to the SQS queue.
    """
    NEW = "post"
    UPDATE = "put"

class OrcaStatus(Enum):
    """
    An enumeration.
    Defines the status value used in the ORCA Recovery database for use by the recovery functions.

    """
    PENDING = 1
    STAGED = 2
    SUCCESS = 3
    FAILED = 4

def post_status_for_job_to_queue(
    job_id: str,
    granule_id: str,
    status_id: OrcaStatus,
    request_time: Optional[str],
    completion_time: Optional[str],
    archive_destination: Optional[str],
    request_method: RequestMethod,
    db_queue_url: str,
):
    """Posts status of jobs to SQS queue.

    Args:
        job_id: The unique identifier used for tracking requests.
        granuleId: The id of the granule being restored.
        status_id: Defines the status id used in the ORCA Recovery database.
        request_time: todo
        completion_time: todo
        archive_destination: The S3 bucket destination of where the data is archived.
        request_method: The method action for the database lambda to take when posting to the SQS queue.
        db_queue_url: The SQS queue URL defined by AWS.

    Returns:
        None

    Raises:
        None
    """

    new_data = {"job_id": job_id, "granule_id": granule_id}
    if request_time is not None:
        new_data["request_time"] = request_time
    if completion_time is not None:
        new_data["completion_time"] = completion_time
    if archive_destination is not None:
        new_data["archive_destination"] = archive_destination

    post_entry_to_queue("orca_recoveryjob", new_data, request_method, db_queue_url)


def post_status_for_file_to_queue(
    job_id: str,
    granule_id: str,
    filename: str,
    key_path: Optional[str],
    restore_destination: Optional[str],
    status_id: OrcaStatus,
    error_message: Optional[str],
    request_time: Optional[str],
    last_update: str,
    completion_time: Optional[str],
    request_method: RequestMethod,
    db_queue_url: str,
):
    """Posts status of files to SQS queue.

    Args:
        job_id: The unique identifier used for tracking requests.
        granuleId: The id of the granule being restored.
        filename: The name of the file being copied.
        key_path: todo
        restore_destination: The name of the bucket the restored file will be moved to.
        status_id: Defines the status id used in the ORCA Recovery database.
        error_message: message displayed on error.
        request_time: todo
        last_update: todo
        completion_time: todo
        request_method: The method action for the database lambda to take when posting to the SQS queue.
        db_queue_url: The SQS queue URL defined by AWS.

    Returns:
        None

    Raises:
        None
    """
    new_data = {"job_id": job_id, "granule_id": granule_id, "filename": filename, "last_update": last_update}
    if key_path is not None:
        new_data["key_path"] = key_path
    if restore_destination is not None:
        new_data["restore_destination"] = restore_destination
    if error_message is not None:
        new_data["error_message"] = error_message
    if request_time is not None:
        new_data["request_time"] = request_time
    if completion_time is not None:
        new_data["completion_time"] = completion_time

    post_entry_to_queue("orca_recoverfile", new_data, request_method, db_queue_url)


def post_entry_to_queue(
    table_name: str,
    new_data: Dict[str, Any],
    request_method: RequestMethod,
    db_queue_url: str,
):
    """Posts the request files to SQS queue.

    Args:
        table_name: The name of the DB table.
        new_data: A dictionary representing the column/value pairs to write to the DB table.
        request_method: The method action for the database lambda to take when posting to the SQS queue.
        db_queue_url: The SQS queue URL defined by AWS.

    Returns:
        None

    Raises:
        None
    """
    body = json.dumps(new_data)

    mysqs_resource = boto3.resource("sqs")
    mysqs = mysqs_resource.Queue(db_queue_url)

    mysqs.send_message(
        QueueUrl=db_queue_url,
        MessageDeduplicationId=table_name + request_method.value + body,
        MessageGroupId="request_files",
        MessageAttributes={
            "RequestMethod": {
                "DataType": "String",
                "StringValue": request_method.value,
            },
            "TableName": {"DataType": "String", "StringValue": table_name},
        },
        MessageBody=body
    )