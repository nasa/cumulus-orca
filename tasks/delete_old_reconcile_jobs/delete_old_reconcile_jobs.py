"""
Name: delete_old_reconcile_jobs.py

Description: Deletes old internal reconciliation reports, reducing DB size.
"""
import os
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, Union

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext  # noqa
from orca_shared.database import shared_db
from sqlalchemy import text
from sqlalchemy.future import Engine

OS_ENVIRON_DB_CONNECT_INFO_SECRET_ARN = "DB_CONNECT_INFO_SECRET_ARN"  # nosec
OS_ENVIRON_INTERNAL_RECONCILIATION_EXPIRATION_DAYS = (
    "INTERNAL_RECONCILIATION_EXPIRATION_DAYS"
)

# Set AWS powertools logger
LOGGER = Logger()


def task(
    internal_reconciliation_expiration_days: int,
    db_connect_info: Dict,
) -> None:
    """
    Gets all jobs older than internal_reconciliation_expiration_days days,
    then deletes their records in Postgres.

    Args:
        internal_reconciliation_expiration_days:
            Only reports updated before this many days ago will be deleted.
        db_connect_info: See shared_db.py's get_configuration for further details.
    """

    user_engine = shared_db.get_user_connection(db_connect_info)
    delete_jobs_older_than_x_days(
        internal_reconciliation_expiration_days,
        user_engine,
    )


@shared_db.retry_operational_error()
def delete_jobs_older_than_x_days(
    internal_reconciliation_expiration_days: int, engine: Engine
) -> None:
    """
    Deletes all records for the given job older than
    internal_reconciliation_expiration_days days.

    Args:
        internal_reconciliation_expiration_days:
        Only reports updated before this many days ago will be retrieved.
        engine: The sqlalchemy engine to use for contacting the database.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(
        days=internal_reconciliation_expiration_days
    )
    params = [{"cutoff": cutoff}]
    try:
        LOGGER.debug(
            f"Deleting data for jobs older than {internal_reconciliation_expiration_days} "
            f"days ago, {cutoff} UTC."
        )
        with engine.begin() as connection:
            start = time.perf_counter()
            sql_cursor = connection.execute(
                delete_catalog_mismatches_older_than_x_days_sql(),
                params,
            )
            LOGGER.info(
                f"Deleted {sql_cursor.rowcount} mismatches "
                f"in {time.perf_counter() - start} seconds."
            )
            start = time.perf_counter()
            sql_cursor = connection.execute(
                delete_catalog_orphans_older_than_x_days_sql(),
                params,
            )
            LOGGER.info(
                f"Deleted {sql_cursor.rowcount} orphans in {time.perf_counter() - start} seconds."
            )
            start = time.perf_counter()
            sql_cursor = connection.execute(
                delete_catalog_phantoms_older_than_x_days_sql(),
                params,
            )
            LOGGER.info(
                f"Deleted {sql_cursor.rowcount} phantoms in {time.perf_counter() - start} seconds."
            )
            start = time.perf_counter()
            sql_cursor = connection.execute(
                delete_catalog_s3_objects_older_than_x_days_sql(),
                params,
            )
            LOGGER.info(
                f"Deleted {sql_cursor.rowcount} s3 objects "
                f"in {time.perf_counter() - start} seconds."
            )
            start = time.perf_counter()
            sql_cursor = connection.execute(
                delete_jobs_older_than_x_days_sql(),
                params,
            )
            LOGGER.info(
                f"Deleted {sql_cursor.rowcount} root jobs "
                f"in {time.perf_counter() - start} seconds."
            )

            LOGGER.info("Finished deleting report data. Closing connection.")
    except Exception as sql_ex:
        LOGGER.error(f"Error while deleting jobs: {sql_ex}")
        raise


def delete_catalog_mismatches_older_than_x_days_sql() -> text:  # pragma: no cover
    """
    SQL for deleting from reconcile_catalog_mismatch_report entries older than a certain date.
    """
    return text(
        """
        DELETE
        FROM
            reconcile_catalog_mismatch_report
        WHERE
            job_id IN (
                SELECT
                    id
                FROM
                    reconcile_job
                WHERE
                    last_update < :cutoff
            )"""
    )


def delete_catalog_orphans_older_than_x_days_sql() -> text:  # pragma: no cover
    """
    SQL for deleting from reconcile_orphan_report entries older than a certain date.
    """
    return text(
        """
        DELETE
        FROM
            reconcile_orphan_report
        WHERE
            job_id IN (
                SELECT
                    id
                FROM
                    reconcile_job
                WHERE
                    last_update < :cutoff
            )"""
    )


def delete_catalog_phantoms_older_than_x_days_sql() -> text:  # pragma: no cover
    """
    SQL for deleting from reconcile_phantom_report entries older than a certain date.
    """
    return text(
        """
        DELETE
        FROM
            reconcile_phantom_report
        WHERE
            job_id IN (
                SELECT
                    id
                FROM
                    reconcile_job
                WHERE
                    last_update < :cutoff
            )"""
    )


def delete_catalog_s3_objects_older_than_x_days_sql() -> text:  # pragma: no cover
    """
    SQL for deleting from reconcile_s3_object entries older than a certain date.
    """
    return text(
        """
        DELETE
        FROM
            reconcile_s3_object
        WHERE
            job_id IN (
                SELECT
                    id
                FROM
                    reconcile_job
                WHERE
                    last_update < :cutoff
            )"""
    )


def delete_jobs_older_than_x_days_sql() -> text:  # pragma: no cover
    """
    SQL for deleting from reconcile_job entries older than a certain date.
    """
    return text(
        """
        DELETE
        FROM
            reconcile_job
        WHERE
            last_update < :cutoff"""
    )


@LOGGER.inject_lambda_context(log_event=True)
def handler(event: Dict[str, Dict[str, Dict[str, Union[str, int]]]], context) -> None:
    """
    Lambda handler. Deletes old internal reconciliation reports, reducing DB size.
    Args:
        event: An object passed through by AWS. Unused.
        context: An object passed through by AWS. Used for tracking.
    Environment Vars:
        DB_CONNECT_INFO_SECRET_ARN (string):
            Secret ARN of the AWS secretsmanager secret for connecting to the database.
            See shared_db.py's get_configuration for further details.
        INTERNAL_RECONCILIATION_EXPIRATION_DAYS (int):
            Only reports updated before this many days ago will be deleted.
    """
    # get the secret ARN from the env variable
    try:
        db_connect_info_secret_arn = os.environ[OS_ENVIRON_DB_CONNECT_INFO_SECRET_ARN]
    except KeyError:
        LOGGER.error(
            f"{OS_ENVIRON_DB_CONNECT_INFO_SECRET_ARN} environment value not found."
        )
        raise

    try:
        internal_reconciliation_expiration_days = os.environ[
            OS_ENVIRON_INTERNAL_RECONCILIATION_EXPIRATION_DAYS
        ]
    except KeyError:
        LOGGER.error(
            f"{OS_ENVIRON_INTERNAL_RECONCILIATION_EXPIRATION_DAYS} environment value not found."
        )
        raise
    try:
        internal_reconciliation_expiration_days = int(
            internal_reconciliation_expiration_days
        )
    except ValueError:
        LOGGER.error(
            f"{OS_ENVIRON_INTERNAL_RECONCILIATION_EXPIRATION_DAYS} "
            f"'{internal_reconciliation_expiration_days}' could not be cast to int."
        )
        raise

    db_connect_info = shared_db.get_configuration(db_connect_info_secret_arn)

    task(internal_reconciliation_expiration_days, db_connect_info)
