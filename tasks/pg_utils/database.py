"""
This module exists to keep all database specific code in a single place. The
cursor and connection objects can be imported and used directly, but for most
queries, simply using the "query()" function will likely suffice.
"""

import logging
import json
import os

from contextlib import contextmanager
import datetime
import uuid
# noinspection PyPackageRequirements
from typing import Optional, Any, Union, List, Dict

# noinspection PyPackageRequirements
import boto3
from psycopg2 import DataError, ProgrammingError
from psycopg2 import connect as psycopg2_connect
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection, cursor

LOGGER = logging.getLogger(__name__)


# TODO develop tests for database.py later. in those mock psycopg2.cursor, etc

class DbError(Exception):
    """
    Exception to be raised if there is a database error.
    """


class ResourceExists(Exception):
    """
    Exception to be raised if there is an existing database resource.
    """


def get_utc_now_iso() -> str:
    """
    Takes the current utc timestamp and returns it an isoformat string.

    Returns:
        An isoformat string.
        ex. '2019-07-17T17:36:38.494918'
    """
    return datetime.datetime.utcnow().isoformat()


def uuid_generator() -> str:
    """
    Generates a unique UUID.

    Returns:
        A string representing a UUID.
        ex. '0000a0a0-a000-00a0-00a0-0000a0000000'
    """
    my_uuid = uuid.uuid4()
    return str(my_uuid)


def result_to_json(result_rows):  # todo: return type
    """
    Converts a database result to Json format

    Args:
        result_rows: The object to convert to json.

    Returns: todo
    """
    json_result = json.loads(json.dumps(result_rows, default=myconverter))  # todo: wha?
    return json_result


# todo: Figure out how the README.md is generated.
def myconverter(obj: any) -> Optional[str]:  # pylint: disable-msg=inconsistent-return-statements
    """
    # todo: The description below is inaccurate. Investigate and fix description or code.
    Returns the current utc timestamp as a string in isoformat
    ex. '2019-07-17T17:36:38.494918'

    Args:
        obj: todo
    """
    if isinstance(obj, datetime.datetime):
        return obj.__str__()


@contextmanager
def get_connection(dbconnect_info: Dict[str, Union[str, int]]) -> connection:
    """
    Retrieves a connection from the connection pool and yields it.

    Args:
        dbconnect_info: A dictionary with the following keys:
            db_port (str): The database port. Default is 5432.
            db_host (str): The database host.
            db_name (str): The database name.
            db_user (str): The username to connect to the database with.
            db_pw (str): The password to connect to the database with.
    """
    # create and yield a connection
    try:
        db_port = dbconnect_info["db_port"]
    except ValueError:
        db_port = 5432

    new_connection = None
    try:
        new_connection = psycopg2_connect(
            host=dbconnect_info["db_host"],
            port=db_port,
            database=dbconnect_info["db_name"],
            user=dbconnect_info["db_user"],
            password=dbconnect_info["db_pw"]
        )
        yield new_connection

    except Exception as ex:
        raise DbError(f"Database Error. {str(ex)}")

    finally:
        if new_connection:
            new_connection.close()


@contextmanager
def get_cursor(dbconnect_info: dict[str, Union[str, int]]) -> cursor:
    """
    Retrieves the cursor from the connection and yields it. Automatically
    commits the transaction if no exception occurred.

    Args:
        dbconnect_info: A dictionary with the following keys:
            db_port (str): The database port. Default is 5432.
            db_host (str): The database host.
            db_name (str): The database name.
            db_user (str): The username to connect to the database with.
            db_pw (str): The password to connect to the database with.
    """
    with get_connection(dbconnect_info) as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            yield cursor
            conn.commit()

        except:
            conn.rollback()
            raise

        finally:
            cursor.close()


def single_query(sql_stmt, dbconnect_info: dict[str, Union[str, int]], params=None):
    """
    This is a convenience function for running single statement transactions
    against the database. It will automatically commit the transaction and
    return a list of the rows.

    For multi-query transactions, see multi_query().

    Args:
        dbconnect_info: A dictionary with the following keys:
            db_port (str): The database port. Default is 5432.
            db_host (str): The database host.
            db_name (str): The database name.
            db_user (str): The username to connect to the database with.
            db_pw (str): The password to connect to the database with.
    """
    rows = []

    with get_cursor(dbconnect_info) as cursor:
        rows = _query(sql_stmt, params, cursor)

    return rows


def read_db_connect_info(param_source):  # todo: wha?
    """
    This function will retrieve database connection parameters from
    the parameter store and/or env vars.

        Args:
            param_source (dict): A dict containing
                "db_host": {env_or_ssm, param_name},
                "db_port": {env_or_ssm, param_name},
                "db_name": {env_or_ssm, param_name},
                "db_user": {env_or_ssm, param_name},
                "db_pw": {env_or_ssm, param_name}
                where the value of env_or_ssm is: "env" to read env var,
                                                  "ssm" to read parameter store


        Returns:
            dbconnect_info: A dict containing
                "db_host": value,
                "db_port": value,
                "db_name": value,
                "db_user": value,
                "db_pw": value
    """
    dbconnect_info = {}
    host_info = param_source["db_host"]
    for key in host_info:  # todo: why is there a loop for setting a single variable?
        val = host_info[key]
        dbconnect_info["db_host"] = get_db_connect_info(key, val, False)

    port_info = param_source["db_port"]
    for key in port_info:
        val = port_info[key]
        dbconnect_info["db_port"] = int(get_db_connect_info(key, val, False))

    name_info = param_source["db_name"]
    for key in name_info:
        val = name_info[key]
        dbconnect_info["db_name"] = get_db_connect_info(key, val, False)

    user_info = param_source["db_user"]
    for key in user_info:
        val = user_info[key]
        dbconnect_info["db_user"] = get_db_connect_info(key, val, False)

    pw_info = param_source["db_pw"]
    for key in pw_info:
        val = pw_info[key]
        dbconnect_info["db_pw"] = get_db_connect_info(key, val, True)

    return dbconnect_info


def get_db_connect_info(env_or_ssm: str, param_name, decrypt: bool = False):
    f"""
    This function will retrieve a database connection parameter from
    the parameter store or an env var.
    
    Args:
        env_or_ssm: "env" to read env var, "ssm" to read parameter store.
        param_name: The name of the parameter to retrieve from env for parameter store.
        decrypt: When true and {env_or_ssm} is "ssm", will tell get_parameter to decrypt.
    """
    if env_or_ssm == "ssm":
        ssm = boto3.client('ssm')
        if decrypt:
            parameter = ssm.get_parameter(Name=param_name, WithDecryption=True)
        else:
            parameter = ssm.get_parameter(Name=param_name)
        param_value = parameter['Parameter']['Value']
    else:
        param_value = os.environ[param_name]

    return param_value


def multi_query(sql_stmt, params, db_cursor: cursor) -> List:
    """
    This function will use the provided cursor to run the query instead of
    retrieving one itself. This is intended to be used when the caller wants
    to make a query that doesn't automatically commit and close the cursor.
    Like single_query(), this will return the rows as a list.

    This function should be used within a context made by get_cursor().
    """

    return _query(sql_stmt, params, db_cursor)


def _query(sql_stmt, params, db_cursor: cursor) -> List:
    """
    Wrapper for running queries that will automatically handle errors in a
    consistent manner.

    Returns the result of the query returned by fetchall()
    """

    try:
        db_cursor.execute(sql.SQL(sql_stmt), params)

    except (ProgrammingError, DataError) as err:
        LOGGER.exception(f"database error - {err}")
        raise DbError("Internal database error, please contact LP DAAC User Services")

    try:
        rows = db_cursor.fetchall()

    except ProgrammingError as err:
        # no results, return an empty list
        rows = []

    return rows


# todo: What is the difference between this and get_connection?
def return_connection(dbconnect_info) -> connection:
    """
    Retrieves a connection from the connection pool.
    """
    # create a connection
    try:
        db_port = dbconnect_info["db_port"]
    except ValueError:
        db_port = 5432

    try:
        return psycopg2_connect(
            host=dbconnect_info["db_host"],
            port=db_port,
            database=dbconnect_info["db_name"],
            user=dbconnect_info["db_user"],
            password=dbconnect_info["db_pw"]
        )

    except Exception as ex:
        LOGGER.exception(f"Exception. {str(ex)}")
        raise DbError(f"Database Error. {str(ex)}")


def return_cursor(conn: connection) -> cursor:
    f"""
    Retrieves the cursor from the connection.
    
    Args:
        conn: The connection to get the cursor for.
    
    Returns:
        The cursor for the given {connection}.
        
    Raises:
        DbError: Any exception occurs while retrieving cursor.
    """
    try:
        return conn.cursor(cursor_factory=RealDictCursor)
    except Exception as ex:
        LOGGER.exception(f"Exception. {str(ex)}")
        raise DbError(f"Database Error. {str(ex)}")


def query_no_params(db_cursor: cursor, sql_stmt) -> str:
    """
    This function will use the provided cursor to run the sql_stmt.

    Args:
        db_cursor: The cursor to the target database.
        sql_stmt: The SQL statement to execute against the database.

    Returns:
        A string indicating that the statement has been executed.

    Raises:
        DbError: Something went wrong while executing the statement.
    """
    try:
        db_cursor.execute(sql.SQL(sql_stmt))
        return f"done executing {sql_stmt}"
    except (ProgrammingError, DataError) as ex:
        LOGGER.exception(f"Database Error - {ex}")
        raise DbError(f"Database Error. {str(ex)}")


def query_from_file(db_cursor: cursor, sql_file):  # todo: filename or path?
    """
    This function will execute the sql in a file.
    """
    try:
        db_cursor.execute(open(sql_file, "r").read())
        return f"sql from {sql_file} executed"
    except (ProgrammingError, DataError) as ex:
        msg = str(ex).replace("\n", "")
        if msg.endswith("already exists"):
            raise ResourceExists(ex)

        LOGGER.exception(f"Database Error. {str(ex)}")
        raise DbError(f"Database Error. {str(ex)}")
