"""
Name: delete_old_reconcile_jobs.py

Description: Deletes old internal reconciliation reports, reducing DB size.
"""
import functools
import os
import random
import time
from typing import Callable, Dict, Union, List

from cumulus_logger import CumulusLogger
from orca_shared.database import shared_db
from orca_shared.database.shared_db import RT
from sqlalchemy import text, bindparam
from sqlalchemy.future import Engine
from sqlalchemy.sql.elements import TextClause

OS_ENVIRON_DB_CONNECT_INFO_SECRET_ARN = "DB_CONNECT_INFO_SECRET_ARN"
OS_ENVIRON_INTERNAL_RECONCILIATION_EXPIRATION_DAYS = (
    "INTERNAL_RECONCILIATION_EXPIRATION_DAYS"
)

LOGGER = CumulusLogger(name="ORCA")


def task(
    internal_reconciliation_expiration_days: int,
    db_connect_info: Dict,
) -> None:
    """
    Gets all jobs older than internal_reconciliation_expiration_days days, then deletes their records in Postgres.

    Args:
        internal_reconciliation_expiration_days: Only reports updated before this many days ago will be deleted.
        db_connect_info: See shared_db.py's get_configuration for further details.
    """

    user_engine = shared_db.get_user_connection(db_connect_info)
    old_job_ids = get_jobs_older_than_x_days(
        internal_reconciliation_expiration_days, user_engine
    )

    if old_job_ids is None:
        LOGGER.info("No jobs found.")
        return

    delete_jobs(
        old_job_ids,
        user_engine,
    )


@shared_db.retry_operational_error()
def get_jobs_older_than_x_days(
    internal_reconciliation_expiration_days: int, engine: Engine
) -> List[int]:
    """
    Gets all jobs older than internal_reconciliation_expiration_days days.
    If none are found, returns null.

    Args:
        internal_reconciliation_expiration_days: Only reports updated before this many days ago will be retrieved.
        engine: The sqlalchemy engine to use for contacting the database.

    Returns: A list of ids for the jobs, or null if none were found.

    """
    try:
        LOGGER.debug(
            f"Getting jobs older than {internal_reconciliation_expiration_days} days."
        )
        with engine.begin() as connection:
            sql_results = connection.execute(
                get_jobs_sql(),
                [
                    {
                        "internal_reconciliation_expiration_days": internal_reconciliation_expiration_days
                    }
                ],
            )
            return sql_results.fetchone()[
                0
            ]  # fetchone returns row. [0] returns the list of ids.
    except Exception as sql_ex:
        LOGGER.error(f"Error while getting jobs: {sql_ex}")
        raise


@shared_db.retry_operational_error()
def delete_jobs(job_ids: List[int], engine: Engine) -> None:
    """
    Deletes all records for the given job ids from the database.

    Args:
        job_ids: The ids of the jobs containing s3 inventory info.
        engine: The sqlalchemy engine to use for contacting the database.
    """
    try:
        LOGGER.debug(f"Deleting data for job ids {job_ids}.")
        with engine.begin() as connection:
            connection.execute(
                # populate reconcile_phantom_report with files in orca.files but NOT reconcile_s3_object
                delete_jobs_sql(),
                [{"job_ids_to_delete": job_ids}],
            )
    except Exception as sql_ex:
        LOGGER.error(f"Error while deleting jobs: {sql_ex}")
        raise


def get_jobs_sql() -> TextClause:
    """
    SQL for getting jobs older than a certain date.
    """
    return text(
        """
        SELECT json_agg(reconcile_job.id)
            FROM reconcile_job
            WHERE last_update < (NOW() - interval ':internal_reconciliation_expiration_days days')"""
    )


def delete_jobs_sql() -> TextClause:
    """
    SQL for deleting all jobs in a given range.
    """
    return text(
        """
        DELETE FROM reconcile_catalog_mismatch_report WHERE job_id = ANY(:job_ids_to_delete);
        DELETE FROM reconcile_orphan_report WHERE job_id = ANY(:job_ids_to_delete);
        DELETE FROM reconcile_phantom_report WHERE job_id = ANY(:job_ids_to_delete);
        DELETE FROM reconcile_s3_object WHERE job_id = ANY(:job_ids_to_delete);
        DELETE FROM reconcile_job WHERE id = ANY(:job_ids_to_delete);"""
    )


def handler(event: Dict[str, Dict[str, Dict[str, Union[str, int]]]], context) -> None:
    """
    Lambda handler. Deletes old internal reconciliation reports, reducing DB size.
    Args:
        event: An object passed through by AWS. Unused.
        context: An object passed through by AWS. Used for tracking.
    Environment Vars:
        DB_CONNECT_INFO_SECRET_ARN (string): Secret ARN of the AWS secretsmanager secret for connecting to the database.
        See shared_db.py's get_configuration for further details.
        INTERNAL_RECONCILIATION_EXPIRATION_DAYS (int): Only reports updated before this many days ago will be deleted.
    """
    LOGGER.setMetadata(event, context)

    # get the secret ARN from the env variable
    try:
        db_connect_info_secret_arn = os.environ[OS_ENVIRON_DB_CONNECT_INFO_SECRET_ARN]
    except KeyError:
        LOGGER.error(
            f"{OS_ENVIRON_DB_CONNECT_INFO_SECRET_ARN} environment value not found."
        )
        raise

    try:
        internal_reconciliation_expiration_days = int(os.environ[
            OS_ENVIRON_INTERNAL_RECONCILIATION_EXPIRATION_DAYS
        ])
    except KeyError:
        LOGGER.error(
            f"{OS_ENVIRON_INTERNAL_RECONCILIATION_EXPIRATION_DAYS} environment value not found."
        )
        raise
    except ValueError:
        LOGGER.error(
            f"{OS_ENVIRON_INTERNAL_RECONCILIATION_EXPIRATION_DAYS} "
            f"'{internal_reconciliation_expiration_days}' could not be cast to int."
        )
        raise

    db_connect_info = shared_db.get_configuration(db_connect_info_secret_arn)

    task(internal_reconciliation_expiration_days, db_connect_info)
