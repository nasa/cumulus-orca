import json
import os
from http import HTTPStatus
from typing import Dict, Union, Any, List

import fastjsonschema as fastjsonschema
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from fastjsonschema import JsonSchemaException
from orca_shared.database.adapters.api import get_configuration
from orca_shared.database.use_cases import create_user_uri

from src.adapters.storage.rdbms import StorageAdapterPostgres
from src.entities.orphan import OrphanRecordFilter
from src.use_cases import get_orphans_page

INPUT_JOB_ID_KEY = "jobId"
INPUT_PAGE_INDEX_KEY = "pageIndex"

OUTPUT_JOB_ID_KEY = "jobId"
OUTPUT_ANOTHER_PAGE_KEY = "anotherPage"
OUTPUT_ORPHANS_KEY = "orphans"
ORPHANS_KEY_PATH_KEY = "keyPath"
ORPHANS_S3_ETAG_KEY = "s3Etag"
ORPHANS_S3_LAST_UPDATE_KEY = "s3FileLastUpdate"
ORPHANS_S3_SIZE_IN_BYTES_KEY = "s3SizeInBytes"
ORPHANS_STORAGE_CLASS_KEY = "s3StorageClass"

PAGE_SIZE = 100

# Set AWS powertools logger
LOGGER = Logger()

# Generating schema validators can take time, so do it once and reuse.
try:
    temp = os.getcwd()
    with open("schemas/input.json", "r") as raw_schema:
        input_schema = json.loads(raw_schema.read())
        _VALIDATE_INPUT = fastjsonschema.compile(input_schema)
    with open("schemas/output.json", "r") as raw_schema:
        output_schema = json.loads(raw_schema.read())
        _VALIDATE_OUTPUT = fastjsonschema.compile(output_schema)
except Exception as ex:
    LOGGER.error(f"Could not build schema validator: {ex}")
    raise


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


OS_ENVIRON_DB_CONNECT_INFO_SECRET_ARN_KEY = "DB_CONNECT_INFO_SECRET_ARN"  # nosec


def handler(
        event: Dict[str, Union[str, int]], context: LambdaContext
) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Entry point for the internal_reconcile_report_orphan Lambda.
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

        db_connect_info = get_configuration(
            check_env_variable(OS_ENVIRON_DB_CONNECT_INFO_SECRET_ARN_KEY),
            LOGGER
        )

        storage_adapter = StorageAdapterPostgres(
            create_user_uri(
                db_connect_info, LOGGER))

        orphan_record_filter = \
            OrphanRecordFilter(job_id=event[INPUT_JOB_ID_KEY],
                               page_index=event[INPUT_PAGE_INDEX_KEY],
                               page_size=PAGE_SIZE)
        orphan_record_page = get_orphans_page.task(
            orphan_record_filter,
            storage_adapter,
            LOGGER
        )
        result = {
            OUTPUT_JOB_ID_KEY: event[INPUT_JOB_ID_KEY],
            OUTPUT_ORPHANS_KEY: [{
                ORPHANS_KEY_PATH_KEY: orphan.key_path,
                ORPHANS_S3_ETAG_KEY: orphan.etag,
                ORPHANS_S3_LAST_UPDATE_KEY: orphan.last_update,
                ORPHANS_S3_SIZE_IN_BYTES_KEY: orphan.size_in_bytes,
                ORPHANS_STORAGE_CLASS_KEY: orphan.storage_class,
            } for orphan in orphan_record_page.orphans],
            OUTPUT_ANOTHER_PAGE_KEY: orphan_record_page.another_page,
        }

        _VALIDATE_OUTPUT(result)

        return result
    except Exception as error:
        return create_http_error_dict(
            "InternalServerError",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            context.aws_request_id,
            error.__str__(),
        )
