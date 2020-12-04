** Shared code to access a postgres database **

- [Setup](#setup)
- [Development](#development)
  * [Unit Testing and Coverage](#unit-testing-and-coverage)
  * [Linting](#linting)
- [Deployment](#deployment)
- [pydoc database](#pydoc-database)


<a name="setup"></a>
# Setup
    See the README in the tasks folder for general development setup instructions

<a name="development"></a>
# Development

<a name="unit-testing-and-coverage"></a>
## Unit Testing and Coverage
```
Run the tests:
cd C:\devpy\poswotdr\tasks\pg_utils\test
λ activate podr
All tests:
(podr) λ pytest

Individual tests (insert desired test file name):
(podr) λ pytest test/test_database.py

Code Coverage:
(podr) λ cd C:\devpy\poswotdr\tasks\pg_utils
(podr) λ coverage run --source pg_utils -m pytest
(podr) λ coverage report

Name          Stmts   Miss  Cover
---------------------------------
database.py     136     56    59%
----------------------------------------------------------------------
Ran 6 tests in 0.753s
```
<a name="linting"></a>
## Linting
```
Run pylint against the code:

(podr) λ pylint database.py
************* Module database
database.py:20:1: W0511: TODO develop tests for database.py later. in those mock psycopg2.cursor, etc (fixme)
-------------------------------------------------------------------
Your code has been rated at 9.92/10 (previous run: 9.92/10, +0.00)

(podr) λ pylint test/test_database.py
--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)

(podr) λ pylint db_config.py
--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)
```
<a name="deployment"></a>
## Deployment
```
https://www.oreilly.com/library/view/head-first-python/9781491919521/ch04.html
Create the distribution file:
    (podr) λ cd C:\devpy\poswotdr\tasks\pg_utils
    (podr) λ py -3 setup.py sdist
    (podr) λ cd dist
    (podr) λ pip install pg_utils-1.0.tar.gz
 
```
<a name="pydoc-database"></a>
## pydoc database
```
NAME
    database

DESCRIPTION
    This module exists to keep all database specific code in a single place. The
    cursor and connection objects can be imported and used directly, but for most
    queries, simply using the "query()" fuction will likely suffice.

CLASSES
    builtins.Exception(builtins.BaseException)
        DbError
        ResourceExists

    class DbError(builtins.Exception)
     |  Exception to be raised if there is a database error.

    class ResourceExists(builtins.Exception)
     |  Exception to be raised if there is an existing database resource.


FUNCTIONS
    get_connection()
        Retrieves a connection from the connection pool and yields it.

    get_cursor()
        Retrieves the cursor from the connection and yields it. Automatically
        commits the transaction if no exception occurred.

    get_utc_now_iso()
        Returns the current utc timestamp as a string in isoformat
        ex. '2019-07-17T17:36:38.494918'

    multi_query(sql_stmt, params, cursor)
        This function will use the provided cursor to run the query instead of
        retreiving one itself. This is intended to be used when the caller wants
        to make a query that doesn't automatically commit and close the cursor.
        Like single_query(), this will return the rows as a list.

        This function should be used within a context made by get_cursor().

    myconverter(obj)
        Returns the current utc timestamp as a string in isoformat
        ex. '2019-07-17T17:36:38.494918'

    query_from_file(cursor, sql_file)
        This function will execute the sql in a file.                

    query_no_params(cursor, sql_stmt)
        This function will use the provided cursor to run the sql_stmt.

    result_to_json(result_rows)
        Converts a database result to Json format

    return_connection()
        Retrieves a connection from the connection pool.

    return_cursor(conn)
        Retrieves the cursor from the connection.

    single_query(sql_stmt, params=None)
        This is a convenience function for running single statement transactions
        against the database. It will automatically commit the transaction and
        return a list of the rows.

        For multi-query transactions, see multi_query().

    uuid_generator()
        Returns a unique UUID
        ex. '0000a0a0-a000-00a0-00a0-0000a0000000'

DATA
    LOGGER = <Logger database (WARNING)>    
```
