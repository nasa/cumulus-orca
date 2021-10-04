"""
Name: post_copy_request_to_queue.py
Description:  lambda function that queries the db for file metadata, updates the status
of recovered file to staged,
and sends the staged file info to staged_recovery queue for further processing.

"""
import os
from typing import Dict, Any
import time
import random

from orca_shared.recovery import shared_recovery
from orca_shared.database import shared_db

from cumulus_logger import CumulusLogger
from sqlalchemy import text

# instantiate CumulusLogger
LOGGER = CumulusLogger()


def task(
    record: Dict[str, Any],
    db_queue_url: str,
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
        record: A dictionary passed through from the handler.
        db_queue_url: The SQS URL of status_update_queue
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
    # grab the key_path and bucket name from event
    # We only expect one record from the event.
    key_path = record["s3"]["object"]["key"]
    bucket_name = record["s3"]["bucket"]["name"]

    # Query the database and get the needed metadata to send to the SQS Queue
    # for the copy_files_to_archive lambda and to update the status in the
    # database.
    try:
        LOGGER.debug("Getting database connection information.")
        db_connect_info = shared_db.get_configuration()
        LOGGER.debug(
            "Retrieved the following database connection info {info}",
            info=db_connect_info,
        )

        engine = shared_db.get_user_connection(db_connect_info)
        LOGGER.debug("Querying database for metadata on {path}", path=key_path)

        # It is possible to have multiple returns so we want to capture all of
        # them to update status
        rows = []
        with engine.begin() as connection:
            # Query for all rows that contain that key and have a status of
            # PENDING
            for row in connection.execute(get_metadata_sql(key_path)):
                # Create dictionary for with the info needed for the
                # copy_files_to_archive lambda
                row_dict = {
                    "job_id": row[0],
                    "granule_id": row[1],
                    "filename": row[2],
                    "restore_destination": row[3],
                    "multipart_chunksize_mb": row[4],
                    "source_key": key_path,
                    "target_key": key_path,  # todo add a card to configure target_key in the future
                    "source_bucket": bucket_name,
                }
                rows.append(row_dict)

        # Check to make sure we found some metadata
        if len(rows) == 0:
            message = f"No metadata found for {key_path}"
            LOGGER.fatal(message)
            raise Exception(message)

    except Exception as ex:
        message = "Unable to retrieve {key_path} metadata. Exception {ex} encountered."
        LOGGER.error(message, key_path=key_path, ex=ex, exc_info=True)
        raise Exception(message.format(key_path=key_path, ex=ex))

    my_base_delay = retry_sleep_secs

    # Iterate through the records. Usually we expect only 1 but we could get
    # multiple.
    for record in rows:
        # Get the values needed for the call to update the status
        job_id = record["job_id"]
        granule_id = record["granule_id"]
        filename = record["filename"]

        # Make sure we update the status, retry if we fail.
        for retry in range(max_retries + 1):
            try:
                shared_recovery.update_status_for_file(
                    job_id,
                    granule_id,
                    filename,
                    shared_recovery.OrcaStatus.STAGED,
                    None,
                    db_queue_url,
                )
                break
            except Exception as ex:
                # Can't use f"" because of '{}' bug in CumulusLogger.
                LOGGER.error(
                    "Ran into error posting to SQS {db_queue_url} {retry} time(s) with exception {ex}",
                    db_queue_url=db_queue_url,
                    retry=retry + 1,
                    ex=str(ex),
                )
                my_base_delay = exponential_delay(my_base_delay, retry_backoff)
                continue
        else:
            message = "Error sending message to db_queue_url for {record}"
            LOGGER.critical(
                message, new_data=str(record)
            )  # Cumulus will update this library in the future to be better behaved.
            raise Exception(message.format(record=str(record)))

        # resetting my_base_delay
        my_base_delay = retry_sleep_secs

        # Post to recovery queue so data is copied back to proper Cumulus
        # primary location. Retry using exponential delay if it fails.
        for retry in range(max_retries + 1):
            try:
                shared_recovery.post_entry_to_queue(
                    record, shared_recovery.RequestMethod.NEW_JOB, recovery_queue_url
                )
                break
            except Exception as ex:
                # Can't use f"" because of '{}' bug in CumulusLogger.
                LOGGER.error(
                    "Ran into error posting to SQS {recovery_queue_url} {retry} time(s) with exception {ex}",
                    recovery_queue_url=recovery_queue_url,
                    retry=retry + 1,
                    ex=str(ex),
                )
                my_base_delay = exponential_delay(my_base_delay, retry_backoff)
                continue
        else:
            message = "Error sending message to recovery_queue_url for {new_data}"
            LOGGER.critical(
                message, new_data=str(record)
            )  # Cumulus will update this library in the future to be better behaved.
            raise Exception(message.format(new_data=str(record)))


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
        _base_delay = int(base_delay)
        _exponential_backoff = int(exponential_backoff)
        delay = _base_delay + (random.randint(0, 1000) / 1000.0)  # nosec
        LOGGER.debug(f"Performing back off retry sleeping {delay} seconds")
        time.sleep(delay)
        return _base_delay * _exponential_backoff
    except ValueError as ve:
        # Can't use f"" because of '{}' bug in CumulusLogger.
        LOGGER.error("arguments are not integer. Raised ValueError: {ve}", ve=ve)
        raise ve


def handler(event: Dict[str, Any], context: None) -> None:
    """
    Lambda handler. This lambda calls the task function to perform db queries
    and send message to SQS.

        Environment Vars:
            PREFIX (string): the prefix
            DATABASE_PORT (string): the database port. The standard is 5432.
            DATABASE_NAME (string): the name of the database.
            DATABASE_USER (string): the name of the application user.
            DB_QUEUE_URL (string): the SQS URL for status-update-queue
            RECOVERY_QUEUE_URL (string): the SQS URL for staged_recovery_queue
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
    backoff_env = [
        "DB_QUEUE_URL",
        "RECOVERY_QUEUE_URL",
        "MAX_RETRIES",
        "RETRY_SLEEP_SECS",
        "RETRY_BACKOFF",
    ]
    backoff_args = []
    for var in backoff_env:
        env_var_value = os.getenv(var, None)
        if env_var_value is None or len(env_var_value) == 0:
            message = f"{var} is not set and is required"
            LOGGER.critical(message)
            raise Exception(message)

        if var in ["MAX_RETRIES", "RETRY_SLEEP_SECS", "RETRY_BACKOFF"]:
            try:
                env_var_value = int(env_var_value)
            except ValueError as ve:
                LOGGER.critical(f"{var} must be set to an integer.")
                raise ve
        backoff_args.append(env_var_value)

    record = event["Records"][0]
    LOGGER.debug("Event passed = {event}", event=event)
    # calling the task function to perform the work
    task(record, *backoff_args)
