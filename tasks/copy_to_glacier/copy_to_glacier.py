"""
Name: copy_to_glacier.py
Description: Lambda function that takes a Cumulus message, extracts a list of files, and copies those files from their current storage location into a staging/glacier location.
"""
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Union

# Third party libraries
import boto3
from boto3.s3.transfer import MB, TransferConfig
from cumulus_logger import CumulusLogger
from run_cumulus_task import run_cumulus_task

import sqs_library

CONFIG_MULTIPART_CHUNKSIZE_MB_KEY = "multipart_chunksize_mb"
CONFIG_EXCLUDE_FILE_TYPES_KEY = "excludeFileTypes"
# Set Cumulus LOGGER
LOGGER = CumulusLogger()


def should_exclude_files_type(granule_url: str, exclude_file_types: List[str]) -> bool:
    """
    Tests whether or not file is included in {excludeFileTypes} from copy to glacier.
    Args:
        granule_url: s3 url of granule.
        exclude_file_types: List of extensions to exclude in the backup
    Returns:
        True if file should be excluded from copy, False otherwise.
    """
    for file_type in exclude_file_types:
        # Returns the first instance in the string that matches .ext or None if no match was found.
        if re.search(f"^.*{file_type}$", granule_url) is not None:
            return True
    return False


def copy_granule_between_buckets(
    source_bucket_name: str,
    source_key: str,
    destination_bucket: str,
    destination_key: str,
    multipart_chunksize_mb: int,
) -> Dict[str, str]:
    """
    Copies granule from source bucket to destination. Also queries the destination_bucket to get additional metadata file info.
    Args:
        source_bucket_name: The name of the bucket in which the granule is currently located.
        source_key: source Granule path excluding s3://[bucket]/
        destination_bucket: The name of the bucket the granule is to be copied to.
        destination_key: Destination granule path excluding s3://[bucket]/
        multipart_chunksize_mb: The maximum size of chunks to use when copying.
    Returns:
        A dictionary containing all the file metadata needed for reconciliation with Cumulus with the following keys:
                "cumulusArchiveLocation" (str): Cumulus S3 bucket where the file is stored in.
                "orcaArchiveLocation" (str): ORCA S3 Glacier bucket that the file object is stored in
                "keyPath" (str): Full AWS key path including file name of the file where the file resides in ORCA.
                "sizeInBytes" (str): Size of the object in bytes
                "version" (str): Latest version of the file in the S3 Glacier bucket
                "ingestTime" (str): Date and time the file was originally ingested into ORCA.
                "etag" (str): etag of the file object in the AWS S3 Glacier bucket.
    """
    s3 = boto3.client("s3")
    copy_source = {"Bucket": source_bucket_name, "Key": source_key}
    s3.copy(
        copy_source,
        destination_bucket,
        destination_key,
        ExtraArgs={
            "StorageClass": "GLACIER",
            "MetadataDirective": "COPY",
            "ContentType": s3.head_object(Bucket=source_bucket_name, Key=source_key)[
                "ContentType"
            ],
            "ACL": "bucket-owner-full-control",  # Sets the x-amz-acl URI Request Parameter. Needed for cross-OU copies.
        },
        Config=TransferConfig(multipart_chunksize=multipart_chunksize_mb * MB),
    )
    # get metadata info from latest file version
    file_versions = s3.list_object_versions(
        Bucket=destination_bucket, Prefix=destination_key
    )
    for ver in file_versions["Versions"]:
        if ver["IsLatest"]:
            LOGGER.info("collecting metadata from file version")
            etag = ver["ETag"]
            sizeInBytes = ver["Size"]
            version = ver["VersionId"]
            break
    files_dictionary = {
        "cumulusArchiveLocation": source_bucket_name,
        "orcaArchiveLocation": destination_bucket,
        "keyPath": destination_key,
        "sizeInBytes": sizeInBytes,
        "version": version,
        "ingestTime": datetime.now(timezone.utc).isoformat(),
        "etag": etag,
    }
    return files_dictionary


# noinspection PyUnusedLocal
def task(event: Dict[str, Union[List[str], Dict]], context: object) -> Dict[str, Any]:
    """
    Copies the files in {event}['input']
    to the ORCA glacier bucket defined in ORCA_DEFAULT_BUCKET.

        Environment Variables:
            ORCA_DEFAULT_BUCKET (string, required): Name of the default ORCA S3 Glacier bucket.
            DEFAULT_MULTIPART_CHUNKSIZE_MB (int, optional): The default maximum size of chunks to use when copying.
                Can be overridden by collection config.
            METADATA_DB_QUEUE_URL (string, required): SQS URL of the metadata queue.

    Args:
        event: Passed through from {handler}
        context: An object required by AWS Lambda. Unused.

    Returns:
        A dict representing input and copied files. See schemas/output.json for more information.
    """
    LOGGER.debug(event)
    event_input = event["input"]
    granules_list = event_input["granules"]
    config = event["config"]

    exclude_file_types = config.get(CONFIG_EXCLUDE_FILE_TYPES_KEY, None)
    if exclude_file_types is None:
        exclude_file_types = []

    # TODO: Should look at bucket type orca and check for default
    #      Should also be flexible enough to handle input precedence order of
    #      - task input
    #      - collection configuration
    #      - default value in buckets
    try:
        default_bucket = os.environ.get("ORCA_DEFAULT_BUCKET", None)
        if default_bucket is None or len(default_bucket) == 0:
            raise KeyError("ORCA_DEFAULT_BUCKET environment variable is not set.")
    except KeyError:
        LOGGER.error("ORCA_DEFAULT_BUCKET environment variable is not set.")
        raise

    multipart_chunksize_mb_str = config.get(CONFIG_MULTIPART_CHUNKSIZE_MB_KEY, None)
    if multipart_chunksize_mb_str is None:
        multipart_chunksize_mb = int(os.environ["DEFAULT_MULTIPART_CHUNKSIZE_MB"])
        LOGGER.debug(
            "{CONFIG_MULTIPART_CHUNKSIZE_MB_KEY} is not set for config. Using default value of {multipart_chunksize_mb}.",
            CONFIG_MULTIPART_CHUNKSIZE_MB_KEY=CONFIG_MULTIPART_CHUNKSIZE_MB_KEY,
            multipart_chunksize_mb=multipart_chunksize_mb,
        )
    else:
        multipart_chunksize_mb = int(multipart_chunksize_mb_str)

    try:
        metadata_queue_url = os.environ.get("METADATA_DB_QUEUE_URL")
        if metadata_queue_url is None or len(metadata_queue_url) == 0:
            raise KeyError("METADATA_DB_QUEUE_URL environment variable is not set.")
    except KeyError:
        LOGGER.error("METADATA_DB_QUEUE_URL environment variable is not set.")
        raise

    granule_data = {}
    copied_file_urls = []

    # initiate empty SQS body dict
    sqs_body = {}
    sqs_body["provider"] = {}
    sqs_body["collection"] = {}
    sqs_body["granule"] = {}
    # 'providerName' set to None because Cumulus only returns providerId for now.
    # In case it is available in the future, update orca_copy_to_glacier_workflow.asl.json and config.json as needed
    sqs_body["provider"]["providerName"] = None
    sqs_body["provider"]["providerId"] = config["providerId"]
    sqs_body["collection"]["shortname"] = config["collectionShortname"]
    sqs_body["collection"]["version"] = config["collectionVersion"]
    # Cumulus currently creates collectionId by concating shortname + ___ + version 
    # See https://github.com/nasa/cumulus-dashboard/blob/18a278ee5a1ac5181ec035b3df0665ef5acadcb0/app/src/js/utils/format.js#L342
    sqs_body["collection"]["collectionId"] = (
        config["collectionShortname"] + "___" + config["collectionVersion"]
    )
    # Iterate through the input granules (>= 0 granules expected)
    for granule in granules_list:
        # noinspection PyPep8Naming
        granuleId = granule["granuleId"]
        if granuleId not in granule_data.keys():
            granule_data[granuleId] = {"granuleId": granuleId, "files": []}
        # populate the SQS body for granules
        sqs_body["granule"]["cumulusGranuleId"] = granuleId
        sqs_body["granule"]["cumulusCreateTime"] = granule["createdAt"].replace("Z", "+00:00")
        LOGGER.info(sqs_body)
        sqs_body["granule"]["executionId"] = config["executionId"]
        sqs_body["granule"]["ingestTime"] = datetime.now(timezone.utc).isoformat()
        sqs_body["granule"]["lastUpdate"] = datetime.now(timezone.utc).isoformat()
        sqs_body["granule"]["files"] = []
        LOGGER.info(sqs_body)

        # Iterate through the files in a granule object
        for file in granule["files"]:
            source_name = file["name"]
            source_filepath = file["filepath"]
            if should_exclude_files_type(source_name, exclude_file_types):
                LOGGER.info(
                    "Excluding {source_name} from glacier backup because of collection configured {CONFIG_EXCLUDE_FILE_TYPES_KEY}.",
                    source_name=source_name,
                    CONFIG_EXCLUDE_FILE_TYPES_KEY=CONFIG_EXCLUDE_FILE_TYPES_KEY,
                )
                continue
            result = copy_granule_between_buckets(
                source_bucket_name=file["bucket"],
                source_key=source_filepath,
                destination_bucket=default_bucket,
                destination_key=source_filepath,
                multipart_chunksize_mb=multipart_chunksize_mb,
            )
            result["name"] = source_name

            result["hash"] = file.get("checksum", None)
            result["hashType"] = file.get("checksumType", None)
            copied_file_urls.append(file["filename"])
            LOGGER.info(
                "Copied {source_filepath} into glacier storage bucket {default_bucket}.",
                source_filepath=source_filepath,
                default_bucket=default_bucket,
            )
            # Add file record to metadata SQS message
            LOGGER.debug(
                "Adding the files dictionary to the SQS body {result}.", result=result
            )
            sqs_body["granule"]["files"].append(result)
        # post to metadata SQS for each granule
        sqs_library.post_to_metadata_queue(sqs_body, metadata_queue_url)

    return {"granules": granules_list, "copied_to_glacier": copied_file_urls}


# handler that is provided to aws lambda
def handler(event: Dict[str, Union[List[str], Dict]], context: object) -> Any:
    """Lambda handler. Runs a cumulus task that
    Copies the files in {event}['input']
    to the default ORCA bucket. Environment variables must be set to
    provide a default ORCA bucket to store the files in.
        Environment Vars:
            ORCA_DEFAULT_BUCKET (str, required): Name of the default S3 Glacier
                                                 ORCA bucket files should be
                                                 archived to.
            DEFAULT_MULTIPART_CHUNKSIZE_MB (int, required): The default maximum size of chunks to use when copying.
                                                                 Can be overridden by collection config.
            METADATA_DB_QUEUE_URL (string, required): SQS URL of the metadata queue.

    Args:
        event: Event passed into the step from the aws workflow.
            See schemas/input.json and schemas/config.json for more information.


        context: An object required by AWS Lambda. Unused.

    Returns:
        The result of the cumulus task. See schemas/output.json for more information.
    """
    return run_cumulus_task(task, event, context)
