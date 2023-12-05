"""
Name: shared_recovery.py
Description: Shared library that combines common functions and classes needed for
             recovery operations.
"""
# Standard libraries
import hashlib
import json
import os
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

# Third party libraries
import boto3
from aws_lambda_powertools import Logger

# Set AWS powertools
LOGGER = Logger()


class RequestMethod(Enum):
    """
    An enumeration.
    Provides potential actions for the database lambda to take when posting to the SQS queue.
    """

    NEW_JOB = "new_job"
    UPDATE_FILE = "update_file"
    DELETE_FILE = "delete_file"
    GET_FILE = "get_file"


class OrcaStatus(Enum):
    """
    An enumeration.
    Defines the status value used in the ORCA Recovery database for use by the recovery functions.
    """

    PENDING = 1
    STAGED = 2
    FAILED = 3
    SUCCESS = 4


def get_aws_region() -> str:
    """
    Gets AWS region variable from the runtime environment variable.
        Returns:
            The AWS region variable.
        Raises:
            Exception: Thrown if AWS region is empty or None.
    """
    LOGGER.debug("Getting environment variable AWS_REGION value.")
    aws_region = os.getenv("AWS_REGION", None)
    if aws_region is None or len(aws_region) == 0:
        message = "Runtime environment variable AWS_REGION is not set."
        LOGGER.critical(message)
        raise ValueError(message)
    LOGGER.debug(f"Got environment variable for AWS_REGION = {aws_region}")
    return aws_region


# Keys for input schema. Utilized by calling code.
JOB_ID_KEY = "jobId"
COLLECTION_ID_KEY = "collectionId"
GRANULE_ID_KEY = "granuleId"
ARCHIVE_DESTINATION_KEY = "archiveDestination"

FILES_KEY = "files"

FILENAME_KEY = "filename"
KEY_PATH_KEY = "keyPath"
RESTORE_DESTINATION_KEY = "restoreDestination"
MULTIPART_CHUNKSIZE_KEY = "s3MultipartChunksizeMb"
STATUS_ID_KEY = "statusId"
ERROR_MESSAGE_KEY = "errorMessage"
REQUEST_TIME_KEY = "requestTime"
LAST_UPDATE_KEY = "lastUpdate"
COMPLETION_TIME_KEY = "completionTime"


def create_status_for_job(
    job_id: str,
    collection_id: str,
    granule_id: str,
    archive_destination: str,
    files: List[Dict[str, Any]],
    db_queue_url: str,
):
    """
    Creates status information for a new job and its files, and posts to queue.
    Args:
        job_id: The unique identifier used for tracking requests.
        collection_id: The id of the collection containing the collection.
        granule_id: The id of the granule being restored.
        archive_destination: The S3 bucket destination of where the data is archived.
        files: A List of Dicts with the following keys:
            'filename' (str)
            'keyPath' (str)
            'restoreDestination' (str)
            's3MultipartChunksizeMb' (int)
            'statusId' (int)
            'errorMessage' (str, Optional)
            'requestTime' (str)
            'lastUpdate' (str)
            'completionTime' (str, Optional)
        db_queue_url: The SQS queue URL defined by AWS.
    """
    new_data = {
        JOB_ID_KEY: job_id,
        COLLECTION_ID_KEY: collection_id,
        GRANULE_ID_KEY: granule_id,
        REQUEST_TIME_KEY: datetime.now(timezone.utc).isoformat(),
        ARCHIVE_DESTINATION_KEY: archive_destination,
        FILES_KEY: files,
    }

    message = f"Sending the following data to queue: {new_data}"
    LOGGER.debug(message)

    post_entry_to_fifo_queue(new_data, RequestMethod.NEW_JOB, db_queue_url)


def update_status_for_file(
    job_id: str,
    collection_id: str,
    granule_id: str,
    filename: str,
    orca_status: OrcaStatus,
    error_message: Optional[str],
    db_queue_url: str,
):
    """
    Creates update information for a file's status entry, and posts to queue.
    Queue entry will be rejected by post_to_database if status for
    job_id + granule_id + filename does not exist.

    Args:
        job_id: The unique identifier used for tracking requests.
        collection_id: The id of the collection containing the collection.
        granule_id: The id of the granule being restored.
        filename: The name of the file being copied.
        orca_status: Defines the status id used in the ORCA Recovery database.
        error_message: message displayed on error.
        db_queue_url: The SQS queue URL defined by AWS.
    """
    last_update = datetime.now(timezone.utc).isoformat()
    new_data = {
        JOB_ID_KEY: job_id,
        COLLECTION_ID_KEY: collection_id,
        GRANULE_ID_KEY: granule_id,
        FILENAME_KEY: filename,
        LAST_UPDATE_KEY: last_update,
        STATUS_ID_KEY: orca_status.value,
    }

    if orca_status == OrcaStatus.SUCCESS or orca_status == OrcaStatus.FAILED:
        new_data[COMPLETION_TIME_KEY] = datetime.now(timezone.utc).isoformat()
        if orca_status == OrcaStatus.FAILED:
            if error_message is None or len(error_message) == 0:
                raise ValueError("Error message is required.")
            new_data[ERROR_MESSAGE_KEY] = error_message

    message = f"Sending the following data to queue: {new_data}"
    LOGGER.debug(message)

    post_entry_to_fifo_queue(new_data, RequestMethod.UPDATE_FILE, db_queue_url)


def post_entry_to_fifo_queue(
    new_data: Dict[str, Any],
    request_method: RequestMethod,
    db_queue_url: str,
) -> None:
    """
    Posts messages to SQS FIFO queue.
    Args:
        new_data: A dictionary representing the column/value pairs to write to the DB table.
        request_method: The action for the database lambda to take when posting to the SQS queue.
        db_queue_url: The SQS queue URL defined by AWS.
    Raises:
        None
    """
    body = json.dumps(new_data)

    # TODO: pass AWS region value to function. SHOULD be gotten from environment
    # higher up. Setting this to us-west-2 initially since that is where
    # EOSDIS runs from normally. SEE ORCA-203 https://bugs.earthdata.nasa.ov/browse/ORCA-203
    LOGGER.debug(f"Creating SQS resource for {db_queue_url}")
    mysqs_resource = boto3.resource("sqs", region_name=get_aws_region())
    mysqs = mysqs_resource.Queue(db_queue_url)

    # Create hash for De-duplication ID max size is 128 characters
    # sha256 will be 64 characters long sha512 is 128 characters
    deduplication_id = (
        request_method.value + hashlib.sha256(body.encode("utf8")).hexdigest()
    )

    md5_body = hashlib.md5(body.encode("utf8")).hexdigest()  # nosec

    LOGGER.debug("Sending message to the QUEUE")
    response = mysqs.send_message(
        QueueUrl=db_queue_url,
        MessageDeduplicationId=deduplication_id,
        MessageGroupId="request_files",
        MessageAttributes={
            "RequestMethod": {
                "DataType": "String",
                "StringValue": request_method.value,
            }
        },
        MessageBody=body,
    )
    LOGGER.debug(f"SQS Message Response: {json.dumps(response)}")

    # Make sure we didn't have an error sending message
    return_status = response["ResponseMetadata"]["HTTPStatusCode"]
    if return_status < 200 or return_status > 299:
        raise Exception(
            f"Failed to send message to Queue. HTTP Response was {return_status}"
        )

    sqs_md5 = response.get("MD5OfMessageBody")
    if md5_body != sqs_md5:
        raise Exception(
            f"Calculated MD5 of {md5_body} does not match SQS MD5 of {sqs_md5}"
        )


def post_entry_to_standard_queue(
    new_data: Dict[str, Any],
    recovery_queue_url: str,
) -> None:
    """
    Posts messages to the recovery standard SQS queue.
    Args:
        new_data: A dictionary representing the column/value pairs to write to the DB table.
        recovery_queue_url: The SQS queue URL defined by AWS.
    Raises:
        None
    """
    body = json.dumps(new_data)

    # TODO: pass AWS region value to function. SHOULD be gotten from environment
    # higher up. Setting this to us-west-2 initially since that is where
    # EOSDIS runs from normally. SEE ORCA-203 https://bugs.earthdata.nasa.ov/browse/ORCA-203
    LOGGER.debug(f"Creating SQS resource for {recovery_queue_url}")
    mysqs_resource = boto3.resource("sqs", region_name=get_aws_region())
    mysqs = mysqs_resource.Queue(recovery_queue_url)

    md5_body = hashlib.md5(body.encode("utf8")).hexdigest()  # nosec

    LOGGER.debug("Sending message to the QUEUE")
    response = mysqs.send_message(
        QueueUrl=recovery_queue_url,
        MessageBody=body,
    )
    LOGGER.debug(f"SQS Message Response: {json.dumps(response)}")

    # Make sure we didn't have an error sending message
    return_status = response["ResponseMetadata"]["HTTPStatusCode"]
    if return_status < 200 or return_status > 299:
        raise Exception(
            f"Failed to send message to Queue. HTTP Response was {return_status}"
        )

    sqs_md5 = response.get("MD5OfMessageBody")
    if md5_body != sqs_md5:
        raise Exception(
            f"Calculated MD5 of {md5_body} does not match SQS MD5 of {sqs_md5}"
        )
