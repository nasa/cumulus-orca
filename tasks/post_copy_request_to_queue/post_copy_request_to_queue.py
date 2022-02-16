"""
Name: post_copy_request_to_queue.py
Description:  lambda function that queries the db for file metadata, updates the status
of recovered file to staged,
and sends the staged file info to staged_recovery queue for further processing.
"""
import os
from typing import Dict, List, Any
import time
import random

from orca_shared.recovery import shared_recovery
from orca_shared.database import shared_db
from orca_shared.database.shared_db import retry_operational_error
from cumulus_logger import CumulusLogger
from sqlalchemy import text

OS_ENVIRON_RECOVERY_QUEUE_URL_KEY = "RECOVERY_QUEUE_URL"
OS_ENVIRON_STATUS_UPDATE_QUEUE_URL_KEY = "STATUS_UPDATE_QUEUE_URL"
OS_ENVIRON_MAX_RETRIES_KEY = "MAX_RETRIES"
OS_ENVIRON_RETRY_SLEEP_SECS_KEY = "RETRY_SLEEP_SECS"
OS_ENVIRON_RETRY_BACKOFF_KEY = "RETRY_BACKOFF"

JOB_ID_KEY = "jobId"
GRANULE_ID_KEY = "granuleId"
FILENAME_KEY = "filename"
RESTORE_DESTINATION_KEY = "restoreDestination"
MULTIPART_CHUNKSIZE_MB_KEY = "s3MultipartChunksizeMb"
SOURCE_KEY_KEY = "sourceKey"
TARGET_KEY_KEY = "targetKey"
SOURCE_BUCKET_KEY = "sourceBucket"

# instantiate CumulusLogger
LOGGER = CumulusLogger()


def task(
    key_path: str,
    bucket_name: str,
    status_update_queue_url: str,
    recovery_queue_url: str,
    max_retries: int,
    retry_sleep_secs: int,
    retry_backoff: int,
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
    Returns:
        None
    Raises:
        Exception: If unable to retrieve key_path or db parameters, convert db result to json,
        or post to queue.
    """
    rows = query_db(key_path, bucket_name)

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
                # Can't use f"" because of '{}' bug in CumulusLogger.
                LOGGER.error(
                    "Ran into error posting to SQS {status_update_queue_url} {attempt} time(s) with exception {ex}",
                    status_update_queue_url=status_update_queue_url,
                    attempt=attempt + 1,
                    ex=str(ex),
                )
                if attempt < max_retries:
                    my_base_delay = exponential_delay(my_base_delay, retry_backoff)
                continue
        else:
            message = "Error sending message to status_update_queue_url for {row}"
            LOGGER.critical(
                message, new_data=str(row)
            )  # Cumulus will update this library in the future to be better behaved.
            raise Exception(message.format(row=str(row)))

        # resetting my_base_delay
        my_base_delay = retry_sleep_secs

        # Post to recovery queue so data is copied back to proper Cumulus
        # primary location. Retry using exponential delay if it fails.
        for attempt in range(max_retries + 1):
            try:
                shared_recovery.post_entry_to_standard_queue(
                    row, recovery_queue_url
                )
                break
            except Exception as ex:
                # Can't use f"" because of '{}' bug in CumulusLogger.
                LOGGER.error(
                    "Ran into error posting to SQS {recovery_queue_url} {attempt} time(s) with exception {ex}",
                    recovery_queue_url=recovery_queue_url,
                    attempt=attempt + 1,
                    ex=str(ex),
                )
                if attempt < max_retries:
                    my_base_delay = exponential_delay(my_base_delay, retry_backoff)
                continue
        else:
            message = "Error sending message to recovery_queue_url for {new_data}"
            LOGGER.critical(
                message, new_data=str(row)
            )  # Cumulus will update this library in the future to be better behaved.
            raise Exception(message.format(new_data=str(row)))


# Define our exponential delay function
# maybe move to shared library or somewhere else?
def exponential_delay(base_delay: int, exponential_backoff: int = 2) -> int:
    """
    Exponential delay function. This function is used for retries during failure.
    Args:
        base_delay: Number of seconds to wait between recovery failure retries.
        exponential_backoff: The multiplier by which the retry interval increases during each attempt.
    Returns:
        An integer which is multiplication of base_delay and exponential_backoff.
    Raises:
        None
    """
    try:
        base_delay = int(base_delay)
        exponential_backoff = int(exponential_backoff)
    except ValueError as ve:
        # Can't use f"" because of '{}' bug in CumulusLogger.
        LOGGER.error("arguments are not integer. Raised ValueError: {ve}", ve=ve)
        raise ve

    random_addition = random.randint(0, 1000) / 1000.0
    delay = base_delay + random_addition
    LOGGER.debug(f"Performing back off retry sleeping {delay} seconds")
    time.sleep(delay)
    return base_delay * exponential_backoff


@retry_operational_error()
def query_db(key_path: str, bucket_name: str) -> List[Dict[str, str]]:
    """
    Connect and query the recover_file status table return needed metadata for posting to the recovery status SQS Queue.

    Args:
        key_path:
           Full AWS key path including file name of the file where the file resides.
        bucket_name: Name of the source S3 bucket.
    Returns:
        A list of dict containing the following keys, matching the input format from copy_files_to_archive:
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
    # for the copy_files_to_archive lambda and to update the status in the
    # database.
    try:
        LOGGER.debug("Getting database connection information.")
        db_connect_info = shared_db.get_configuration()
        LOGGER.debug("Retrieved the database connection info")

        engine = shared_db.get_user_connection(db_connect_info)
        LOGGER.debug("Querying database for metadata on {path}", path=key_path)

        # It is possible to have multiple returns, so we capture all of
        # them to update status
        rows = []
        with engine.begin() as connection:
            # Query for all rows that contain that key and have a status of
            # PENDING
            for row in connection.execute(get_metadata_sql(key_path)):
                # Create dictionary for with the info needed for the
                # copy_files_to_archive lambda
                row_dict = {
                    JOB_ID_KEY: row[0],
                    GRANULE_ID_KEY: row[1],
                    FILENAME_KEY: row[2],
                    RESTORE_DESTINATION_KEY: row[3],
                    MULTIPART_CHUNKSIZE_MB_KEY: row[4],
                    SOURCE_KEY_KEY: key_path,
                    TARGET_KEY_KEY: key_path,  # todo add a card to configure targetKey in the future
                    SOURCE_BUCKET_KEY: bucket_name,  # todo add to database and retrieve. ORCA-351
                }
                rows.append(row_dict)

        # Check to make sure we found some metadata
        if len(rows) == 0:
            message = f"No metadata found for {key_path}"
            LOGGER.fatal(message)
            raise Exception(message)

    except Exception as ex:
        message = "Unable to retrieve {key_path} metadata. Exception '{ex}' encountered."
        LOGGER.error(message, key_path=key_path, ex=ex, exc_info=True)
        raise Exception(message.format(key_path=key_path, ex=ex))
    return rows


def get_metadata_sql(key_path: str) -> text:
    """
    Query for finding metadata based on key_path and PENDING status.

    Args:
        key_path (str): s3 key for the file less the bucket name
    Returns:
        (sqlalchemy.text): SQL statement
    """
    return text(
        f"""
            SELECT
                job_id, granule_id, filename, restore_destination, multipart_chunksize_mb
            FROM
                recovery_file
            WHERE
                key_path = '{key_path}'
            AND
                status_id = {shared_recovery.OrcaStatus.PENDING.value}
        """
    )


def handler(event: Dict[str, Any], context) -> None:
    """
    Lambda handler. This lambda calls the task function to perform db queries
    and send message to SQS.
    
        Environment Vars:
            RECOVERY_QUEUE_URL (string): the SQS URL for staged_recovery_queue
            DB_QUEUE_URL (string): the SQS URL for status-update-queue
            MAX_RETRIES (string): Number of times the code will retry in case of failure.
            RETRY_SLEEP_SECS (string): Number of seconds to wait between recovery failure retries.
            RETRY_BACKOFF (string): The multiplier by which the retry interval increases during each attempt.
            Required by shared_db.get_configuration():
                PREFIX (string): the prefix
                DATABASE_PORT (string): the database port. The standard is 5432.
                DATABASE_NAME (string): the name of the database.
                DATABASE_USER (string): the name of the application user.
        Parameter store:
            {prefix}-drdb-host (string): host name that will be retrieved from secrets manager
            {prefix}-drdb-user-pass (string):db password that will be retrieved from secrets manager
    Args:
        event:
            A dictionary from the S3 bucket. See schemas/input.json for more information.
        context: An object required by AWS Lambda. Unused.
    Returns:
        None
    Raises:
        Exception: If unable to retrieve the SQS URLs or exponential retry fields from env variables.
    """
    LOGGER.setMetadata(event, context)

    # retrieving values from the env variables
    backoff_env = [  # This order must exactly match the parameters in task.
        OS_ENVIRON_STATUS_UPDATE_QUEUE_URL_KEY,
        OS_ENVIRON_RECOVERY_QUEUE_URL_KEY,
        OS_ENVIRON_MAX_RETRIES_KEY,
        OS_ENVIRON_RETRY_SLEEP_SECS_KEY,
        OS_ENVIRON_RETRY_BACKOFF_KEY,
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
            except ValueError as _:
                error = ValueError(f"{var} must be set to an integer.")
                LOGGER.critical(error)
                raise error
        environment_args.append(env_var_value)

    if len(event["Records"]) != 1:
        raise ValueError(f"Must be passed a single record. Was {len(event['Records'])}")
    record = event["Records"][0]
    LOGGER.debug("Event passed = {event}", event=event)
    # grab the key_path and bucket name from record
    key_path = record["s3"]["object"]["key"]
    bucket_name = record["s3"]["bucket"]["name"]
    # calling the task function to perform the work
    task(key_path, bucket_name, *environment_args)