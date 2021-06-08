from typing import Dict, Any

from cumulus_logger import CumulusLogger

LOGGER = CumulusLogger()


def task(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transforms event from Cumulus format to Orca copy_to_glacier format.
    Args:
        event: See schemas/input.json

    Returns:
        See schemas/output.json
    """
    return event


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    # noinspection SpellCheckingInspection
    """
    Entry point for the copy_to_glacier_cumulus_translator Lambda.
    Args:
        event: A dict with the following keys:
            TODO
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
    return task(event)
