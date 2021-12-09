from http import HTTPStatus
from typing import Dict, Any, List, Union

from cumulus_logger import CumulusLogger
from orca_shared.database import shared_db
from sqlalchemy import text
from sqlalchemy.future import Engine

INPUT_GRANULE_ID_KEY = "granule_id"
INPUT_JOB_ID_KEY = "asyncOperationId"

OUTPUT_GRANULE_ID_KEY = "granule_id"
OUTPUT_JOB_ID_KEY = "asyncOperationId"
OUTPUT_FILES_KEY = "files"
OUTPUT_FILENAME_KEY = "file_name"
OUTPUT_RESTORE_DESTINATION_KEY = "restore_destination"
OUTPUT_STATUS_KEY = "status"
OUTPUT_ERROR_MESSAGE_KEY = "error_message"
OUTPUT_REQUEST_TIME_KEY = "request_time"
OUTPUT_COMPLETION_TIME_KEY = "completion_time"

LOGGER = CumulusLogger()


def task(
    granule_id: str, db_connect_info: Dict, request_id: str, job_id: str = None
) -> Dict[str, Any]:
    # noinspection SpellCheckingInspection
    """
    Args:
        granule_id: The unique ID of the granule to retrieve status for.
        db_connect_info: The {database}.py defined db_connect_info.
        request_id: An ID provided by AWS Lambda. Used for context tracking.
        job_id: An optional additional filter to get a specific job's entry.
    Returns: A Dict with the following keys:
        'granule_id' (str): The unique ID of the granule to retrieve status for.
        'asyncOperationId' (str): The unique ID of the asyncOperation.
        'files' (List): Description and status of the files within the given granule. List of Dicts with keys:
            'file_name' (str): The name and extension of the file.
            'restore_destination' (str): The name of the glacier bucket the file is being copied to.
            'status' (str):
                The status of the restoration of the file. May be 'pending', 'staged', 'success', or 'failed'.
            'error_message' (str, Optional): If the restoration of the file errored, the error will be stored here.
        'request_time' (DateTime): The time, in UTC isoformat, when the request to restore the granule was initiated.
        'completion_time' (DateTime, Optional):
            The time, in UTC isoformat, when all granule_files were no longer 'pending'/'staged'.

        Will also return a dict from create_http_error_dict with error NOT_FOUND if job/granule could not be found.
    """
    if granule_id is None or len(granule_id) == 0:
        raise ValueError("granule_id must be set to a non-empty value.")

    engine = shared_db.get_user_connection(db_connect_info)

    if job_id is None or len(job_id) == 0:
        job_id = get_most_recent_job_id_for_granule(granule_id, engine)
        if job_id is None:
            return create_http_error_dict(
                "NotFound",
                HTTPStatus.NOT_FOUND,
                request_id,
                f"No job for granule id '{granule_id}'.",
            )

    job_entry = get_job_entry_for_granule(granule_id, job_id, engine)
    if job_entry is None:
        return create_http_error_dict(
            "NotFound",
            HTTPStatus.NOT_FOUND,
            request_id,
            f"No job found for granule id '{granule_id}' and job id '{job_id}'.",
        )

    if job_entry[OUTPUT_COMPLETION_TIME_KEY] is None:
        del job_entry[OUTPUT_COMPLETION_TIME_KEY]

    file_entries = get_file_entries_for_granule_in_job(granule_id, job_id, engine)
    for file_entry in file_entries:
        if file_entry[OUTPUT_ERROR_MESSAGE_KEY] is None:
            del file_entry[OUTPUT_ERROR_MESSAGE_KEY]

    job_entry[OUTPUT_FILES_KEY] = file_entries
    return job_entry


@shared_db.retry_operational_error()
def get_most_recent_job_id_for_granule(
    granule_id: str, engine: Engine
) -> Union[str, None]:
    """
    Gets the job_id for the most recent job that restores the given granule.

    Args:
        granule_id: The unique ID of the granule.
        engine: The sqlalchemy engine to use for contacting the database.

    Returns: The job_id for the given granule's restore job.
    """
    try:
        with engine.begin() as connection:
            results = connection.execute(
                get_most_recent_job_id_for_granule_sql(),
                [
                    {
                        "granule_id": granule_id,
                    }
                ],
            )
    except Exception as err:
        # Can't use f"" because '{}' of bug in CumulusLogger.
        LOGGER.error("DbError: {err}", err=str(err))
        raise

    row = None
    for row in results:
        break

    if row is None:
        return None
    return row["job_id"]


def get_most_recent_job_id_for_granule_sql() -> text:
    return text(
        """
            SELECT
                job_id
            FROM
                recovery_job
            WHERE
                granule_id = :granule_id
            ORDER BY
                 request_time DESC
            LIMIT 1"""
    )


@shared_db.retry_operational_error()
def get_job_entry_for_granule(
    granule_id: str, job_id: str, engine: Engine
) -> Union[Dict[str, Any], None]:
    # noinspection SpellCheckingInspection
    """
    Gets the recovery_file status entries for the associated granule_id.
    If async_operation_id is non-None, then it will be used to filter results.
    Otherwise, only the item with the most recent request_time will be returned.

    Args:
        granule_id: The unique ID of the granule to retrieve status for.
        job_id: An optional additional filter to get a specific job's entry.
        engine: The sqlalchemy engine to use for contacting the database.
    Returns: A Dict with the following keys:
        'granule_id' (str): The unique ID of the granule to retrieve status for.
        'job_id' (str): The unique ID of the asyncOperation.
        'request_time' (DateTime): The time, in UTC isoformat, when the request to restore the granule was initiated.
        'completion_time' (DateTime, Optional):
            The time, in UTC isoformat, when all granule_files were no longer 'pending'/'staged'.
    """
    try:
        with engine.begin() as connection:
            results = connection.execute(
                get_job_entry_for_granule_sql(),
                [
                    {
                        "granule_id": granule_id,
                        "job_id": job_id,
                    }
                ],
            )
    except Exception as err:
        # Can't use f"" because of '{}' bug in CumulusLogger.
        LOGGER.error("DbError: {err}", err=str(err))
        raise

    row = None
    for row in results:
        break

    if row is None:
        return None
    return {
        OUTPUT_GRANULE_ID_KEY: row[OUTPUT_GRANULE_ID_KEY],
        OUTPUT_JOB_ID_KEY: row[OUTPUT_JOB_ID_KEY],
        OUTPUT_REQUEST_TIME_KEY: row[OUTPUT_REQUEST_TIME_KEY],
        OUTPUT_COMPLETION_TIME_KEY: row[OUTPUT_COMPLETION_TIME_KEY],
    }


def get_job_entry_for_granule_sql() -> text:
    return text(
        f"""
                SELECT
                    granule_id as "{OUTPUT_GRANULE_ID_KEY}",
                    job_id as "{OUTPUT_JOB_ID_KEY}",
                    request_time as "{OUTPUT_REQUEST_TIME_KEY}",
                    completion_time as "{OUTPUT_COMPLETION_TIME_KEY}"
                FROM
                    recovery_job
                WHERE
                    granule_id = :granule_id AND job_id = :job_id"""
    )


@shared_db.retry_operational_error()
def get_file_entries_for_granule_in_job(
    granule_id: str, job_id: str, engine: Engine
) -> List[Dict]:
    """
    Gets the individual status entries for the files for the given job+granule.

    Args:
        granule_id: The id of the granule to get file statuses for.
        job_id: The id of the job to get file statuses for.
        engine: The sqlalchemy engine to use for contacting the database.

    Returns: A Dict with the following keys:
        'file_name' (str): The name and extension of the file.
        'restore_destination' (str): The name of the glacier bucket the file is being copied to.
        'status' (str): The status of the restoration of the file. May be 'pending', 'staged', 'success', or 'failed'.
        'error_message' (str): If the restoration of the file errored, the error will be stored here. Otherwise, None.
    """
    try:
        with engine.begin() as connection:
            results = connection.execute(
                get_file_entries_for_granule_in_job_sql(),
                [
                    {
                        "granule_id": granule_id,
                        "job_id": job_id,
                    }
                ],
            )
    except Exception as err:
        # Can't use f"" because of '{}' bug in CumulusLogger.
        LOGGER.error("DbError: {err}", err=str(err))
        raise

    rows = []
    for row in results:
        rows.append(
            {
                OUTPUT_FILENAME_KEY: row[OUTPUT_FILENAME_KEY],
                OUTPUT_RESTORE_DESTINATION_KEY: row[OUTPUT_RESTORE_DESTINATION_KEY],
                OUTPUT_STATUS_KEY: row[OUTPUT_STATUS_KEY],
                OUTPUT_ERROR_MESSAGE_KEY: row[OUTPUT_ERROR_MESSAGE_KEY],
            }
        )

    return rows


def get_file_entries_for_granule_in_job_sql() -> text:
    return text(
        f"""
            SELECT
                recovery_file.filename AS "{OUTPUT_FILENAME_KEY}",
                recovery_file.restore_destination AS "{OUTPUT_RESTORE_DESTINATION_KEY}",
                recovery_status.value AS "{OUTPUT_STATUS_KEY}",
                recovery_file.error_message as "{OUTPUT_ERROR_MESSAGE_KEY}"
            FROM
                recovery_file
            JOIN recovery_status ON recovery_file.status_id=recovery_status.id
            WHERE
                granule_id = :granule_id AND job_id = :job_id
            ORDER BY filename desc"""
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
    # CumulusLogger will error if a string containing '{' or '}' is passed in without escaping.
    message = message.replace("{", "{{").replace("}", "}}")
    LOGGER.error(message)
    return {
        "errorType": error_type,
        "httpStatus": http_status_code,
        "requestId": request_id,
        # CumulusLogger will error if a string containing '{' or '}' is passed in without escaping.
        "message": message.replace("{", "{{").replace("}", "}}"),
    }


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    # noinspection SpellCheckingInspection
    """
    Entry point for the request_status_for_granule Lambda.
    Args:
        event: A dict with the following keys:
            granule_id: The unique ID of the granule to retrieve status for.
            asyncOperationId (Optional): The unique ID of the asyncOperation.
                May apply to a request that covers multiple granules.
        context: An object provided by AWS Lambda. Used for context tracking.

    Environment Vars: See shared_db.py's get_configuration for further details.

    Returns: A Dict with the following keys:
        'granule_id' (str): The unique ID of the granule to retrieve status for.
        'asyncOperationId' (str): The unique ID of the asyncOperation.
        'files' (List): Description and status of the files within the given granule. List of Dicts with keys:
            'file_name' (str): The name and extension of the file.
            'restore_destination' (str): The name of the glacier bucket the file is being copied to.
            'status' (str): The status of the restoration of the file.
                May be 'pending', 'staged', 'success', or 'failed'.
            'error_message' (str, Optional): If the restoration of the file errored, the error will be stored here.
        'request_time' (DateTime): The time, in UTC isoformat, when the request to restore the granule was initiated.
        'completion_time' (DateTime, Optional):
            The time, in UTC isoformat, when all granule_files were no longer 'pending'/'staged'.

        Or, if an error occurs, see create_http_error_dict
            400 if granule_id is missing. 500 if an error occurs when querying the database, 404 if not found.
    """
    try:
        LOGGER.setMetadata(event, context)

        granule_id = event.get(INPUT_GRANULE_ID_KEY, None)
        if granule_id is None or len(granule_id) == 0:
            return create_http_error_dict(
                "BadRequest",
                HTTPStatus.BAD_REQUEST,
                context.aws_request_id,
                f"{INPUT_GRANULE_ID_KEY} must be set to a non-empty value.",
            )

        db_connect_info = shared_db.get_configuration()

        return task(
            granule_id,
            db_connect_info,
            context.aws_request_id,
            event.get(INPUT_JOB_ID_KEY, None),
        )
    except Exception as error:
        return create_http_error_dict(
            "InternalServerError",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            context.aws_request_id,
            error.__str__(),
        )
