"""
This module exists to keep all database specific code for the request_status
table in a single place.
"""
import os
import json
import logging
import uuid
import datetime
from typing import Optional

import dateutil.parser
import database
from database import DbError

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
    Returns a request_group_id (UUID) to be used to identify all the files for a granule
    ex. '0000a0a0-a000-00a0-00a0-0000a0000000'
    """
    restore_request_group_id = uuid.uuid4()
    return str(restore_request_group_id)


def get_dbconnect_info():
    """
    Gets the dbconnection info. PREFIX environment variable expected to be set.
    """
    dbconnect_info = {}
    db_params = {}
    prefix = os.environ['PREFIX']
    db_params['db_host'] = {"secretsmanager": f"{prefix}-drdb-host"}
    db_params['db_port'] = {'env': 'DATABASE_PORT'}
    db_params['db_name'] = {'env': 'DATABASE_NAME'}
    db_params['db_user'] = {'env': 'DATABASE_USER'}
    db_params['db_pw'] = {'secretsmanager': f"{prefix}-drdb-user-pass"}
    dbconnect_info = database.read_db_connect_info(db_params)
    return dbconnect_info


def submit_request(data):
    """
    Takes the provided request data (as a dict) and attempts to update the
    database with a new request.

    Raises BadRequestError if there is a problem with the input.
    """
    # build and run the insert
    sql = """
        INSERT INTO request_status (
            request_id, request_group_id, granule_id,
            object_key, job_type,
            restore_bucket_dest,
            archive_bucket_dest,
            job_status, request_time, last_update_time,
            err_msg
      
        ) VALUES (
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s
        )
        """
    # date might be provided, if not use current utc date
    date = get_utc_now_iso()

    # data["request_id"] = request_id

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

    if not "archive_bucket_dest" in data:
        data["archive_bucket_dest"] = None

    if not "err_msg" in data:
        data["err_msg"] = None

    try:
        params = (
            data["request_id"],
            data["request_group_id"],
            data["granule_id"],
            data["object_key"],
            data["job_type"],
            data["restore_bucket_dest"],
            data["archive_bucket_dest"],
            data["job_status"],
            rq_date,
            lu_date,
            data["err_msg"],
        )
    except KeyError as err:
        raise BadRequestError(f"Missing {str(err)} in input data")
    try:
        dbconnect_info = get_dbconnect_info()
        database.single_query(sql, dbconnect_info, params)
    except DbError as err:
        LOGGER.exception(f"DbError: {str(err)}")
        raise DatabaseError(str(err))
    return data["request_id"]


def get_job_by_request_id(request_id):
    """
    Reads a row from request_status by request_id.
    """
    sql = """
        SELECT
            request_id,
            request_group_id,
            granule_id,
            object_key,
            job_type,
            restore_bucket_dest,
            archive_bucket_dest,
            job_status,
            request_time,
            last_update_time,
            err_msg
        FROM
            request_status
        WHERE
            request_id = %s
        """
    try:
        dbconnect_info = get_dbconnect_info()
        rows = database.single_query(sql, dbconnect_info, (request_id,))
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
            request_id,
            request_group_id,
            granule_id,
            object_key,
            job_type,
            restore_bucket_dest,
            archive_bucket_dest,
            job_status,
            request_time,
            last_update_time,
            err_msg
        FROM
            request_status
        WHERE
            granule_id = %s
        ORDER BY last_update_time desc
        """
    try:
        dbconnect_info = get_dbconnect_info()
        rows = database.single_query(sql, dbconnect_info, (granule_id,))
        result = result_to_json(rows)
    except DbError as err:
        LOGGER.exception(f"DbError: {str(err)}")
        raise DatabaseError(str(err))

    return result


def get_jobs_by_object_key(object_key):
    """
    Reads rows from request_status by object_key.
    """
    sql = """
        SELECT
            request_id,
            request_group_id,
            granule_id,
            object_key,
            job_type,
            restore_bucket_dest,
            archive_bucket_dest,
            job_status,
            request_time,
            last_update_time,
            err_msg
        FROM
            request_status
        WHERE
            object_key = %s
        ORDER BY last_update_time desc
        """
    try:
        dbconnect_info = get_dbconnect_info()
        rows = database.single_query(sql, dbconnect_info, (object_key,))
        result = result_to_json(rows)
    except DbError as err:
        LOGGER.exception(f"DbError: {str(err)}")
        raise DatabaseError(str(err))

    return result


def update_request_status_for_job(request_id, status, err_msg=None):
    """
    Updates the status of a job.
    """
    if request_id is None:
        raise BadRequestError("No request_id provided")

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
            request_id = %s
    """
    try:
        dbconnect_info = get_dbconnect_info()
        result = database.single_query(sql, dbconnect_info, (status, date, err_msg, request_id))
    except DbError as err:
        msg = f"DbError updating status for job {request_id} to {status}. {str(err)}"
        LOGGER.exception(msg)
        raise DatabaseError(str(err))
    return result


def delete_request(request_id):
    """
    Deletes a job by request_id.
    """
    if request_id is None:
        raise BadRequestError("No request_id provided")

    sql = """
        DELETE FROM
            request_status
        WHERE
            request_id = %s
    """
    try:
        dbconnect_info = get_dbconnect_info()
        result = database.single_query(sql, dbconnect_info, (request_id,))
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

    sql = """
        DELETE FROM request_status
    """
    try:
        dbconnect_info = get_dbconnect_info()
        result = database.single_query(sql, dbconnect_info, ())
    except DbError as err:
        LOGGER.exception(f"DbError: {str(err)}")
        raise DatabaseError(str(err))

    return result


def get_all_requests():
    """
    Returns all of the requests.
    """
    sql = """
        SELECT
            request_id,
            request_group_id,
            granule_id,
            object_key,
            job_type,
            restore_bucket_dest,
            archive_bucket_dest,
            job_status,
            request_time,
            last_update_time,
            err_msg
        FROM
            request_status
        ORDER BY last_update_time desc """

    try:
        dbconnect_info = get_dbconnect_info()
        rows = database.single_query(sql, dbconnect_info, ())
        result = result_to_json(rows)
    except DbError as err:
        LOGGER.exception(f"DbError: {str(err)}")
        raise DatabaseError(str(err))

    return result


def create_data(obj,  # pylint: disable-msg=too-many-arguments
                job_type=None, job_status=None,
                request_time=None,
                last_update_time=None, err_msg=None):
    """
    Creates a dict containing the input data for submit_request.
    """
    data = {}
    data["request_id"] = request_id_generator()
    if obj["request_group_id"]:
        data["request_group_id"] = obj["request_group_id"]
    if obj["granule_id"]:
        data["granule_id"] = obj["granule_id"]
    if obj["key"]:
        data["object_key"] = obj["key"]
    if job_type:
        data["job_type"] = job_type
    if obj["glacier_bucket"]:
        data["restore_bucket_dest"] = obj["glacier_bucket"]
    if obj["dest_bucket"]:
        data["archive_bucket_dest"] = obj["dest_bucket"]
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
            request_id,
            request_group_id,
            granule_id,
            object_key,
            job_type,
            restore_bucket_dest,
            archive_bucket_dest,
            job_status,
            request_time,
            last_update_time,
            err_msg
        FROM
            request_status
        WHERE
            job_status = %s
        """
    order_by = """ order by last_update_time desc """
    try:
        dbconnect_info = get_dbconnect_info()
        if max_days_old:
            sql2 = """ and last_update_time > CURRENT_DATE at time zone 'utc' - INTERVAL '%s' DAY"""
            sql = sql + sql2 + order_by
            rows = database.single_query(sql, dbconnect_info, (status, max_days_old,))
            result = result_to_json(rows)
        else:
            sql = sql + order_by
            rows = database.single_query(sql, dbconnect_info, (status,))
            result = result_to_json(rows)
    except DbError as err:
        LOGGER.exception(f"DbError: {str(err)}")
        raise DatabaseError(str(err))

    return result


def get_jobs_by_request_group_id(request_group_id):
    """
    Returns rows from request_status for a request_group_id
    """
    if request_group_id is None:
        raise BadRequestError("A request_group_id must be provided")

    sql = """
        SELECT
            request_id,
            request_group_id,
            granule_id,
            object_key,
            job_type,
            restore_bucket_dest,
            archive_bucket_dest,
            job_status,
            request_time,
            last_update_time,
            err_msg
        FROM
            request_status
        WHERE
        request_group_id = %s
        """
    orderby = """ order by last_update_time desc """
    try:
        sql = sql + orderby
        dbconnect_info = get_dbconnect_info()
        rows = database.single_query(sql, dbconnect_info, (request_group_id,))
        result = result_to_json(rows)
    except DbError as err:
        LOGGER.exception(f"DbError: {str(err)}")
        raise DatabaseError(str(err))

    return result


def result_to_json(result_rows: list) -> list:
    """
    Converts a database result to Json format

    Args:
        result_rows: The object to convert to json.

    Returns: todo
    """
    json_result = json.loads(json.dumps(result_rows, default=datetime_to_string_converter))
    return json_result


# todo: Why is this the default?
def datetime_to_string_converter(obj: any) -> Optional[str]:  # pylint: disable-msg=inconsistent-return-statements
    f"""
    # todo: The description below is inaccurate. Investigate and fix description or code.
    If {obj} is a {datetime.datetime}, returns the {datetime.datetime.__str__}.

    Args:
        obj: The object to convert.
        
    Returns: The datetime as a string.
        ex. '2019-07-17 17:36:38.494918'
    """
    if isinstance(obj, datetime.datetime):
        return obj.__str__()
