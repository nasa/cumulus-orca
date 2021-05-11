"""
Name: post_copy_request_to_queue.py
Description:  lambda function that queries the db for file metadata, updates the status
of recovered file to staged, and sends the staged file info to staged_recovery queue for further processing.

"""
from enum import Enum
import json
import os
import boto3
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import time
import random
from shared_recovery import (
    OrcaStatus,
    RequestMethod,
    post_status_for_file_to_queue,
    post_entry_to_queue,
)
from requests_db import get_dbconnect_info,DatabaseError
from database import single_query, result_to_json
from cumulus_logger import CumulusLogger
import logging

# instantiate CumulusLogger
LOGGER = CumulusLogger()


def task(
    records: Dict[str, Any],
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
        records: A dictionary passed through from the handler.
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
    # grab the key_path and bucketname from event
    # We only expect one record.
    for record in records:
        key_path = record["s3"]["object"]["key"]
        bucket_name = record["s3"]["bucket"]["name"]

    sql = """
        SELECT
            job_id, granule_id, filename, restore_destination
        FROM
            orca_recoverfile
        WHERE
            key_path = %s
        AND
            status_id = %d
    """
    # Gets the dbconnection info.
    # query the db table
    try:
        db_connect_info = get_dbconnect_info()
        rows = single_query(sql, db_connect_info, (key_path, OrcaStatus.PENDING.value))
        if len(rows) == 0:
            message = f"No metadata found for {key_path}"
            LOGGER.fatal(message)
            raise Exception(message)
        # convert db result to json
        db_result_json = result_to_json(rows)

    except Exception as ex:
        message = f"Unable to retrieve {key_path} metadata"
        LOGGER.error(message)
        raise ex(message)

    # grab the parameters from the db in json format.
    job_id = db_result_json["job_id"]
    granule_id = db_result_json["granule_id"]
    filename = db_result_json["filename"]
    restore_destination = db_result_json["restore_destination"]

    my_base_delay = retry_sleep_secs
    # define the input body for copy_files_to_archive lambda
    new_data = {
        "job_id": job_id,
        "granule_id": granule_id,
        "filename": filename,
        "source_key": key_path,
        "target_key": key_path,  # todo add a card to configure target_key in the future
        "restore_destination": restore_destination,
        "source_bucket": bucket_name,
    }
    # post to recovery queue. Retry using exponential delay if it fails
    for retry in range(max_retries):
        try:
            post_entry_to_queue(
                orca_recoveryfile, new_data, RequestMethod.NEW, recovery_queue_url
            )
        except Exception:
            LOGGER.error(
                f"Ran into error posting to SQS {recovery_queue_url} {retry+1} time(s)"
            )
            my_base_delay = exponential_delay(my_base_delay, retry_backoff)
            continue
        break
    else:
        message = f"Error sending message to {recovery_queue_url} for {new_data}"
        logging.critical(message)
        raise Exception(message)

    # resetting my_base_delay
    my_base_delay = retry_sleep_secs
    # post to DB-queue. Retry using exponential delay if it fails
    for retry in range(max_retries):
        try:
            post_status_for_file_to_queue(
                job_id,
                granule_id,
                filename,
                restore_destination,
                OrcaStatus.STAGED,
                None,
                RequestMethod.UPDATE,
                db_queue_url,
            )
        except Exception:
            LOGGER.error(
                f"Ran into error posting to SQS {db_queue_url} {retry+1} time(s)"
            )
            my_base_delay = exponential_delay(my_base_delay, retry_backoff)
            continue
        break
    else:
        message = f"Error sending message to {db_queue_url} for {new_data}"
        logging.critical(message)
        raise Exception(message)


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
    delay = base_delay + (random.randint(0, 1000) / 1000.0)
    time.sleep(delay)
    LOGGER.debug(f"Performing back off retry sleeping {delay} seconds")
    return base_delay * exponential_backoff


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

    records = event["Records"]
    # calling the task function to perform the work
    task(records, *backoff_args)
