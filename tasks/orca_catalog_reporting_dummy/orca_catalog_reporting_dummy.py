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
        # CumulusLogger will error if a string containing '{' or '}' is passed in without escaping.
        "message": message.replace("{", "{{").replace("}", "}}")
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

    result = {
      "anotherPage": False,
      "granules": [
        {
          "providerId": "lpdaac",
          "collectionId": "MOD14A1___061",
          "id": "MOD14A1.061.A23V45.2020235",
          "createdAt": "2020-01-01T23:00:00Z",
          "executionId": "u654-123-Yx679",
          "ingestDate": "2020-01-01T23:00:00Z",
          "lastUpdate": "2020-01-01T23:00:00Z",
          "files": [
            {
              "name": "MOD14A1.061.A23V45.2020235.2020240145621.hdf",
              "cumulusArchiveLocation": "cumulus-bucket",
              "orcaArchiveLocation": "orca-archive",
              "keyPath": "MOD14A1/061/032/MOD14A1.061.A23V45.2020235.2020240145621.hdf",
              "sizeBytes": 100934568723,
              "hash": "ACFH325128030192834127347",
              "hashType": "SHA-256",
              "version": "VXCDEG902"
            }
          ]
        }
      ]
    }
    with open("schemas/output.json", "r") as raw_schema:
        schema = json.loads(raw_schema.read())

    validate = fastjsonschema.compile(schema)
    validate(result)
    return result
