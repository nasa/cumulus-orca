"""
Name: db_deploy.py

Description:  Deploys a database, roles, users, schema, and tables.
"""
import os
from os import walk
import logging
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT, ISOLATION_LEVEL_READ_COMMITTED
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

def task(event, context):    #pylint: disable-msg=unused-argument
    """
    Task called by the handler to perform the work.

        Args:
            event (dict): passed through from the handler
            context (Object): passed through from the handler

        Returns:
            string: description of status.

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
    db_pw = parameter['SecretString']

    parameter = secretsmanager.get_secret_value(SecretId=sm_keys['admin-pass'])
    master_user_pw = parameter['SecretString']
    os.environ['MASTER_USER_PW'] = master_user_pw

    parameter = secretsmanager.get_secret_value(SecretId=sm_keys['host'])
    db_host = parameter['SecretString']
    os.environ['DATABASE_HOST'] = db_host

    os.environ['DATABASE_NAME'] = 'postgres'
    os.environ['DATABASE_USER'] = 'postgres'

    os.environ['DATABASE_PW'] = master_user_pw
    #connect as postgres to create the new database
    con = get_db_connnection()

    status = log_status('connected to postgres')
    db_existed, status = create_database(con)
    if not db_existed:
        os.environ['DATABASE_PW'] = db_pw
        status = create_roles_and_users(con, db_user)
    con.close()

    #connect to the database we just created as postgres
    os.environ['DATABASE_NAME'] = db_name
    os.environ['DATABASE_PW'] = master_user_pw
    con = get_db_connnection()
    status = log_status(f"connected to {db_name}")
    status = create_schema(con)
    con.close()
    status = create_tables()

    status = log_status('database ddl execution complete')
    return status

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

def create_database(con):
    """
    Creates the database, dropping it first if requested.

        Args:
            con (object): a connection to the postgres database

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
        drop = 'False'
    if drop == 'True':
        sql_file = f"database{SEP}database_drop.sql"
        status = execute_sql_from_file(cur, sql_file, 'drop database')
    try:
        sql_file = f"database{SEP}database_create.sql"
        status = execute_sql_from_file(cur, sql_file, 'database create')
        sql_file = f"database{SEP}database_comment.sql"
        status = execute_sql_from_file(cur, sql_file, 'database comment')
        db_existed = False
    except ResourceExists as err:
        _LOG.warning(f"ResourceExists: {str(err)}")
        db_existed = True
        status = log_status('database already exists')
    cur.close()
    return db_existed, status

def create_roles_and_users(con, db_user):
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
    status = execute_sql_from_file(cur, sql_file, 'create application role')
    sql_file = f"roles{SEP}appdbo_role.sql"
    status = execute_sql_from_file(cur, sql_file, 'create appdbo role')
    sql_file = f"users{SEP}dbo.sql"
    status = execute_sql_from_file(cur, sql_file, 'create dbo user')
    sql_file = f"users{SEP}appuser.sql"
    status = execute_sql_from_file(cur, sql_file, 'create application user')
    db_pw = os.environ['DATABASE_PW']
    sql_stmt = f"ALTER USER {db_user} WITH PASSWORD '{db_pw}';"
    status = execute_sql(cur, sql_stmt, 'set pw for application user')
    sql_stmt = f"ALTER USER dbo WITH PASSWORD '{db_pw}';"
    status = execute_sql(cur, sql_stmt, 'set pw for dbo user')
    con.commit()
    cur.close()
    return status

def create_schema(con):
    """
    Creates the database schema.

        Args:
            con (object): a connection to the new database just created

        Returns:
            string: description of status of create schema.

        Raises:
            DatabaseError: An error occurred.
    """
    platform = os.environ['PLATFORM']
    _LOG.info(f"platform: {platform}")
    cur = get_cursor(con)
    if platform == 'AWS':
        sql_stmt = """SET SESSION AUTHORIZATION dbo;"""
        status = execute_sql(cur, sql_stmt, 'auth dbo')

    sql_file = f"schema{SEP}app.sql"
    status = execute_sql_from_file(cur, sql_file, 'create schema')
    cur.close()
    con.commit()
    return status

def create_tables():
    """
    Creates the database tables.

        Args:
            con (object): a connection to the new database just created

        Returns:
            string: description of status of create tables.

        Raises:
            DatabaseError: An error occurred.
    """
    ddl_dir = os.environ['DDL_DIR']
    table_dir = f"{ddl_dir}{SEP}tables"
    sql_files = get_files_in_dir(table_dir)
    for file in sql_files:
        sql_file = f"tables{SEP}{file}"
        try:
            con = get_db_connnection()
            cur = get_cursor(con)
            sql_stmt = """SET SESSION AUTHORIZATION dbo;"""
            status = execute_sql(cur, sql_stmt, 'auth dbo')
            status = execute_sql_from_file(cur, sql_file, f"create table in {sql_file}")
            con.close()
        except ResourceExists as dd_err:
            _LOG.warning(f"ResourceExists: {str(dd_err)}")
            status = log_status(f"table in {sql_file} already exists")
    return status

def get_files_in_dir(directory):
    """
    Returns a list of all the filenames in the given directory.

        Args:
            directory (string): the name of the directory containing the files

        Returns:
            list(string): list of the files in the given directory.
    """
    dir_files = []
    for (_, _, filenames) in walk(directory):
        for name in filenames:
            if name != 'init.sql':
                dir_files.append(name)
    dir_files.sort()
    return dir_files

def log_status(status):
    """
    Logs the status of the commands

        Args:
            status (string): the status to be logged

        Returns:
            string: the status, same as was input
    """
    _LOG.info(status)
    #print(status)
    return status

def get_db_connnection():
    """
    Gets a database connection.

        Returns:
            object: a connection to a database

        Raises:
            DatabaseError: An error occurred.
    """
    try:
        log_status(f"Connect to database started")
        dbconnect_info = {}
        dbconnect_info['db_host'] = os.environ['DATABASE_HOST']
        dbconnect_info['db_port'] = os.environ['DATABASE_PORT']
        dbconnect_info['db_name'] = os.environ['DATABASE_NAME']
        dbconnect_info['db_user'] = os.environ['DATABASE_USER']
        dbconnect_info['db_pw'] = os.environ['DATABASE_PW']

        con = database.return_connection(dbconnect_info)
        log_status(f'Connect to database completed')
    except DbError as err:
        _LOG.exception(f"DbError: {str(err)}")
        log_status('Connect to database DbError')
        raise DatabaseError(str(err))
    return con

def get_cursor(con):
    """
    Gets a cursor for the database connection.

        Args:
            con (object): a connection to a database

        Returns:
            object: a cursor for the given connection

        Raises:
            DatabaseError: An error occurred.
    """
    try:
        cursor = database.return_cursor(con)
    except DbError as err:
        _LOG.exception(f"DbError: {str(err)}")
        log_status('Get cursor DbError')
        raise DatabaseError(str(err))
    return cursor

def execute_sql(cur, sql_stmt, activity):
    """
    Executes the sqlstmt.

        Args:
            cur (object): a cursor to the database
            sql_stmt (string): the sql statment to execute
            activity (string): brief description of what the sql does

        Returns:
            string: description of status of the sql_stmt.

        Raises:
            DatabaseError: An error occurred.
    """
    try:
        status = log_status(f"{activity} started")
        database.query_no_params(cur, sql_stmt)
        status = log_status(f"{activity} completed")
    except DbError as err:
        _LOG.exception(f"DbError: {str(err)}")
        log_status(f"{activity} DbError")
        raise DatabaseError(str(err))
    return status

def execute_sql_from_file(cur, sql_file, activity):
    """
    Executes the sql in a file.

        Args:
            cur (object): a cursor to the database
            sql_file (string): the file containing a sql statment to execute
            activity (string): brief description of what the sql does

        Returns:
            string: description of status of the sql_stmt.

        Raises:
            DatabaseError: An error occurred.
    """
    ddl_dir = os.environ['DDL_DIR']
    try:
        status = log_status(f"{activity} started")
        sql_path = f"{ddl_dir}{sql_file}"
        database.query_from_file(cur, sql_path)
        status = log_status(f"{activity} completed")
    except FileNotFoundError as fnf:
        _LOG.exception(f"DbError: {str(fnf)}")
        log_status(f"{activity} DbError")
        raise DatabaseError(str(fnf))
    except DbError as err:
        _LOG.exception(f"DbError: {str(err)}")
        log_status(f"{activity} DbError")
        raise DatabaseError(str(err))
    return status


def handler(event, context):            #pylint: disable-msg=unused-argument
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
            event (dict): empty
                Example: event: {}
            context (Object): None

        Returns:
            string: status description.

        Raises:
            DatabaseError: An error occurred.
    """
    result = task(event, context)
    return result
