"""
This module exists to keep all database specific code for the request_status
table in a single place.
"""
import json
import logging
import uuid
import datetime
import dateutil.parser
import utils
import utils.database
from utils.database import DbError

LOGGER = logging.getLogger(__name__)


class BadRequestError(Exception):
    """
    Exception to be raised if there is a problem with the request.
    """


class NotFound(Exception):
    """
    Exception to be raised when a request doesn't exist.
    """

class DatabaseError(Exception):
    """
    Exception to be raised when there's a database error.
    """

def get_utc_now_iso():
    """
    Returns the current utc timestamp as a string in isoformat
    ex. '2019-07-17T17:36:38.494918'
    """
    return datetime.datetime.utcnow().isoformat()


def request_id_generator():
    """
    Returns a request_id (UUID) to be used to identify all the files for a granule
    ex. '0000a0a0-a000-00a0-00a0-0000a0000000'
    """
    restore_request_id = uuid.uuid4()
    return str(restore_request_id)


def submit_request(data):
    """
    Takes the provided request data (as a dict) and attempts to update the
    database with a new request.

    Returns the request id if successful, otherwise raises BadRequestError.
    """
    # build and run the insert
    sql = """
        INSERT INTO request_status (
            request_id, granule_id,
            object_key, job_type,
            restore_bucket_dest,
            job_status, request_time, last_update_time,
            err_msg
      
        ) VALUES (
            %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s
        )
        RETURNING job_id
        """
    # date might be provided, if not use current utc date
    date = get_utc_now_iso()

    if "request_time" in data:
        rq_date = dateutil.parser.parse(data["request_time"])
    else:
        rq_date = date

    if "last_update_time" in data:
        lu_date = dateutil.parser.parse(data["last_update_time"])
    else:
        lu_date = date

    if not "restore_bucket_dest" in data:
        data["restore_bucket_dest"] = None
    if not "err_msg" in data:
        data["err_msg"] = None

    try:
        params = (
            data["request_id"],
            data["granule_id"],
            data["object_key"],
            data["job_type"],
            data["restore_bucket_dest"],
            data["job_status"],
            rq_date,
            lu_date,
            data["err_msg"],
        )
    except KeyError as err:
        raise BadRequestError(f"Missing {str(err)} in input data")
    try:
        rows = utils.database.single_query(sql, params)
        job_id = None
        if rows:
            job_id = rows[0]["job_id"]
    except DbError as err:
        LOGGER.exception(f"DbError: {str(err)}")
        raise DatabaseError(str(err))

    return job_id


def get_job_by_job_id(job_id):
    """
    Reads a row from request_status by job_id.
    """
    sql = """
        SELECT
            job_id,
            request_id,
            granule_id,
            object_key,
            job_type,
            restore_bucket_dest,
            job_status,
            request_time,
            last_update_time,
            err_msg
        FROM
            request_status
        WHERE
            job_id = %s
        """
    try:
        rows = utils.database.single_query(sql, (job_id,))
        result = result_to_json(rows)
    except DbError as err:
        LOGGER.exception(f"DbError: {str(err)}")
        raise DatabaseError(str(err))

    return result

def get_jobs_by_granule_id(granule_id):
    """
    Reads rows from request_status by granule_id.
    """
    sql = """
        SELECT
            job_id,
            request_id,
            granule_id,
            object_key,
            job_type,
            restore_bucket_dest,
            job_status,
            request_time,
            last_update_time,
            err_msg
        FROM
            request_status
        WHERE
            granule_id = %s
        """
    try:
        rows = utils.database.single_query(sql, (granule_id,))
        result = result_to_json(rows)
    except DbError as err:
        LOGGER.exception(f"DbError: {str(err)}")
        raise DatabaseError(str(err))

    return result


def update_request_status(object_key, status, err_msg=None):
    """
    Updates the status of an inprogress request.
    """
    if object_key is None:
        raise BadRequestError("No object_key provided")

    # must have a status provided
    if status is None:
        raise BadRequestError("A new status must be provided")

    date = get_utc_now_iso()

    # run the update

    sql = """
        UPDATE
            request_status
        SET
            job_status = %s,
            last_update_time = %s,
            err_msg = %s
        WHERE
            object_key = %s
            and job_status = %s
    """
    try:
        result = utils.database.single_query(sql, (status, date, err_msg, object_key, "inprogress"))
    except DbError as err:
        msg = f"DbError updating status for {object_key} from 'inprogress' to {status}. {str(err)}"
        LOGGER.exception(msg)
        raise DatabaseError(str(err))
    return result

def delete_request(job_id):
    """
    Deletes a job by job_id.
    """
    if job_id is None:
        raise BadRequestError("No job_id provided")

    sql = """
        DELETE FROM
            request_status
        WHERE
            job_id = %s
    """
    try:
        result = utils.database.single_query(sql, (job_id,))
    except DbError as err:
        LOGGER.exception(f"DbError: {str(err)}")
        raise DatabaseError(str(err))
    return result

def delete_all_requests():
    """
    Deletes everything from the request_status table.

    TODO: Currently this method is only used to facilitate testing,
    so unit tests may not be complete.
    """
    try:
        result = get_all_requests()
        for job in result:
            try:
                delete_request(job["job_id"])
            except DbError as err:
                LOGGER.exception(f"DbError: {str(err)}")
                raise DatabaseError(str(err))
        result = get_all_requests()
        return result
    except DbError as err:
        LOGGER.exception(f"DbError: {str(err)}")
        raise DatabaseError(str(err))

def get_all_requests():
    """
    Returns all of the requests.
    """
    sql = """
        SELECT
            job_id,
            request_id,
            granule_id,
            object_key,
            job_type,
            restore_bucket_dest,
            job_status,
            request_time,
            last_update_time,
            err_msg
        FROM
            request_status
        ORDER BY job_id """

    try:
        rows = utils.database.single_query(sql, ())
        result = result_to_json(rows)
    except DbError as err:
        LOGGER.exception(f"DbError: {str(err)}")
        raise DatabaseError(str(err))

    return result

def create_data(request_id=None, granule_id=None, object_key=None, job_type=None,
                restore_bucket=None, job_status=None, request_time=None,
                last_update_time=None, err_msg=None):
    """
    Creates a dict containing the input data for submit_request.
    """
    data = {}
    if request_id:
        data["request_id"] = request_id
    if granule_id:
        data["granule_id"] = granule_id
    if object_key:
        data["object_key"] = object_key
    if job_type:
        data["job_type"] = job_type
    if restore_bucket:
        data["restore_bucket_dest"] = restore_bucket
    if job_status:
        data["job_status"] = job_status
    if request_time:
        data["request_time"] = request_time
    if last_update_time:
        data["last_update_time"] = last_update_time
    if err_msg:
        data["err_msg"] = err_msg
    return data

def get_jobs_by_status(status, max_days_old=None):
    """
    Returns rows from request_status by status, and optional days old
    """
    if status is None:
        raise BadRequestError("A status must be provided")

    sql = """
        SELECT
            job_id,
            request_id,
            granule_id,
            object_key,
            job_type,
            restore_bucket_dest,
            job_status,
            request_time,
            last_update_time,
            err_msg
        FROM
            request_status
        WHERE
            job_status = %s
        """
    orderby = """ order by last_update_time """
    try:
        if max_days_old:
            sql2 = """ and last_update_time > CURRENT_DATE at time zone 'utc' - INTERVAL '%s' DAY"""
            sql = sql +  sql2 + orderby
            rows = utils.database.single_query(sql, (status, max_days_old,))
            result = result_to_json(rows)
        else:
            sql = sql + orderby
            rows = utils.database.single_query(sql, (status,))
            result = result_to_json(rows)
    except DbError as err:
        LOGGER.exception(f"DbError: {str(err)}")
        raise DatabaseError(str(err))

    return result


def get_jobs_by_request_id(request_id):
    """
    Returns rows from request_status for a request_id
    """
    if request_id is None:
        raise BadRequestError("A request_id must be provided")

    sql = """
        SELECT
            job_id,
            request_id,
            granule_id,
            object_key,
            job_type,
            restore_bucket_dest,
            job_status,
            request_time,
            last_update_time,
            err_msg
        FROM
            request_status
        WHERE
        request_id = %s
        """
    orderby = """ order by last_update_time """
    try:
        sql = sql + orderby
        rows = utils.database.single_query(sql, (request_id,))
        result = result_to_json(rows)
    except DbError as err:
        LOGGER.exception(f"DbError: {str(err)}")
        raise DatabaseError(str(err))

    return result


def result_to_json(result_rows):
    """
    Converts a database result to Json format
    """
    json_result = json.loads(json.dumps(result_rows, default=myconverter))
    return json_result


def myconverter(obj):
    """
    Returns the current utc timestamp as a string in isoformat
    ex. '2019-07-17T17:36:38.494918'
    """
    if isinstance(obj, datetime.datetime):
        return obj.__str__()
