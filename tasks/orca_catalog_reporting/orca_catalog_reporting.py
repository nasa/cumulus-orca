import json
from http import HTTPStatus
from typing import Dict, Any, List, Union

import fastjsonschema as fastjsonschema
from cumulus_logger import CumulusLogger
from fastjsonschema import JsonSchemaException
from orca_shared import database
from sqlalchemy.exc import DatabaseError

LOGGER = CumulusLogger()


def task(
    provider_id: Union[None, List[str]],
    collection_id: Union[None, List[str]],
    granule_id: Union[None, List[str]],
    start_timestamp: Union[None, str],
    end_timestamp: str,
    page_index: int,
    db_connect_info: Dict[str, str],
    request_id: str
) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Args:
        provider_id: The unique ID of the provider(s) making the request.
        collection_id: The unique ID of collection(s) to compare.
        granule_id: The unique ID of granule(s) to compare.
        start_timestamp: Cumulus createdAt start time for date range to compare data.
        end_timestamp: Cumulus createdAt end-time for date range to compare data.
        page_index: The 0-based index of the results page to return.
        db_connect_info: See requests_db.py's get_dbconnect_info for further details.
        request_id: An ID provided by AWS Lambda. Used for context tracking.
    """
    pass


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


def handler(event: Dict[str, Any], context: Any) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    # noinspection SpellCheckingInspection
    """
    Entry point for the orca_catalog_reporting Lambda.
    Args:
        event: See schemas/input.json
        context: An object provided by AWS Lambda. Used for context tracking.

    Environment Vars: See requests_db.py's get_dbconnect_info for further details.

    Returns:
        See schemas/output.json
        Or, if an error occurs, see create_http_error_dict
    """
    LOGGER.setMetadata(event, context)

    end_timestamp = event.get("endTimestamp", None)
    if end_timestamp is None or len(end_timestamp) == 0:
        return create_http_error_dict(
            "BadRequest",
            HTTPStatus.BAD_REQUEST,
            context.aws_request_id,
            f"endTimestamp must be set to a non-empty value.",
        )
    page_index = event.get("pageIndex", None)
    if page_index is None or len(page_index) == 0:
        return create_http_error_dict(
            "BadRequest",
            HTTPStatus.BAD_REQUEST,
            context.aws_request_id,
            f"pageIndex must be set to a non-empty value.",
        )
    try:
        page_index = int(page_index)
    except ValueError as value_error:
        return create_http_error_dict(
            "BadRequest",
            HTTPStatus.BAD_REQUEST,
            context.aws_request_id,
            f"pageIndex must be an integer.",
        )

    try:
        with open("schemas/input.json", "r") as raw_schema:
            schema = json.loads(raw_schema.read())

        validate = fastjsonschema.compile(schema)
        validate(event)
    except JsonSchemaException as json_schema_exception:
        return create_http_error_dict(
            "BadRequest",
            HTTPStatus.BAD_REQUEST,
            context.aws_request_id,
            json_schema_exception.__str__(),
        )

    db_connect_info = database.get_dbconnect_info()
    try:
        return task(
            event.get("providerId", None),
            event.get("collectionId", None),
            event.get("granuleId", None),
            event.get("startTimestamp", None),
            end_timestamp,
            page_index,
            db_connect_info,
            context.aws_request_id,
        )
    except DatabaseError as db_error:
        return create_http_error_dict(
            "InternalServerError",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            context.aws_request_id,
            db_error.__str__(),
        )
