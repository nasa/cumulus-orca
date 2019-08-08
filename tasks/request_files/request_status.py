"""
Name: request_status.py

Description:  Queries the request_status table.
"""

#from run_cumulus_task import run_cumulus_task
#from cumulus_logger import CumulusLogger

#LOGGER = CumulusLogger()
import requests

#class ExtractFilePathsError(Exception):
#    """Exception to be raised if any errors occur"""

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
        function = event['function']
    except KeyError as err:
        raise

    if function == "query":
        try:
            granule_id = event['granule_id']
        except KeyError as err:
            pass
        try:
            request_id = event['request_id']
        except KeyError as err:
            pass
        result = requests.get_all_requests()
    else:
        if function == "add":
            data = {}
            data["request_id"] = "request_id"
            data["granule_id"] = "granule_1"
            data["object_key"] = "my_test_filename"
            data["job_type"] = "restore"
            data["restore_bucket_dest"] = "my_test_bucket"
            data["job_status"] = "error"
            job_id = requests.submit_request(data)

    #if granule_id is None and request_id is None:
    #    raise ExtractFilePathsError(f'KeyError: granule_id or request_id is required')

    result = requests.get_all_requests()
    return result

def handler(event, context):            #pylint: disable-msg=unused-argument
    """Lambda handler. Extracts the key's for a granule from an input dict.

        Args:
            event (dict): A dict with one or more of the following keys:

                granule_id (string): A granule_id to retrieve
                request_id (string): A request_id (uuid) to retrieve

                Example: event: {'granuleId': 'granxyz',
                                 'request_id': 'd554f623-b926-452b-868e-f5543932e3da',
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
    #LOGGER.setMetadata(event, context)
    #result = run_cumulus_task(task, event, context)
    result = task(event, context)
    return result
