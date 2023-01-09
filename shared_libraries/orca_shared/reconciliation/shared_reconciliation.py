"""
Name: shared_reconciliation.py
Description: Shared library that combines common functions and classes needed for
             reconciliation operations.
"""
import logging
from datetime import datetime, timezone

# Standard libraries
from enum import Enum
from typing import Optional

# Third party libraries
from sqlalchemy import text
from sqlalchemy.future import Engine

from orca_shared.database import shared_db
from orca_shared.database.use_cases.validation import validate_postgres_name

LOGGER = logging.Logger("ORCA")


class OrcaStatus(Enum):
    """
    An enumeration.
    Defines the status value used in the ORCA Reconciliation database
    for use by the reconciliation functions.
    """

    GETTING_S3_LIST = 1
    STAGED = 2
    GENERATING_REPORTS = 3
    ERROR = 4
    SUCCESS = 5


def get_partition_name_from_bucket_name(bucket_name: str):
    """
    Used for interacting with the reconcile_s3_object table.
    Provides a valid partition name given an Orca bucket name.
    Changes to this function may require a DB migration to recreate partitions.

    bucket_name: The name of the Orca bucket in AWS.
    """
    partition_name = "reconcile_s3_object_" + bucket_name.replace("-", "_")
    validate_postgres_name(partition_name, f"Partition name '{partition_name}'", LOGGER)
    return partition_name


def update_job(
    job_id: int,
    status: OrcaStatus,
    error_message: Optional[str],
    engine: Engine,
) -> None:
    """
    Updates the status entry for a job.

    Args:
        job_id: The id of the job to associate info with.
        status: The status to update the job with.
        error_message: The error to post to the job, if any.
        engine: The sqlalchemy engine to use for contacting the database.
    """
    if status == OrcaStatus.ERROR:
        if error_message is None or len(error_message) == 0:
            raise ValueError("Error message is required.")
    elif error_message is not None:
        raise ValueError("Cannot set error message outside of error status entries.")

    last_update = datetime.now(timezone.utc)
    end_time = None
    if status == OrcaStatus.ERROR or status == OrcaStatus.SUCCESS:
        end_time = last_update
    internal_update_job(job_id, status, last_update, end_time, error_message, engine)


@shared_db.retry_operational_error()
def internal_update_job(
    job_id: int,
    status: OrcaStatus,
    last_update: datetime,
    end_time: Optional[datetime],
    error_message: Optional[str],
    engine: Engine,
) -> None:
    """
    Updates the status entry for a job.

    Args:
        job_id: The id of the job to associate info with.
        status: The status to update the job with.
        last_update: Datetime returned by datetime.now(timezone.utc)
        end_time: Datetime the job ended, if applicable
        error_message: The error to post to the job, if any.
        engine: The sqlalchemy engine to use for contacting the database.
    """
    try:
        LOGGER.debug(f"Creating reconcile records for job {job_id}.")
        with engine.begin() as connection:
            connection.execute(
                update_job_sql(),
                [
                    {
                        "id": job_id,
                        "status_id": status.value,
                        "last_update": last_update,
                        "end_time": end_time,
                        "error_message": error_message,
                    }
                ],
            )
    except Exception as sql_ex:
        LOGGER.error(f"Error while updating job '{job_id}': {sql_ex}")
        raise


def update_job_sql() -> text:  # pragma: no cover
    return text(
        """
        UPDATE
            orca.reconcile_job
        SET
            status_id = :status_id,
            last_update = :last_update,
            end_time = :end_time,
            error_message = :error_message
        WHERE
            id = :id"""
    )
