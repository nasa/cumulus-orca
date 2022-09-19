"""
Name: copy_files_to_archive.py
Description:  Lambda function that copies files from one s3 bucket
to another s3 bucket.
"""
import json
import os
import time
from typing import Any, Dict, List, Optional, Union

# noinspection PyPackageRequirements
import boto3
import fastjsonschema
from boto3.s3.transfer import MB, TransferConfig
from botocore.client import BaseClient
from botocore.exceptions import ClientError
from cumulus_logger import CumulusLogger

# noinspection PyPackageRequirements
from orca_shared.recovery import shared_recovery

OS_ENVIRON_STATUS_UPDATE_QUEUE_URL_KEY = "STATUS_UPDATE_QUEUE_URL"

# These will determine what the output looks like.
FILE_SUCCESS_KEY = "success"
FILE_ERROR_MESSAGE_KEY = "errorMessage"
FILE_MESSAGE_RECEIPT = "receiptHandle"

# These are tied to the input schema.
INPUT_JOB_ID_KEY = "jobId"
INPUT_GRANULE_ID_KEY = "granuleId"
INPUT_FILENAME_KEY = "filename"
INPUT_SOURCE_KEY_KEY = "sourceKey"
INPUT_TARGET_KEY_KEY = "targetKey"
INPUT_TARGET_BUCKET_KEY = "restoreDestination"
INPUT_SOURCE_BUCKET_KEY = "sourceBucket"
INPUT_MULTIPART_CHUNKSIZE_MB_KEY = "s3MultipartChunksizeMb"

LOGGER = CumulusLogger()
# Generating schema validators can take time, so do it once and reuse.
try:
    with open("schemas/input.json", "r") as raw_schema:
        _INPUT_VALIDATE = fastjsonschema.compile(json.loads(raw_schema.read()))
except Exception as ex:
    LOGGER.error(f"Could not build schema validator: {ex}")
    raise

try:
    with open("schemas/sub_schemas/body.json", "r") as raw_schema:
        _BODY_VALIDATE = fastjsonschema.compile(json.loads(raw_schema.read()))
except Exception as ex:
    LOGGER.error(f"Could not build schema validator: {ex}")
    raise


class CopyRequestError(Exception):
    """
    Exception to be raised if the copy request fails for any of the files.
    """


def task(
    records: List[Dict[str, Any]],
    max_retries: int,
    retry_sleep_secs: float,
    status_update_queue_url: str,
    default_multipart_chunksize_mb: int,
    recovery_queue_url: str,
) -> None:
    """
    Task called by the handler to perform the work.
    This task will call copy_object for each file. A copy will be tried
    up to {retries} times if it fails, waiting {retry_sleep_secs}
    between each attempt.
    Args:
        records: Passed through from the handler.
        max_retries: The number of attempts to retry a failed copy.
        retry_sleep_secs: The number of seconds
            to sleep between retry attempts.
        status_update_queue_url: The URL of the queue that posts status entries.
        default_multipart_chunksize_mb: The multipart_chunksize to use if not set on file.
        recovery_queue_url: The URL of the queue that this lambda is receiving messages from.
    Raises:
        CopyRequestError: Thrown if there are errors with the input records or the copy failed.
    """
    files = get_files_from_records(records)
    s3 = boto3.client("s3")  # pylint: disable-msg=invalid-name
    aws_client_sqs = boto3.client("sqs")

    for attempt in range(1, max_retries + 1):
        for a_file in files:
            # All files from get_files_from_records start with 'success' == False.
            if not a_file[FILE_SUCCESS_KEY]:
                LOGGER.debug(f"Restoring file {a_file[INPUT_SOURCE_KEY_KEY]}")
                err_msg = copy_object(
                    s3,
                    a_file[INPUT_SOURCE_BUCKET_KEY],
                    a_file[INPUT_SOURCE_KEY_KEY],
                    a_file[INPUT_TARGET_BUCKET_KEY],
                    a_file.get(INPUT_MULTIPART_CHUNKSIZE_MB_KEY, None)
                    or default_multipart_chunksize_mb,
                    a_file[INPUT_TARGET_KEY_KEY],
                )

                # Check to see that our copy for the file was a success
                if err_msg is None:
                    # Send updated status to database queue
                    a_file[FILE_SUCCESS_KEY] = True
                    shared_recovery.update_status_for_file(
                        a_file[INPUT_JOB_ID_KEY],
                        a_file[INPUT_GRANULE_ID_KEY],
                        a_file[INPUT_FILENAME_KEY],
                        shared_recovery.OrcaStatus.SUCCESS,
                        None,
                        status_update_queue_url,
                    )

                    # Remove message from the queue we are listening to so we
                    # don't try to do it again if something else fails.
                    aws_client_sqs.delete_message(
                        QueueUrl=recovery_queue_url,
                        ReceiptHandle=a_file[FILE_MESSAGE_RECEIPT],
                    )

                else:
                    a_file[FILE_ERROR_MESSAGE_KEY] = err_msg

        if attempt < max_retries + 1:  # Only sleep if not on the last attempt.
            if all(
                a_file[FILE_SUCCESS_KEY] for a_file in files
            ):  # Check for early completion
                break
            LOGGER.warn(
                f"Attempt {attempt +1} of restore failed. Retrying in {retry_sleep_secs} seconds."
            )
            time.sleep(retry_sleep_secs)

    any_error = False
    for a_file in files:
        if not a_file[FILE_SUCCESS_KEY]:
            any_error = True
            shared_recovery.update_status_for_file(
                a_file[INPUT_JOB_ID_KEY],
                a_file[INPUT_GRANULE_ID_KEY],
                a_file[INPUT_FILENAME_KEY],
                shared_recovery.OrcaStatus.FAILED,
                a_file.get(FILE_ERROR_MESSAGE_KEY, None),
                status_update_queue_url,
            )
    if any_error:
        LOGGER.error("File copy failed. {files}", files=files)
        raise CopyRequestError(f"File copy failed. {files}")


def get_files_from_records(
    records: List[Dict[str, Any]]
) -> List[Dict[str, Union[str, bool]]]:
    """
    Parses the input records and returns the files to be restored.
    Args:
        records: passed through from the handler.
    Returns:
        records, parsed into Dicts, with the additional KVP 'success' = False
    """
    files = []
    for record in records:
        a_file = json.loads(record["body"])
        LOGGER.debug("Validating {file}", file=a_file)
        _BODY_VALIDATE(a_file)
        a_file[FILE_SUCCESS_KEY] = False
        a_file[FILE_MESSAGE_RECEIPT] = record[FILE_MESSAGE_RECEIPT]
        files.append(a_file)
    return files


def copy_object(
    s3_cli: BaseClient,
    src_bucket_name: str,
    src_object_name: str,
    dest_bucket_name: str,
    multipart_chunksize_mb: int,
    dest_object_name: str = None,
) -> Optional[str]:
    """Copy an Amazon S3 bucket object
    Args:
        s3_cli: An instance of boto3 s3 client.
        src_bucket_name: The source S3 bucket name.
        src_object_name: The key of the s3 object being copied.
        dest_bucket_name: The target S3 bucket name.
        multipart_chunksize_mb: The maximum size of chunks to use when copying.
        dest_object_name: Optional; The key of the destination object.
            If an object with the same name exists in the given bucket, the object is overwritten.
            Defaults to {src_object_name}.
    Returns:
        None if object was copied, otherwise contains error message.
    """

    if dest_object_name is None:
        dest_object_name = src_object_name
    # Construct source bucket/object parameter
    copy_source = {"Bucket": src_bucket_name, "Key": src_object_name}

    # Copy the object
    try:
        LOGGER.debug(
            f"Copying {src_object_name} to {dest_bucket_name} "
            f" with chunk size of {multipart_chunksize_mb}MB."
        )
        s3_cli.copy(
            copy_source,
            dest_bucket_name,
            dest_object_name,
            ExtraArgs={
                # 'StorageClass': 'GLACIER',
                # 'MetadataDirective': 'COPY',
                # 'ContentType': s3_cli.head_object(Bucket=src_bucket_name,
                #  Key=src_object_name)['ContentType'],
                # 'ACL': 'bucket-owner-full-control'
                # Sets the x-amz-acl URI Request Parameter. Needed for cross-OU copies.
            },
            Config=TransferConfig(multipart_chunksize=multipart_chunksize_mb * MB),
        )
        LOGGER.debug(f"Object {src_object_name} copied.")
    except ClientError as ex:
        LOGGER.error("Client error: {ex}", ex=ex)
        return ex.__str__()
    return None


# noinspection PyUnusedLocal
def handler(
    event: Dict[str, Any], context: object
) -> None:  # pylint: disable-msg=unused-argument
    """Lambda handler. Copies a file from its temporary s3 bucket to the s3 archive.
    If the copy for a file in the request fails, the lambda
    throws an exception. Environment variables can be set to override how many
    times to retry a copy before failing, and how long to wait between retries.
        Environment Vars:
            COPY_RETRIES (number, optional, default = 3): The number of
                attempts to retry a copy that failed.
            COPY_RETRY_SLEEP_SECS (number, optional, default = 0): The number of seconds
                to sleep between retry attempts.
            DATABASE_PORT (string): the database port. The standard is 5432.
            DATABASE_NAME (string): the name of the database.
            DATABASE_USER (string): the name of the application user.
            STATUS_UPDATE_QUEUE_URL (string): The URL of the SQS queue to post status to.
        Parameter Store:
                drdb-user-pass (string): the password for the application user (DATABASE_USER).
                drdb-host (string): the database host
    Args:
        event:
            A dict from the SQS queue. See schemas/input.json for more information.
        context: An object required by AWS Lambda. Unused.
    Raises:
        CopyRequestError: An error occurred calling copy for one or more files.
        The same dict that is returned for a successful copy will be included in the
        message, with 'success' = False for the files for which the copy failed.
    """
    LOGGER.setMetadata(event, context)
    _INPUT_VALIDATE(event)

    try:
        str_env_val = os.environ["COPY_RETRIES"]
        retries = int(str_env_val)
    except KeyError:
        LOGGER.warn("Setting COPY_RETRIES value to a default of 2")
        retries = 2

    try:
        str_env_val = os.environ["COPY_RETRY_SLEEP_SECS"]
        retry_sleep_secs = float(str_env_val)
    except KeyError:
        LOGGER.warn("Setting COPY_RETRY_SLEEP_SECS value to a default of 30")
        retry_sleep_secs = 30

    try:
        status_update_queue_url = str(
            os.environ[OS_ENVIRON_STATUS_UPDATE_QUEUE_URL_KEY]
        )
    except KeyError as key_error:
        LOGGER.error(
            f"{OS_ENVIRON_STATUS_UPDATE_QUEUE_URL_KEY} environment value not found."
        )
        raise key_error

    try:
        default_multipart_chunksize_mb = int(
            os.environ["DEFAULT_MULTIPART_CHUNKSIZE_MB"]
        )
    except KeyError as key_error:
        LOGGER.error("DEFAULT_MULTIPART_CHUNKSIZE_MB environment value not found.")
        raise key_error

    try:
        recovery_queue_url = str(os.environ["RECOVERY_QUEUE_URL"])
    except KeyError as key_error:
        LOGGER.error("RECOVERY_QUEUE_URL environment value not found.")
        raise key_error

    LOGGER.debug("event: {event}", event=event)
    records = event["Records"]

    task(
        records,
        retries,
        retry_sleep_secs,
        status_update_queue_url,
        default_multipart_chunksize_mb,
        recovery_queue_url,
    )
