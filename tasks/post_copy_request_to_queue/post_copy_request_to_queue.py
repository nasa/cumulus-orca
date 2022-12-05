"""
Name: post_copy_request_to_queue.py
Description:  lambda function that queries the db for file metadata, updates the status
of recovered file to staged,
and sends the staged file info to staged_recovery queue for further processing.
"""
import json
import os
import random
import time
from typing import Any, Dict, List

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from orca_shared.database import shared_db
from orca_shared.database.shared_db import retry_operational_error
from orca_shared.recovery import shared_recovery
from sqlalchemy import text

OS_ENVIRON_RECOVERY_QUEUE_URL_KEY = "RECOVERY_QUEUE_URL"
OS_ENVIRON_STATUS_UPDATE_QUEUE_URL_KEY = "STATUS_UPDATE_QUEUE_URL"
OS_ENVIRON_MAX_RETRIES_KEY = "MAX_RETRIES"
OS_ENVIRON_RETRY_SLEEP_SECS_KEY = "RETRY_SLEEP_SECS"
OS_ENVIRON_RETRY_BACKOFF_KEY = "RETRY_BACKOFF"
OS_ENVIRON_DB_CONNECT_INFO_SECRET_ARN_KEY = "DB_CONNECT_INFO_SECRET_ARN"  # nosec

JOB_ID_KEY = "jobId"
GRANULE_ID_KEY = "granuleId"
FILENAME_KEY = "filename"
RESTORE_DESTINATION_KEY = "restoreDestination"
MULTIPART_CHUNKSIZE_MB_KEY = "s3MultipartChunksizeMb"
SOURCE_KEY_KEY = "sourceKey"
TARGET_KEY_KEY = "targetKey"
SOURCE_BUCKET_KEY = "sourceBucket"

# Set AWS powertools logger
LOGGER = Logger()


def task(
    key_path: str,
    bucket_name: str,
    status_update_queue_url: str,
    recovery_queue_url: str,
    max_retries: int,
    retry_sleep_secs: int,
    retry_backoff: int,
    db_connect_info_secret_arn: str,
) -> None:
    """
    Task called by the handler to perform the work.
    This task queries all entries from orca_recoverfile table
    that match the given filename and whose status_id is 'PENDING'.
    The result is then sent to the staged-recovery-queue SQS and status-update-queue SQS.
    Args:
        key_path:
           Full AWS key path including file name of the file where the file resides.
        bucket_name: Name of the source S3 bucket.
        status_update_queue_url: The SQS URL of status_update_queue
        recovery_queue_url: The SQS URL of staged_recovery_queue
        max_retries: Number of times the code will retry in case of failure.
        retry_sleep_secs: Number of seconds to wait between recovery failure retries.
        retry_backoff: The multiplier by which the retry interval increases during each attempt.
        db_connect_info_secret_arn: Secret ARN of the secretsmanager secret to connect to the DB.
    Returns:
        None
    Raises:
        Exception: If unable to retrieve key_path or db parameters, convert db result to json,
        or post to queue.
    """
    rows = query_db(key_path, bucket_name, db_connect_info_secret_arn)

    my_base_delay = retry_sleep_secs

    # Iterate through the records. Usually we expect only 1, but we could get multiple.
    for row in rows:
        # Get the values needed for the call to update the status
        job_id = row[JOB_ID_KEY]
        granule_id = row[GRANULE_ID_KEY]
        filename = row[FILENAME_KEY]

        # Make sure we update the status, retry if we fail.
        for attempt in range(max_retries + 1):
            try:
                shared_recovery.update_status_for_file(
                    job_id,
                    granule_id,
                    filename,
                    shared_recovery.OrcaStatus.STAGED,
                    None,
                    status_update_queue_url,
                )
                break
            except Exception as ex:
                LOGGER.error(
                    f"Ran into error posting to SQS {status_update_queue_url} {attempt+1} "
                    f"time(s) with exception {ex}",
                )
                if attempt < max_retries:
                    my_base_delay = exponential_delay(my_base_delay, retry_backoff)
                continue
        else:
            message = f"Error sending message to status_update_queue_url for {row}"
            LOGGER.critical(message)
            raise Exception(message)

        # resetting my_base_delay
        my_base_delay = retry_sleep_secs

        # Post to recovery queue so data is copied back to proper Cumulus
        # primary location. Retry using exponential delay if it fails.
        for attempt in range(max_retries + 1):
            try:
                shared_recovery.post_entry_to_standard_queue(row, recovery_queue_url)
                break
            except Exception as ex:
                LOGGER.error(
                    f"Ran into error posting to SQS {recovery_queue_url} {attempt+1} "
                    f"time(s) with exception {ex}"
                )
                if attempt < max_retries:
                    my_base_delay = exponential_delay(my_base_delay, retry_backoff)
                continue
        else:
            message = f"Error sending message to recovery_queue_url for {row}"
            LOGGER.critical(message)
            raise Exception(message)


# Define our exponential delay function
# maybe move to shared library or somewhere else?
def exponential_delay(base_delay: int, exponential_backoff: int = 2) -> int:
    """
    Exponential delay function. This function is used for retries during failure.
    Args:
        base_delay:
            Number of seconds to wait between recovery failure retries.
        exponential_backoff:
            The multiplier by which the retry interval increases during each attempt.
    Returns:
        An integer which is multiplication of base_delay and exponential_backoff.
    Raises:
        None
    """
    try:
        base_delay = int(base_delay)
        exponential_backoff = int(exponential_backoff)
    except ValueError as ve:
        LOGGER.error(f"arguments are not integer. Raised ValueError: {ve}")
        raise ve

    random_addition = random.randint(0, 1000) / 1000.0  # nosec
    delay = base_delay + random_addition
    LOGGER.debug(f"Performing back off retry sleeping {delay} seconds")
    time.sleep(delay)
    return base_delay * exponential_backoff


@retry_operational_error()
def query_db(
    key_path: str, bucket_name: str, db_connect_info_secret_arn: str
) -> List[Dict[str, str]]:
    """
    Connect and query the recover_file status table return needed
    metadata for posting to the recovery status SQS Queue.

    Args:
        key_path:
           Full AWS key path including file name of the file where the file resides.
        bucket_name:
            Name of the source S3 bucket.
        db_connect_info_secret_arn:
            Secret ARN of the secretsmanager secret to connect to the DB.
    Returns:
        A list of dict containing the following keys, matching the input
        format from copy_from_archive:
            "jobId" (str):
            "granuleId"(str):
            "filename" (str):
            "restoreDestination" (str):
            "s3MultipartChunksizeMb" (str):
            "sourceKey" (str):
            "targetKey" (str):
            "sourceBucket" (str):
    Raises:
        Exception: If unable to retrieve the metadata by querying the DB.
    """

    # Query the database and get the needed metadata to send to the SQS Queue
    # for the copy_from_archive lambda and to update the status in the
    # database.
    try:
        LOGGER.debug("Getting database connection information.")
        db_connect_info = shared_db.get_configuration(db_connect_info_secret_arn)
        LOGGER.debug("Retrieved the database connection info")

        engine = shared_db.get_user_connection(db_connect_info)
        LOGGER.debug(f"Querying database for metadata on {key_path}")

        # It is possible to have multiple returns, so we capture all of
        # them to update status
        rows = []
        with engine.begin() as connection:
            # Query for all rows that contain that key and have a status of
            # PENDING
            for row in connection.execute(
                get_metadata_sql(),
                {
                    "key_path": key_path,
                    "status_id": shared_recovery.OrcaStatus.PENDING.value
                }
            ):
                # Create dictionary for with the info needed for the
                # copy_from_archive lambda
                row_dict = {
                    JOB_ID_KEY:
                        row[0],
                    GRANULE_ID_KEY:
                        row[1],
                    FILENAME_KEY:
                        row[2],
                    RESTORE_DESTINATION_KEY:
                        row[3],
                    MULTIPART_CHUNKSIZE_MB_KEY:
                        row[4],
                    SOURCE_KEY_KEY:
                        key_path,
                    TARGET_KEY_KEY:
                        key_path,  # todo add a card to configure targetKey in the future
                    SOURCE_BUCKET_KEY:
                        bucket_name,  # todo add to database and retrieve. ORCA-351
                }
                rows.append(row_dict)

        # Check to make sure we found some metadata
        if len(rows) == 0:
            message = f"No metadata found for {key_path}"
            LOGGER.fatal(message)
            raise Exception(message)

    except Exception as ex:
        message = (
            f"Unable to retrieve {key_path} metadata. Exception '{ex}' encountered."
        )
        LOGGER.error(message, exc_info=True)
        raise Exception(message.format(key_path=key_path, ex=ex))
    return rows


def get_metadata_sql() -> text:
    """
    Query for finding metadata based on key_path and status_id.

    Args:
        None
    Returns:
        (sqlalchemy.text): SQL statement
    """
    return text(
        """
            SELECT
                job_id, granule_id, filename, restore_destination, multipart_chunksize_mb
            FROM
                recovery_file
            WHERE
                key_path = :key_path
            AND
                status_id = :status_id
        """
    )


@LOGGER.inject_lambda_context
def handler(event: Dict[str, Any], context: LambdaContext) -> None:
    """
    Lambda handler. This lambda calls the task function to perform db queries
    and send message to SQS.

    Environment Vars:
        RECOVERY_QUEUE_URL (string):
            the SQS URL for staged_recovery_queue
        DB_QUEUE_URL (string):
            the SQS URL for status-update-queue
        MAX_RETRIES (string):
            Number of times the code will retry in case of failure.
        RETRY_SLEEP_SECS (string):
            Number of seconds to wait between recovery failure retries.
        RETRY_BACKOFF (string):
            The multiplier by which the retry interval increases during each attempt.
        DB_CONNECT_INFO_SECRET_ARN (string):
            Secret ARN of the AWS secretsmanager secret for connecting to the database.
    Args:
        event:
            A dictionary from the S3 bucket. See schemas/input.json for more information.
        context: This object provides information about the lambda invocation, function,
            and execution env.
    Returns:
        None
    Raises:
        Exception: If unable to retrieve the SQS URLs or
            exponential retry fields from env variables.
    """
    # retrieving values from the env variables
    backoff_env = [  # This order must exactly match the parameters in task.
        OS_ENVIRON_STATUS_UPDATE_QUEUE_URL_KEY,
        OS_ENVIRON_RECOVERY_QUEUE_URL_KEY,
        OS_ENVIRON_MAX_RETRIES_KEY,
        OS_ENVIRON_RETRY_SLEEP_SECS_KEY,
        OS_ENVIRON_RETRY_BACKOFF_KEY,
        OS_ENVIRON_DB_CONNECT_INFO_SECRET_ARN_KEY,
    ]
    environment_args = []
    for var in backoff_env:
        env_var_value = os.getenv(var, None)
        if env_var_value is None or len(env_var_value) == 0:
            message = f"{var} is not set and is required"
            LOGGER.critical(message)
            raise Exception(message)

        if var in [
            OS_ENVIRON_MAX_RETRIES_KEY,
            OS_ENVIRON_RETRY_SLEEP_SECS_KEY,
            OS_ENVIRON_RETRY_BACKOFF_KEY,
        ]:
            try:
                env_var_value = int(env_var_value)
            except ValueError:
                error = ValueError(f"{var} must be set to an integer.")
                LOGGER.critical(error)
                raise error
        environment_args.append(env_var_value)

    records = event["Records"]
    if len(records) != 1:
        raise ValueError(f"Must be passed as a single record. Was {len(records)}")
    record = records[0]
    LOGGER.debug(f"Event passed = {event}")

    # pull the body out & json load it
    record_json = json.loads(record["body"])

    # AWS definitions are loose, hence looping is used to capture more than 1 record if present
    for s3_record in record_json["Records"]:
        # grab the key_path and bucket name from record
        key_path = s3_record["s3"]["object"]["key"]
        bucket_name = s3_record["s3"]["bucket"]["name"]
        # calling the task function to perform the work
        task(key_path, bucket_name, *environment_args)
