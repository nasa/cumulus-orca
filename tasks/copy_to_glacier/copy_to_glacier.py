import re
import os
from typing import Dict, Any, List, Union

import boto3
from boto3.s3.transfer import TransferConfig, MB
from run_cumulus_task import run_cumulus_task

CONFIG_COLLECTION_KEY = 'collection'
CONFIG_MULTIPART_CHUNKSIZE_MB_KEY = 'multipart_chunksize_mb'

COLLECTION_META_KEY = 'meta'
EXCLUDE_FILE_TYPES_KEY = 'excludeFileTypes'


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
    Copies the files in {event}['input'] from the collection specified in {config}
    to the ORCA glacier bucket defined in ORCA_DEFAULT_BUCKET.

        Environment Variables:
            ORCA_DEFAULT_BUCKET (string, required): Name of the default ORCA S3 Glacier bucket.
            DEFAULT_MULTIPART_CHUNKSIZE_MB (int, optional): The default maximum size of chunks to use when copying. Can be overridden by collection config.

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

    collection = config.get(CONFIG_COLLECTION_KEY, {})
    exclude_file_types = collection.get(COLLECTION_META_KEY, {}).get(EXCLUDE_FILE_TYPES_KEY, [])

    # TODO: Should look at bucket type orca and check for default
    #      Should also be flexible enough to handle input precedence order of
    #      - task input
    #      - collection configuration
    #      - default value in buckets
    try:
        default_bucket = os.environ.get('ORCA_DEFAULT_BUCKET', None)
        if default_bucket is None or len(default_bucket) == 0:
            raise KeyError('ORCA_DEFAULT_BUCKET environment variable is not set.')
    except KeyError:
        # TODO: Change this to a logging statement
        print('ORCA_DEFAULT_BUCKET environment variable is not set.')
        raise
    try:
        multipart_chunksize_mb = int(config[CONFIG_MULTIPART_CHUNKSIZE_MB_KEY])
    except KeyError:
        # TODO: Change this to a logging statement
        multipart_chunksize_mb = int(os.environ['DEFAULT_MULTIPART_CHUNKSIZE_MB'])
        print(f'{CONFIG_MULTIPART_CHUNKSIZE_MB_KEY} is not set for config. Using default value of {multipart_chunksize_mb}.')

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
            source_name = file['name']
            source_filepath = file['filepath']
            if should_exclude_files_type(source_name, exclude_file_types):
                print(
                    f"Excluding {source_name} from glacier backup "
                    f"because of collection configured {EXCLUDE_FILE_TYPES_KEY}.")
                continue
            copy_granule_between_buckets(source_bucket_name=file['bucket'],
                                         source_key=source_filepath,
                                         destination_bucket=default_bucket,
                                         destination_key=source_filepath,
                                         multipart_chunksize_mb=multipart_chunksize_mb)
            copied_file_urls.append(file['filename'])
            print(f"Copied {source_filepath} into glacier storage bucket {default_bucket}.")

    return {'granules': granules_list, 'copied_to_glacier': copied_file_urls}


# handler that is provided to aws lambda
def handler(event: Dict[str, Union[List[str], Dict]], context: object) -> Any:
    """Lambda handler. Runs a cumulus task that
    Copies the files in {event}['input'] from the collection specified in
    {config} to the default ORCA bucket. Environment variables must be set to
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
