"""
This module exists to keep all database specific code in a single place. The
cursor and connection objects can be imported and used directly, but for most
queries, simply using the "query()" fuction will likely suffice.
"""

import logging

import os

from contextlib import contextmanager

from psycopg2 import DataError, ProgrammingError
from psycopg2 import connect as psycopg2_connect
from psycopg2.extras import RealDictCursor

LOGGER = logging.getLogger(__name__)

class DbError(Exception):
    """
    Exception to be raised if there is a database error.
    """


@contextmanager
def get_connection():
    """
    Retrieves a connection from the connection pool and yields it.
    """
    # create and yield a connection
    connection = None
    try:
        connection = psycopg2_connect(
            host=os.environ["DATABASE_HOST"],
            database=os.environ["DATABASE_NAME"],
            user=os.environ["DATABASE_USER"],
            password=os.environ["DATABASE_PW"],
        )
        yield connection

    except Exception as ex:
        raise DbError("Database Error. {}".format(str(ex)))

    finally:
        if connection:
            connection.close()


@contextmanager
def get_cursor():
    """
    Retrieves the cursor from the connection and yields it. Automatically
    commits the transaction if no exception occurred.
    """
    with get_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            yield cursor
            conn.commit()

        except:
            conn.rollback()
            raise

        finally:
            cursor.close()


def single_query(sql, params=None):
    """
    This is a convenience function for running single statement transactions
    against the database. It will automatically commit the transaction and
    return a list of the rows.

    For multi-query transactions, see multi_query().
    """
    rows = []
    with get_cursor() as cursor:
        rows = _query(sql, params, cursor)

    return rows


def multi_query(sql, params, cursor):
    """
    This function will use the provided cursor to run the query instead of
    retreiving one itself. This is intended to be used when the caller wants
    to make a query that doesn't automatically commit and close the cursor.
    Like single_query(), this will return the rows as a list.

    This function should be used within a context made by get_cursor().
    """

    return _query(sql, params, cursor)


def _query(sql, params, cursor):
    """
    Wrapper for running queries that will automatically handle errors in a
    consistent manner.

    Returns the result of the query returned by fetchall()
    """

    try:
        cursor.execute(sql, params)

    except (ProgrammingError, DataError) as err:
        LOGGER.exception(f"database error - {err}")
        raise DbError("Internal database error, please contact LP DAAC User Services")

    try:
        rows = cursor.fetchall()

    except (ProgrammingError) as err:
        # no results, return an empty list
        rows = []

    return rows
