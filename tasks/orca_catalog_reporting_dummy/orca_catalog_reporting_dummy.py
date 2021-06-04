import json
import uuid
from datetime import datetime, timezone, timedelta
from http import HTTPStatus
from typing import Dict, Any, List

import fastjsonschema as fastjsonschema
from cumulus_logger import CumulusLogger
from fastjsonschema import JsonSchemaException

LOGGER = CumulusLogger()


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


def handler(event: Dict[str, Any], context: Any) -> List[Dict[str, Any]]:
    # noinspection SpellCheckingInspection
    """
    Entry point for the request_status_for_granule Lambda.
    Args:
        event: A dict with the following keys:
            granule_id: The unique ID of the granule to retrieve status for.
            asyncOperationId (Optional): The unique ID of the asyncOperation.
                May apply to a request that covers multiple granules.
        context: An object provided by AWS Lambda. Used for context tracking.

    Returns: A Dict with the following keys:
        'granule_id' (str): The unique ID of the granule to retrieve status for.
        'asyncOperationId' (str): The unique ID of the asyncOperation.
        'files' (List): Description and status of the files within the given granule. List of Dicts with keys:
            'file_name' (str): The name and extension of the file.
            'restore_destination' (str): The name of the glacier bucket the file is being copied to.
            'status' (str): The status of the restoration of the file. May be 'pending', 'staged', 'success', or 'failed'.
            'error_message' (str, Optional): If the restoration of the file errored, the error will be stored here.
        'request_time' (DateTime): The time, in UTC isoformat, when the request to restore the granule was initiated.
        'completion_time' (DateTime, Optional):
            The time, in UTC isoformat, when all granule_files were no longer 'pending'/'staged'.
            
        Or, if an error occurs, see create_http_error_dict
            400 if granule_id is missing. 500 if an error occurs when querying the database, 404 if not found.
    """
    LOGGER.setMetadata(event, context)

    with open("schemas/input.json", "r") as raw_schema:
        schema = json.loads(raw_schema.read())

    validate = fastjsonschema.compile(schema)
    validate(event)

    result = [
        {
            "providerId": "lpdaac",
            "collections": [
                {
                    "collectionId": "MOD14A1__061",
                    "granules": [
                        {
                            "granuleId": "MOD14A1.061.A23V45.2020235",
                            "date": "TBD",
                            "createDate": "2020-01-01T23:00:00+00:00",  # todo: Mind if we add these 0s?
                            "lastUpdate": "2020-01-01T23:00:00+00:00",
                            "files": [
                                {
                                    "fileName": "MOD14A1.061.A23V45.2020235.2020240145621.hdf",
                                    "orcaLocation": "s3://orca-archive/MOD14A1/061/...",
                                    "fileSize": 100934568723,
                                    "fileChecksum": "ACFH325128030192834127347",
                                    "fileChecksumType": "SHA-256",
                                    "fileVersion": "VXCDEG902",
                                    "orcaEtag": "YXC432BGT789"
                                },
                            ]
                        },
                    ]
                },
            ]
        },
    ]
    with open("schemas/output.json", "r") as raw_schema:
        schema = json.loads(raw_schema.read())

    validate = fastjsonschema.compile(schema)
    validate(result)
    return result
