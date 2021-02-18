from typing import Dict, Any, List

import database
from cumulus_logger import CumulusLogger
from requests_db import get_dbconnect_info, DatabaseError

GRANULE_ID_KEY = 'granule_id'
ASYNC_OPERATION_ID_KEY = 'asyncOperationId'

LOGGER = CumulusLogger()


def task(granule_id: str, async_operation_id: str = None) -> Dict[str, Any]:
    """

    Args:
        granule_id: The unique ID of the granule to retrieve status for.
        async_operation_id: An optional additional filter to get a specific job's entry.
    Returns:
        todo
    """
    if granule_id is None:
        raise ValueError(f"{GRANULE_ID_KEY} cannot be None.")
    pass


def get_status_entries_for_granule(granule_id: str, async_operation_id: str = None) -> List[Dict[str, Any]]:
    """
    Gets the orca_recoverfile status entry for the associated granule_id.
    If async_operation_id is non-None, then it will be used to filter results.
    Otherwise, only the item with the most recent request_time will be returned.

    Args:
        granule_id: The unique ID of the granule to retrieve status for.
        async_operation_id: An optional additional filter to get a specific job's entry.
    Returns: todo
    """
    raise NotImplementedError
    # todo: Move this code into a new requests_db.py when able.
    # todo: Do we join in restore_destination/request_time/completion_time, or just get the whole orca_recoveryjob?
    # todo: The above may affect what we get from orca_recoverfile, as some properties may be redundant.
    sql = """
            SELECT
                orca_recoverfile.granule_id,
                orca_recoverfile.job_id,
                orca_recoverfile.filename,
                orca_recoverfile.status_id,
                orca_recoverfile.error_message,
                orca_recoverfile.request_time,
                orca_status.value
            FROM
                orca_recoverfile
            INNER JOIN orca_status ON orca_recoverfile.status_id=orca_status.id
            WHERE
                granule_id = %s"""
    if async_operation_id is not None:
        sql += " AND job_id = %s"
    sql += """
            ORDER BY last_update desc
            """
    try:
        dbconnect_info = get_dbconnect_info()
        if async_operation_id is not None:
            rows = database.single_query(sql, dbconnect_info, (granule_id, async_operation_id,))
        else:
            rows = database.single_query(sql, dbconnect_info, (granule_id,))
        result = database.result_to_json(rows)
        return result
    except database.DbError as err:
        LOGGER.exception(f"DbError: {str(err)}")
        raise DatabaseError(str(err))

    # todo: The below transformations should NOT HAPPEN HERE.
    # todo: transform job_id into asyncOperationId


def handler(event: Dict[str, Any], context: object) -> Dict[str, Any]:
    """
    Entry point for the request_status_for_granule Lambda.
    Args:
        event: A dict with the following keys:
            granule_id: The unique ID of the granule to retrieve status for.
            asyncOperationId (Optional): The unique ID of the asyncOperation.
                May apply to a request that covers multiple granules.
        context: An object required by AWS Lambda. Unused.

    todo: env variables.

    Returns: The most recent/only matching granule record, representing as a Dict with the following keys:
        granule_id (str): The unique ID of the granule to retrieve status for.
        asyncOperationId (str): The unique ID of the asyncOperation.
        granule_files (Array[Dict]): Description and status of the individual files within the given granule.
            file_name (str): The name and extension of the file.
            status (str): The status of the restoration of the file. May be 'pending', 'success', or 'failed'.
            error_message (str): If the restoration of the file errored, the error will be stored here.
        restore_destination (str): The name of the glacier bucket the granule is being copied to.
        request_time (str): The time, in UTC and isoformat, when the request to restore the granule was initiated.
        completion_time (str): The time, in UTC and isoformat, when all granule_files were no longer 'pending'.
    """
    LOGGER.setMetadata(event, context)

    return task(event[GRANULE_ID_KEY], event.get(ASYNC_OPERATION_ID_KEY, None))
