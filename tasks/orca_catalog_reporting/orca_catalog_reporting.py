import json
from http import HTTPStatus
from typing import Dict, Any, List, Union

import fastjsonschema as fastjsonschema
from cumulus_logger import CumulusLogger
from fastjsonschema import JsonSchemaException
from orca_shared.database import shared_db
from orca_shared.database.shared_db import retry_operational_error
from sqlalchemy import text
from sqlalchemy.exc import DatabaseError
from sqlalchemy.future import Engine

LOGGER = CumulusLogger()

PAGE_SIZE = 100


def task(
    provider_id: Union[None, List[str]],
    collection_id: Union[None, List[str]],
    granule_id: Union[None, List[str]],
    start_timestamp: Union[None, str],
    end_timestamp: str,
    page_index: int,
    db_connect_info: Dict[str, str],
) -> Dict[str, Any]:
    """
    Args:
        provider_id: The unique ID of the provider(s) making the request.
        collection_id: The unique ID of collection(s) to compare.
        granule_id: The unique ID of granule(s) to compare.
        start_timestamp: Cumulus createdAt start time for date range to compare data.
        end_timestamp: Cumulus createdAt end-time for date range to compare data.
        page_index: The 0-based index of the results page to return.
        db_connect_info: See requests_db.py's get_configuration for further details.
    """
    engine = shared_db.get_user_connection(db_connect_info)
    granules = query_db(
        engine,
        provider_id,
        collection_id,
        granule_id,
        start_timestamp,
        end_timestamp,
        page_index,
    )

    return {"anotherPage": len(granules) > PAGE_SIZE, "granules": granules[0:PAGE_SIZE]}


@retry_operational_error()
def query_db(
    engine: Engine,
    provider_id: Union[None, List[str]],
    collection_id: Union[None, List[str]],
    granule_id: Union[None, List[str]],
    start_timestamp: Union[None, str],
    end_timestamp: str,
    page_index: int,
) -> List[Dict[str, Any]]:
    """

    Args:
        provider_id: The unique ID of the provider(s) making the request.
        collection_id: The unique ID of collection(s) to compare.
        granule_id: The unique ID of granule(s) to compare.
        start_timestamp: Cumulus createdAt start time for date range to compare data.
        end_timestamp: Cumulus createdAt end-time for date range to compare data.
        page_index: The 0-based index of the results page to return.
        engine: The sqlalchemy engine to use for contacting the database.
    """
    with engine.begin() as connection:
        sql_results = connection.execute(
            get_catalog_sql(),
            [
                {
                    "provider_id": provider_id,
                    "collection_id": collection_id,
                    "granule_id": granule_id,
                    "start_timestamp": start_timestamp,
                    "end_timestamp": end_timestamp,
                    "page_index": page_index,
                    "page_size": PAGE_SIZE,
                }
            ],
        )

        granules = []
        for sql_result in sql_results:
            granules.append(
                {
                    "providerId": sql_result["provider_ids"],
                    "collectionId": sql_result["collection_id"],
                    "id": sql_result["id"],
                    "createdAt": str(sql_result["cumulus_create_time"]).replace(
                        "+00:00", "Z", 1
                    ),
                    "executionId": sql_result["execution_id"],
                    "ingestDate": str(sql_result["ingest_time"]).replace(
                        "+00:00", "Z", 1
                    ),
                    "lastUpdate": str(sql_result["last_update"]).replace(
                        "+00:00", "Z", 1
                    ),
                    "files": sql_result["files"],
                }
            )
        return granules


def get_catalog_sql() -> text:
    return text(
        """
SELECT
    *
    FROM
    (
    SELECT 
        *
        FROM
        (
            SELECT 
                granules.id,
                granules.collection_id, 
                granules.cumulus_granule_id, 
                granules.cumulus_create_time, 
                granules.execution_id, 
                granules.ingest_time, 
                granules.last_update
            FROM
            (SELECT DISTINCT
                granules.cumulus_granule_id
            FROM granules
            WHERE 
                (:granule_id is null or cumulus_granule_id=ANY(:granule_id)) and 
                (:collection_id is null or collection_id=ANY(:collection_id)) and 
                (:start_timestamp is null or cumulus_create_time>=:start_timestamp) and 
                (:end_timestamp is null or cumulus_create_time<:end_timestamp)
            ORDER BY cumulus_granule_id
            ) as granule_ids
            JOIN
                granules ON granule_ids.cumulus_granule_id = granules.cumulus_granule_id
        ) as granules
    JOIN LATERAL
        (SELECT array_agg(provider_collection_xref.provider_id) AS provider_ids
        FROM provider_collection_xref
        WHERE
            (:provider_id is null or provider_collection_xref.provider_id=ANY(:provider_id)) and
            granules.collection_id = provider_collection_xref.collection_id
    ) as granules_collections_and_providers on TRUE
    OFFSET :page_index*:page_size
    LIMIT :page_size+1
) as granules_collections_and_providers
LEFT JOIN LATERAL
    (SELECT json_agg(files) as files
    FROM (
    SELECT json_build_object(
        'name', files.name, 
        'cumulusArchiveLocation', files.cumulus_archive_location, 
        'orcaArchiveLocation', files.orca_archive_location,
        'keyPath', files.key_path,
        'sizeBytes', files.size_in_bytes,
        'hash', files.hash,
        'hashType', files.hash_type,
        'version', files.version) AS files
    FROM files
    WHERE granules_collections_and_providers.id = files.granule_id
    ) as files
) as grouped on TRUE"""
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
    LOGGER.error(message)
    return {
        "errorType": error_type,
        "httpStatus": http_status_code,
        "requestId": request_id,
        # CumulusLogger will error if a string containing '{' or '}' is passed in without escaping.
        "message": message.replace("{", "{{").replace("}", "}}"),
    }


def handler(
    event: Dict[str, Any], context: Any
) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    # noinspection SpellCheckingInspection
    """
    Entry point for the orca_catalog_reporting Lambda.
    Args:
        event: See schemas/input.json
        context: An object provided by AWS Lambda. Used for context tracking.

    Environment Vars: See requests_db.py's get_configuration for further details.

    Returns:
        See schemas/output.json
        Or, if an error occurs, see create_http_error_dict
    """
    LOGGER.setMetadata(event, context)

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

    db_connect_info = shared_db.get_configuration()
    try:
        result = task(
            event.get("providerId", None),
            event.get("collectionId", None),
            event.get("granuleId", None),
            event.get("startTimestamp", None),
            event["endTimestamp"],
            event["pageIndex"],
            db_connect_info,
        )
    except Exception as error:
        return create_http_error_dict(
            "InternalServerError",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            context.aws_request_id,
            error.__str__(),
        )

    try:
        with open("schemas/output.json", "r") as raw_schema:
            schema = json.loads(raw_schema.read())

        validate = fastjsonschema.compile(schema)
        validate(result)
    except JsonSchemaException as json_schema_exception:
        return create_http_error_dict(
            "InternalServerError",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            context.aws_request_id,
            json_schema_exception.__str__(),
        )

    return result
