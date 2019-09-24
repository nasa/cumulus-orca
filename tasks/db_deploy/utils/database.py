"""
This module exists to keep all database specific code in a single place.

It depends on environment variables:
    DATABASE_HOST - the server where the database will reside.
    DATABASE_NAME - the name of the database being created.
    DATABASE_USER - the name of the application user.
    DATABASE_PW - the password for the application user.
"""

import logging

import os

from psycopg2 import DataError, ProgrammingError
from psycopg2 import connect as psycopg2_connect
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

LOGGER = logging.getLogger(__name__)

#TODO develop tests for database.py later. in those mock psycopg2.cursor, etc

class DbError(Exception):
    """
    Exception to be raised if there is a database error.
    """

class ResourceExists(Exception):
    """
    Exception to be raised if there is an existing database resource.
    """

def return_connection():
    """
    Retrieves a connection from the connection pool.
    """
    # create a connection
    connection = None
    try:
        connection = psycopg2_connect(
            host=os.environ["DATABASE_HOST"],
            database=os.environ["DATABASE_NAME"],
            user=os.environ["DATABASE_USER"],
            password=os.environ["DATABASE_PW"]
        )
        return connection

    except Exception as ex:
        LOGGER.exception(f"Exception. {str(ex)}")
        raise DbError(f"Database Error. {str(ex)}")


def return_cursor(conn):
    """
    Retrieves the cursor from the connection.
    """
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        return cursor
    except Exception as ex:
        LOGGER.exception(f"Exception. {str(ex)}")
        raise DbError(f"Database Error. {str(ex)}")


def query_no_params(cursor, sql_stmt):
    """
    This function will use the provided cursor to run the sql_stmt.
    """
    try:
        cursor.execute(sql.SQL(sql_stmt))
        return f"done executing {sql_stmt}"
    except (ProgrammingError, DataError) as ex:
        LOGGER.exception(f"Database Error - {ex}")
        raise DbError(f"Database Error. {str(ex)}")

def query_from_file(cursor, sql_file):
    """
    This function will execute the sql in a file.
    """
    try:
        cursor.execute(open(sql_file, "r").read())
        return f"sql from {sql_file} executed"
    except FileNotFoundError as fnfe:
        LOGGER.exception(f"FileNotFoundError. {str(fnfe)}")
        raise DbError(f"Database Error. {str(fnfe)}")
    except (ProgrammingError, DataError) as ex:
        msg = str(ex).replace("\n", "")
        if msg.endswith("already exists"):
            raise ResourceExists(ex)
        LOGGER.exception(f"Database Error. {str(ex)}")
        raise DbError(f"Database Error. {str(ex)}")
