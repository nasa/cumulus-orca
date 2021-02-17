from typing import Dict, Any
from cumulus_logger import CumulusLogger

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


def get_status_entry_for_granule(granule_id: str, async_operation_id: str = None):
    """
    Gets the orca_recoverfile status entry for the associated granule_id.
    If async_operation_id is non-None, then it will be used to filter results.
    Otherwise, only the item with the most recent request_time will be returned.

    Args:
        granule_id: The unique ID of the granule to retrieve status for.
        async_operation_id: An optional additional filter to get a specific job's entry.
    Returns: todo
    """
    # todo: Get the orca_recoverfile for the granule_id.
    # todo: Either add the async_operation_id, or only get the entry with the most recent request_time
    raise NotImplementedError


def handler(event: Dict[str, Any], context: object) -> Dict[str, Any]:
    """
    Entry point for the request_status_for_granule Lambda.
    Args:
        event: A dict with the following keys:
            granule_id: The unique ID of the granule to retrieve status for.
            asyncOperationId (Optional): The unique ID of the asyncOperation.
                May apply to a request that covers multiple granules.
        context: An object required by AWS Lambda. Unused.

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
