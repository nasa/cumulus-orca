from typing import Dict, Any

from cumulus_logger import CumulusLogger

LOGGER = CumulusLogger()


def task():
    pass


def handler(event: Dict[str, Any], context: object) -> Dict[str, Any]:
    """
    Args:
        Entry point for the request_status_for_granule Lambda.

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

    return task()
