from typing import Dict, Any
from cumulus_logger import CumulusLogger

ASYNC_OPERATION_ID_KEY = 'asyncOperationId'

LOGGER = CumulusLogger()


def task(async_operation_id: str) -> Dict[str, Any]:
    """

    Args:
        async_operation_id: The unique asyncOperationId of the recovery job.
    Returns:
        todo
    """
    if async_operation_id is None:
        raise ValueError(f"{ASYNC_OPERATION_ID_KEY} cannot be None.")
    pass


def get_status_entry_for_job(async_operation_id: str):
    """
    Gets the orca_recoveryjob status entry for the associated async_operation_id,
    along with sums representing how many files are in a given status.

    Args:
        async_operation_id: The unique asyncOperationId of the recovery job to retrieve status for.

    Returns: todo: A single entry.
    """
    # todo: Get the orca_recoveryjob entry and sums of status codes on associated orca_recoverfile entries.
    raise NotImplementedError


def handler(event: Dict[str, Any], context: object) -> Dict[str, Any]:
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
        granule_files (Array[Dict]): Description and status of the individual files within the given granule.
            file_name (str): The name and extension of the file.
            status (str): The status of the restoration of the file. May be 'pending', 'success', or 'failed'.
            error_message (str): If the restoration of the file errored, the error will be stored here.
        granules (Array[Dict]): An array of Dicts representing each granule being copied as part of the job.
            granule_id (str): The unique ID of the granule.
            status (str): The status of the restoration of the file. May be 'pending', 'success', or 'failed'.
    """
    LOGGER.setMetadata(event, context)

    return task(event[ASYNC_OPERATION_ID_KEY])
