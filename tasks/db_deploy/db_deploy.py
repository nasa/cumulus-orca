"""
Name: db_deploy.py

Description:  Deploys a database, roles, users, schema, and tables.
"""
import os
from os import walk
import logging
from typing import Dict, Tuple, List, Iterator

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


def task() -> None:
    """
    Task called by the handler to perform the work.

        Environment Vars:
            Same as Handler.
            TODO. Ideally move them into handler so this can be pure params

    Raises:
        DatabaseError: An error occurred.
    """
    status = log_status('start')
    db_name = os.environ['DATABASE_NAME']
    db_user = os.environ['DATABASE_USER']
    sm_keys = get_secretsmanager_keys({
        'host': 'drdb-host',
        'user-pass': 'drdb-user-pass',
        'admin-pass': 'drdb-admin-pass'
    })

    secretsmanager = boto3.client('secretsmanager')
    parameter = secretsmanager.get_secret_value(SecretId=sm_keys['user-pass'])
    db_user_pw = parameter['SecretString']

    parameter = secretsmanager.get_secret_value(SecretId=sm_keys['admin-pass'])
    master_user_pw = parameter['SecretString']

    parameter = secretsmanager.get_secret_value(SecretId=sm_keys['host'])
    db_host = parameter['SecretString']

    drop_database = os.environ.get(OS_ENVIRON_DROP_DATABASE_KEY, 'False')
    drop_database = (drop_database == 'True')

    inner_task(db_host,
               os.environ[OS_ENVIRON_DATABASE_NAME_KEY],
               os.environ[OS_ENVIRON_DATABASE_PORT_KEY],
               os.environ[OS_ENVIRON_DATABASE_USER_KEY],
               db_user_pw, master_user_pw, drop_database)


def inner_task(db_host: str, db_name: str, db_port: str, db_user: str, db_user_pass: str, db_admin_pass: str,
               drop_database: bool) -> None:  # todo: Once large tests are adjusted/dropped, consider code reorg.
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
    _LOG.info("start")

    # connect as postgres to create the new database
    con = get_db_connection(db_host, 'postgres', db_port, 'postgres', db_admin_pass)

    _LOG.info("Connected to postgres")
    db_existed = create_database(con, drop_database)
    if not db_existed:
        create_roles_and_users(con, db_user, db_user_pass)
    con.close()

    # Connect to the database we just created.
    con = get_db_connection(db_host, db_name, db_port, 'postgres', db_admin_pass)
    _LOG.info(f"connected to {db_name}")
    create_schema(con)
    con.close()
    create_tables(db_host, db_name, db_port, 'postgres', db_admin_pass)
    _LOG.info("database ddl execution complete")


def get_secretsmanager_keys(params):
    """
    Returns dictionary with values prefixed by os.environ['PREFIX']. If PREFIX
    isn't an environment variable, do nothing.

        Args:
            params (dict): Dictionary of key, string pairs.

        Returns:
            dict: Dictionary with passed in keys and prefixed string values.
    """
    if 'PREFIX' in os.environ:
        prefix = os.environ['PREFIX']
        for key in params.keys():
            params[key] = prefix + '-' + params[key]
    return params


def create_database(con: connection, drop_database: bool) -> bool:
    """
    Creates the database, dropping it first if requested.

    Args:
        con: A connection to the postgres database.
        drop_database: When true, will execute a DROP DATABASE command.

    Returns:
        True if the database already existed
            when the create was run.

    Raises:
        DatabaseError: An error occurred.
    """
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = get_cursor(con)

    if drop_database:
        _LOG.warning('Dropping database.')
        sql_file = f"database{SEP}database_drop.sql"
        execute_sql_from_file(cur, sql_file, "drop database")
    try:
        sql_file = f"database{SEP}database_create.sql"
        execute_sql_from_file(cur, sql_file, "database create")
        sql_file = f"database{SEP}database_comment.sql"
        execute_sql_from_file(cur, sql_file, "database comment")
        db_existed = False
        _LOG.warning('Database did not exist.')
    except ResourceExists as err:
        db_existed = True
        _LOG.warning(f"Database already exists: {str(err)}")
    finally:
        cur.close()
    return db_existed


def create_roles_and_users(con: connection, db_user: str, db_password: str) -> None:
    """
    Creates the roles and users.

    Args:
        con (object): a connection to the postgres database
        db_user: The username to connect to the database with.
        db_password: The password to connect to the database with.

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
    execute_sql(cur, sql_stmt, "set pw for dbo user")
    con.commit()
    cur.close()


def create_schema(con: connection) -> None:
    """
    Pulls in 'schema\app.sql' and applies it to the database over the given {con}.

    Args:
        con: A connection to the database.

    Raises:
        DatabaseError: An error occurred.
    """
    platform = os.environ[OS_ENVIRON_PLATFORM_KEY]
    _LOG.info(f"platform: {platform}")
    cur = get_cursor(con)
    if platform == 'AWS':
        sql_stmt = """SET SESSION AUTHORIZATION dbo;"""
        execute_sql(cur, sql_stmt, "auth dbo")

    sql_file = f"schema{SEP}app.sql"
    execute_sql_from_file(cur, sql_file, "create schema")
    cur.close()
    con.commit()


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
    table_dir = f"{ddl_dir}tables"
    sql_file_names = get_file_names_in_dir(table_dir)
    con = get_db_connection(db_host, db_name, db_port, db_user, db_password)
    cur = get_cursor(con)
    try:
        sql_stmt = """SET SESSION AUTHORIZATION dbo;"""
        execute_sql(cur, sql_stmt, "auth dbo")
        for file in sql_file_names:
            sql_file = f"tables{SEP}{file}"
            try:
                execute_sql_from_file(cur, sql_file, f"create table in {sql_file}")
            except ResourceExists as dd_err:
                _LOG.warning(f"ResourceExists error. Table in {sql_file} already exists: {str(dd_err)}")
    finally:
        cur.close()
        con.close()


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
            if name != 'init.sql':  # todo: Is this the correct level to filter this?
                dir_files.append(name)
    dir_files.sort()
    return dir_files


def walk_wrapper(directory: str) -> Iterator[Tuple[str, List[str], List[str]]]:
    """
    A wrapper for os.walk for testing purposes, as os.walk cannot be easily mocked.
    """
    return walk(directory)


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
        _LOG.info(f"Connect to database started")
        db_connect_info = {"db_host": db_host,
                           "db_port": db_port,
                           "db_name": db_name,
                           "db_user": db_user,
                           "db_pw": db_password}

        con = database.return_connection(db_connect_info)
        _LOG.info(f"Connect to database completed")
    except DbError as err:
        _LOG.critical(f"DbError while connecting to database: {str(err)}")
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
        _LOG.critical(f"DbError while getting cursor: {str(err)}")
        # todo: Seems the point here is to mask DbErrors. Why do we not want them raised?
        raise DatabaseError(str(err))
    return cur


def execute_sql(cur: cursor, sql_stmt: str, description: str) -> None:
    """
    Executes the given SQL statement using the given cursor.

    Args:
        cur: A cursor to the database.
        sql_stmt: The sql statement to execute.
        description: A brief description of what the sql does. Used for logging.

    Raises:
        DatabaseError: An error occurred.
    """
    try:
        _LOG.info(f"{description} started")
        database.query_no_params(cur, sql_stmt)
        _LOG.info(f"{description} completed")
    except DbError as err:
        _LOG.critical(f"DbError during '{description}': {str(err)}")
        raise DatabaseError(str(err))


def execute_sql_from_file(cur: cursor, sql_file_name: str, description: str) -> None:
    """
    Executes the sql in a file.

    Args:
        cur: a cursor to the database
        sql_file_name: Name of the file containing a sql statement to execute.
            Must be in the folder pointed to by os.environ["DDL_DIR"].
        description: A brief description of what the sql does. Used for logging.

    Raises:
        DatabaseError: An error occurred.
    """
    ddl_dir = os.environ[OS_ENVIRON_DDL_DIR_KEY]
    _LOG.info(f"{description} started")
    sql_path = f"{ddl_dir}{sql_file_name}"
    try:
        database.query_from_file(cur, sql_path)
        _LOG.info(f"{description} completed")
    except FileNotFoundError as fnf:
        _LOG.critical(f"FileNotFound during '{description}': {str(fnf)}")
        raise DatabaseError(str(fnf))
    except DbError as err:
        _LOG.critical(f"DbError during '{description}': {str(err)}")
        raise DatabaseError(str(err))


# noinspection PyUnusedLocal
def handler(event: Dict, context: object) -> None:  # pylint: disable-msg=unused-argument
    """
    This task will create the database, roles, users, schema, and tables.

    Environment Vars:
        DATABASE_PORT (str): The database port. The standard is 5432 (default within pg_utils).
        DATABASE_NAME (str): The name of the database being created.
        DATABASE_USER (str): The name of the application user.
        PLATFORM (string): 'onprem' or 'AWS'
        DDL_DIR (str): Path (relative or absolute) to the ddl folder containing sql scripts. Must end with trailing '\'
        DROP_DATABASE (str, optional, default is False): When 'True', will
            execute a DROP DATABASE command.

    Parameter Store:
        drdb-user-pass (string): The password for the application user (DATABASE_USER).
        drdb-host (string): The database host.
        drdb-admin-pass: The password for the admin user

    Args:
        event: An object required by AWS Lambda. Unused.
        context: An object required by AWS Lambda. Unused.

    Raises:
        DatabaseError: An error occurred.  todo: Why not use the DbError that is already defined? todo: Add detail.
    """
    task()
