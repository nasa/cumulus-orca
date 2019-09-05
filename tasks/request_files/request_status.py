"""
Name: request_status.py

Description:  Queries the request_status table.
"""
import logging

import requests

# Set Global Variables
_LOG = logging.getLogger(__name__)

class BadRequestError(Exception):
    """
    Exception to be raised if there is a problem with the request.
    """

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
    _LOG.warning(f"event: '{event}' ")
    _LOG.info(f"event: '{event}' ")
    try:
        function = event['function']
        _LOG.warning(f"function: {function}")
    except KeyError as err:
        raise BadRequestError("Missing 'function' in input data")

    if function == "query":
        try:
            granule_id = event['granule_id']
            _LOG.warning(f"granule_id: {granule_id}")
        except KeyError:
            granule_id = None
        try:
            request_id = event['request_id']
            _LOG.warning(f"request_id: {request_id}")
        except KeyError:
            request_id = None
        try:
            job_id = event['job_id']
            _LOG.warning(f"job_id: {job_id}")
        except KeyError:
            job_id = None
        if job_id:
            result = requests.get_job_by_job_id(job_id)
        else:
            if request_id:
                result = requests.get_jobs_by_request_id(request_id)
            else:
                if granule_id:
                    result = requests.get_jobs_by_granule_id(granule_id)
                else:
                    result = requests.get_all_requests()
        return result

    if function == "add":
        try:
            granule_id = event['granule_id']
        except KeyError:
            raise BadRequestError("Missing 'granule_id' in input data")
        try:
            request_id = event['request_id']
        except KeyError:
            raise BadRequestError("Missing 'request_id' in input data")
        try:
            status = event['status']
        except KeyError:
            status = "error"

        data = {}
        data["request_id"] = request_id
        data["granule_id"] = granule_id
        data["object_key"] = "my_test_filename"
        data["job_type"] = "restore"
        data["restore_bucket_dest"] = "my_test_bucket"
        data["job_status"] = status
        if status == "error":
            data["err_msg"] = "error message goes here"
        _LOG.warning(f"data: '{data}'")
        job_id = requests.submit_request(data)
        _LOG.warning(f"job_id: {job_id}")
        result = requests.get_job_by_job_id(job_id)
        return result

    if function == "clear":
        result = requests.delete_all_requests()
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
    _LOG.warning("in handler")
    result = task(event, context)
    return result
