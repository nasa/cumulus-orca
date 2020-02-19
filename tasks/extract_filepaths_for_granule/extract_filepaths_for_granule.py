"""
Name: extract_filepaths_for_granule.py

Description:  Extracts the keys (filepaths) for a granule's files from a Cumulus Message.
"""

import re

from cumulus_logger import CumulusLogger
from run_cumulus_task import run_cumulus_task

LOGGER = CumulusLogger()

class ExtractFilePathsError(Exception):
    """Exception to be raised if any errors occur"""

def task(event, context):    #pylint: disable-msg=unused-argument
    """
    Task called by the handler to perform the work.

    This task will parse the input, removing the granuleId and file keys for a granule.

        Args:
            event (dict): passed through from the handler
            context (Object): passed through from the handler

        Returns:
            dict: dict containing granuleId and keys. See handler for detail.

        Raises:
            ExtractFilePathsError: An error occurred parsing the input.
    """
    result = {}
    try:
        regex_buckets = get_regex_buckets(event)
        level = "event['input']"
        grans = []
        for ev_granule in event['input']['granules']:
            gran = {}
            files = []
            level = "event['input']['granules'][]"
            gran['granuleId'] = ev_granule['granuleId']
            for afile in ev_granule['files']:
                level = "event['input']['granules'][]['files']"
                file_name = afile['fileName']
                fkey = afile['key']
                dest_bucket = None
                for key in regex_buckets:
                    pat = re.compile(key)
                    if pat.match(file_name):
                        dest_bucket = regex_buckets[key]
                files.append({"key": fkey, "dest_bucket": dest_bucket})
            gran["keys"] = files
            grans.append(gran)
        result['granules'] = grans
    except KeyError as err:
        raise ExtractFilePathsError(f'KeyError: "{level}[{str(err)}]" is required')
    return result

def get_regex_buckets(event):
    """
    Gets a dict of regular expressions and the corresponding archive bucket for files
    matching the regex.

        Args:
            event (dict): passed through from the handler

        Returns:
            dict: dict containing regex and bucket.

        Raises:
            ExtractFilePathsError: An error occurred parsing the input.
    """
    buckets = {}
    try:
        level = "event['config']"
        buckets["protected"] = event['config']['protected-bucket']
        buckets["internal"] = event['config']['internal-bucket']
        buckets["private"] = event['config']['private-bucket']
        buckets["public"] = event['config']['public-bucket']
        file_buckets = event['config']['file-buckets']
        # file_buckets example:
        # [{'regex': '.*.h5$', 'sampleFileName': 'L0A_0420.h5', 'bucket': 'protected'},
        # {'regex': '.*.iso.xml$', 'sampleFileName': 'L0A_0420.iso.xml', 'bucket': 'protected'},
        # {'regex': '.*.h5.mp$', 'sampleFileName': 'L0A_0420.h5.mp', 'bucket': 'public'},
        # {'regex': '.*.cmr.json$', 'sampleFileName': 'L0A_0420.cmr.json', 'bucket': 'public'}]
        regex_buckets = {}
        for regx in file_buckets:
            regex_buckets[regx["regex"]] = buckets[regx["bucket"]]

        # regex_buckets example:
        # {'.*.h5$': 'podaac-sndbx-cumulus-protected',
        #  '.*.iso.xml$': 'podaac-sndbx-cumulus-protected',
        #  '.*.h5.mp$': 'podaac-sndbx-cumulus-public',
        #  '.*.cmr.json$': 'podaac-sndbx-cumulus-public'}
    except KeyError as err:
        raise ExtractFilePathsError(f'KeyError: "{level}[{str(err)}]" is required')
    return regex_buckets

def handler(event, context):            #pylint: disable-msg=unused-argument
    """Lambda handler. Extracts the key's for a granule from an input dict.

        Args:
            event (dict): A dict with the following keys:

                granules (list(dict)): A list of dict with the following keys:
                    granuleId (string): The id of a granule.
                    files (list(dict)): list of dict with the following keys:
                        key (string): The key of the file to be returned.
                        other dictionary keys may be included, but are not used.
                    other dictionary keys may be included, but are not used.

                Example: event: {'granules': [
                                      {'granuleId': 'granxyz',
                                       'version": '006',
                                       'files': [
                                            {'name': 'file1',
                                             'key': 'key1',
                                             'filename': 's3://dr-test-sandbox-protected/file1',
                                             'type': 'metadata'} ]
                                       }
                                    ]
                                 }

            context (Object): None

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
    LOGGER.setMetadata(event, context)
    result = run_cumulus_task(task, event, context)
    return result
