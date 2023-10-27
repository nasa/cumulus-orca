import json
import os
from http import HTTPStatus
from typing import Any, Dict, List, Union

import fastjsonschema as fastjsonschema
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from fastjsonschema import JsonSchemaException
from orca_shared.database import shared_db
from orca_shared.database.shared_db import retry_operational_error
from sqlalchemy import text
from sqlalchemy.future import Engine

OS_ENVIRON_DB_CONNECT_INFO_SECRET_ARN_KEY = "DB_CONNECT_INFO_SECRET_ARN"  # nosec

OUTPUT_JOB_ID_KEY = "jobId"
OUTPUT_ANOTHER_PAGE_KEY = "anotherPage"
OUTPUT_MISMATCHES_KEY = "mismatches"
MISMATCHES_COLLECTION_ID_KEY = "collectionId"
MISMATCHES_GRANULE_ID_KEY = "granuleId"
MISMATCHES_FILENAME_KEY = "filename"
MISMATCHES_KEY_PATH_KEY = "keyPath"
MISMATCHES_CUMULUS_ARCHIVE_LOCATION_KEY = "cumulusArchiveLocation"
MISMATCHES_ORCA_ETAG_KEY = "orcaEtag"
MISMATCHES_S3_ETAG_KEY = "s3Etag"
MISMATCHES_ORCA_LAST_UPDATE_KEY = "orcaGranuleLastUpdate"
MISMATCHES_S3_LAST_UPDATE_KEY = "s3FileLastUpdate"
MISMATCHES_ORCA_SIZE_IN_BYTES_KEY = "orcaSizeInBytes"
MISMATCHES_S3_SIZE_IN_BYTES_KEY = "s3SizeInBytes"
MISMATCHES_ORCA_STORAGE_CLASS_KEY = "orcaStorageClass"
MISMATCHES_S3_STORAGE_CLASS_KEY = "s3StorageClass"
MISMATCHES_DISCREPANCY_TYPE_KEY = "discrepancyType"
MISMATCHES_COMMENT_KEY = "comment"

# Set AWS powertools logger
LOGGER = Logger()

PAGE_SIZE = 100

# Generating schema validators can take time, so do it once and reuse.
try:
    with open("schemas/input.json", "r") as raw_schema:
        input_schema = json.loads(raw_schema.read())
        _VALIDATE_INPUT = fastjsonschema.compile(input_schema)
    with open("schemas/output.json", "r") as raw_schema:
        output_schema = json.loads(raw_schema.read())
        _VALIDATE_OUTPUT = fastjsonschema.compile(output_schema)
except Exception as ex:
    LOGGER.error(f"Could not build schema validator: {ex}")
    raise


def task(
    job_id: int,
    page_index: int,
    db_connect_info: Dict[str, str],
) -> Dict[str, Any]:
    """
    Args:
        job_id: The unique ID of job/report.
        page_index: The 0-based index of the results page to return.
        db_connect_info: See requests_db.py's get_configuration for further details.
    """
    engine = shared_db.get_user_connection(db_connect_info)
    mismatches = query_db(
        engine,
        job_id,
        page_index,
    )

    return {
        OUTPUT_JOB_ID_KEY: job_id,
        OUTPUT_ANOTHER_PAGE_KEY: len(mismatches) > PAGE_SIZE,
        OUTPUT_MISMATCHES_KEY: mismatches[
            0:PAGE_SIZE
        ],  # we get one extra for anotherPage calculation.
    }


@retry_operational_error()
def query_db(
    engine: Engine,
    job_id: str,
    page_index: int,
) -> List[Dict[str, Any]]:
    """
    Gets mismatches for the given job/page, up to PAGE_SIZE + 1 results.

    Args:
        engine: The sqlalchemy engine to use for contacting the database.
        job_id: The unique ID of job/report.
        page_index: The 0-based index of the results page to return.

    Returns:
        A list containing dicts matching the format of "mismatches" in output.json.
    """
    LOGGER.info(f"Retrieving page '{page_index}' of reports for job '{job_id}'")
    with engine.begin() as connection:
        sql_results = connection.execute(
            get_mismatches_sql(),
            [
                {
                    "job_id": job_id,
                    "page_index": page_index,
                    "page_size": PAGE_SIZE,
                }
            ],
        )

        mismatches = []
        for sql_result in sql_results.mappings():
            mismatches.append(
                {
                    MISMATCHES_COLLECTION_ID_KEY: sql_result["collection_id"],
                    MISMATCHES_GRANULE_ID_KEY: sql_result["granule_id"],
                    MISMATCHES_FILENAME_KEY: sql_result["filename"],
                    MISMATCHES_KEY_PATH_KEY: sql_result["key_path"],
                    MISMATCHES_CUMULUS_ARCHIVE_LOCATION_KEY: sql_result[
                        "cumulus_archive_location"
                    ],
                    MISMATCHES_ORCA_ETAG_KEY: sql_result["orca_etag"],
                    MISMATCHES_S3_ETAG_KEY: sql_result["s3_etag"],
                    MISMATCHES_ORCA_LAST_UPDATE_KEY: sql_result["orca_last_update"],
                    MISMATCHES_S3_LAST_UPDATE_KEY: sql_result["s3_last_update"],
                    MISMATCHES_ORCA_SIZE_IN_BYTES_KEY: sql_result["orca_size_in_bytes"],
                    MISMATCHES_S3_SIZE_IN_BYTES_KEY: sql_result["s3_size_in_bytes"],
                    MISMATCHES_ORCA_STORAGE_CLASS_KEY: sql_result["orca_storage_class"],
                    MISMATCHES_S3_STORAGE_CLASS_KEY: sql_result["s3_storage_class"],
                    MISMATCHES_DISCREPANCY_TYPE_KEY: sql_result["discrepancy_type"],
                    MISMATCHES_COMMENT_KEY: sql_result["comment"],
                }
            )
        return mismatches


def get_mismatches_sql() -> text:  # pragma: no cover
    """
    SQL for getting mismatch report entries for a given job_id, page_size, and page_index.
    Formats datetimes in milliseconds since 1 January 1970 UTC.
    """
    return text(
        """
SELECT
    collection_id,
    granule_id,
    filename,
    key_path,
    cumulus_archive_location,
    orca_etag,
    s3_etag,
    (EXTRACT(EPOCH FROM date_trunc('milliseconds', orca_last_update)
     AT TIME ZONE 'UTC') * 1000)::bigint as orca_last_update,
    (EXTRACT(EPOCH FROM date_trunc('milliseconds', s3_last_update)
     AT TIME ZONE 'UTC') * 1000)::bigint as s3_last_update,
    orca_size_in_bytes,
    s3_size_in_bytes,
    storage_class.value AS orca_storage_class,
    s3_storage_class,
    discrepancy_type,
    CASE
        WHEN (reconcile_job.inventory_creation_time <= orca_last_update)
            THEN 'Error may be due to race condition, and should be checked manually.'
        WHEN (reconcile_job.inventory_creation_time <= s3_last_update)
            THEN 'Error may be due to race condition, and should be checked manually.'
    END AS comment
    FROM reconcile_catalog_mismatch_report
    INNER JOIN reconcile_job ON
    (
        reconcile_job.id = reconcile_catalog_mismatch_report.job_id
    )
    INNER JOIN storage_class ON
    (
        orca_storage_class_id=storage_class.id
    )
    WHERE job_id = :job_id
    ORDER BY collection_id, granule_id, filename
    OFFSET :page_index*:page_size
    LIMIT :page_size+1"""
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


def check_env_variable(env_name: str) -> str:
    """
    Checks for the lambda environment variable.
    Args:
        env_name (str): The environment variable name set in lambda configuration.
    Raises: KeyError in case the environment variable is not found.
    """
    try:
        env_value = os.environ[env_name]
        if len(env_value) == 0 or env_value is None:
            raise KeyError(f"Empty value for {env_name}")
    except KeyError:
        LOGGER.error(f"{env_name} environment value not found.")
        raise

    return env_value


@LOGGER.inject_lambda_context
def handler(
    event: Dict[str, Union[str, int]], context: LambdaContext
) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Entry point for the internal_reconcile_report_mismatch Lambda.
    Args:
        event: See schemas/input.json
        context: This object provides information about the lambda invocation, function,
            and execution env.
    Environment Vars:
        DB_CONNECT_INFO_SECRET_ARN (string):
            Secret ARN of the AWS secretsmanager secret for connecting to the database.
        See shared_db.py's get_configuration for further details.

    Returns:
        See schemas/output.json
        Or, if an error occurs, see create_http_error_dict
            400 if input does not match schemas/input.json.
            500 if an error occurs when querying the database.
    """
    try:
        try:
            _VALIDATE_INPUT(event)
        except JsonSchemaException as json_schema_exception:
            return create_http_error_dict(
                "BadRequest",
                HTTPStatus.BAD_REQUEST,
                context.aws_request_id,
                json_schema_exception.__str__(),
            )

        db_connect_info = shared_db.get_configuration(
            check_env_variable(OS_ENVIRON_DB_CONNECT_INFO_SECRET_ARN_KEY)
        )

        result = task(
            event["jobId"],
            event["pageIndex"],
            db_connect_info,
        )
        _VALIDATE_OUTPUT(result)

        return result
    except Exception as error:
        return create_http_error_dict(
            "InternalServerError",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            context.aws_request_id,
            error.__str__(),
        )
