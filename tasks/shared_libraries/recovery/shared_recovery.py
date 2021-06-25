"""
Name: shared_recovery.py
Description: Shared library that combines common functions and classes needed for recovery operations.
"""
from enum import Enum
import json
import boto3
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import os
from cumulus_logger import CumulusLogger

# instantiate CumulusLogger
logger = CumulusLogger()

class RequestMethod(Enum):
    """
    An enumeration.
    Provides potential actions for the database lambda to take when posting to the SQS queue.
    """
    NEW_JOB = "new_job"
    UPDATE_FILE = "update_file"


class OrcaStatus(Enum):
    """
    An enumeration.
    Defines the status value used in the ORCA Recovery database for use by the recovery functions.
    """
    PENDING = 1
    STAGED = 2
    FAILED = 3
    SUCCESS = 4

def get_aws_region()-> str:
    """
    Gets AWS region variable from the runtime environment variable.
        Returns:
            The AWS region variable.
        Raises:
            Exception: Thrown if AWS region is empty or None.
    """
    logger.debug("Getting environment variable AWS_REGION value.")
    aws_region = os.getenv("AWS_REGION", None)
    if aws_region is None or len(aws_region) == 0:
        message = "Runtime environment variable AWS_REGION is not set."
        logger.critical(message)
        raise Exception(message)
    logger.debug(f"Got environment variable for AWS_REGION = {aws_region}")
    return aws_region

def create_status_for_job(
    job_id: str,
    granule_id: str,
    archive_destination: str,
    files: List[Dict[str, Any]],
    db_queue_url: str
):
    """
    Creates status information for a new job and its files, and posts to queue.
    Args:
        job_id: The unique identifier used for tracking requests.
        granule_id: The id of the granule being restored.
        archive_destination: The S3 bucket destination of where the data is archived.
        files: A List of Dicts with the following keys:
            'filename' (str)
            'key_path' (str)
            'restore_destination' (str)
            'status_id' (int)
            'error_message' (str, Optional)
            'request_time' (str)
            'last_update' (str)
            'completion_time' (str, Optional)
        db_queue_url: The SQS queue URL defined by AWS.
    """
    new_data = {"job_id": job_id, "granule_id": granule_id,
                "request_time": datetime.now(timezone.utc).isoformat(), "archive_destination": archive_destination,
                "files": files}

    post_entry_to_queue(new_data, RequestMethod.NEW_JOB, db_queue_url)


def update_status_for_file(
    job_id: str,
    granule_id: str,
    filename: str,
    orca_status: OrcaStatus,
    error_message: Optional[str],
    db_queue_url: str
):
    """
    Creates update information for a file's status entry, and posts to queue.
    Queue entry will be rejected by post_to_database if status for job_id + granule_id + filename does not exist.
    Args:
        job_id: The unique identifier used for tracking requests.
        granule_id: The id of the granule being restored.
        filename: The name of the file being copied.
        orca_status: Defines the status id used in the ORCA Recovery database.
        error_message: message displayed on error.
        db_queue_url: The SQS queue URL defined by AWS.
    """
    last_update = datetime.now(timezone.utc).isoformat()
    new_data = {
        "job_id": job_id,
        "granule_id": granule_id,
        "filename": filename,
        "last_update": last_update,
        "status_id": orca_status.value,
    }

    if orca_status == OrcaStatus.SUCCESS or orca_status == OrcaStatus.FAILED:
        new_data["completion_time"] = datetime.now(timezone.utc).isoformat()
        if orca_status == OrcaStatus.FAILED:
            if len(error_message) == 0 or error_message is None:
                raise Exception("error message is required.")
            new_data["error_message"] = error_message

    post_entry_to_queue(new_data, RequestMethod.UPDATE_FILE, db_queue_url)


def post_entry_to_queue(
    new_data: Dict[str, Any],
    request_method: RequestMethod,
    db_queue_url: str,
) -> None:
    """
    Posts messages to an SQS queue.
    Args:
        new_data: A dictionary representing the column/value pairs to write to the DB table.
        request_method: The method action for the database lambda to take when posting to the SQS queue.
        db_queue_url: The SQS queue URL defined by AWS.
    Raises:
        None
    """
    body = json.dumps(new_data)

    mysqs_resource = boto3.resource("sqs", region_name= get_aws_region())
    mysqs = mysqs_resource.Queue(db_queue_url)

    mysqs.send_message(
        QueueUrl=db_queue_url,
        MessageDeduplicationId=request_method.value + body,
        MessageGroupId="request_files",
        MessageAttributes={
            "RequestMethod": {
                "DataType": "String",
                "StringValue": request_method.value,
            }
        },
        MessageBody=body,
    )