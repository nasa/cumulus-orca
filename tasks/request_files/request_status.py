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
    _LOG.info(f"event: '{event}' ")
    try:
        function = event['function']
    except KeyError:
        raise BadRequestError("Missing 'function' in input data")

    if function == "query":
        result = query_requests(event)

    if function == "add":
        result = add_request(event)

    if function == "clear":
        result = requests.delete_all_requests()

    return result

def query_requests(event):
    """
    Queries the database for requests
    """
    try:
        granule_id = event['granule_id']
    except KeyError:
        granule_id = None
    try:
        request_id = event['request_id']
    except KeyError:
        request_id = None
    try:
        job_id = event['job_id']
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

def add_request(event):
    """
    Adds a request to the database
    """
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
    job_id = requests.submit_request(data)
    result = requests.get_job_by_job_id(job_id)
    return result

def handler(event, context):            #pylint: disable-msg=unused-argument
    """Lambda handler. Retrieves job(s) from the database.

        Environment Vars:
            DATABASE_HOST (string): the server where the database resides.
            DATABASE_PORT (string): the database port. The standard is 5432.
            DATABASE_NAME (string): the name of the database.
            DATABASE_USER (string): the name of the application user.
            DATABASE_PW (string): the password for the application user.

        Args:
            event (dict): A dict with zero or one of the following keys:

                granule_id (string): A granule_id to retrieve
                request_id (string): A request_id (uuid) to retrieve
                job_id (string): A job_id to retrieve

                Example: event: {'granuleId': 'granxyz'
                                }

            context (Object): None

        Returns:
            (list(dict)): A list of dict with the following keys:
                'job_id' (number): Sequential id, uniquely identifying a table entry.
                'request_id' (string): The request_id the job belongs to.
                'granule_id' (string): The id of a granule.
                'object_key' (string): The name of the file that was requested.
                'job_type' (string): The type of job. "restore" or "regenerate"
                'restore_bucket_dest' (string): The bucket where the restored file will be put.
                'job_status' (string): The current status of the job
                'request_time' (string): UTC time that the request was initiated.
                'last_update_time' (string): UTC time of the last update to job_status.
                'err_msg' (string): Description of the error if the job_status is 'error'.

            Example:
                [
                    {
                        "job_id": 1,
                        "request_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
                        "granule_id": "granxyz",
                        "object_key": "my_test_filename",
                        "job_type": "restore",
                        "restore_bucket_dest": "my_test_bucket",
                        "job_status": "inprogress",
                        "request_time": "2019-09-30 18:24:38.370252+00:00",
                        "last_update_time": "2019-09-30 18:24:38.370252+00:00",
                        "err_msg": null
                    }
                ]

        Raises:
            BadRequestError: An error occurred parsing the input.
    """
    result = task(event, context)
    return result
