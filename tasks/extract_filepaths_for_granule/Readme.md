NAME
    extract_filepaths_for_granule - Name: extract_filepaths_for_granule.py

DESCRIPTION
    Description:  Lambda handler that extracts the filepath's for a granule from an input dict.

CLASSES
    builtins.Exception(builtins.BaseException)
        ExtractFilePathsError

    class ExtractFilePathsError(builtins.Exception)
     |  Exception to be raised if any errors occur
     
FUNCTIONS
    handler(event, context)
        Lambda handler. Extracts the filepath's for a granule from an input dict.

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
