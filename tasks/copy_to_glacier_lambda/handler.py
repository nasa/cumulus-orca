from run_cumulus_task import run_cumulus_task
import boto3
import re
import os

file_types_to_exclude = [".example"] #ex: [".tar", ".gz"]


def exclude_file_types(file_url):
    """
    Tests whether or not file is included in file types to exclude from copy to glacier
    :param file_url: s3 url of granule
    :return: boolean describe if file should be excluded from copy
    """
    for file_type in file_types_to_exclude:
        if re.search(f"^.*{file_type}$", file_url) is not None:
            return True
    return False


def copy(source_bucket, source_key, destination_bucket, destination_key):
    """
    Copies granule from source bucket to destination
    :param source_bucket: bucket granule is currently located
    :param destination_bucket: bucket granule is to be copied to
    :param source_key: source granule path excluding s3://[bucket]/
    :param destination_key: destination granule path excluding s3://[bucket]/
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


def get_source_bucket_and_key(file_url):
    """
    Parses source bucket and key from s3 url
    :param file_url: s3 url path to granule
    :return: re.Match object with argument [1] equal to source bucket and [2] equal to source key
    """
    return re.search("s3://([^/]*)/(.*)", file_url)


def get_bucket(filename, files):
    """
    Extract the bucket from the files
    :param filename: Granule file name
    :param files: list of collection files
    :return: Bucket name
    """
    for file in files:
        if re.match(file.get('regex', '*.'), filename):
            return file['bucket']
    return 'public'


def get_granule_from_event(event):
    """
    Given an event, grab the first granule object in the granules list.
    :param event: Event object passed into the lambda
    :return: Granule object from event
    """
    granules = event.get('granules', [])
    if len(granules) == 1:
        return granules[0]
    else:
        print(f"event.input.granules must have only 1 granule.")
        return {}


def get_file_urls(granule):
    """
    Given a list of files for a granule, return a list of S3 urls, one url per file.
    :param granules: List of granule objects with a 'filename' attribute
    :return: List of s3 urls for each file in the granule
    """
    files = granule.get('files', [])
    return [ file.get('filename') for file in files ]


def task(event, context):
    """

    :param event: Event passed into the step from the aws worklow
    :param context:
    :return:
    """
    print(event)
    event_input = event.get('input', {})
    granule = get_granule_from_event(event_input)
    file_urls = get_file_urls(granule)
    config = event.get('config')
    collection = config.get('collection')
    config['fileStagingDir'] = config.get('fileStagingDir',
                                          f"{collection['name']}__{collection['version']}")
    glacier_bucket = config.get('buckets').get('glacier').get('name')
    url_path = collection.get('url_path')
    granule_data = {}
    for file_url in file_urls:
        filename = os.path.basename(file_url)
        if filename not in granule_data.keys():
            granule_data[filename] = {'granuleId': filename, 'files': []}
        granule_data[filename]['files'].append(
            {
                "path": config['fileStagingDir'],
                "url_path": config.get('url_path', config['fileStagingDir']),
                "bucket": get_bucket(filename, collection.get('files', [])),
                "filename": file_url,
                "name": file_url
            }
        )
        if exclude_file_types(file_url):
            continue
        source = get_source_bucket_and_key(file_url)
        copy(source[1], source[2], glacier_bucket, f"{url_path}/{filename}")

    final_output = list(granule_data.values())
    return {"granules": final_output, "input": event_input}


# handler that is provided to aws lambda
def handler(event, context):
    return run_cumulus_task(task, event, context)


if __name__ == '__main__':
    event = {
        "input": {
            "granules": [
                {
                    "files": [
                        {
                            "filename": "s3://ghrcsbxw-internal/file-staging/ghrcsbxw/goesrpltavirisng__1/goesrplt_avng_20170328t210208.tar.gz"
                        }
                    ]
                }
            ]
        },
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

    context = []
    task(event, context)
