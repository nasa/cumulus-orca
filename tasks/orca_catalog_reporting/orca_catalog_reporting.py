import json
from http import HTTPStatus
from typing import Dict, Any, List, Union
import os
import fastjsonschema as fastjsonschema
from cumulus_logger import CumulusLogger
from fastjsonschema import JsonSchemaException
from orca_shared.database import shared_db
from orca_shared.database.shared_db import retry_operational_error
from sqlalchemy import text
from sqlalchemy.future import Engine

LOGGER = CumulusLogger()

PAGE_SIZE = 100
# Generating schema validators can take time, so do it once and reuse.
try:
    with open("schemas/input.json", "r") as raw_schema:
        _INPUT_VALIDATE = fastjsonschema.compile(json.loads(raw_schema.read()))
except Exception as ex:
    LOGGER.error(f"Could not build schema validator: {ex}")
    raise

try:
    with open("schemas/output.json", "r") as raw_schema:
        _OUTPUT_VALIDATE = fastjsonschema.compile(json.loads(raw_schema.read()))
except Exception as ex:
    LOGGER.error(f"Could not build schema validator: {ex}")
    raise


def task(
    provider_id: Union[None, List[str]],
    collection_id: Union[None, List[str]],
    granule_id: Union[None, List[str]],
    start_timestamp: Union[None, int],
    end_timestamp: int,
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
    start_timestamp: Union[None, int],
    end_timestamp: int,
    page_index: int,
) -> List[Dict[str, Any]]:
    """

    Args:
        engine: The sqlalchemy engine to use for contacting the database.
        provider_id: The unique ID of the provider(s) making the request.
        collection_id: The unique ID of collection(s) to compare.
        granule_id: The unique ID of granule(s) to compare.
        start_timestamp: Cumulus createdAt start time for date range to compare data.
        end_timestamp: Cumulus createdAt end-time for date range to compare data.
        page_index: The 0-based index of the results page to return.
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
                    "providerId": sql_result["provider_id"],
                    "collectionId": sql_result["collection_id"],
                    "id": sql_result["cumulus_granule_id"],
                    "createdAt": sql_result["cumulus_create_time"],
                    "executionId": sql_result["execution_id"],
                    "ingestDate": sql_result["ingest_time"],
                    "lastUpdate": sql_result["last_update"],
                    "files": sql_result["files"],
                }
            )
        return granules


def get_catalog_sql() -> text:  # pragma: no cover
    return text(
        # todo: Optimize for large data sets. https://bugs.earthdata.nasa.gov/browse/ORCA-286
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
                granules.provider_id,
                granules.collection_id, 
                granules.cumulus_granule_id, 
                (EXTRACT(EPOCH FROM date_trunc('milliseconds', granules.cumulus_create_time) AT TIME ZONE 'UTC') * 1000)::bigint as cumulus_create_time, 
                granules.execution_id, 
                (EXTRACT(EPOCH FROM date_trunc('milliseconds', granules.ingest_time) AT TIME ZONE 'UTC') * 1000)::bigint as ingest_time, 
                (EXTRACT(EPOCH FROM date_trunc('milliseconds', granules.last_update) AT TIME ZONE 'UTC') * 1000)::bigint as last_update
            FROM
            (SELECT DISTINCT
                granules.cumulus_granule_id
            FROM granules
            WHERE 
                (:provider_id is null or provider_id=ANY(:provider_id)) and 
                (:collection_id is null or collection_id=ANY(:collection_id)) and 
                (:granule_id is null or cumulus_granule_id=ANY(:granule_id)) and 
                (:start_timestamp is null or (EXTRACT(EPOCH FROM date_trunc('milliseconds', cumulus_create_time) AT TIME ZONE 'UTC') * 1000)::bigint>=:start_timestamp) and 
                (:end_timestamp is null or (EXTRACT(EPOCH FROM date_trunc('milliseconds', cumulus_create_time) AT TIME ZONE 'UTC') * 1000)::bigint<:end_timestamp)
            ) as granule_ids
            JOIN
                granules ON granule_ids.cumulus_granule_id = granules.cumulus_granule_id
        ) as granules
    ORDER BY cumulus_granule_id, provider_id
    OFFSET :page_index*:page_size
    LIMIT :page_size+1
) as granules
LEFT JOIN LATERAL
    (SELECT COALESCE(json_agg(files), '[]'::json) as files
    FROM (
    SELECT json_build_object(
        'name', files.name, 
        'cumulusArchiveLocation', files.cumulus_archive_location, 
        'orcaArchiveLocation', files.orca_archive_location,
        'keyPath', files.key_path,
        'sizeBytes', files.size_in_bytes,
        'hash', files.hash,
        'hashType', files.hash_type,
        'storageClass', storage_class.value,
        'version', files.version) AS files
    FROM files
    JOIN
        storage_class ON storage_class_id=storage_class.id
    WHERE granules.id = files.granule_id
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
        "message": message,
    }


def handler(
    event: Dict[str, Union[str, int]], context: Any
) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    # noinspection SpellCheckingInspection
    """
    Entry point for the orca_catalog_reporting Lambda.
    Args:
        event: See schemas/input.json
        context: An object provided by AWS Lambda. Used for context tracking.

    Environment Vars:
        DB_CONNECT_INFO_SECRET_ARN (string): Secret ARN of the AWS secretsmanager secret for connecting to the database.
        See shared_db.py's get_configuration for further details.

    Returns:
        See schemas/output.json
        Or, if an error occurs, see create_http_error_dict
            400 if input does not match schemas/input.json. 500 if an error occurs when querying the database.
    """
    try:
        LOGGER.setMetadata(event, context)

        try:
            _INPUT_VALIDATE(event)
        except JsonSchemaException as json_schema_exception:
            return create_http_error_dict(
                "BadRequest",
                HTTPStatus.BAD_REQUEST,
                context.aws_request_id,
                json_schema_exception.__str__(),
            )
        # get the secret ARN from the env variable
        try:
            db_connect_info_secret_arn = os.environ["DB_CONNECT_INFO_SECRET_ARN"]
        except KeyError as key_error:
            LOGGER.error("DB_CONNECT_INFO_SECRET_ARN environment value not found.")
            raise

        db_connect_info = shared_db.get_configuration(db_connect_info_secret_arn)

        result = task(
            event.get("providerId", None),
            event.get("collectionId", None),
            event.get("granuleId", None),
            event.get("startTimestamp", None),
            event["endTimestamp"],
            event["pageIndex"],
            db_connect_info,
        )
        _OUTPUT_VALIDATE(result)

        return result
    except Exception as error:
        return create_http_error_dict(
            "InternalServerError",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            context.aws_request_id,
            error.__str__(),
        )
