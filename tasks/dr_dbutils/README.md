**Lambda function request_files **

- [Setup](#setup)
- [Deployment](#deployment)
- [pydoc requests_db](#pydoc-requests-db)


<a name="setup"></a>
# Setup
    See the README in the tasks folder for general development setup instructions
    See the README in the tasks/pg_utils folder to install pg_utils

<a name="development"></a>
# Development

## Deployment
```
https://www.oreilly.com/library/view/head-first-python/9781491919521/ch04.html
Create the distribution file:
    (podr) λ cd C:\devpy\poswotdr\tasks\dr_dbutils
    (podr) λ py -3 setup.py sdist
    (podr) λ cd dist
    (podr) λ pip install dr_dbutils-1.0.tar.gz
 
```
<a name="pydoc-requests-db"></a>
## pydoc requests_db
```
NAME
    requests_db

DESCRIPTION
    This module exists to keep all database specific code for the request_status
    table in a single place.

CLASSES
    builtins.Exception(builtins.BaseException)
        BadRequestError
        DatabaseError
        NotFound

    class BadRequestError(builtins.Exception)
     |  Exception to be raised if there is a problem with the request.

    class DatabaseError(builtins.Exception)
     |  Exception to be raised when there's a database error.

    class NotFound(builtins.Exception)
     |  Exception to be raised when a request doesn't exist.

FUNCTIONS
    create_data(obj, job_type=None, job_status=None, request_time=None, last_update_time=None, err_msg=None)
        Creates a dict containing the input data for submit_request.

    delete_all_requests()
        Deletes everything from the request_status table.

        TODO: Currently this method is only used to facilitate testing,
        so unit tests may not be complete.

    delete_request(request_id)
        Deletes a job by request_id.

    get_all_requests()
        Returns all of the requests.

    get_job_by_request_id(request_id)
        Reads a row from request_status by request_id.

    get_jobs_by_granule_id(granule_id)
        Reads rows from request_status by granule_id.

    get_jobs_by_object_key(object_key)
        Reads rows from request_status by object_key.

    get_jobs_by_request_group_id(request_group_id)
        Returns rows from request_status for a request_group_id

    get_jobs_by_status(status, max_days_old=None)
        Returns rows from request_status by status, and optional days old

    get_utc_now_iso()
        Returns the current utc timestamp as a string in isoformat
        ex. '2019-07-17T17:36:38.494918'

    myconverter(obj)
        Returns the current utc timestamp as a string in isoformat
        ex. '2019-07-17T17:36:38.494918'

    request_id_generator()
        Returns a request_group_id (UUID) to be used to identify all the files for a granule
        ex. '0000a0a0-a000-00a0-00a0-0000a0000000'

    result_to_json(result_rows)
        Converts a database result to Json format

    submit_request(data)
        Takes the provided request data (as a dict) and attempts to update the
        database with a new request.

        Raises BadRequestError if there is a problem with the input.

    update_request_status_for_job(request_id, status, err_msg=None)
        Updates the status of a job.
              
```
