from http import HTTPStatus
from typing import Dict, Any, List

import database
import requests_db
from cumulus_logger import CumulusLogger
from requests_db import DatabaseError

INPUT_JOB_ID_KEY = 'asyncOperationId'

LOGGER = CumulusLogger()


def task(job_id: str, db_connect_info: Dict) -> Dict[str, Any]:
    f"""

    Args:
        job_id: The unique asyncOperationId of the recovery job.
        db_connect_info: The {database}.py defined db_connect_info.
    Returns:
        A dictionary with the following keys:
            'asyncOperationId' (str): The {job_id}.
            'job_status_totals' (Dict): A dictionary with the following keys:
                'pending' (int)
                'success' (int)
                'failed' (int)
            'granules' (List): A list of dicts with the following keys:
                granule_id (str)
                status (str): pending|success|failed
    """
    if job_id is None or len(job_id) == 0:
        raise ValueError(f"async_operation_id must be set to a non-empty value.")
    status_entries = get_granule_status_entries_for_job(job_id, db_connect_info)
    status_totals = get_status_totals_for_job(job_id, db_connect_info)
    return {
        'asyncOperationId': job_id,
        'job_status_totals': status_totals,
        'granules': status_entries
    }


def get_granule_status_entries_for_job(async_operation_id: str, db_connect_info: Dict) -> List[Dict[str, Any]]:
    f"""
    Gets the orca_recoveryjob status entry for the associated async_operation_id.

    Args:
        async_operation_id: The unique asyncOperationId of the recovery job to retrieve status for.
        db_connect_info: The {database} defined db_connect_info.

    Returns: todo
    """
    sql = f"""
            SELECT
                granule_id,
                orca_status.value AS status
            FROM
                orca_recoveryjob
            JOIN orca_status ON orca_recoveryjob.status_id=orca_status.id
            WHERE
                job_id = %s
            """

    try:
        rows = database.single_query(sql, db_connect_info, (async_operation_id,))
    except database.DbError as err:
        LOGGER.error(f"DbError: {str(err)}")
        raise DatabaseError(str(err))
    result = database.result_to_json(rows)
    return result


def get_status_totals_for_job(job_id: str, db_connect_info: Dict) -> Dict[str, int]:
    # noinspection SpellCheckingInspection
    f"""
    Gets the number of orca_recoveryjobs for the given {job_id} for each possible status value.

    Args:
        job_id: The unique id of the recovery job to retrieve status for.
        db_connect_info: The {database} defined db_connect_info.

    Returns: A dictionary with the following keys:
        'pending' (int)
        'success' (int)
        'failed' (int)
    """
    # noinspection SpellCheckingInspection
    sql = f"""
            with granule_status_count AS (
                SELECT status_id
                    , count(*) as total
                FROM orca_recoveryjob
                WHERE job_id = %s
                GROUP BY 1
            )
            SELECT value
                , coalesce(total, 0)
            FROM orca_status os
            LEFT JOIN granule_status_count gsc ON (gsc.status_id = os.id)"""

    try:
        rows = database.single_query(sql, db_connect_info, (job_id,))
    except database.DbError as err:
        LOGGER.error(f"DbError: {str(err)}")
        raise DatabaseError(str(err))
    result = database.result_to_json(rows)
    totals = {result[i]['value']: result[i]['coalesce'] for i in range(0, len(result), 1)}
    return totals


def create_http_error_dict(error_type: str, http_status_code: int, request_id: str, message: str) -> Dict[str, Any]:
    LOGGER.error(message)
    return {
        'errorType': error_type,
        'httpStatus': http_status_code,
        'requestId': request_id,
        'message': message
    }


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Entry point for the request_status_for_job Lambda.
    Args:
        event: A dict with the following keys:
            asyncOperationId: The unique asyncOperationId of the recovery job.
        context: An object required by AWS Lambda. Unused.

    Returns: A Dict with the following keys:
        asyncOperationId (str): The unique ID of the asyncOperation.
        job_status_totals (Dict[str, int]): Sums of how many granules are in each particular restoration status.
            pending (int): The number of granules that still need to be copied.
            success (int): The number of granules that have been successfully copied.
            failed (int): The number of granules that did not copy and will not copy due to an error.
        granules (Array[Dict]): An array of Dicts representing each granule being copied as part of the job.
            granule_id (str): The unique ID of the granule.
            status (str): The status of the restoration of the file. May be 'pending', 'success', or 'failed'.

        Or, if an error occurs, see {create_http_error_dict}
            400 if asyncOperationId is missing.
    """
    LOGGER.setMetadata(event, context)

    job_id = event.get(INPUT_JOB_ID_KEY, None)
    if job_id is None or len(job_id) == 0:
        return create_http_error_dict("BadRequest", HTTPStatus.BAD_REQUEST, context.aws_request_id,
                                      f"{INPUT_JOB_ID_KEY} must be set to a non-empty value.")
    db_connect_info = requests_db.get_dbconnect_info()
    return task(job_id, db_connect_info)


#temp_db_connect_info = {
#    'db_host': 'localhost',
#    'db_port': '5432',
#    'db_name': 'disaster_recovery',
#    'db_user': 'postgres',
#    'db_pw': 'postgres'
#}
#print(task('job_id_0', temp_db_connect_info))
