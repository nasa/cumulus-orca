"""
Name: copy_to_archive.py
Description: Lambda function that takes a Cumulus message, extracts a list of files,
and copies those files from their current storage location into a staging/archive location.
"""
import json
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Union

# Third party libraries
import boto3
import fastjsonschema as fastjsonschema
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from boto3.s3.transfer import MB, TransferConfig
from fastjsonschema import JsonSchemaException

import sqs_library

# Set AWS powertools logger
LOGGER = Logger()

OS_ENVIRON_DEFAULT_STORAGE_CLASS_KEY = "DEFAULT_STORAGE_CLASS"
OS_ENVIRON_ORCA_DEFAULT_BUCKET_KEY = "ORCA_DEFAULT_BUCKET"
OS_ENVIRON_DEFAULT_MULTIPART_CHUNKSIZE_MB_KEY = "DEFAULT_MULTIPART_CHUNKSIZE_MB"
OS_ENVIRON_METADATA_DB_QUEUE_URL_KEY = "METADATA_DB_QUEUE_URL"

EVENT_CONFIG_KEY = "config"
EVENT_INPUT_KEY = "input"
EVENT_OPTIONAL_VALUES_KEY = "optionalValues"

CONFIG_PROVIDER_NAME_KEY = "providerName"
CONFIG_MULTIPART_CHUNKSIZE_MB_KEY = "s3MultipartChunksizeMb"
CONFIG_EXCLUDED_FILE_EXTENSIONS_KEY = "excludedFileExtensions"
CONFIG_DEFAULT_BUCKET_OVERRIDE_KEY = "defaultBucketOverride"
CONFIG_DEFAULT_STORAGE_CLASS_OVERRIDE_KEY = "defaultStorageClassOverride"
CONFIG_PROVIDER_ID_KEY = "providerId"
CONFIG_COLLECTION_SHORT_NAME_KEY = "collectionShortname"
CONFIG_COLLECTION_VERSION_KEY = "collectionVersion"
CONFIG_EXECUTION_ID_KEY = "executionId"

FILE_BUCKET_KEY = "bucket"
FILE_FILEPATH_KEY = "key"
FILE_HASH_KEY = "checksum"
FILE_HASH_TYPE_KEY = "checksumType"

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


def should_exclude_files_type(file_key: str, exclude_file_types: List[str]) -> bool:
    """
    Tests whether file is included in {excludedFileExtensions}.
    Args:
        file_key: The key of the file within the s3 bucket.
        exclude_file_types: List of extensions to exclude in the backup.
    Returns:
        True if file should be excluded from copy, False otherwise.
    """
    for file_type in exclude_file_types:
        # Returns the first instance in the string that matches .ext or None if no match was found.
        if re.search(f"^.*{file_type}$", file_key) is not None:
            return True
    return False


def copy_granule_between_buckets(
    source_bucket_name: str,
    source_key: str,
    destination_bucket: str,
    destination_key: str,
    multipart_chunksize_mb: int,
    storage_class: str,
) -> Dict[str, str]:
    """
    Copies granule from source bucket to destination.
    Also queries the destination_bucket to get additional metadata file info.
    Args:
        source_bucket_name: The name of the bucket in which the granule is currently located.
        source_key: source Granule path excluding s3://[bucket]/
        destination_bucket: The name of the bucket the granule is to be copied to.
        destination_key: Destination granule path excluding s3://[bucket]/
        multipart_chunksize_mb: The maximum size of chunks to use when copying.
        storage_class: The storage class to store in.
    Returns:
        A dictionary containing all the file metadata needed
        for reconciliation with Cumulus with the following keys:
                "cumulusArchiveLocation" (str):
                    Cumulus bucket the file is stored in.
                "orcaArchiveLocation" (str):
                    ORCA archive bucket the file object is stored in.
                "keyPath" (str):
                    Full AWS key path including file name of the file
                    where the file resides in ORCA.
                "sizeInBytes" (str):
                    Size of the object in bytes
                "version" (str):
                    Latest version of the file in the archive bucket
                "ingestTime" (str):
                    Date and time the file was originally ingested into ORCA.
                "etag" (str):
                    etag of the file object in the archive bucket.
    """
    s3 = boto3.client("s3")
    copy_source = {"Bucket": source_bucket_name, "Key": source_key}
    s3.copy(
        copy_source,
        destination_bucket,
        destination_key,
        ExtraArgs={
            "StorageClass": storage_class,
            "MetadataDirective": "COPY",
            "ContentType": s3.head_object(Bucket=source_bucket_name, Key=source_key)[
                "ContentType"
            ],
            "ACL": "bucket-owner-full-control",  # Sets the x-amz-acl URI Request Parameter.
                                                 # Needed for cross-OU copies.
        },
        Config=TransferConfig(multipart_chunksize=multipart_chunksize_mb * MB),
    )
    # get metadata info from latest file version
    file_versions = s3.list_object_versions(
        Bucket=destination_bucket, Prefix=destination_key
    )
    latest_version = next(  # Find the first item in file_versions["Versions"]
                            # that has "IsLatest" set to true.
        filter(lambda file_version: file_version["IsLatest"], file_versions["Versions"])
    )
    LOGGER.info("collecting metadata from file version")
    etag = latest_version["ETag"]
    size_in_bytes = latest_version["Size"]
    version = latest_version["VersionId"]
    files_dictionary = {
        "cumulusArchiveLocation": source_bucket_name,
        "orcaArchiveLocation": destination_bucket,
        "keyPath": destination_key,
        "sizeInBytes": size_in_bytes,
        "version": version,
        "ingestTime": datetime.now(timezone.utc).isoformat(),
        "etag": etag,
        "storageClass": storage_class,
    }
    return files_dictionary


# noinspection PyUnusedLocal
def task(task_input: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Copies the files in input['files']
    to the ORCA archive bucket defined in ORCA_DEFAULT_BUCKET.

        Environment Variables:
            ORCA_DEFAULT_BUCKET (string, required):
                Name of the default archive bucket.
                Overridden by bucket specified in config.
            DEFAULT_MULTIPART_CHUNKSIZE_MB (int, optional):
                The default maximum size of chunks to use when copying.
                Can be overridden by collection config.
            METADATA_DB_QUEUE_URL (string, required):
                SQS URL of the metadata queue.

    Args:
        task_input: See schemas/input.json
        config: See schemas/config.json

    Returns:
        A dict representing input and copied files. See schemas/output.json for more information.
    """
    exclude_file_types = config.get(CONFIG_EXCLUDED_FILE_EXTENSIONS_KEY, None)
    if exclude_file_types is None:
        exclude_file_types = []

    destination_bucket = get_destination_bucket_name(config)
    storage_class = get_storage_class(config)

    multipart_chunksize_mb_str = config.get(CONFIG_MULTIPART_CHUNKSIZE_MB_KEY, None)
    if multipart_chunksize_mb_str is None:
        multipart_chunksize_mb = int(os.environ[OS_ENVIRON_DEFAULT_MULTIPART_CHUNKSIZE_MB_KEY])
        LOGGER.debug(
            "{CONFIG_MULTIPART_CHUNKSIZE_MB_KEY} is not set for config."
            "Using default value of {multipart_chunksize_mb}.",
            CONFIG_MULTIPART_CHUNKSIZE_MB_KEY=CONFIG_MULTIPART_CHUNKSIZE_MB_KEY,
            multipart_chunksize_mb=multipart_chunksize_mb,
        )
    else:
        multipart_chunksize_mb = int(multipart_chunksize_mb_str)

    try:
        metadata_queue_url = os.environ.get(OS_ENVIRON_METADATA_DB_QUEUE_URL_KEY)
        if metadata_queue_url is None or len(metadata_queue_url) == 0:
            raise KeyError(
                f"{OS_ENVIRON_METADATA_DB_QUEUE_URL_KEY} environment variable is not set.")
    except KeyError:
        LOGGER.error(f"{OS_ENVIRON_METADATA_DB_QUEUE_URL_KEY} environment variable is not set.")
        raise

    granule_data = {}
    copied_file_urls = []

    # initiate empty SQS body dict
    sqs_body = {"provider": {}, "collection": {}, "granule": {}}
    sqs_body["provider"]["name"] = config.get(CONFIG_PROVIDER_NAME_KEY, None)
    sqs_body["provider"]["providerId"] = config[CONFIG_PROVIDER_ID_KEY]
    sqs_body["collection"]["shortname"] = config[CONFIG_COLLECTION_SHORT_NAME_KEY]
    sqs_body["collection"]["version"] = config[CONFIG_COLLECTION_VERSION_KEY]
    # Cumulus currently creates collectionId by concatenating
    # shortname + ___ + version
    # See https://github.com/nasa/cumulus-dashboard/blob/
    # 18a278ee5a1ac5181ec035b3df0665ef5acadcb0/app/src/js/utils/format.js#L342
    sqs_body["collection"]["collectionId"] = (
        config[CONFIG_COLLECTION_SHORT_NAME_KEY] + "___" + config[CONFIG_COLLECTION_VERSION_KEY]
    )
    # Iterate through the input granules (>= 0 granules expected)
    for granule in task_input["granules"]:
        # noinspection PyPep8Naming
        granuleId = granule["granuleId"]
        if granuleId not in granule_data.keys():
            granule_data[granuleId] = {"granuleId": granuleId, "files": []}
        # populate the SQS body for granules
        sqs_body["granule"]["cumulusGranuleId"] = granuleId
        sqs_body["granule"]["cumulusCreateTime"] = datetime.fromtimestamp(
            granule["createdAt"] / 1000, timezone.utc
        ).isoformat()
        sqs_body["granule"]["executionId"] = config[CONFIG_EXECUTION_ID_KEY]
        sqs_body["granule"]["ingestTime"] = datetime.now(timezone.utc).isoformat()
        sqs_body["granule"]["lastUpdate"] = datetime.now(timezone.utc).isoformat()
        sqs_body["granule"]["files"] = []

        # Iterate through the files in a granule object
        for file in granule["files"]:
            file_filepath = file[FILE_FILEPATH_KEY]
            file_bucket = file[FILE_BUCKET_KEY]
            file_source_uri = f"s3://{file_bucket}/{file_filepath}"
            file_hash = file.get(FILE_HASH_KEY, None)
            file_hash_type = file.get(FILE_HASH_TYPE_KEY, None)
            if should_exclude_files_type(file_filepath, exclude_file_types):
                LOGGER.info(
                    f"Excluding {file_filepath} from backup "
                    f"because of collection configured {CONFIG_EXCLUDED_FILE_EXTENSIONS_KEY}."
                )
                continue
            result = copy_granule_between_buckets(
                source_bucket_name=file_bucket,
                source_key=file_filepath,
                destination_bucket=destination_bucket,
                destination_key=file_filepath,
                multipart_chunksize_mb=multipart_chunksize_mb,
                storage_class=storage_class,
            )

            result["name"] = file_filepath.split("/")[
                -1
            ]  # since fileName is no longer available in event
            result["hash"] = file_hash
            result["hashType"] = file_hash_type
            copied_file_urls.append(file_source_uri)
            LOGGER.info(
                f"Copied {file_filepath} into archive bucket {destination_bucket}."
            )
            # Add file record to metadata SQS message
            LOGGER.debug(
                "Adding the files dictionary to the SQS body. {result}.", result=result
            )
            sqs_body["granule"]["files"].append(result)
        # post to metadata SQS for each granule
        sqs_library.post_to_metadata_queue(sqs_body, metadata_queue_url)

    # Using "copied_to_orca" instead of "copied_to_archive" until we decouple from Cumulus.
    return {"granules": task_input["granules"], "copied_to_orca": copied_file_urls}


def get_destination_bucket_name(config: Dict[str, Any]) -> str:
    """
    Returns the bucket to copy to.
    Uses the collection value in config if present,
    otherwise the default.

    Environment Vars:
        ORCA_DEFAULT_BUCKET (str): Name of the default archive
                                   bucket files should be
                                   archived to.

    Args:
        config: See schemas/config.json for more information.

    Returns:
        The name of the bucket to use.
    """
    try:
        destination_bucket = config[CONFIG_DEFAULT_BUCKET_OVERRIDE_KEY]
    except KeyError:
        LOGGER.warning(
            f"{CONFIG_DEFAULT_BUCKET_OVERRIDE_KEY} is not set. "
            f"Using {OS_ENVIRON_ORCA_DEFAULT_BUCKET_KEY} environment value."
        )
        destination_bucket = None

    if destination_bucket is None:
        try:
            destination_bucket = os.environ.get(
                OS_ENVIRON_ORCA_DEFAULT_BUCKET_KEY, None
            )
            if destination_bucket is None or len(destination_bucket) == 0:
                raise KeyError(
                    f"{OS_ENVIRON_ORCA_DEFAULT_BUCKET_KEY} environment variable is not set."
                )
        except KeyError:
            LOGGER.error(
                f"{OS_ENVIRON_ORCA_DEFAULT_BUCKET_KEY} environment variable is not set."
            )
            raise

    return destination_bucket


def get_storage_class(config: Dict[str, Any]) -> str:
    """
    Returns the storage class to use on ingest.
    Uses the collection value in config if present,
    otherwise the default.

    Environment Vars:
        DEFAULT_STORAGE_CLASS (str):
            The class of storage to use when ingesting files.
            Can be overridden by collection config.
            Must match value in storage_class table.

    Args:
        config: See schemas/config.json for more information.

    Returns:
        The name of the storage class to use.
    """
    try:
        # run_cumulus_task checked config against config.json,
        # so the number of values this can be is limited.
        storage_class = config[CONFIG_DEFAULT_STORAGE_CLASS_OVERRIDE_KEY]
    except KeyError:
        LOGGER.warning(
            f"{CONFIG_DEFAULT_STORAGE_CLASS_OVERRIDE_KEY} is not set. "
            f"Using {OS_ENVIRON_DEFAULT_STORAGE_CLASS_KEY} environment value."
        )
        storage_class = None

    if storage_class is None:
        try:
            storage_class = os.environ.get(OS_ENVIRON_DEFAULT_STORAGE_CLASS_KEY, None)
            if storage_class is None or len(storage_class) == 0:
                raise KeyError(
                    f"{OS_ENVIRON_DEFAULT_STORAGE_CLASS_KEY} environment variable is not set."
                )
        except KeyError:
            LOGGER.error(
                f"{OS_ENVIRON_DEFAULT_STORAGE_CLASS_KEY} environment variable is not set."
            )
            raise

    return storage_class


# Copied from request_from_archive.py
def set_optional_event_property(event: Dict[str, Any], target_path_cursor: Dict,
                                target_path_segments: List) -> None:
    """Sets the optional variable value from event if present, otherwise sets to None.
    Args:
        event: See schemas/input.json.
        target_path_cursor: Cursor of the current section to check.
        target_path_segments: The path to the current cursor.
    Returns:
        None
    """
    for optionalValueTargetPath in target_path_cursor:
        temp_target_path_segments = target_path_segments.copy()
        temp_target_path_segments.append(optionalValueTargetPath)
        if isinstance(target_path_cursor[optionalValueTargetPath], dict):
            set_optional_event_property(
                event,
                target_path_cursor[optionalValueTargetPath],
                temp_target_path_segments
            )
        elif isinstance(target_path_cursor[optionalValueTargetPath], str):
            source_path = target_path_cursor[optionalValueTargetPath]
            source_path_segments = source_path.split(".")

            # ensure that the path up to the target_path exists
            event_cursor = event
            for target_path_segment in temp_target_path_segments[:-1]:
                event_cursor[target_path_segment] =\
                    event_cursor.get(target_path_segment, {})
                event_cursor = event_cursor[target_path_segment]
            event_cursor[temp_target_path_segments[-1]] = None

            # get the value for the optional element
            source_path_cursor = event
            for source_path_segment in source_path_segments:
                source_path_cursor = source_path_cursor.get(source_path_segment, None)
                if source_path_cursor is None:
                    LOGGER.info(f"When retrieving '{'.'.join(temp_target_path_segments)}', "
                                f"no value found in '{source_path}' at key {source_path_segment}. "
                                f"Defaulting to null.")
                    break
            event_cursor[temp_target_path_segments[-1]] = source_path_cursor
        else:
            raise Exception(f"Illegal type {type(target_path_cursor[optionalValueTargetPath])} "
                            f"found at {'.'.join(temp_target_path_segments)}")


# noinspection PyUnusedLocal
@LOGGER.inject_lambda_context
def handler(event: Dict[str, Union[List[str], Dict]], context: LambdaContext) -> Any:
    """Lambda handler. Runs a cumulus task that
    Copies the files in event['input']['files']
    to the default ORCA bucket. Environment variables must be set to
    provide a default ORCA bucket to store the files in.

    Environment Vars:
        DEFAULT_MULTIPART_CHUNKSIZE_MB (int):
            The default maximum size of chunks to use when copying.
            Can be overridden by collection config.
        DEFAULT_STORAGE_CLASS (str):
            The class of storage to use when ingesting files.
            Can be overridden by collection config.
            Must match value in storage_class table.
        ORCA_DEFAULT_BUCKET (str):
            Name of the default
            archive bucket that files should be archived to.
        METADATA_DB_QUEUE_URL (string, required): SQS URL of the metadata queue.

    Args:
        event: Event passed into the step from the aws workflow.
            See schemas/input.json and schemas/config.json for more information.

        context: This object provides information about the lambda invocation, function,
            and execution env.

    Returns:
        See schemas/output.json for more information.
    """
    LOGGER.debug(f"event: {event}")

    # set the optional variables to None if not configured
    try:
        set_optional_event_property(event, event.get(EVENT_OPTIONAL_VALUES_KEY, {}), [])
    except Exception as ex:
        LOGGER.error(ex)
        raise ex
    try:
        _VALIDATE_INPUT(event[EVENT_INPUT_KEY])
    except JsonSchemaException as json_schema_exception:
        LOGGER.error(json_schema_exception)
        raise

    try:
        _VALIDATE_CONFIG(event[EVENT_CONFIG_KEY])
    except JsonSchemaException as json_schema_exception:
        LOGGER.error(json_schema_exception)
        raise

    result = task(event[EVENT_INPUT_KEY], event[EVENT_CONFIG_KEY])

    try:
        _VALIDATE_OUTPUT(result)
    except JsonSchemaException as json_schema_exception:
        LOGGER.error(json_schema_exception)
        raise

    return result
