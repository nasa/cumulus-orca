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
OUTPUT_ANOTHER_PAGE_KEY = "anotherPage"
OUTPUT_JOBS_KEY = "jobs"
JOBS_ID_KEY = "id"
JOBS_ORCA_ARCHIVE_LOCATION_KEY = "orcaArchiveLocation"
JOBS_STATUS_KEY = "status"
JOBS_INVENTORY_CREATION_TIME_KEY = "inventoryCreationTime"
JOBS_LAST_UPDATE_KEY = "lastUpdate"
JOBS_ERROR_MESSAGE_KEY = "errorMessage"
JOBS_REPORT_TOTALS_KEY = "reportTotals"
REPORT_TOTALS_ORPHAN_KEY = "orphan"
REPORT_TOTALS_PHANTOM_KEY = "phantom"
REPORT_TOTALS_CATALOG_MISMATCH_KEY = "catalogMismatch"

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
        page_index: int,
        db_connect_info: Dict[str, str],
) -> Dict[str, Any]:
    """
    Args:
        page_index: The 0-based index of the results page to return.
        db_connect_info: See requests_db.py's get_configuration for further details.
    """
    engine = shared_db.get_user_connection(db_connect_info)
    jobs = query_db(
        engine,
        page_index,
    )

    return {
        OUTPUT_ANOTHER_PAGE_KEY: len(jobs) > PAGE_SIZE,
        OUTPUT_JOBS_KEY: jobs[
                            0:PAGE_SIZE
                            ],  # we get one extra for anotherPage calculation.
    }


@retry_operational_error()
def query_db(
        engine: Engine,
        page_index: int,
) -> List[Dict[str, Any]]:
    """
    Gets jobs for the given page, up to PAGE_SIZE + 1 results.

    Args:
        engine: The sqlalchemy engine to use for contacting the database.
        page_index: The 0-based index of the results page to return.

    Returns:
        A list containing dicts matching the format of "jobs" in output.json.
    """
    LOGGER.info(f"Retrieving page '{page_index}' of jobs.'")
    with engine.begin() as connection:
        sql_results = connection.execute(
            get_jobs_sql(),
            [
                {
                    "page_index": page_index,
                    "page_size": PAGE_SIZE,
                }
            ],
        )

        jobs = []
        for sql_result in sql_results:
            jobs.append(
                {
                    JOBS_ID_KEY: sql_result["id"],
                    JOBS_ORCA_ARCHIVE_LOCATION_KEY: sql_result["orca_archive_location"],
                    JOBS_STATUS_KEY: sql_result["status"],
                    JOBS_INVENTORY_CREATION_TIME_KEY: sql_result["inventory_creation_time"],
                    JOBS_LAST_UPDATE_KEY: sql_result["last_update"],
                    JOBS_ERROR_MESSAGE_KEY: sql_result["error_message"],
                    JOBS_REPORT_TOTALS_KEY: {
                        REPORT_TOTALS_ORPHAN_KEY: sql_result["orphan_count"],
                        REPORT_TOTALS_PHANTOM_KEY: sql_result["phantom_count"],
                        REPORT_TOTALS_CATALOG_MISMATCH_KEY: sql_result["catalog_mismatch_count"]
                    }
                }
            )
        return jobs


def get_jobs_sql() -> text:  # pragma: no cover
    """
    SQL for getting jobs and associated metadata from Postgres.
    Formats datetimes in milliseconds since 1 January 1970 UTC.
    """
    return text(
        """
SELECT
    reconcile_job.id,
    orca_archive_location,
    reconcile_status.value as status,
    (EXTRACT(EPOCH FROM date_trunc('milliseconds', inventory_creation_time)
     AT TIME ZONE 'UTC') * 1000)::bigint as inventory_creation_time,
    (EXTRACT(EPOCH FROM date_trunc('milliseconds', reconcile_job.last_update)
     AT TIME ZONE 'UTC') * 1000)::bigint as last_update,
    error_message,
    (SELECT COUNT(*) FROM reconcile_orphan_report WHERE job_id=reconcile_job.id) AS orphan_count,
    (SELECT COUNT(*) FROM reconcile_phantom_report WHERE job_id=reconcile_job.id) AS phantom_count,
    (SELECT COUNT(*) FROM reconcile_catalog_mismatch_report
     WHERE job_id=reconcile_job.id) AS catalog_mismatch_count
FROM
    reconcile_job
JOIN
    reconcile_status ON status_id=reconcile_status.id
ORDER BY
    inventory_creation_time DESC
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
    Entry point for the internal_reconcile_report_job Lambda.
    Args:
        event: See schemas/input.json for details.
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
