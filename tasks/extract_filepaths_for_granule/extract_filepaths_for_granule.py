"""
Name: extract_filepaths_for_granule.py

Description:  Extracts the keys (filepaths) for a granule's files from a Cumulus Message.
"""

import json
import re
from typing import Any, Dict, List

import fastjsonschema as fastjsonschema
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from fastjsonschema import JsonSchemaException

# Set AWS powertools logger
LOGGER = Logger()

CONFIG_EXCLUDED_FILE_EXTENSIONS_KEY = "excludedFileExtensions"
CONFIG_FILE_BUCKETS_KEY = "fileBucketMaps"
CONFIG_BUCKETS_KEY = "buckets"

INPUT_GRANULES_KEY = "granules"
INPUT_GRANULE_RECOVERY_BUCKET_OVERRIDE_KEY = "recoveryBucketOverride"
INPUT_GRANULE_ID_KEY = "granuleId"
INPUT_GRANULE_FILES_KEY = "files"
INPUT_GRANULE_FILE_FILENAME_KEY = "fileName"
INPUT_GRANULE_FILE_KEY_KEY = "key"

OUTPUT_GRANULES_KEY = "granules"
OUTPUT_DESTINATION_BUCKET_KEY = "destBucket"
OUTPUT_KEY_KEY = "key"

# Generating schema validators can take time, so do it once and reuse.
try:
    with open("schemas/input.json", "r") as raw_schema:
        input_schema = json.loads(raw_schema.read())
        _VALIDATE_INPUT = fastjsonschema.compile(input_schema)
    with open("schemas/config.json", "r") as raw_schema:
        config_schema = json.loads(raw_schema.read())
        _VALIDATE_CONFIG = fastjsonschema.compile(config_schema)
    with open("schemas/output.json", "r") as raw_schema:
        output_schema = json.loads(raw_schema.read())
        _VALIDATE_OUTPUT = fastjsonschema.compile(output_schema)
except Exception as ex:
    LOGGER.error(f"Could not build schema validator: {ex}")
    raise


class ExtractFilePathsError(Exception):
    """Exception to be raised if any errors occur"""


def task(task_input: Dict[str, Any], config: Dict[str, Any]):
    """
    Task called by the handler to perform the work.

    This task will parse the input, removing the granuleId and file keys for a granule.

        Args:
            task_input: See schemas/input.json
            config: See schemas/config.json

        Returns:
            dict: dict containing granuleId and keys. See handler for detail.

        Raises:
            ExtractFilePathsError: An error occurred parsing the input.
    """
    try:
        exclude_file_types = config.get(CONFIG_EXCLUDED_FILE_EXTENSIONS_KEY, None)
        if exclude_file_types is None:
            exclude_file_types = []
        if len(exclude_file_types) == 0:
            LOGGER.debug(
                f"The configuration list {CONFIG_EXCLUDED_FILE_EXTENSIONS_KEY} is empty."
            )
        else:
            LOGGER.debug(
                f"The configuration {CONFIG_EXCLUDED_FILE_EXTENSIONS_KEY} "
                f"list {exclude_file_types} was found."
            )
    except KeyError as ke:
        message = f"Key {ke} is missing from the event configuration: {config}"
        LOGGER.error(message)
        raise KeyError(message)
    regex_buckets = get_regex_buckets(config)
    result_granules = []
    for a_granule in task_input[INPUT_GRANULES_KEY]:
        recovery_bucket_override = \
            a_granule.get(INPUT_GRANULE_RECOVERY_BUCKET_OVERRIDE_KEY, None)
        files = []
        for a_file in a_granule[INPUT_GRANULE_FILES_KEY]:
            file_name = a_file[INPUT_GRANULE_FILE_FILENAME_KEY]
            LOGGER.debug(f"Validating file {file_name}")
            # filtering excludedFileExtensions
            if should_exclude_files_type(file_name, exclude_file_types):
                LOGGER.info(f"Excluding file '{file_name}'")
            else:
                LOGGER.debug(f"File {file_name} will be restored")
                file_key = a_file[INPUT_GRANULE_FILE_KEY_KEY]
                LOGGER.debug(f"Retrieving information for {file_key}")

                if recovery_bucket_override is not None:
                    destination_bucket = recovery_bucket_override
                else:
                    matching_regex = next(
                        filter(lambda key: re.compile(key).match(file_name), regex_buckets),
                        None
                    )
                    if matching_regex is None:
                        raise ExtractFilePathsError(f"No matching regex for '{file_key}'")
                    destination_bucket = regex_buckets[matching_regex]

                LOGGER.debug(
                    f"Found retrieval destination {destination_bucket} for {file_name}"
                )

                files.append(
                    {
                        OUTPUT_KEY_KEY: file_key,
                        OUTPUT_DESTINATION_BUCKET_KEY: destination_bucket,
                    }
                )
        if len(files) == 0:
            LOGGER.warning(f"All files for granule '{a_granule['granuleId']}' excluded.")
        result_granules.append({
            "granuleId": a_granule[INPUT_GRANULE_ID_KEY],
            "keys": files,
        })
    return {OUTPUT_GRANULES_KEY: result_granules}


# todo: create dedicated unit tests
def get_regex_buckets(config: Dict[str, Any]) -> Dict[str, str]:
    """
    Gets a dict of regular expressions and the corresponding archive bucket for files
    matching the regex.

        Args:
            config: See schemas/config.json

        Returns:
            dict: dict containing regex and bucket.

        Raises:
            ExtractFilePathsError: An error occurred parsing the input.
    """
    file_buckets = config[CONFIG_FILE_BUCKETS_KEY]
    # file_buckets example:
    # [{'regex': '.*.h5$', 'sampleFileName': 'L0A_0420.h5', 'bucket': 'protected'},
    # {'regex': '.*.iso.xml$', 'sampleFileName': 'L0A_0420.iso.xml', 'bucket': 'protected'},
    # {'regex': '.*.h5.mp$', 'sampleFileName': 'L0A_0420.h5.mp', 'bucket': 'public'},
    # {'regex': '.*.cmr.json$', 'sampleFileName': 'L0A_0420.cmr.json', 'bucket': 'public'}]
    buckets = config[CONFIG_BUCKETS_KEY]
    # buckets example:
    # {"protected": {"name": "sndbx-cumulus-protected", "type": "protected"},
    # "internal": {"name": "sndbx-cumulus-internal", "type": "internal"},
    # "private": {"name": "sndbx-cumulus-private", "type": "private"},
    # "public": {"name": "sndbx-cumulus-public", "type": "public"}}
    regex_buckets = {}
    for regx in file_buckets:
        regex_buckets[regx["regex"]] = buckets[regx["bucket"]]["name"]
    # regex_buckets example:
    # {'.*.h5$': 'podaac-sndbx-cumulus-protected',
    #  '.*.iso.xml$': 'podaac-sndbx-cumulus-protected',
    #  '.*.h5.mp$': 'podaac-sndbx-cumulus-public',
    #  '.*.cmr.json$': 'podaac-sndbx-cumulus-public'}
    return regex_buckets


def should_exclude_files_type(file_key: str, exclude_file_types: List[str]) -> bool:
    """
    Tests whether or not file is included in {excludedFileExtensions} from copy_to_archive.
    Args:
        file_key: The key of the file within the s3 bucket.
        exclude_file_types: List of extensions to exclude in the backup.
    Returns:
        True if file should be excluded from copy, False otherwise.
    """
    for file_type in exclude_file_types:
        # Returns the first instance in the string that matches .ext or None if no match was found.
        if re.search(f"^.*{file_type}$", file_key) is not None:
            LOGGER.warning(
                f"The file {file_key} will not be restored "
                f"because it matches the excluded file type {file_type}."
            )
            return True
    return False


@LOGGER.inject_lambda_context
def handler(event: Dict[str, Dict[str, Any]],
            context: LambdaContext):  # pylint: disable-msg=unused-argument
    """Lambda handler. Extracts the key's for a granule from an input dict.

    Args:
        event: A dict with the following keys:
            granules (list(dict)): A list of dict with the following keys:
                granuleId (string): The id of a granule.
                files (list(dict)): list of dict with the following keys:
                    key (string): The key of the file to be returned.
                    other dictionary keys may be included, but are not used.
                other dictionary keys may be included, but are not used.

            Example:
                    {
                        "event": {
                            "granules": [
                                {
                                    "granuleId": "granxyz",
                                    "recoveryBucketOverride": "test-recovery-bucket",
                                    "version": "006",
                                    "files": [
                                    {
                                        "fileName": "file1",
                                        "key": "key1",
                                        "source": "s3://dr-test-sandbox-protected/file1",
                                        "type": "metadata"
                                    }
                                    ]
                                }
                            ]
                        }
                    }
        context: This object provides information about the lambda invocation, function,
            and execution env.

    Returns:
        dict: A dict with the following keys:

            'granules' (list(dict)): list of dict with the following keys:
                'granuleId' (string): The id of a granule.
                'keys' (list(string)): list of keys for the granule.

        Example:
            {"granules": [{"granuleId": "granxyz",
                         "keys": ["key1",
                                       "key2"]}]}

    Raises:
        ExtractFilePathsError: An error occurred parsing the input.
    """
    LOGGER.debug(f"event: {event}")
    task_input = event["input"]
    try:
        _VALIDATE_INPUT(task_input)
    except JsonSchemaException as json_schema_exception:
        LOGGER.error(json_schema_exception)
        raise

    config = event["config"]
    try:
        _VALIDATE_CONFIG(config)
    except JsonSchemaException as json_schema_exception:
        LOGGER.error(json_schema_exception)
        raise

    result = task(task_input, config)

    try:
        _VALIDATE_OUTPUT(result)
    except JsonSchemaException as json_schema_exception:
        LOGGER.error(json_schema_exception)
        raise

    return result
