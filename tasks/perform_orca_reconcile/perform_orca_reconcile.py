"""
Name: perform_orca_reconcile.py

Description: Compares entries in reconcile_s3_objects to the Orca catalog,
writing differences to reconcile_catalog_mismatch_report,
reconcile_orphan_report, and reconcile_phantom_report.
"""
import functools
import json
import os
import random
import time
from typing import Any, Callable, Dict, Union

import boto3
import fastjsonschema
from cumulus_logger import CumulusLogger
from orca_shared.database import shared_db
from orca_shared.database.shared_db import RT
from orca_shared.reconciliation import OrcaStatus, update_job
from sqlalchemy import text
from sqlalchemy.future import Engine

OS_ENVIRON_INTERNAL_REPORT_QUEUE_URL_KEY = "INTERNAL_REPORT_QUEUE_URL"

INPUT_EVENT_KEY = "event"
EVENT_JOB_ID_KEY = "jobId"
EVENT_ORCA_ARCHIVE_LOCATION_KEY = "orcaArchiveLocation"
EVENT_MESSAGE_RECEIPT_HANDLE_KEY = "messageReceiptHandle"

OUTPUT_JOB_ID_KEY = "jobId"

LOGGER = CumulusLogger(name="ORCA")
# Generating schema validators can take time, so do it once and reuse.
try:
    with open("schemas/input.json", "r") as raw_schema:
        _INPUT_VALIDATE = fastjsonschema.compile(json.loads(raw_schema.read()))
    with open("schemas/output.json", "r") as raw_schema:
        _OUTPUT_VALIDATE = fastjsonschema.compile(json.loads(raw_schema.read()))
except Exception as ex:
    LOGGER.error(f"Could not build schema validator: {ex}")
    raise


def task(
    job_id: int,
    orca_archive_location: str,
    internal_report_queue_url: str,
    message_receipt_handle: str,
    db_connect_info: Dict,
) -> Dict[str, Any]:
    """
    Reads the record to find the location of manifest.json,
    then uses that information to spawn of business logic
    for pulling manifest's data into sql.
    Args:
        job_id: The id of the job containing s3 inventory info.
        orca_archive_location: The name of the archive bucket the job targets.
        internal_report_queue_url: The url of the queue containing the message.
        message_receipt_handle: The ReceiptHandle for the event in the queue.
        db_connect_info: See shared_db.py's get_configuration for further details.
    Returns: See output.json for details.
    """

    user_engine = shared_db.get_user_connection(db_connect_info)
    update_job(
        job_id,
        OrcaStatus.GENERATING_REPORTS,
        None,
        user_engine,
    )

    try:
        generate_reports(job_id, orca_archive_location, user_engine)
        update_job(
            job_id,
            OrcaStatus.SUCCESS,
            None,
            user_engine,
        )
    except Exception as fatal_exception:
        # On error, set job status to failure.
        LOGGER.error(f"Encountered a fatal error: {fatal_exception}")
        # noinspection PyArgumentList
        update_job(
            job_id,
            OrcaStatus.ERROR,
            str(fatal_exception),
            user_engine,
        )
        raise
    remove_job_from_queue(internal_report_queue_url, message_receipt_handle)
    return {OUTPUT_JOB_ID_KEY: job_id}


@shared_db.retry_operational_error()
def generate_reports(job_id: int, orca_archive_location: str, engine: Engine) -> None:
    """
    Generates and posts phantom, orphan, and mismatch reports within the same transaction.

    Args:
        job_id: The id of the job containing s3 inventory info.
        orca_archive_location: The name of the bucket to generate the reports for.
        engine: The sqlalchemy engine to use for contacting the database.
    """
    try:
        LOGGER.debug(f"Generating reports for job id {job_id}.")
        with engine.begin() as connection:
            LOGGER.debug(f"Generating phantom reports for job id {job_id}.")
            connection.execute(
                # populate reconcile_phantom_report with files in orca.files
                # but NOT reconcile_s3_object
                generate_phantom_reports_sql(),
                [{"job_id": job_id, "orca_archive_location": orca_archive_location}],
            )
            LOGGER.debug(f"Generating orphan reports for job id {job_id}.")
            connection.execute(
                # populate reconcile_orphan_report with files in reconcile_s3_object
                # but NOT orca.files
                generate_orphan_reports_sql(),
                [{"job_id": job_id, "orca_archive_location": orca_archive_location}],
            )
            LOGGER.debug(f"Generating mismatch reports for job id {job_id}.")
            connection.execute(
                # populate reconcile_orphan_report with files in reconcile_s3_object and orca.files
                # but with differences.
                generate_mismatch_reports_sql(),
                [{"job_id": job_id, "orca_archive_location": orca_archive_location}],
            )
    except Exception as sql_ex:
        LOGGER.error(f"Error while generating reports for job {job_id}: {sql_ex}")
        raise


def generate_phantom_reports_sql() -> text:  # pragma: no cover
    """
    SQL for generating reports on files in the Orca catalog, but not S3.
    """
    return text(
        """
        WITH
            phantom_files AS
            (
                SELECT
                    files.granule_id,
                    files.name,
                    files.key_path,
                    files.etag,
                    files.size_in_bytes,
                    files.storage_class_id

                FROM
                    files
                LEFT OUTER JOIN reconcile_s3_object USING
                (
                    orca_archive_location, key_path
                )
                WHERE
                    files.orca_archive_location = :orca_archive_location AND
                    reconcile_s3_object.key_path IS NULL
            ),
            phantom_reports AS
            (
                SELECT
                    granule_id,
                    collection_id,
                    name,
                    key_path,
                    etag,
                    last_update,
                    size_in_bytes,
                    cumulus_granule_id,
                    storage_class_id
                FROM
                    phantom_files
                INNER JOIN granules ON
                (
                    phantom_files.granule_id=granules.id
                )
            )
        INSERT INTO reconcile_phantom_report
        (
            job_id,
            collection_id,
            granule_id,
            filename,
            key_path,
            orca_etag,
            orca_last_update,
            orca_size,
            orca_storage_class_id
        )
        SELECT
            :job_id,
            collection_id,
            cumulus_granule_id,
            name,
            key_path,
            etag,
            last_update,
            size_in_bytes,
            storage_class_id
        FROM
            phantom_reports"""
    )


def generate_orphan_reports_sql() -> text:  # pragma: no cover
    """
    SQL for generating reports on files in S3, but not the Orca catalog.
    """
    return text(
        """
        WITH
            orphan_reports AS
            (
                SELECT
                    reconcile_s3_object.key_path,
                    reconcile_s3_object.etag,
                    reconcile_s3_object.last_update,
                    reconcile_s3_object.size_in_bytes,
                    reconcile_s3_object.storage_class
                FROM
                    reconcile_s3_object
                LEFT OUTER JOIN files USING
                (
                    orca_archive_location, key_path
                )
                WHERE
                    reconcile_s3_object.orca_archive_location = :orca_archive_location AND
                    files.key_path IS NULL
            )
        INSERT INTO reconcile_orphan_report
        (
            job_id,
            key_path,
            etag,
            last_update,
            size_in_bytes,
            storage_class
        )
            SELECT
                :job_id,
                key_path,
                etag,
                last_update,
                size_in_bytes,
                storage_class
            FROM
                orphan_reports"""  # noqa
    )


def generate_mismatch_reports_sql() -> text:  # pragma: no cover
    """
    SQL for retrieving mismatches between entries in S3 and the Orca catalog.
    """
    return text(
        """
        INSERT INTO orca.reconcile_catalog_mismatch_report
        (
            job_id,
            collection_id,
            granule_id,
            filename,
            key_path,
            cumulus_archive_location,
            orca_etag,
            s3_etag,
            orca_last_update,
            s3_last_update,
            orca_size_in_bytes,
            s3_size_in_bytes,
            orca_storage_class_id,
            s3_storage_class,
            discrepancy_type
        )
        SELECT
            :job_id,
            granules.collection_id,
            granules.cumulus_granule_id AS granule_id,
            files.name AS filename,
            files.key_path,
            files.cumulus_archive_location,
            files.etag AS orca_etag,
            reconcile_s3_object.etag AS s3_etag,
            granules.last_update AS orca_last_update,
            reconcile_s3_object.last_update AS s3_last_update,
            files.size_in_bytes AS orca_size_in_bytes,
            reconcile_s3_object.size_in_bytes AS s3_size_in_bytes,
            files.storage_class_id AS orca_storage_class_id,
            reconcile_s3_object.storage_class AS s3_storage_class,
            CASE
                WHEN (files.etag != reconcile_s3_object.etag AND
                    files.size_in_bytes != reconcile_s3_object.size_in_bytes AND
                    storage_class.value != reconcile_s3_object.storage_class)
                    THEN 'etag, size_in_bytes, storage_class'
                WHEN (files.etag != reconcile_s3_object.etag AND
                    files.size_in_bytes != reconcile_s3_object.size_in_bytes)
                    THEN 'etag, size_in_bytes'
                WHEN files.etag != reconcile_s3_object.etag AND
                    storage_class.value != reconcile_s3_object.storage_class
                    THEN 'etag, storage_class'
                WHEN files.size_in_bytes != reconcile_s3_object.size_in_bytes AND
                    storage_class.value != reconcile_s3_object.storage_class
                    THEN 'size_in_bytes, storage_class'
                WHEN files.etag != reconcile_s3_object.etag
                    THEN 'etag'
                WHEN files.size_in_bytes != reconcile_s3_object.size_in_bytes
                    THEN 'size_in_bytes'
                WHEN storage_class.value != reconcile_s3_object.storage_class
                    THEN 'storage_class'
                ELSE 'UNKNOWN'
            END AS discrepancy_type
        FROM
            reconcile_s3_object
        INNER JOIN files USING
        (
            orca_archive_location, key_path
        )
        INNER JOIN granules ON
        (
            files.granule_id=granules.id
        )
        INNER JOIN storage_class ON
        (
            storage_class_id=storage_class.id
        )
        WHERE
            reconcile_s3_object.orca_archive_location = :orca_archive_location
            AND
            (
                files.etag != reconcile_s3_object.etag OR
                files.size_in_bytes != reconcile_s3_object.size_in_bytes OR
                storage_class.value != reconcile_s3_object.storage_class
            )"""  # noqa
    )


# copied from shared_db.py
# Retry decorator for functions
def retry_error(
    max_retries: int = 3,
    backoff_in_seconds: int = 1,
    backoff_factor: int = 2,
) -> Callable[[Callable[[], RT]], Callable[[], RT]]:
    """
    Decorator takes arguments to adjust number of retries and backoff strategy.
    Args:
        max_retries (int): number of times to retry in case of failure.
        backoff_in_seconds (int): Number of seconds to sleep the first time through.
        backoff_factor (int): Value of the factor used for backoff.
    """

    def decorator_retry_error(func: Callable[[], RT]) -> Callable[[], RT]:
        """
        Main Decorator that takes our function as an argument
        """

        @functools.wraps(func)  # Use built in for decorators
        def wrapper_retry_error(*args, **kwargs) -> RT:
            """
            Wrapper that performs our extra tasks on the function
            """
            # Initialize the retry loop
            total_retries = 0

            # Enter loop
            while True:
                # Try the function and catch the expected error
                try:
                    return func(*args, **kwargs)
                except Exception:
                    if total_retries == max_retries:
                        # Log it and re-raise if we maxed our retries + initial attempt
                        LOGGER.error(
                            "Encountered Errors {total_attempts} times. Reached max retry limit.",
                            total_attempts=total_retries,
                        )
                        raise
                    else:
                        # perform exponential delay
                        backoff_time = (
                            backoff_in_seconds * backoff_factor ** total_retries
                            + random.uniform(0, 1)  # nosec
                        )
                        LOGGER.error(
                            f"Encountered Error on attempt {total_retries}. "
                            f"Sleeping {backoff_time} seconds."
                        )
                        time.sleep(backoff_time)
                        total_retries += 1

        # Return our wrapper
        return wrapper_retry_error

    # Return our decorator
    return decorator_retry_error


@retry_error()
def remove_job_from_queue(internal_report_queue_url: str, message_receipt_handle: str):
    """
    Removes the completed job from the queue, preventing it from going to the dead-letter queue.

    Args:
        internal_report_queue_url: The url of the queue containing the message.
        message_receipt_handle: The ReceiptHandle for the event in the queue.
    """
    aws_client_sqs = boto3.client("sqs")
    LOGGER.debug(
        f"Deleting message '{message_receipt_handle}' from queue '{internal_report_queue_url}'")
    # Remove message from the queue we are listening to.
    aws_client_sqs.delete_message(
        QueueUrl=internal_report_queue_url,
        ReceiptHandle=message_receipt_handle,
    )


def handler(
    event: Dict[str, Dict[str, Dict[str, Union[str, int]]]], context
) -> Dict[str, Any]:
    """
    Lambda handler. Receives a list of s3 events from an SQS queue,
    and loads the s3 inventory specified into postgres.
    Args:
        event: See input.json for details.
        context: An object passed through by AWS. Used for tracking.
    Environment Vars:
        INTERNAL_REPORT_QUEUE_URL (string):
            The URL of the SQS queue the job came from.
        DB_CONNECT_INFO_SECRET_ARN (string):
            Secret ARN of the AWS secretsmanager secret for connecting to the database.
        See shared_db.py's get_configuration for further details.
    Returns: See output.json for details.
    """
    LOGGER.setMetadata(event, context)

    _INPUT_VALIDATE(event)

    try:
        internal_report_queue_url = str(
            os.environ[OS_ENVIRON_INTERNAL_REPORT_QUEUE_URL_KEY]
        )
    except KeyError as key_error:
        LOGGER.error(
            f"{OS_ENVIRON_INTERNAL_REPORT_QUEUE_URL_KEY} environment value not found."
        )
        raise key_error
    # get the secret ARN from the env variable
    try:
        db_connect_info_secret_arn = os.environ["DB_CONNECT_INFO_SECRET_ARN"]
    except KeyError:
        LOGGER.error("DB_CONNECT_INFO_SECRET_ARN environment value not found.")
        raise

    inner_event = event[INPUT_EVENT_KEY]
    job_id = inner_event[EVENT_JOB_ID_KEY]
    orca_archive_location = inner_event[EVENT_ORCA_ARCHIVE_LOCATION_KEY]
    message_receipt_handle = inner_event[EVENT_MESSAGE_RECEIPT_HANDLE_KEY]

    db_connect_info = shared_db.get_configuration(db_connect_info_secret_arn)

    result = task(
        job_id,
        orca_archive_location,
        internal_report_queue_url,
        message_receipt_handle,
        db_connect_info,
    )
    _OUTPUT_VALIDATE(result)
    return result
