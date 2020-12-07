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
# noinspection PyPackageRequirements
import database
# noinspection PyPackageRequirements
from database import DbError, ResourceExists

# Set Global Variables
_LOG = logging.getLogger(__name__)
SEP = os.path.sep

OS_ENVIRON_DATABASE_PORT_KEY = 'DATABASE_PORT'
OS_ENVIRON_DATABASE_NAME_KEY = 'DATABASE_NAME'
OS_ENVIRON_DATABASE_USER_KEY = 'DATABASE_USER'
OS_ENVIRON_PLATFORM_KEY = 'PLATFORM'
OS_ENVIRON_DDL_DIR_KEY = 'DDL_DIR'
OS_ENVIRON_DROP_DATABASE_KEY = 'DROP_DATABASE'


class DatabaseError(Exception):
    """
    Exception to be raised when there's a database error.
    """


def task() -> str:
    """
    Task called by the handler to perform the work.

        Environment Vars: TODO. Ideally move them into handler so this can be pure params

    Returns:
        string: description of status.

    Raises:
        DatabaseError: An error occurred.
    """

    ssm = boto3.client('ssm')
    parameter = ssm.get_parameter(Name='drdb-user-pass', WithDecryption=True)
    db_user_pw = parameter['Parameter']['Value']

    parameter = ssm.get_parameter(Name='drdb-admin-pass', WithDecryption=True)
    master_user_pw = parameter['Parameter']['Value']

    parameter = ssm.get_parameter(Name='drdb-host', WithDecryption=False)
    db_host = parameter['Parameter']['Value']

    drop_database = os.environ.get(OS_ENVIRON_DROP_DATABASE_KEY, 'False')
    drop_database = (drop_database == 'True')

    return inner_task(db_host,
                      os.environ[OS_ENVIRON_DATABASE_NAME_KEY],
                      os.environ[OS_ENVIRON_DATABASE_PORT_KEY],
                      os.environ[OS_ENVIRON_DATABASE_USER_KEY],
                      db_user_pw, master_user_pw, drop_database)


def inner_task(db_host: str, db_name: str, db_port: str, db_user: str, db_user_pass: str, db_admin_pass: str,
               drop_database: bool) -> str:  # todo: Once large tests are adjusted/dropped, consider code reorg.
    """
    Task called by the handler to perform the work.

    Args:
        db_host: The database host.
        db_name: The name of the database.
        db_port: The database port.
        db_user: The name of the application user.
        db_user_pass: The password for the application user to connect to the database with.
        db_admin_pass: An admin level password to connect to the database with.
        drop_database: When true, will execute a DROP DATABASE command.

    Returns:
        string: description of status.

    Raises:
        DatabaseError: An error occurred.
    """
    log_status("start")

    # connect as postgres to create the new database
    con = get_db_connection(db_host, 'postgres', db_port, 'postgres', db_admin_pass)

    log_status("Connected to postgres")
    db_existed, status = create_database(con, drop_database)
    if not db_existed:
        create_roles_and_users(con, db_user, db_user_pass)
    con.close()

    # Connect to the database we just created.
    con = get_db_connection(db_host, db_name, db_port, 'postgres', db_admin_pass)
    log_status(f"connected to {db_name}")
    status = create_schema(con)
    con.close()
    create_tables(db_host, db_name, db_port, 'postgres', db_admin_pass)

    log_status("database ddl execution complete")
    return status


def create_database(con: connection, drop_database: bool) -> Tuple[bool, str]:
    """
    Creates the database, dropping it first if requested.

    Args:
        con: A connection to the postgres database.
        drop_database: When true, will execute a DROP DATABASE command.

    Returns:
        bool: True if the database already existed
            when the create was run.
        string: description of status of create database.

    Raises:
        DatabaseError: An error occurred.
    """
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = get_cursor(con)

    if drop_database:
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


def create_roles_and_users(con: connection, db_user: str, db_password: str) -> str:
    """
    Creates the roles and users.

    Args:
        con (object): a connection to the postgres database
        db_user: The username to connect to the database with.
        db_password: The password to connect to the database with.

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
    sql_stmt = f"ALTER USER {db_user} WITH PASSWORD '{db_password}';"
    execute_sql(cur, sql_stmt, "set pw for application user")
    sql_stmt = f"ALTER USER dbo WITH PASSWORD '{db_password}';"
    status = execute_sql(cur, sql_stmt, "set pw for dbo user")
    con.commit()
    cur.close()
    return status


def create_schema(con: connection) -> str:
    """
    Pulls in 'schema\app.sql' and applies it to the database over the given {con}.

    Args:
        con: A connection to the database.

    Returns:
        Description of status of create schema.

    Raises:
        DatabaseError: An error occurred.
    """
    platform = os.environ[OS_ENVIRON_PLATFORM_KEY]
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


def create_tables(db_host: str, db_name: str, db_port: str, db_user: str, db_password: str) -> None:
    """
    Creates the database tables.

    Args:
        db_host: The database host.
        db_name: The name of the database.
        db_port: The database port.
        db_user: The username to connect to the database with.
        db_password: The password to connect to the database with.

    Raises:
        DatabaseError: An error occurred.
    """
    ddl_dir = os.environ[OS_ENVIRON_DDL_DIR_KEY]  # todo: Move close to other os.environ
    table_dir = f"{ddl_dir}{SEP}tables"
    sql_file_names = get_file_names_in_dir(table_dir)
    for file in sql_file_names:
        sql_file = f"tables{SEP}{file}"
        try:
            con = get_db_connection(db_host, db_name, db_port, db_user, db_password)
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
        directory: The name of the directory containing the files. todo: Given usage, this is a path. Please confirm.

    Returns:
        List of the file names in the given directory.
    """
    dir_files = []
    for (_, _, filenames) in walk_wrapper(directory):
        for name in filenames:
            if name != 'init.sql':
                dir_files.append(name)
    dir_files.sort()
    return dir_files


def walk_wrapper(directory: str) -> List[Tuple[str, List, str]]:
    """
    A wrapper for os.walk for testing purposes.
    """
    return walk(directory)


def log_status(status) -> None:
    """
    Writes an info level event to _LOG.

    Args:
        status (string): The status to be logged.
    """
    _LOG.info(status)
    # print(status)


def get_db_connection(db_host: str, db_name: str, db_port: str, db_user: str, db_password: str) -> connection:
    """
    Gets a database connection to the database pointed to by environment variables.

    Args:
        db_host: The database host.
        db_name: The name of the database.
        db_port: The database port.
        db_user: The username to connect to the database with.
        db_password: The password to connect to the database with.

    Returns:
        A connection to a database.

    Raises:
        DatabaseError: An error occurred.
    """
    try:
        log_status(f"Connect to database {db_name} as user {db_user} started")
        db_connect_info = {"db_host": db_host,
                           "db_port": db_port,
                           "db_name": db_name,
                           "db_user": db_user,
                           "db_pw": db_password}

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
        # todo: Seems the point here is to mask DbErrors. Why do we not want them raised?
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


def execute_sql_from_file(cur: cursor, sql_file_name: str, description: str) -> str:
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
    ddl_dir = os.environ[OS_ENVIRON_DDL_DIR_KEY]
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


# noinspection PyUnusedLocal
def handler(event: Dict, context: object) -> str:  # pylint: disable-msg=unused-argument
    """
    This task will create the database, roles, users, schema, and tables.

    Environment Vars:
        DATABASE_PORT (str): The database port. The standard is 5432 (default within pg_utils).
        DATABASE_NAME (str): The name of the database being created.
        DATABASE_USER (str): The name of the application user.
        PLATFORM (string): 'onprem' or 'AWS'
        DDL_DIR (str): todo
        DROP_DATABASE (str, optional, default is False): When 'True', will
            execute a DROP DATABASE command.

    Parameter Store:
        drdb-user-pass (string): The password for the application user (DATABASE_USER).
        drdb-host (string): The database host.
        drdb-admin-pass: The password for the admin user

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
