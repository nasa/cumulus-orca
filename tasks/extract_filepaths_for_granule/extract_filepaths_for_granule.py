"""
Name: extract_filepaths_for_granule.py

Description:  Lambda handler that extracts the filepath's for a granule from an input dict.
"""

import json

class ExtractFilePathsError(Exception):
    """Exception to be raised if any errors occur"""

def task(event):
    """
    Task called by the handler to perform the work.

    This task will parse the input, removing the granuleId and filepaths for a granule.

        Args:
            event (dict): passed through from the handler
            context (Object): passed through from the handler

        Returns:
            dict: dict containing granuleId and filepaths. See handler for detail.

        Raises:
            ExtractFilePathsError: An error occurred parsing the input.
    """
    result = {}
    try:
        level = "event."
        result['glacierBucket'] = event['glacierBucket']
        grans = []
        for ev_granule in event['granules']:
            gran = {}
            files = []
            level = "event.granules[{"
            gran['granuleId'] = ev_granule['granuleId']
            for afile in ev_granule['files']:
                level = "event.granules[{files[{"
                files.append(afile['filepath'])
            gran["filepaths"] = files
            grans.append(gran)
        result['granules'] = grans
    except KeyError as err:
        val = str(err).strip("\'")
        raise ExtractFilePathsError(f"KeyError: '{level}{val}' is required")
    return result

def handler(event, context):            #pylint: disable-msg=unused-argument
    """Lambda handler. Extracts the filepath's for a granule from an input dict.

        Args:
            event (dict): A dict with the following keys:

                glacierBucket (string) :  The name of a glacier bucket.
                granules (list(dict)): A list of dict with the following keys:
                    granuleId (string): The id of a granule.
                    files (list(dict)): list of dict with the following keys:
                        filepath (string): The key (filepath) of the file.
                        other keys may be included, but are not used.
                    other keys may be included, but are not used.

                Example: event: {'glacierBucket': 'some_bucket',
                                 'granules': [
                                      {'granuleId': 'granxyz',
                                       'version": '006',
                                       'files': [
                                            {'name': 'file1',
                                             'filepath': 'filepath1',
                                             'filename': 's3://dr-test-sandbox-protected/file1',
                                             'type': 'metadata'} ]
                                       }
                                    ]
                                 }

            context (Object): None

        Returns:
            dict: A dict with the following keys:

                'glacierBucket' (string): The name of a glacier bucket.
                'granules' (list(dict)): list of dict with the following keys:
                    'granuleId' (string): The id of a granule.
                    'filepaths' (list(string)): list of filepaths for the granule.

            Example:
                {"glacierBucket": "some_bucket",
                 "granules": [{"granuleId": "granxyz",
                             "filepaths": ["filepath1",
                                           "filepath2"]}]}

        Raises:
            ExtractFilePathsError: An error occurred parsing the input.
    """
    result = task(event)
    return json.dumps(result)
