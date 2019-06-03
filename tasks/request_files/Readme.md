NAME
    request_files - Name: request_files.py

DESCRIPTION
    Description:  Lambda function that makes a restore request from glacier for each input file.

CLASSES
    builtins.Exception(builtins.BaseException)
        RestoreRequestError

    class RestoreRequestError(builtins.Exception)
     |  Exception to be raised if the restore request fails submission for any of the files.

FUNCTIONS
    handler(event, context)
        Lambda handler. Initiates a restore_object request from glacier for each file of a granule.

        Note that this function is set up to accept a list of granules, (because Cumulus sends a list),
        but at this time, only 1 granule will be accepted.
        This is due to the error handling. If the restore request for any file for a
        granule fails to submit, the entire granule (workflow) fails. If more than one granule were
        accepted, and a failure occured, at present, it would fail all of them.

        Args:
            event (dict): A dict with the following keys:

                glacierBucket (string) :  The name of the glacier bucket from which the files
                    will be restored.
                granules (list(dict)): A list of dict with the following keys:
                    granuleId (string): The id of the granule being restored.
                    filepaths (list(string)): list of filepaths (glacier keys) for the granule

                Example: event: {'glacierBucket': 'some_bucket',
                            'granules': [{'granuleId': 'granxyz',
                                        'filepaths': ['path1', 'path2']}]
                           }

            context (Object): None

        Returns:
            dict: The dict returned from the task. All 'success' values will be True. If they were
            not all True, the RestoreRequestError exception would be raised.

        Raises:
            RestoreRequestError: An error occurred calling restore_object for one or more files.
            The dict that is returned for a successful granule restore, will be included in the message,
            with 'success' = False for the files for which the restore request failed to submit.
