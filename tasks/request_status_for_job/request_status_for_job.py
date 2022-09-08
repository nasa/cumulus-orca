import os
from http import HTTPStatus
from typing import Any, Dict, List

from cumulus_logger import CumulusLogger
from orca_shared.database import shared_db
from sqlalchemy import text
from sqlalchemy.future import Engine

INPUT_JOB_ID_KEY = "asyncOperationId"

OUTPUT_JOB_ID_KEY = "asyncOperationId"
OUTPUT_JOB_STATUS_TOTALS_KEY = "jobStatusTotals"
OUTPUT_GRANULES_KEY = "granules"
OUTPUT_STATUS_KEY = "status"
OUTPUT_GRANULE_ID_KEY = "granuleId"

LOGGER = CumulusLogger()


def task(job_id: str, db_connect_info: Dict, request_id: str) -> Dict[str, Any]:
    """

    Args:
        job_id: The unique asyncOperationId of the recovery job.
        db_connect_info: The database.py defined db_connect_info.
        request_id: An ID provided by AWS Lambda. Used for context tracking.
    Returns:
        A dictionary with the following keys:
            'asyncOperationId' (str): The job_id.
            'job_status_totals' (Dict): A dictionary with the following keys:
                'pending' (int)
                'staged' (int)
                'success' (int)
                'failed' (int)
            'granules' (List): A list of dicts with the following keys:
                'granule_id' (str)
                'status' (str): pending|staged|success|failed

        Will also return a dict from create_http_error_dict with
        error NOT_FOUND if job could not be found.
    """
    if job_id is None or len(job_id) == 0:
        raise ValueError("job_id must be set to a non-empty value.")

    engine = shared_db.get_user_connection(db_connect_info)

    status_entries = get_granule_status_entries_for_job(job_id, engine)
    if len(status_entries) == 0:
        return create_http_error_dict(
            "NotFound",
            HTTPStatus.NOT_FOUND,
            request_id,
            f"No granules found for job id '{job_id}'.",
        )

    status_totals = get_status_totals_for_job(job_id, engine)
    return {
        OUTPUT_JOB_ID_KEY: job_id,
        OUTPUT_JOB_STATUS_TOTALS_KEY: status_totals,
        OUTPUT_GRANULES_KEY: status_entries,
    }


@shared_db.retry_operational_error()
def get_granule_status_entries_for_job(
    job_id: str, engine: Engine
) -> List[Dict[str, Any]]:
    """
    Gets the recovery_job status entry for the associated job_id.

    Args:
        job_id: The unique asyncOperationId of the recovery job to retrieve status for.
        engine: The sqlalchemy engine to use for contacting the database.

    Returns: A list of dicts with the following keys:
        'granule_id' (str)
        'status' (str): pending|staged|success|failed

    """
    try:
        with engine.begin() as connection:
            results = connection.execute(
                get_granule_status_entries_for_job_sql(),
                [{"job_id": job_id}],
            )
    except Exception as err:
        # Can't use f"" because of '{}' bug in CumulusLogger.
        LOGGER.error("DbError: {err}", err=str(err))
        raise

    rows = []
    for row in results:
        rows.append(
            {
                OUTPUT_GRANULE_ID_KEY: row[OUTPUT_GRANULE_ID_KEY],
                OUTPUT_STATUS_KEY: row[OUTPUT_STATUS_KEY],
            }
        )
    return rows


def get_granule_status_entries_for_job_sql() -> text:  # pragma: no cover
    return text(
        f"""
                SELECT
                    granule_id as "{OUTPUT_GRANULE_ID_KEY}",
                    recovery_status.value AS "{OUTPUT_STATUS_KEY}"
                FROM
                    recovery_job
                JOIN recovery_status ON recovery_job.status_id=recovery_status.id
                WHERE
                    job_id = :job_id
                """
    )


@shared_db.retry_operational_error()
def get_status_totals_for_job(job_id: str, engine: Engine) -> Dict[str, int]:
    # noinspection SpellCheckingInspection
    """
    Gets the number of recovery_job for the given job_id for each possible status value.

    Args:
        job_id: The unique id of the recovery job to retrieve status for.
        engine: The sqlalchemy engine to use for contacting the database.

    Returns: A dictionary with the following keys:
        'pending' (int)
        'staged' (int)
        'success' (int)
        'failed' (int)
    """
    try:
        with engine.begin() as connection:
            results = connection.execute(
                get_status_totals_for_job_sql(),
                [{"job_id": job_id}],
            )
    except Exception as err:
        # Can't use f"" because of '{}' bug in CumulusLogger.
        LOGGER.error("DbError: {err}", err=str(err))
        raise

    totals = {row["value"]: row["total"] for row in results}
    return totals


def get_status_totals_for_job_sql() -> text:  # pragma: no cover
    return text(
        f"""
                with granule_status_count AS (
                    SELECT status_id
                        , count(*) as total
                    FROM recovery_job
                    WHERE job_id = :job_id
                    GROUP BY status_id
                )
                SELECT value
                    , coalesce(total, 0) as total
                FROM recovery_status os
                LEFT JOIN granule_status_count gsc ON (gsc.status_id = os.id)"""  # nosec   # noqa
    )


def create_http_error_dict(
    error_type: str, http_status_code: int, request_id: str, message: str
) -> Dict[str, Any]:
    """
    Creates a standardized dictionary for error reporting.
    Args:
        error_type: The string representation of http_status_code.
        http_status_code: The integer representation of the http error.
        request_id: The incoming request's id.
        message: The message to display to the user and to record for debugging.
    Returns:
        A dict with the following keys:
            'errorType' (str)
            'httpStatus' (int)
            'requestId' (str)
            'message' (str)
    """
    LOGGER.error(message)
    return {
        "errorType": error_type,
        "httpStatus": http_status_code,
        "requestId": request_id,
        "message": message,
    }


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Entry point for the request_status_for_job Lambda.
    Args:
        event: A dict with the following keys:
            asyncOperationId: The unique asyncOperationId of the recovery job.
        context: An object provided by AWS Lambda. Used for context tracking.

    Environment Vars:
        DB_CONNECT_INFO_SECRET_ARN (string):
            Secret ARN of the AWS secretsmanager secret for connecting to the database.
        See shared_db.py's get_configuration for further details.

    Returns: A Dict with the following keys:
        asyncOperationId (str): The unique ID of the asyncOperation.
        job_status_totals (Dict[str, int]): Sums of how many granules are in each
            particular restoration status.
                pending (int): The number of granules that still need to be copied.
                staged (int): Currently unimplemented.
                success (int): The number of granules that have been successfully copied.
                failed (int): The number of granules that did not copy
                              and will not copy due to an error.
        granules (Array[Dict]): An array of Dicts representing each granule
            being copied as part of the job.
                granule_id (str): The unique ID of the granule.
                status (str): The status of the restoration of the file.
                    May be 'pending', 'staged', 'success', or 'failed'.

        Or, if an error occurs, see create_http_error_dict
            400 if asyncOperationId is missing. 500 if an error occurs when querying the database.
    """
    # get the secret ARN from the env variable
    try:
        db_connect_info_secret_arn = os.environ["DB_CONNECT_INFO_SECRET_ARN"]
    except KeyError:
        LOGGER.error("DB_CONNECT_INFO_SECRET_ARN environment value not found.")
        raise
    try:
        LOGGER.setMetadata(event, context)

        job_id = event.get(INPUT_JOB_ID_KEY, None)
        if job_id is None or len(job_id) == 0:
            return create_http_error_dict(
                "BadRequest",
                HTTPStatus.BAD_REQUEST,
                context.aws_request_id,
                f"{INPUT_JOB_ID_KEY} must be set to a non-empty value.",
            )
        db_connect_info = shared_db.get_configuration(db_connect_info_secret_arn)
        return task(job_id, db_connect_info, context.aws_request_id)
    except Exception as error:
        return create_http_error_dict(
            "InternalServerError",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            context.aws_request_id,
            error.__str__(),
        )
