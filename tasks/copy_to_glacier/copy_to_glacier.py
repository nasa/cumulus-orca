"""
Name: copy_to_glacier.py
Description: Lambda function that takes a Cumulus message, extracts a list of files,
and copies those files from their current storage location into a staging/glacier location.
"""
import re
import os
from typing import Dict, Any, List, Union

import boto3
from boto3.s3.transfer import TransferConfig, MB
from run_cumulus_task import run_cumulus_task

CONFIG_MULTIPART_CHUNKSIZE_MB_KEY = 'multipart_chunksize_mb'
CONFIG_EXCLUDE_FILE_TYPES_KEY = 'excludeFileTypes'
CONFIG_COLLECTION_BUCKET_KEY = 'collectionBucket'

FILE_FILENAME_KEY = "fileName"
FILE_BUCKET_KEY = "bucket"
FILE_FILEPATH_KEY = "key"
FILE_SOURCE_URI_KEY = "source"


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


def copy_granule_between_buckets(source_bucket_name: str, source_key: str, destination_bucket: str,
                                 destination_key: str, multipart_chunksize_mb: int) -> None:
    """
    Copies granule from source bucket to destination.
    Args:
        source_bucket_name: The name of the bucket in which the granule is currently located.
        source_key: source Granule path excluding s3://[bucket]/
        destination_bucket: The name of the bucket the granule is to be copied to.
        destination_key: Destination granule path excluding s3://[bucket]/
        multipart_chunksize_mb: The maximum size of chunks to use when copying.
    Returns:
        None
    """
    s3 = boto3.client('s3')
    copy_source = {
        'Bucket': source_bucket_name,
        'Key': source_key
    }
    s3.copy(
        copy_source,
        destination_bucket, destination_key,
        ExtraArgs={
            'StorageClass': 'GLACIER',
            'MetadataDirective': 'COPY',
            'ContentType': s3.head_object(Bucket=source_bucket_name, Key=source_key)['ContentType'],
            'ACL': 'bucket-owner-full-control'  # Sets the x-amz-acl URI Request Parameter. Needed for cross-OU copies.
        },
        Config=TransferConfig(multipart_chunksize=multipart_chunksize_mb * MB)
    )


# noinspection PyUnusedLocal
def task(event: Dict[str, Union[List[str], Dict]], context: object) -> Dict[str, Any]:
    """
    Copies the files in {event}['input']
    to the ORCA glacier bucket defined in ORCA_DEFAULT_BUCKET.

        Environment Variables:
            ORCA_DEFAULT_BUCKET (string, required): Name of the default ORCA S3 Glacier bucket.
            DEFAULT_MULTIPART_CHUNKSIZE_MB (int, optional): The default maximum size of chunks to use when copying.
                Can be overridden by collection config.

    Args:
        event: Passed through from {handler}
        context: An object required by AWS Lambda. Unused.

    Returns:
        A dict representing input and copied files. See schemas/output.json for more information.
    """
    # TODO: Possibly remove print statement and change to a logging statement.
    print(event)
    event_input = event['input']
    granules_list = event_input['granules']
    config = event['config']

    exclude_file_types = config.get(CONFIG_EXCLUDE_FILE_TYPES_KEY, None)
    if exclude_file_types is None:
        exclude_file_types = []

    # TODO: Should look at bucket type orca and check for default
    #      Should also be flexible enough to handle input precedence order of
    #      - task input
    #      - collection configuration
    #      - default value in buckets
    default_bucket = config.get(CONFIG_COLLECTION_BUCKET_KEY, None)
    if default_bucket is None:
        try:
            default_bucket = os.environ.get('ORCA_DEFAULT_BUCKET', None)
            if default_bucket is None or len(default_bucket) == 0:
                raise KeyError('ORCA_DEFAULT_BUCKET environment variable is not set.')
        except KeyError:
            # TODO: Change this to a logging statement
            print('ORCA_DEFAULT_BUCKET environment variable is not set.')
            raise

    multipart_chunksize_mb_str = config.get(CONFIG_MULTIPART_CHUNKSIZE_MB_KEY, None)
    if multipart_chunksize_mb_str is None:
        # TODO: Change this to a logging statement
        multipart_chunksize_mb = int(os.environ['DEFAULT_MULTIPART_CHUNKSIZE_MB'])
        print(f'{CONFIG_MULTIPART_CHUNKSIZE_MB_KEY} is not set for config. '
              f'Using default value of {multipart_chunksize_mb}.')
    else:
        multipart_chunksize_mb = int(multipart_chunksize_mb_str)

    granule_data = {}
    copied_file_urls = []

    # Iterate through the input granules (>= 0 granules expected)
    for granule in granules_list:
        # noinspection PyPep8Naming
        granuleId = granule['granuleId']
        if granuleId not in granule_data.keys():
            granule_data[granuleId] = {'granuleId': granuleId, 'files': []}

        # Iterate through the files in a granule object
        for file in granule['files']:
            file_name = file[FILE_FILENAME_KEY]
            file_filepath = file[FILE_FILEPATH_KEY]
            file_bucket = file[FILE_BUCKET_KEY]
            file_source_uri = file[FILE_SOURCE_URI_KEY]

            if should_exclude_files_type(file_name, exclude_file_types):
                print(
                    f"Excluding {file_name} from glacier backup "
                    f"because of collection configured {CONFIG_EXCLUDE_FILE_TYPES_KEY}.")
                continue
            copy_granule_between_buckets(source_bucket_name=file_bucket,
                                         source_key=file_filepath,
                                         destination_bucket=default_bucket,
                                         destination_key=file_filepath,
                                         multipart_chunksize_mb=multipart_chunksize_mb)
            copied_file_urls.append(file_source_uri)
            print(f"Copied {file_filepath} into glacier storage bucket {default_bucket}.")

    return {'granules': granules_list, 'copied_to_glacier': copied_file_urls}


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

    Args:
        event: Event passed into the step from the aws workflow.
            See schemas/input.json and schemas/config.json for more information.


        context: An object required by AWS Lambda. Unused.

    Returns:
        The result of the cumulus task. See schemas/output.json for more information.
    """
    return run_cumulus_task(task, event, context)
