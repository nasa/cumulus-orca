"""
Name: copy_to_archive.py
Description: Lambda function that takes a Cumulus message, extracts a list of files,
and copies those files from their current storage location into a staging/archive location.
"""
from typing import Any, Dict, List, Union

# Third party libraries
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from run_cumulus_task import run_cumulus_task

CONFIG_MULTIPART_CHUNKSIZE_MB_KEY = "s3MultipartChunksizeMb"
CONFIG_EXCLUDED_FILE_EXTENSIONS_KEY = "excludedFileExtensions"
CONFIG_DEFAULT_BUCKET_OVERRIDE_KEY = "defaultBucketOverride"
CONFIG_DEFAULT_STORAGE_CLASS_OVERRIDE_KEY = "defaultStorageClassOverride"

# Set AWS powertools logger
LOGGER = Logger()


# noinspection PyUnusedLocal
def task(event: Dict[str, Union[List[str], Dict]], context: object) -> Dict[str, Any]:
    """
    Converts event to a format accepted by ORCA's copy_to_archive lambda,
    then calls copy_to_archive and returns the result.

    Args:
        event: Passed through from {handler}
        context: An object required by AWS Lambda. Unused.

    Returns:
        A dict representing files to copy. See schemas/output.json for more information.
    """
    return event["input"]


@LOGGER.inject_lambda_context
def handler(event: Dict[str, Union[List[str], Dict]], context: LambdaContext) -> Any:
    """Lambda handler. Runs a cumulus task that
    Formats the input from the Cumulus format
    to the format required by ORCA's copy_to_archive Lambda,
    then calls copy_to_archive and returns the result.

    Args:
        event: Event passed into the step from the aws workflow.
            See schemas/input.json and schemas/config.json for more information.


        context: This object provides information about the lambda invocation, function,
            and execution env.

    Returns:
        The result of the cumulus task. See schemas/output.json for more information.
    """
    return run_cumulus_task(task, event, context)
