from typing import Dict, Any, List

import run_cumulus_task
from cumulus_logger import CumulusLogger

LOGGER = CumulusLogger()


class ReformatRequestError(Exception):
    """
    Exception to be raised if the request fails in any way.
    """


def task(event: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Transforms event from Cumulus format to Orca copy_to_glacier format.
    Args:
        event: See schemas/input.json

    Returns:
        See schemas/output.json
    """
    LOGGER.debug(f"event: {event}")
    file_name_mapping = event['config']['file_mapping']["name"]
    file_filepath_mapping = event['config']['file_mapping']["filepath"]
    file_bucket_mapping = event['config']['file_mapping']["bucket"]
    file_filename_mapping = event['config']['file_mapping'].get('filename', None)
    output_file_types = event['config'].get('output_file_types', [])
    granules = event['input']['granules']
    translated_granules = []
    for granule in granules:
        # todo: Make sure schema errors cover this adequately.
        # todo: If it does, we don't need to store this value.
        granule_id = granule['granuleId']

        translated_files = []
        for file in granule['files']:
            try:
                if any(file[file_name_mapping].endswith(ext) for ext in output_file_types):
                    continue
            except KeyError:
                raise ReformatRequestError(
                    f"file: {file} does not contain a value for '{file[file_name_mapping]}'")

            translated_file = {
                'name': file[file_name_mapping],
                'bucket': file[file_bucket_mapping],
                'filepath': file[file_filepath_mapping]
            }
            if file_filename_mapping is None or not file.keys().__contains__(file_filename_mapping):
                translated_file['filename'] = '/'.join(['s3:/', translated_file['bucket'], translated_file['filepath']])
            else:
                translated_file['filename'] = file[file_filename_mapping]

            LOGGER.info(f"Translated File: {translated_file}")
            translated_files += translated_file
        translated_granules += {'granuleId': granule_id,
                                'files': translated_files}

    return {'granules': translated_granules}


def handler(event: Dict[str, Any], context: Any) -> List[Dict[str, Any]]:
    # noinspection SpellCheckingInspection
    """
    Entry point for the copy_to_glacier_cumulus_translator Lambda.
    Args:
        event: See schemas/input.json
        context: An object provided by AWS Lambda. Used for context tracking.

    Returns: A Dict with the following keys:
        input (dict): Dictionary with the followig keys:
            granules (List): List of dicts with the following keys:
                granuleId (str):
                files (List): List of dicts with the following keys:
                    name (str):
                    filepath (str):
                    bucket (str):
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
            buckets (dict): A dict with the following keys:
                glacier (dict): A dict with the following keys:
                    name (str): The name of the bucket to copy to.
    """
    LOGGER.setMetadata(event, context)
    return run_cumulus_task.run_cumulus_task(task, event, context)
