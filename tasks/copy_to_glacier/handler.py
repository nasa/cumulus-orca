import os
import re
from re import Match
from typing import Dict, Any, List, Optional, Union

import boto3
from run_cumulus_task import run_cumulus_task

CONFIG_FILE_STAGING_DIRECTORY_KEY = 'fileStagingDir'
CONFIG_BUCKETS_KEY = 'buckets'
CONFIG_COLLECTION_KEY = 'collection'
CONFIG_URL_PATH_KEY = 'url_path'

COLLECTION_NAME_KEY = 'name'
COLLECTION_VERSION_KEY = 'version'
COLLECTION_URL_PATH_KEY = 'url_path'
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
                                 destination_key: str) -> None:
    """
    Copies granule from source bucket to destination.
    Args:
        source_bucket_name: The name of the bucket in which the granule is currently located.
        source_key: source Granule path excluding s3://[bucket]/
        destination_bucket: The name of the bucket the granule is to be copied to.
        destination_key: Destination granule path excluding s3://[bucket]/
    """
    s3 = boto3.client('s3')
    copy_source = {
        'Bucket': source_bucket_name,
        'Key': source_key
    }
    s3.copy(
        copy_source, destination_bucket, destination_key,
        ExtraArgs={
            'StorageClass': 'GLACIER',
            'MetadataDirective': 'COPY',
            'ContentType': s3.head_object(Bucket=source_bucket_name, Key=source_key)['ContentType']
        }
    )

# noinspection PyUnusedLocal
def task(event: Dict[str, Union[List[str], Dict]], context: object) -> Dict[str, Any]:
    """
    Copies the files in {event}['input'] from the collection specified in {config} to the {config}'s 'glacier' bucket.

    Args:
        event: Passed through from {handler}


        context: An object required by AWS Lambda. Unused.

    Returns:
        A dict with the following keys:
            granules (List[Dict[str, Union[str, bytes, list]]]): A list of dicts where each dict has the following keys:
                granuleId (str): The filename from the granule url.
                files (List): A list of dicts with the following keys:
                    path (str): config['fileStagingDir']
                    url_path (str): config['url_path'] if present, otherwise config['fileStagingDir']
                    bucket (str): The name of the config['buckets'] that matches the filename.
                    filename (str): The granule_url from event['input']
                    # todo: It is confusing that granuleId holds the filename while filename holds the url.
                    name (str): The granule_url from event['input']
                    # todo: This inclusion implies to me we are matching an un-linked schema.
            input (list): event['input']
    """
    print(event)
    event_input = event.get('input')
    granules_list = event_input.get('granules')
    config = event.get('config')
    collection = config.get(CONFIG_COLLECTION_KEY)
    exclude_file_types = collection.get(COLLECTION_META_KEY, {}).get(EXCLUDE_FILE_TYPES_KEY, [])
    glacier_bucket = config.get(CONFIG_BUCKETS_KEY).get('glacier').get('name')
    granule_data = {}
    copied_file_urls = []

    # Iterate through the input granules (>= 0 granules expected)
    for granule in granules_list:
        granuleId = granule['granuleId']
        if granuleId not in granule_data.keys():
            granule_data[granuleId] = {'granuleId': granuleId, 'files': []}

        # Iterate through the files in a granule object
        for file in granule['files']:
            source_name = file['name']
            source_filepath = file['filepath']
            if should_exclude_files_type(source_name, exclude_file_types):
                print(f"Excluding {source_name} from glacier backup because of collection configured {EXCLUDE_FILE_TYPES_KEY}.")
                continue
            copy_granule_between_buckets(source_bucket_name=file['bucket'],
                                         source_key=source_filepath,
                                         destination_bucket=glacier_bucket,
                                         destination_key=source_filepath)
            copied_file_urls.append(file['filename'])
            print(f"Copied {source_filepath} into glacier storage bucket {glacier_bucket}.")

    return {'granules': granules_list, 'copied_to_glacier': copied_file_urls}

# handler that is provided to aws lambda
def handler(event: Dict[str, Union[List[str], Dict]], context: object) -> Any:
    """Lambda handler. Runs a cumulus task that
    copies the files in {event}['input'] from the collection specified in {config} to the {config}'s 'glacier' bucket.

    Args:
        event: Event passed into the step from the aws workflow. A dict with the following keys:
            input (list): A list of urls for granules to copy. Defaults to an empty list.
            config (dict): A dict with the following keys:
                collection (dict): The collection from AWS.
                    See https://nasa.github.io/cumulus/docs/data-cookbooks/sips-workflow
                    A dict with the following keys:
                    name (str): The name of the collection.
                        Used when generating the default value for {event}[config][fileStagingDir].
                    version (str): The version of the collection.
                        Used when generating the default value for {event}[config][fileStagingDir].
                    files (list[Dict]): A list of dicts representing file types within the collection.
                        The first file where the file's ['regex'] matches the filename from the input
                        Is used to identify the bucket referenced in return's['granules'][filename]['files']['bucket']
                        Each dict contains the following keys:
                            regex (str): The regex that all files in the bucket must match with their name.
                            bucket (str): The name of the bucket containing the files.
                    url_path (str): Used when calling {copy_granule_between_buckets} as a part of the destination_key.

                fileStagingDir (str): Is placed as the value of the return's['granules'][filename]['files']['path']
                    Will default to name__version where 'name' and 'version' come from 'config[collection]'.
                buckets (dict): A dict with the following keys:
                    glacier (dict): A dict with the following keys:
                        name (str): The name of the bucket to copy to.
                url_path (str): Is placed as the value of the return's['granules'][filename]['files']['url_path']
                    Will default to the fileStagingDir.


        context: An object required by AWS Lambda. Unused.

    Returns:
        The result of the cumulus task.
    """
    return run_cumulus_task(task, event, context)
