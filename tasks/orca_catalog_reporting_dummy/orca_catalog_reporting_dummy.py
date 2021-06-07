import json
from typing import Dict, Any, List

import fastjsonschema as fastjsonschema
from cumulus_logger import CumulusLogger

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
    Entry point for the orca_catalog_reporting_dummy Lambda.
    Args:
        event: See schemas/input.json
        context: An object provided by AWS Lambda. Used for context tracking.

    Returns:
        See schemas/output.json
        Or, if an error occurs, see create_http_error_dict
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
