from re import Match
from typing import Dict, Any, List, Optional, AnyStr, Union

from run_cumulus_task import run_cumulus_task
import boto3
import re
import os

CONFIG_FILE_STAGING_DIRECTORY_KEY = 'fileStagingDir'
CONFIG_BUCKETS_KEY = 'buckets'
CONFIG_COLLECTION_KEY = 'collection'

COLLECTION_NAME_KEY = 'name'
COLLECTION_VERSION_KEY = 'version'
COLLECTION_URL_PATH_KEY = 'url_path'

file_types_to_exclude = [".example"]  # ex: [".tar", ".gz"]


def should_exclude_files_type(granule_url: str) -> bool:
    """
    Tests whether or not file is included in {file_types_to_exclude} from copy to glacier.
    Args:
        granule_url: s3 url of granule.
    Returns:
        True if file should be excluded from copy, False otherwise.
    """
    for file_type in file_types_to_exclude:
        # Returns the first instance in the string that matches .ext or None if no match was found.
        if re.search(f"^.*{file_type}$", granule_url) is not None:
            return True
    return False


def copy_granule_between_buckets(source_bucket: str, source_key: str, destination_bucket: str,
                                 destination_key: str) -> None:
    """
    Copies granule from source bucket to destination.
    Args:
        source_bucket: The name of the bucket in which the granule is currently located.
        source_key: source Granule path excluding s3://[bucket]/
        destination_bucket: The name of the bucket the granule is to be copied to.
        destination_key: Destination granule path excluding s3://[bucket]/
    """
    s3 = boto3.client('s3')
    copy_source = {
        'Bucket': source_bucket,
        'Key': source_key
    }
    s3.copy(
        copy_source, destination_bucket, destination_key,
        ExtraArgs={
            'StorageClass': 'GLACIER',
            'MetadataDirective': 'COPY',
            'ContentType': s3.head_object(Bucket=source_bucket, Key=source_key)["ContentType"]
        }
    )


# todo: Once aws upgrades to Python 3.8, have this return Optional[Match[AnyStr]]
def get_source_bucket_and_key(granule_url) -> Optional[Match]:
    """
    Parses source bucket and key from s3 url.
    Args:
        granule_url: s3 url path to granule.
    Returns:  TODO: Strip 0th element from return value.
        re.Match object with argument [1] equal to source bucket and [2] equal to source key.
    """
    return re.search("s3://([^/]*)/(.*)", granule_url)


def get_bucket(filename: str, collection_files: List[Dict[str, Any]]) -> str:
    """
    Retrieves the first file pattern in {collection_files} where the file's ['regex'] matches the {filename}
    And returns that file's ['bucket']
    Args:
        filename: Granule file name.
        collection_files: List of collection files.
            Each file is a dict with the following keys:
                regex (str): The regex that all files in the bucket must match with their name.
                bucket (str): The name of the bucket containing the files.
    Returns:
        Bucket name.
    """
    for file in collection_files:
        if re.match(file.get('regex', '*.'), filename):
            return file['bucket']
    return 'public'


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
                path (str): config['fileStagingDir']
                url_path (str): config['url_path'] if present, otherwise config['fileStagingDir']
                bucket (str): The name of the config['buckets'] that matches the filename.
                filename (str): The granule_url from event['input']
                name (str): The granule_url from event['input']
            input (list): event['input']
    """
    print(event)
    granule_urls = event.get('input', [])
    config = event.get('config')
    collection = config.get(CONFIG_COLLECTION_KEY)
    config[CONFIG_FILE_STAGING_DIRECTORY_KEY] = \
        config.get(CONFIG_FILE_STAGING_DIRECTORY_KEY,
                   f"{collection[COLLECTION_NAME_KEY]}__{collection[COLLECTION_VERSION_KEY]}")
    glacier_bucket = config.get(CONFIG_BUCKETS_KEY).get('glacier').get('name')
    collection_url_path = collection.get(COLLECTION_URL_PATH_KEY)
    granule_data = {}
    for granule_url in granule_urls:
        filename = os.path.basename(granule_url)
        if filename not in granule_data.keys():
            granule_data[filename] = {'granuleId': filename, 'files': []}
        granule_data[filename]['files'].append(
            {
                'path': config[CONFIG_FILE_STAGING_DIRECTORY_KEY],
                'url_path': config.get('url_path', config[CONFIG_FILE_STAGING_DIRECTORY_KEY]),
                'bucket': get_bucket(filename, collection.get('files', [])),
                'filename': granule_url,
                'name': granule_url
            }
        )
        if should_exclude_files_type(granule_url):
            continue  # todo: This should be logged in output so users know that their file wasn't copied and why.
        source = get_source_bucket_and_key(granule_url)  # todo: Handle 'None' return value.
        copy_granule_between_buckets(source_bucket=source[1],
                                     source_key=source[2],
                                     destination_bucket=glacier_bucket,
                                     destination_key=f"{collection_url_path}/{filename}")

    final_output = list(granule_data.values())
    return {"granules": final_output, "input": granule_urls}


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
                        Used when generating the default value for {config}[fileStagingDir]
                    version (str): The version of the collection.
                        Used when constructing the default fileStagingDir.
                    files (list[Dict]): A list of dicts representing file types within the collection.
                        The first file where the file's ['regex'] matches the filename from the input
                        Is used to identify the bucket referenced in return's['granules'][filename]['files']['bucket']
                        Each dict contains the following keys:
                            regex (str): The regex that all files in the bucket must match with their name.
                            bucket (str): The name of the bucket containing the files.
                    url_path (str): Used when calling {copy_granule_between_buckets} as a part of the destination_key.

                fileStagingDir (str): Unused except in output if url_path is missing.
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


if __name__ == '__main__':
    dummy_event = {
        "input": [
            "s3://ghrcsbxw-internal/file-staging/ghrcsbxw/goesrpltavirisng__1/goesrplt_avng_20170328t210208.tar.gz"
        ],
        "config": {
            "files_config": [
                {
                    "regex": "^(.*).*\\.cmr.xml$",
                    "sampleFileName": "goesrplt_avng_20170323t184858.tar.gz.cmr.xml",
                    "bucket": "public"
                },
                {
                    "regex": "^(.*).*(\\.gz|\\.hdr|clip)$",
                    "sampleFileName": "goesrplt_avng_20170323t184858.tar.gz",
                    "bucket": "protected"
                }
            ],
            "buckets": {
                "protected": {
                    "type": "protected",
                    "name": "ghrcsbxw-protected"
                },
                "internal": {
                    "type": "internal",
                    "name": "ghrcsbxw-internal"
                },
                "private": {
                    "type": "private",
                    "name": "ghrcsbxw-private"
                },
                "public": {
                    "type": "public",
                    "name": "ghrcsbxw-public"
                },
                "glacier": {
                    "type": "private",
                    "name": "ghrcsbxw-glacier"
                }
            },
            "collection": {
                "name": "goesrpltavirisng",
                "version": "1",
                "dataType": "goesrpltavirisng",
                "process": "metadataextractor",
                "provider_path": "/goesrpltavirisng/fieldCampaigns/goesrplt/AVIRIS-NG/data/",
                "url_path": "goesrpltavirisng__1",
                "duplicateHandling": "replace",
                "granuleId": "^goesrplt_avng_.*(\\.gz|\\.hdr|clip)$",
                "granuleIdExtraction": "^((goesrplt_avng_).*)",
                "sampleFileName": "goesrplt_avng_20170323t184858.tar.gz",
                "files": [
                    {
                        "bucket": "public",
                        "regex": "^goesrplt_avng_(.*).*\\.cmr.xml$",
                        "sampleFileName": "goesrplt_avng_20170323t184858.tar.gz.cmr.xml"
                    },
                    {
                        "bucket": "protected",
                        "regex": "^goesrplt_avng_(.*).*(\\.gz|\\.hdr|clip)$",
                        "sampleFileName": "goesrplt_avng_20170323t184858.tar.gz"
                    }
                ],
                "meta": {
                    "metadata_extractor": [
                        {
                            "regex": "^(.*).*(\\.gz|\\.hdr|clip)$",
                            "module": "ascii"
                        }
                    ],
                    "granuleRecoveryWorkflow": "DrRecoveryWorkflow"
                }}
        }
    }

    dummy_context = []
    task(dummy_event, dummy_context)
