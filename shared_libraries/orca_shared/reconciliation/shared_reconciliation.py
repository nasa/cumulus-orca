"""
Name: shared_reconciliation.py
Description: Shared library that combines common functions and classes needed for
             reconciliation operations.
"""
from typing import Optional

from orca_shared.database import shared_db
# Standard libraries
from enum import Enum
from datetime import datetime, timezone

# Third party libraries
from sqlalchemy import text
from sqlalchemy.future import Engine
from sqlalchemy.sql.elements import TextClause


class OrcaStatus(Enum):
    """
    An enumeration.
    Defines the status value used in the ORCA Reconciliation database for use by the reconciliation functions.
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
    if not partition_name.replace("_", "").isalnum():
        raise Exception(f"'{partition_name}' is not a valid partition name.")
    return partition_name


@shared_db.retry_operational_error()
def update_job(job_id: int, status: OrcaStatus, now: str, error_message: Optional[str], engine: Engine, logger) -> None:
    """
    Updates the status entry for a job.

    Args:
        job_id: The id of the job to associate info with.
        status: The status to update the job with.
        now: Datetime returned by datetime.now(timezone.utc).isoformat()
        error_message: The error to post to the job, if any.
        engine: The sqlalchemy engine to use for contacting the database.
        logger: Logger.
    """
    try:
        logger.debug(f"Creating reconcile records for job {job_id}.")
        with engine.begin() as connection:
            end_time = None
            if status == OrcaStatus.ERROR or status == OrcaStatus.SUCCESS:
                end_time = now
            connection.execute(
                update_job_sql(),
                [
                    {
                        "id": job_id,
                        "status_id": status.value,
                        "last_update": now,
                        "end_time": end_time,
                        "error_message": error_message,
                    }
                ],
            )
    except Exception as sql_ex:
        logger.error(f"Error while updating job '{job_id}': {sql_ex}")
        raise


def update_job_sql() -> TextClause:
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
