"""
Name: request_status.py

Description:  Queries the request_status table.
"""
import logging
import requests_db

# Set Global Variables
_LOG = logging.getLogger(__name__)


class BadRequestError(Exception):
    """
    Exception to be raised if there is a problem with the request.
    """


def task(event, context):  # pylint: disable-msg=unused-argument
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
    _LOG.debug(f"event: '{event}' ")
    try:
        function = event['function']
    except KeyError:
        raise BadRequestError("Missing 'function' in input data")

    if function == "query":
        result = query_requests(event)

    if function == "add":
        result = add_request(event)

    if function == "clear":
        result = requests_db.delete_all_requests()

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
        request_group_id = event['request_group_id']
    except KeyError:
        request_group_id = None
    try:
        request_id = event['request_id']
    except KeyError:
        request_id = None
    try:
        object_key = event['object_key']
    except KeyError:
        object_key = None

    if request_id:
        result = requests_db.get_job_by_request_id(request_id)
    else:
        if request_group_id:
            result = requests_db.get_jobs_by_request_group_id(request_group_id)
        else:
            if granule_id:
                result = requests_db.get_jobs_by_granule_id(granule_id)
            else:
                if object_key:
                    result = requests_db.get_jobs_by_object_key(object_key)
                else:
                    result = requests_db.get_all_requests()
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
        request_group_id = event['request_group_id']
    except KeyError:
        raise BadRequestError("Missing 'request_group_id' in input data")
    try:
        status = event['status']
    except KeyError:
        status = "error"

    data = {
        "request_id": requests_db.request_id_generator(),
        "request_group_id": request_group_id,
        "granule_id": granule_id, "object_key": "my_test_filename",
        "job_type": "restore",
        "restore_bucket_dest": "my_test_bucket",
        "job_status": status
    }
    if status == "error":
        data["err_msg"] = "error message goes here"
    request_id = requests_db.submit_request(data)
    result = requests_db.get_job_by_request_id(request_id)
    return result


def handler(event, context):  # pylint: disable-msg=unused-argument
    """Lambda handler. Retrieves job(s) from the database.

        Environment Vars:
            DATABASE_PORT (string): the database port. The standard is 5432.
            DATABASE_NAME (string): the name of the database.
            DATABASE_USER (string): the name of the application user.

        Parameter Store:
            drdb-user-pass (string): the password for the application user (DATABASE_USER).
            drdb-host (string): the database host

        Args:
            event (dict): A dict with the following keys:
                function (string): 'query', 'add', or 'clear'.

                Only one of the following is used during a 'query' request, and none are used during a 'clear' request.
                granule_id (string, optional): A granule_id to retrieve
                request_group_id (string, optional): A request_group_id (uuid) to retrieve
                request_id (string, optional): A request_id to retrieve
                object_key (string, optional): An object_key to retrieve

                Examples:
                    event: {'function': 'query'}
                    event: {'function': 'query',
                            'granule_id': 'L0A_HR_RAW_product_0006-of-0420'
                           }
                    event: {'function': 'query',
                            'request_id': 'B2FE0827DD30B8D1'
                           }
                    event: {'function': 'query',
                            'request_group_id': 'e91ef763-65bb-4dd2-8ba0-9851337e277e'
                           }
                    event: {'function': 'query',
                            'object_key': 'L0A_HR_RAW_product_0006-of-0420.h5'
                           }

            context (Object): None

        Returns:
            (list(dict)): A list of dict with the following keys:
                'request_id' (string): id uniquely identifying a table entry.
                'request_group_id' (string): The request_group_id the job belongs to.
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
                        "request_id": "B2FE0827DD30B8D1",
                        "request_group_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
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
    logging.basicConfig(level=logging.INFO,
                        format='%(levelname)s: %(asctime)s: %(message)s')
    result = task(event, context)
    return result
