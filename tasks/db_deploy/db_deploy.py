"""
Name: db_deploy.py

Description:  Deploys a database, roles, users, schema, and tables.
"""
import os
from os import walk
import logging
from typing import Dict, Tuple, List

from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT, ISOLATION_LEVEL_READ_COMMITTED, connection, cursor
import boto3
import database
from database import DbError, ResourceExists

# Set Global Variables
_LOG = logging.getLogger(__name__)
SEP = os.path.sep


class DatabaseError(Exception):
    """
    Exception to be raised when there's a database error.
    """


def task():
    """
    Task called by the handler to perform the work.

        Environment Vars: TODO. Ideally move them into handler so this can be pure params

    Returns:
        string: description of status.

    Raises:
        DatabaseError: An error occurred.
    """
    log_status("start")

    ssm = boto3.client('ssm')
    param_name = 'drdb-user-pass'
    parameter = ssm.get_parameter(Name=param_name, WithDecryption=True)
    db_pw = parameter['Parameter']['Value']

    param_name = 'drdb-admin-pass'
    parameter = ssm.get_parameter(Name=param_name, WithDecryption=True)
    master_user_pw = parameter['Parameter']['Value']
    os.environ["MASTER_USER_PW"] = master_user_pw

    param_name = 'drdb-host'
    parameter = ssm.get_parameter(Name=param_name, WithDecryption=False)
    db_host = parameter['Parameter']['Value']
    os.environ["DATABASE_HOST"] = db_host

    db_name = os.environ["DATABASE_NAME"]
    db_user = os.environ["DATABASE_USER"]
    os.environ["DATABASE_NAME"] = "postgres"
    os.environ["DATABASE_USER"] = "postgres"

    os.environ["DATABASE_PW"] = master_user_pw
    # connect as postgres to create the new database
    con = get_db_connection()

    log_status("Connected to postgres")
    db_existed, status = create_database(con)
    if not db_existed:
        os.environ["DATABASE_PW"] = db_pw
        create_roles_and_users(con, db_user)
    con.close()

    # Connect to the database we just created.
    os.environ["DATABASE_NAME"] = db_name
    os.environ["DATABASE_PW"] = master_user_pw
    con = get_db_connection()
    log_status(f"connected to {db_name}")
    status = create_schema(con)
    con.close()
    create_tables()

    log_status("database ddl execution complete")
    return status


def create_database(con: connection) -> Tuple[bool, str]:
    """
    Creates the database, dropping it first if requested.

        Args:
            con: a connection to the postgres database

        Returns:
            bool: True if the database already existed
                when the create was run.
            string: description of status of create database.

        Raises:
            DatabaseError: An error occurred.
    """
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = get_cursor(con)
    try:
        drop = os.environ["DROP_DATABASE"]
    except KeyError:
        drop = "False"
    if drop == "True":  # todo: Fix dangerous string compare
        sql_file = f"database{SEP}database_drop.sql"
        execute_sql_from_file(cur, sql_file, "drop database")
    try:
        sql_file = f"database{SEP}database_create.sql"
        execute_sql_from_file(cur, sql_file, "database create")
        sql_file = f"database{SEP}database_comment.sql"
        status = execute_sql_from_file(cur, sql_file, "database comment")
        db_existed = False
    except ResourceExists as err:
        _LOG.warning(f"ResourceExists: {str(err)}")
        db_existed = True
        status = "database already exists"
        log_status(status)
    cur.close()
    return db_existed, status


def create_roles_and_users(con: connection, db_user):
    """
    Creates the roles and users.

        Args:
            con (object): a connection to the postgres database
            db_user (string): the application user

        Returns:
            string: description of status of create roles and users.

        Raises:
            DatabaseError: An error occurred.
    """
    con.set_isolation_level(ISOLATION_LEVEL_READ_COMMITTED)
    cur = get_cursor(con)
    sql_file = f"roles{SEP}app_role.sql"
    execute_sql_from_file(cur, sql_file, "create application role")
    sql_file = f"roles{SEP}appdbo_role.sql"
    execute_sql_from_file(cur, sql_file, "create appdbo role")
    sql_file = f"users{SEP}dbo.sql"
    execute_sql_from_file(cur, sql_file, "create dbo user")
    sql_file = f"users{SEP}appuser.sql"
    execute_sql_from_file(cur, sql_file, "create application user")
    db_pw = os.environ["DATABASE_PW"]
    sql_stmt = f"ALTER USER {db_user} WITH PASSWORD '{db_pw}';"
    execute_sql(cur, sql_stmt, "set pw for application user")
    sql_stmt = f"ALTER USER dbo WITH PASSWORD '{db_pw}';"
    status = execute_sql(cur, sql_stmt, "set pw for dbo user")
    con.commit()
    cur.close()
    return status


def create_schema(con: connection) -> str:
    """
    Creates the database schema.

        Args:
            con (object): a connection to the new database just created

        Returns:
            string: description of status of create schema.

        Raises:
            DatabaseError: An error occurred.
    """
    platform = os.environ["PLATFORM"]
    _LOG.info(f"platform: {platform}")
    cur = get_cursor(con)
    if platform == "AWS":
        sql_stmt = """SET SESSION AUTHORIZATION dbo;"""
        execute_sql(cur, sql_stmt, "auth dbo")

    sql_file = f"schema{SEP}app.sql"
    status = execute_sql_from_file(cur, sql_file, "create schema")
    cur.close()
    con.commit()
    return status


def create_tables():
    """
    Creates the database tables.

        Raises:
            DatabaseError: An error occurred.
    """
    ddl_dir = os.environ["DDL_DIR"]
    table_dir = f"{ddl_dir}{SEP}tables"
    sql_file_names = get_file_names_in_dir(table_dir)
    for file in sql_file_names:
        sql_file = f"tables{SEP}{file}"
        try:
            con = get_db_connection()
            cur = get_cursor(con)
            sql_stmt = """SET SESSION AUTHORIZATION dbo;"""
            execute_sql(cur, sql_stmt, "auth dbo")
            execute_sql_from_file(cur, sql_file, f"create table in {sql_file}")
            con.close()
        except ResourceExists as dd_err:
            _LOG.warning(f"ResourceExists: {str(dd_err)}")
            log_status(f"table in {sql_file} already exists")


def get_file_names_in_dir(directory: str) -> List[str]:
    """
    Returns a list of all the filenames in the given directory.

    Args:
        directory: The name of the directory containing the files. todo: Path or name?

    Returns:
        List of the file names in the given directory.
    """
    dir_files = []
    for (_, _, filenames) in walk(directory):
        for name in filenames:
            if name != "init.sql":
                dir_files.append(name)
    dir_files.sort()
    return dir_files


def log_status(status) -> None:
    """
    Writes an info level event to _LOG.

    Args:
        status (string): The status to be logged.
    """
    _LOG.info(status)
    # print(status)


def get_db_connection() -> connection:
    """
    Gets a database connection.

    Returns:
        A connection to a database.  todo: which database?

    Raises:
        DatabaseError: An error occurred.
    """
    try:
        log_status(f"Connect to database started")
        db_connect_info = {"db_host": os.environ["DATABASE_HOST"], "db_port": os.environ["DATABASE_PORT"],
                          "db_name": os.environ["DATABASE_NAME"], "db_user": os.environ["DATABASE_USER"],
                          "db_pw": os.environ["DATABASE_PW"]}

        con = database.return_connection(db_connect_info)
        log_status(f"Connect to database completed")
    except DbError as err:
        _LOG.exception(f"DbError: {str(err)}")
        log_status("Connect to database DbError")
        raise DatabaseError(str(err))
    return con


def get_cursor(con: connection) -> cursor:
    """
    Gets a cursor for the database connection.

        Args:
            con: A connection to a database.

        Returns:
            A cursor for the given connection.

        Raises:
            DatabaseError: An error occurred.
    """
    try:
        cur = database.return_cursor(con)
    except DbError as err:
        _LOG.exception(f"DbError: {str(err)}")
        log_status("Get cursor DbError")
        raise DatabaseError(str(err))
    return cur


def execute_sql(cur: cursor, sql_stmt: str, description: str) -> str:
    """
    Executes the given SQL statement using the given cursor.

        Args:
            cur: A cursor to the database.
            sql_stmt: The sql statement to execute.
            description: A brief description of what the sql does. Used for logging.

        Returns:
            Description of status of the sql_stmt.

        Raises:
            DatabaseError: An error occurred.
    """
    try:
        log_status(f"{description} started")
        database.query_no_params(cur, sql_stmt)
        status = f"{description} completed"
        log_status(status)
    except DbError as err:
        _LOG.exception(f"DbError: {str(err)}")
        log_status(f"{description} DbError")
        raise DatabaseError(str(err))
    return status  # todo: Remove unused return


def execute_sql_from_file(cur: cursor, sql_file_name: str, description: str):
    """
    Executes the sql in a file.

        Args:
            cur: a cursor to the database
            sql_file_name: Name of the file containing a sql statement to execute.
                Must be in the folder pointed to by os.environ["DDL_DIR"].
            description: A brief description of what the sql does. Used for logging.

        Returns:
            Description of status of the sql_stmt.

        Raises:
            DatabaseError: An error occurred.
    """
    ddl_dir = os.environ["DDL_DIR"]
    try:
        log_status(f"{description} started")
        sql_path = f"{ddl_dir}{sql_file_name}"
        database.query_from_file(cur, sql_path)
        status = f"{description} completed"
        log_status(status)
    except FileNotFoundError as fnf:
        _LOG.exception(f"DbError: {str(fnf)}")
        log_status(f"{description} DbError")
        raise DatabaseError(str(fnf))
    except DbError as err:
        _LOG.exception(f"DbError: {str(err)}")
        log_status(f"{description} DbError")
        raise DatabaseError(str(err))
    return status  # todo: Remove unused return


def handler(event: Dict, context: object) -> str:  # pylint: disable-msg=unused-argument
    """
    This task will create the database, roles, users, schema, and tables.

        Environment Vars:
            DATABASE_PORT (string): the database port. The standard is 5432.
            DATABASE_NAME (string): the name of the database being created.
            DATABASE_USER (string): the name of the application user.
            DROP_DATABASE (bool, optional, default is False): When true, will
                execute a DROP DATABASE command.
            PLATFORM (string): 'onprem' or 'AWS'

        Parameter Store:
            drdb-user-pass (string): the password for the application user (DATABASE_USER).
            drdb-host (string): the database host
            drdb-admin-pass: the password for the admin user

        Args:
            event: An object required by AWS Lambda. Unused.
            context: An object required by AWS Lambda. Unused.

        Returns:
            Status description.

        Raises:
            DatabaseError: An error occurred.  todo: Why not use the DbError that is already defined? todo: Add detail.
    """
    result = task()
    return result
