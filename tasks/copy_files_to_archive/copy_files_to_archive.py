"""
Name: copy_files_to_archive.py
Description:  Lambda function that copies files from one s3 bucket
to another s3 bucket.
"""
import json
import os
import time
from typing import Any, List, Dict, Optional, Union

import boto3
import fastjsonschema

# noinspection PyPackageRequirements
from boto3.s3.transfer import TransferConfig, MB
from botocore.client import BaseClient

# noinspection PyPackageRequirements
from botocore.exceptions import ClientError
from orca_shared import shared_recovery
from cumulus_logger import CumulusLogger


OS_ENVIRON_DB_QUEUE_URL_KEY = "DB_QUEUE_URL"

# These will determine what the output looks like.
FILE_SUCCESS_KEY = "success"
FILE_ERROR_MESSAGE_KEY = "err_msg"

# These are tied to the input schema.
INPUT_JOB_ID_KEY = "job_id"
INPUT_GRANULE_ID_KEY = "granule_id"
INPUT_FILENAME_KEY = "filename"
INPUT_SOURCE_KEY_KEY = "source_key"
INPUT_TARGET_KEY_KEY = "target_key"
INPUT_TARGET_BUCKET_KEY = "restore_destination"
INPUT_SOURCE_BUCKET_KEY = "source_bucket"

LOGGER = CumulusLogger()


class CopyRequestError(Exception):
    """
    Exception to be raised if the copy request fails for any of the files.
    """


def task(
        records: List[Dict[str, Any]],
        max_retries: int,
        retry_sleep_secs: float,
        db_queue_url: str,
        multipart_chunksize_mb: float
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
        db_queue_url: The URL of the queue that posts status entries.
        multipart_chunksize_mb: The maximum size of chunks to use when copying.
    Raises:
        CopyRequestError: Thrown if there are errors with the input records or the copy failed.
    """
    files = get_files_from_records(records)
    s3 = boto3.client("s3")  # pylint: disable-msg=invalid-name
    for attempt in range(1, max_retries + 1):
        for a_file in files:
            # All files from get_files_from_records start with 'success' == False.
            if not a_file[FILE_SUCCESS_KEY]:
                err_msg = copy_object(
                    s3,
                    a_file[INPUT_SOURCE_BUCKET_KEY],
                    a_file[INPUT_SOURCE_KEY_KEY],
                    a_file[INPUT_TARGET_BUCKET_KEY],
                    multipart_chunksize_mb,
                    a_file[INPUT_TARGET_KEY_KEY],
                )
                if err_msg is None:
                    a_file[FILE_SUCCESS_KEY] = True
                    shared_recovery.update_status_for_file(
                        a_file[INPUT_JOB_ID_KEY],
                        a_file[INPUT_GRANULE_ID_KEY],
                        a_file[INPUT_FILENAME_KEY],
                        shared_recovery.OrcaStatus.SUCCESS,
                        None,
                        db_queue_url,
                    )
                else:
                    a_file[FILE_ERROR_MESSAGE_KEY] = err_msg

        if attempt < max_retries + 1:  # Only sleep if not on the last attempt.
            if all(
                a_file[FILE_SUCCESS_KEY] for a_file in files
            ):  # Check for early completion
                break
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
                db_queue_url,
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
    with open("schemas/sub_schemas/body.json", "r") as raw_schema:
        schema = json.loads(raw_schema.read())

    validate = fastjsonschema.compile(schema)
    files = []
    for record in records:
        a_file = json.loads(record["body"])
        LOGGER.debug("Validating {file}", file=a_file)
        validate(a_file)
        a_file[FILE_SUCCESS_KEY] = False
        files.append(a_file)
    return files


def copy_object(
        s3_cli: BaseClient,
        src_bucket_name: str,
        src_object_name: str,
        dest_bucket_name: str,
        multipart_chunksize_mb: float,
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
        s3_cli.copy(
            copy_source, dest_bucket_name, dest_object_name,
            ExtraArgs={
                # 'StorageClass': 'GLACIER',
                # 'MetadataDirective': 'COPY',
                # 'ContentType': s3_cli.head_object(Bucket=src_bucket_name, Key=src_object_name)['ContentType'],
                # 'ACL': 'bucket-owner-full-control'
                # Sets the x-amz-acl URI Request Parameter. Needed for cross-OU copies.
            },
            Config=TransferConfig(multipart_chunksize=multipart_chunksize_mb * MB)
        )
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
        db_queue_url = str(os.environ[OS_ENVIRON_DB_QUEUE_URL_KEY])
    except KeyError as key_error:
        LOGGER.error(f"{OS_ENVIRON_DB_QUEUE_URL_KEY} environment value not found.")
        raise key_error
    LOGGER.debug("event: {event}", event=event)
    records = event["Records"]

    try:
        multipart_chunksize_mb = float(event['input']['config']['collection']
                                       ['multipart_chunksize_mb'])
    except KeyError:
        LOGGER.debug('ORCA_DEFAULT_MULTIPART_CHUNKSIZE_MB environment variable is not set.')
        multipart_chunksize_mb = float(os.environ['ORCA_DEFAULT_MULTIPART_CHUNKSIZE_MB'])

    task(records, retries, retry_sleep_secs, db_queue_url, multipart_chunksize_mb)
