"""
Name: shared_recovery.py
Description: Shared library that combines common functions and classes needed for recovery operations.
"""
from enum import Enum
import json
import boto3
from typing import Dict, Any, Optional
from datetime import datetime, timezone


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
    archive_destination: Optional[str],
    request_method: RequestMethod,
    db_queue_url: str,
):
    """
    Posts status of jobs to SQS queue.

    Args:
        job_id: The unique identifier used for tracking requests.
        granuleId: The id of the granule being restored.
        status_id: Defines the status id used in the ORCA Recovery database.
        archive_destination: The S3 bucket destination of where the data is archived.
        request_method: The method action for the database lambda to take when posting to the SQS queue.
        db_queue_url: The SQS queue URL defined by AWS.

    Returns:
        None

    Raises:
        None
    """

    new_data = {
        "job_id": job_id,
        "granule_id": granule_id,
        "status_id": status_id.value,
    }
    if request_method == RequestMethod.NEW:
        new_data["request_time"] = datetime.now(timezone.utc).isoformat()
        if len(archive_destination) == 0 or archive_destination is None:
            raise Exception("archive_destination is required for new records.")
        new_data["archive_destination"] = archive_destination
    if status_id == OrcaStatus.SUCCESS or status_id == OrcaStatus.FAILED:
        new_data["completion_time"] = datetime.now(timezone.utc).isoformat()

    post_entry_to_queue("orca_recoveryjob", new_data, request_method, db_queue_url)


def post_status_for_file_to_queue(
    job_id: str,
    granule_id: str,
    filename: str,
    key_path: Optional[str],
    restore_destination: Optional[str],
    status_id: OrcaStatus,
    error_message: Optional[str],
    request_method: RequestMethod,
    db_queue_url: str,
):
    """
    Posts status of files to SQS queue.

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
    last_update = datetime.now(timezone.utc).isoformat()
    new_data = {
        "job_id": job_id,
        "granule_id": granule_id,
        "filename": filename,
        "last_update": last_update,
        "status_id": status_id.value,
    }

    if request_method == RequestMethod.NEW:
        new_data["request_time"] = datetime.now(timezone.utc).isoformat()
        if len(key_path) == 0 or key_path is None:
            raise Exception("key_path is required.")
        if len(restore_destination) == 0 or restore_destination is None:
            raise Exception("restore_destination is required.")
        new_data["key_path"] = key_path
        new_data["restore_destination"] = restore_destination

    if status_id == OrcaStatus.SUCCESS or status_id == OrcaStatus.FAILED:
        new_data["completion_time"] = datetime.now(timezone.utc).isoformat()
        if status_id == OrcaStatus.FAILED:
            if len(error_message) == 0 or error_message is None:
                raise Exception("error message is required.")
            new_data["error_message"] = error_message

    post_entry_to_queue("orca_recoverfile", new_data, request_method, db_queue_url)


def post_entry_to_queue(
    table_name: str,
    new_data: Dict[str, Any],
    request_method: RequestMethod,
    db_queue_url: str,
):
    """
    Posts messages to an SQS queue.

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

    # TODO: pass AWS region value to function. SHOULD be gotten from environment
    # higher up. Setting this to us-west-2 initially since that is where
    # EOSDIS runs from normally. SEE ORCA-203 https://bugs.earthdata.nasa.ov/browse/ORCA-203
    mysqs_resource = boto3.resource("sqs", region_name="us-west-2")
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
        MessageBody=body,
    )
