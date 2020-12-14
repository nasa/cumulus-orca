"""
Name: test_db_deploy.py

Description:  Unit tests for db_deploy.py.
"""
import os
import unittest
import uuid
from random import randint
from typing import Dict
from unittest import mock
from unittest.mock import Mock, call, patch, MagicMock

from database import ResourceExists, DbError
from psycopg2._psycopg import connection
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT, ISOLATION_LEVEL_READ_COMMITTED

import db_deploy


class TestDbDeploy(unittest.TestCase):
    """
    TestDbDeploy.
    """

    # <editor-fold desc="Large Tests">
    #    def setUp(self):
    #        private_config = f"{os.path.realpath(__file__)}".replace(os.path.basename(__file__),
    #                                                                 'private_config.json')
    #        db_config.set_env(private_config)
    #        os.environ["PLATFORM"] = "ONPREM"
    #        os.environ["DDL_DIR"] = "C:\\devpy\\poswotdr\\database\\ddl\\base\\"
    #        private_configs = None
    #        with open(private_config) as private_file:
    #            private_configs = json.load(private_file)
    #        os.environ["MASTER_USER_PW"] = private_configs["MASTER_USER_PW"]
    #
    #    def tearDown(self):
    #        del os.environ["DATABASE_HOST"]
    #        del os.environ["DATABASE_PORT"]
    #        del os.environ["DATABASE_NAME"]
    #        del os.environ["DATABASE_USER"]
    #        del os.environ["DATABASE_PW"]
    #        del os.environ["MASTER_USER_PW"]
    #        del os.environ["PLATFORM"]
    #
    #    @staticmethod
    #    def mock_ssm_get_parameter(n_times):
    #        """
    #        mocks the reads from the parameter store for the dbconnect values
    #        """
    #        params = []
    #        db_host = {"Parameter": {"Value": os.environ['DATABASE_HOST']}}
    #        db_pw = {"Parameter": {"Value": os.environ['DATABASE_PW']}}
    #        admin_pw = {"Parameter": {"Value": os.environ['MASTER_USER_PW']}}
    #        loop = 0
    #        while loop < n_times:
    #            params.append(db_pw)
    #            params.append(admin_pw)
    #            params.append(db_host)
    #            loop = loop + 1
    #        ssm_cli = boto3.client('ssm')
    #        ssm_cli.get_parameter = Mock(side_effect=params)
    #
    #    def test_handler_drop(self):
    #        """
    #        Test db_deploy handler creating database from scratch.
    #        """
    #        handler_input_event = {}
    #        boto3.client = Mock()
    #        self.mock_ssm_get_parameter(1)
    #        expected = "database ddl execution complete"
    #        os.environ["DROP_DATABASE"] = "True"
    #        try:
    #            result = db_deploy.handler(handler_input_event, None)
    #            self.assertEqual(expected, result)
    #        except DatabaseError as err:
    #            self.fail(str(err))
    #
    #    def test_task_no_drop(self):
    #        """
    #        Test db_deploy task when database exists
    #        """
    #        handler_input_event = {}
    #        boto3.client = Mock()
    #        self.mock_ssm_get_parameter(1)
    #        expected = "database ddl execution complete"
    #        os.environ["DROP_DATABASE"] = "False"
    #        del os.environ["DROP_DATABASE"]
    #        try:
    #            result = db_deploy.task(handler_input_event, None)
    #            self.assertEqual(expected, result)
    #        except DatabaseError as err:
    #            self.fail(str(err))
    #
    #    def test_task_no_drop_platform_aws(self):
    #        """
    #        Test db_deploy task local with platform=AWS
    #        """
    #        handler_input_event = {}
    #        boto3.client = Mock()
    #        self.mock_ssm_get_parameter(1)
    #        expected = "Database Error. permission denied for database disaster_recovery\n"
    #        os.environ["PLATFORM"] = "AWS"
    #        try:
    #            db_deploy.task(handler_input_event, None)
    #            self.fail("expected DatabaseError")
    #        except DatabaseError as err:
    #            self.assertEqual(expected, str(err))
    #
    #    def test_execute_sql_from_file_exception(self):
    #        """
    #        tests an error reading sql from a file.
    #        """
    #        con = db_deploy.get_db_connnection()
    #        cur = db_deploy.get_cursor(con)
    #        sql_file = "my_nonexistent.sql"
    #        activity = "test file not exists"
    #
    #        exp_err = "[Errno 2] No such file or directory"
    #        try:
    #            db_deploy.execute_sql_from_file(cur, sql_file, activity)
    #            self.fail("expected DbError")
    #        except DatabaseError as err:
    #            self.assertIn(exp_err, str(err))
    #
    #    def test_execute_sql_exception(self):
    #        """
    #        tests an error querying non-existant table.
    #        """
    #        con = db_deploy.get_db_connnection()
    #        cur = db_deploy.get_cursor(con)
    #        activity = "test table no exist"
    #        sql_stmt = """SELECT * from table_no_exist;"""
    #        exp_err = 'Database Error. relation "table_no_exist" does not exist'
    #        try:
    #            db_deploy.execute_sql(cur, sql_stmt, activity)
    #            self.fail("expected DbError")
    #        except DatabaseError as err:
    #            self.assertIn(exp_err, str(err))
    #            cur.close()
    #            con.close()
    #
    #    def test_get_cursor_exception(self):
    #        """
    #        tests an error opening cursor.
    #        """
    #        exp_err = "Database Error. 'NoneType' object has no attribute 'cursor'"
    #        con = None
    #        try:
    #            db_deploy.get_cursor(con)
    #            self.fail("expected DbError")
    #        except DatabaseError as err:
    #            self.assertEqual(exp_err, str(err))
    #
    #    def test_get_db_connnection_exception(self):
    #        """
    #        tests an error connecting to database.
    #        """
    #        exp_err = 'Database Error. FATAL:  database "dbnoexist" does not exist\n'
    #        os.environ["DATABASE_NAME"] = "dbnoexist"
    #        try:
    #            db_deploy.get_db_connnection()
    #            self.fail("expected DbError")
    #        except DatabaseError as err:
    #            self.assertEqual(exp_err, str(err))
    #
    #    def test_get_files_in_dir(self):
    #        """
    #        tests an error getting file list.
    #        """
    #        exp_dir = "really*bad$path%name"
    #        exp_files = []
    #        file_list = db_deploy.get_files_in_dir(exp_dir)
    #        self.assertEqual(exp_files, file_list)
    # </editor-fold>

    @patch('database.return_cursor')
    @patch('database.return_connection')
    @patch('database.query_from_file')
    @patch('database.query_no_params')
    @patch('db_deploy.walk_wrapper')
    @patch('boto3.client')
    def test_regression_test(self,
                             mock_boto3_client: MagicMock,
                             mock_walk_wrapper: MagicMock,
                             mock_query_no_params: MagicMock,
                             mock_query_from_file: MagicMock,
                             mock_return_connection: MagicMock,
                             mock_return_cursor: MagicMock):
        """
        A deliberately brittle test as a stopgap against accidental parameter/function call changes.
        """
        db_user_pass = uuid.uuid4().__str__()
        db_admin_pass = uuid.uuid4().__str__()
        db_host = uuid.uuid4().__str__()
        db_name = uuid.uuid4().__str__()
        db_user = uuid.uuid4().__str__()
        db_port = randint(0, 99999).__str__()
        ddl_dir = uuid.uuid4().__str__()
        script_filename_1 = uuid.uuid4().__str__()
        script_filename_2 = uuid.uuid4().__str__()
        drop_database = 'True'

        ssm_vars = {
            'drdb-user-pass': (db_user_pass, True),
            'drdb-admin-pass': (db_admin_pass, True),
            'drdb-host': (db_host, False)
        }

        mock_ssm = mock_boto3_client('ssm')

        # noinspection PyPep8Naming

        def ssm_return_function(Name, WithDecryption):
            item = ssm_vars[Name]
            if item[1] != WithDecryption:
                raise KeyError
            return {'Parameter': {'Value': item[0]}}

        mock_ssm.get_parameter = ssm_return_function

        os.environ['DATABASE_NAME'] = db_name
        os.environ['DATABASE_USER'] = db_user
        os.environ['DATABASE_PORT'] = db_port
        os.environ['DROP_DATABASE'] = drop_database
        os.environ['DDL_DIR'] = ddl_dir + db_deploy.SEP
        os.environ['PLATFORM'] = 'AWS'

        postgres_con = Mock()
        another_postgres_con = Mock()

        def return_connection_function(connection_info: Dict):
            if connection_info == {"db_host": db_host,
                                   "db_port": db_port,
                                   "db_name": 'postgres',
                                   "db_user": 'postgres',
                                   "db_pw": db_admin_pass}:
                return postgres_con
            if connection_info == {"db_host": db_host,
                                   "db_port": db_port,
                                   "db_name": db_name,
                                   "db_user": 'postgres',
                                   "db_pw": db_admin_pass}:
                return another_postgres_con

        mock_return_connection.side_effect = return_connection_function
        postgres_con_cursor = Mock()
        another_postgres_con_cursor = Mock()

        # noinspection PyPep8Naming
        def return_cursor_return_function(conn: connection):
            if conn is postgres_con:
                return postgres_con_cursor
            if conn is another_postgres_con:
                return another_postgres_con_cursor

        mock_return_cursor.side_effect = return_cursor_return_function

        walk_return_value = [(None, None, [script_filename_1, script_filename_2, 'init.sql'])]

        mock_walk_wrapper.return_value = walk_return_value

        db_deploy.task()

        mock_walk_wrapper.assert_called_once_with(f"{ddl_dir}{db_deploy.SEP}tables")
        mock_query_from_file.assert_has_calls([
            call(postgres_con_cursor, f"{ddl_dir}{db_deploy.SEP}database{db_deploy.SEP}database_drop.sql"),
            call(postgres_con_cursor,
                 f"{ddl_dir}{db_deploy.SEP}database{db_deploy.SEP}database_create.sql"),
            call(postgres_con_cursor,
                 f"{ddl_dir}{db_deploy.SEP}database{db_deploy.SEP}database_comment.sql"),
            call(postgres_con_cursor, f"{ddl_dir}{db_deploy.SEP}roles{db_deploy.SEP}app_role.sql"),
            call(postgres_con_cursor, f"{ddl_dir}{db_deploy.SEP}roles{db_deploy.SEP}appdbo_role.sql"),
            call(postgres_con_cursor, f"{ddl_dir}{db_deploy.SEP}users{db_deploy.SEP}dbo.sql"),
            call(postgres_con_cursor, f"{ddl_dir}{db_deploy.SEP}users{db_deploy.SEP}appuser.sql"),
            call(another_postgres_con_cursor, f"{ddl_dir}{db_deploy.SEP}schema{db_deploy.SEP}app.sql")
        ], any_order=False)
        mock_query_from_file.assert_has_calls([
            call(another_postgres_con_cursor,
                 f"{ddl_dir}{db_deploy.SEP}tables{db_deploy.SEP}{script_filename_1}"),
            call(another_postgres_con_cursor,
                 f"{ddl_dir}{db_deploy.SEP}tables{db_deploy.SEP}{script_filename_2}")
        ], any_order=True)
        self.assertEqual(10, mock_query_from_file.call_count)
        mock_query_no_params.assert_has_calls([
            call(postgres_con_cursor, f"ALTER USER {db_user} WITH PASSWORD '{db_user_pass}';"),
            call(postgres_con_cursor, f"ALTER USER dbo WITH PASSWORD '{db_user_pass}';"),
            call(another_postgres_con_cursor, """SET SESSION AUTHORIZATION dbo;"""),
            call(another_postgres_con_cursor, """SET SESSION AUTHORIZATION dbo;""")
        ], any_order=False)
        self.assertEqual(4, mock_query_no_params.call_count)

    @patch('boto3.client')
    @patch('db_deploy.inner_task')
    def test_task_pulls_correct_environment_variables(self,
                                                      inner_task_mock,
                                                      boto3_client_mock):
        """
        Verifies that environment variables are passed to inner_task correctly.
        """
        db_user_pass = uuid.uuid4().__str__()
        db_admin_pass = uuid.uuid4().__str__()
        db_host = uuid.uuid4().__str__()
        db_name = uuid.uuid4().__str__()
        db_user = uuid.uuid4().__str__()
        db_port = randint(0, 99999).__str__()
        drop_database = 'True'

        ssm_vars = {
            'drdb-user-pass': (db_user_pass, True),
            'drdb-admin-pass': (db_admin_pass, True),
            'drdb-host': (db_host, False)
        }

        ssm_mock = boto3_client_mock('ssm')

        # noinspection PyPep8Naming
        def ssm_return_function(Name, WithDecryption):
            item = ssm_vars[Name]
            if item[1] != WithDecryption:
                raise KeyError
            return {'Parameter': {'Value': item[0]}}

        ssm_mock.get_parameter.side_effect = ssm_return_function

        os.environ[db_deploy.OS_ENVIRON_DATABASE_NAME_KEY] = db_name
        os.environ[db_deploy.OS_ENVIRON_DATABASE_USER_KEY] = db_user
        os.environ[db_deploy.OS_ENVIRON_DATABASE_PORT_KEY] = db_port
        os.environ[db_deploy.OS_ENVIRON_DROP_DATABASE_KEY] = drop_database

        db_deploy.task()

        inner_task_mock.assert_called_once_with(db_host, db_name, db_port, db_user, db_user_pass, db_admin_pass,
                                                True)

    @patch('db_deploy.get_db_connection')
    @patch('db_deploy.create_database')
    @patch('db_deploy.create_roles_and_users')
    @patch('db_deploy.create_schema')
    @patch('db_deploy.create_tables')
    def test_inner_task_minimal_path(self,
                                     mock_create_tables,
                                     mock_create_schema,
                                     mock_create_roles_and_users,
                                     mock_create_database,
                                     mock_get_db_connection):
        """
        A basic test of the function that orchestrates db deployment.
        No additional need to create roles and users.
        """
        db_user_pass = uuid.uuid4().__str__()
        db_admin_pass = uuid.uuid4().__str__()
        db_host = uuid.uuid4().__str__()
        db_name = uuid.uuid4().__str__()
        db_user = uuid.uuid4().__str__()
        db_port = randint(0, 99999).__str__()
        drop_database = True

        creation_connection = Mock()
        creation_connection.close = Mock()
        updating_connection = Mock()
        updating_connection.close = Mock()

        mock_db_connections = {
            (db_host, 'postgres', db_port, 'postgres', db_admin_pass): creation_connection,
            (db_host, db_name, db_port, 'postgres', db_admin_pass): updating_connection
        }

        mock_get_db_connection_unmocked_call = None

        def mock_get_db_connection_func(inner_db_host: str, inner_db_name: str, inner_db_port: str, inner_db_user: str,
                                        inner_db_password: str):
            key = (inner_db_host, inner_db_name, inner_db_port, inner_db_user, inner_db_password)
            if key in mock_db_connections.keys():
                return mock_db_connections[key]
            else:
                nonlocal mock_get_db_connection_unmocked_call
                mock_get_db_connection_unmocked_call = key
                return None

        db_deploy.get_db_connection = mock_get_db_connection_func

        db_created = False
        mock_create_database_unmocked_call = None

        def mock_create_database_func(inner_connection: connection, inner_drop_database: bool):
            if inner_connection == creation_connection and inner_drop_database == drop_database:
                nonlocal db_created
                db_created = True
                return True
            else:
                nonlocal mock_create_database_unmocked_call
                mock_create_database_unmocked_call = (inner_connection, inner_drop_database)

        db_deploy.create_database = mock_create_database_func

        db_deploy.inner_task(
            db_host, db_name, db_port, db_user, db_user_pass, db_admin_pass, drop_database)
        self.assertTrue(db_created)
        mock_create_roles_and_users.assert_not_called()
        creation_connection.close.assert_called_once()
        mock_create_schema.assert_called_once_with(updating_connection)
        updating_connection.close.assert_called_once()
        mock_create_tables.assert_called_once_with(
            db_host, db_name, db_port, 'postgres', db_admin_pass)
        self.assertIsNone(mock_get_db_connection_unmocked_call)
        self.assertIsNone(mock_create_database_unmocked_call)
        self.assertTrue(db_created)

    @patch('db_deploy.get_db_connection')
    @patch('db_deploy.create_roles_and_users')
    @patch('db_deploy.create_schema')
    @patch('db_deploy.create_tables')
    @patch('db_deploy.create_database')
    def test_inner_task_db_did_not_exist(self,
                                         mock_create_database: MagicMock,
                                         mock_create_tables: MagicMock,
                                         mock_create_schema: MagicMock,
                                         mock_create_roles_and_users: MagicMock,
                                         mock_get_db_connection: MagicMock):
        """
        create_database returns that the db did not exist, requiring a call to create_roles_and_users
        """
        db_user_pass = uuid.uuid4().__str__()
        db_admin_pass = uuid.uuid4().__str__()
        db_host = uuid.uuid4().__str__()
        db_name = uuid.uuid4().__str__()
        db_user = uuid.uuid4().__str__()
        db_port = randint(0, 99999).__str__()
        drop_database = True

        creation_connection = Mock()
        creation_connection.close = Mock()
        updating_connection = Mock()
        updating_connection.close = Mock()

        mock_db_connections = {
            (db_host, 'postgres', db_port, 'postgres', db_admin_pass): creation_connection,
            (db_host, db_name, db_port, 'postgres', db_admin_pass): updating_connection
        }

        mock_get_db_connection_unmocked_call = None

        def mock_get_db_connection_return(inner_db_host: str, inner_db_name: str, inner_db_port: str,
                                          inner_db_user: str,
                                          inner_db_password: str):
            key = (inner_db_host, inner_db_name, inner_db_port, inner_db_user, inner_db_password)
            if key in mock_db_connections.keys():
                return mock_db_connections[key]
            else:
                nonlocal mock_get_db_connection_unmocked_call
                mock_get_db_connection_unmocked_call = key
                return None

        mock_get_db_connection.side_effect = mock_get_db_connection_return

        db_created = False
        mock_create_database_unmocked_call = None

        def mock_create_database_return(inner_connection: connection, inner_drop_database: bool):
            if inner_connection == creation_connection and inner_drop_database == drop_database:
                nonlocal db_created
                db_created = True
                return False
            else:
                nonlocal mock_create_database_unmocked_call
                mock_create_database_unmocked_call = (inner_connection, inner_drop_database)

        mock_create_database.side_effect = mock_create_database_return

        db_deploy.inner_task(db_host, db_name, db_port, db_user, db_user_pass, db_admin_pass, drop_database)
        self.assertTrue(db_created)
        mock_create_roles_and_users.assert_called_once_with(creation_connection, db_user, db_user_pass)
        creation_connection.close.assert_called_once()
        mock_create_schema.assert_called_once_with(updating_connection)
        updating_connection.close.assert_called_once()
        mock_create_tables.assert_called_once_with(db_host, db_name, db_port, 'postgres', db_admin_pass)
        self.assertIsNone(mock_get_db_connection_unmocked_call)
        self.assertIsNone(mock_create_database_unmocked_call)
        self.assertTrue(db_created)

    @patch('db_deploy.execute_sql_from_file')
    @patch('db_deploy.get_cursor')
    def test_create_database_minimal_path(self,
                                          mock_get_cursor: MagicMock,
                                          mock_execute_sql_from_file: MagicMock):
        mock_con = Mock()
        mock_cursor = Mock()
        mock_get_cursor.return_value = mock_cursor

        db_existed_result = db_deploy.create_database(mock_con, False)

        mock_get_cursor.assert_called_once_with(mock_con)
        mock_con.set_isolation_level.assert_called_once_with(ISOLATION_LEVEL_AUTOCOMMIT)
        mock_execute_sql_from_file.assert_has_calls([
            call(mock_cursor, f"database{db_deploy.SEP}database_create.sql", mock.ANY),
            call(mock_cursor, f"database{db_deploy.SEP}database_comment.sql", mock.ANY)
        ])
        self.assertEqual(2, mock_execute_sql_from_file.call_count)
        mock_cursor.close.assert_called_once()
        self.assertFalse(db_existed_result)

    @patch('db_deploy.execute_sql_from_file')
    @patch('db_deploy.get_cursor')
    def test_create_database_drop_database(self,
                                           mock_get_cursor: MagicMock,
                                           mock_execute_sql_from_file: MagicMock):
        """
        Same as minimal path, but with the extra drop_database=True
        """
        mock_con = Mock()
        mock_cursor = Mock()
        mock_get_cursor.return_value = mock_cursor

        db_existed_result = db_deploy.create_database(mock_con, True)

        mock_get_cursor.assert_called_once_with(mock_con)
        mock_con.set_isolation_level.assert_called_once_with(ISOLATION_LEVEL_AUTOCOMMIT)
        mock_execute_sql_from_file.assert_has_calls([
            call(mock_cursor, f"database{db_deploy.SEP}database_drop.sql", mock.ANY),
            call(mock_cursor, f"database{db_deploy.SEP}database_create.sql", mock.ANY),
            call(mock_cursor, f"database{db_deploy.SEP}database_comment.sql", mock.ANY)
        ])
        self.assertEqual(3, mock_execute_sql_from_file.call_count)
        mock_cursor.close.assert_called_once()
        self.assertFalse(db_existed_result)

    @patch('db_deploy.execute_sql_from_file')
    @patch('db_deploy.get_cursor')
    def test_create_database_database_exists(self,
                                             mock_get_cursor: MagicMock,
                                             mock_execute_sql_from_file: MagicMock):
        """
        Same as minimal path, but sql command raises ResourceExists
        """
        mock_con = Mock()
        mock_cursor = Mock()
        mock_get_cursor.return_value = mock_cursor
        mock_execute_sql_from_file.side_effect = ResourceExists(Exception())

        db_existed_result = db_deploy.create_database(mock_con, False)

        mock_get_cursor.assert_called_once_with(mock_con)
        mock_con.set_isolation_level.assert_called_once_with(ISOLATION_LEVEL_AUTOCOMMIT)
        mock_execute_sql_from_file.assert_called_once_with(
            mock_cursor, f"database{db_deploy.SEP}database_create.sql", mock.ANY
        )
        mock_cursor.close.assert_called_once()
        self.assertTrue(db_existed_result)

    @patch('db_deploy.execute_sql')
    @patch('db_deploy.execute_sql_from_file')
    @patch('db_deploy.get_cursor')
    def test_create_roles_and_users_minimal_path(self,
                                                 mock_get_cursor: MagicMock,
                                                 mock_execute_sql_from_file: MagicMock,
                                                 mock_execute_sql: MagicMock):
        db_user = uuid.uuid4().__str__()
        db_password = uuid.uuid4().__str__()

        mock_con = Mock()
        mock_cursor = Mock()
        mock_get_cursor.return_value = mock_cursor

        db_deploy.create_roles_and_users(mock_con, db_user, db_password)

        mock_get_cursor.assert_called_once_with(mock_con)
        mock_con.set_isolation_level.assert_called_once_with(ISOLATION_LEVEL_READ_COMMITTED)
        mock_execute_sql_from_file.assert_has_calls([
            call(mock_cursor, f"roles{db_deploy.SEP}app_role.sql", mock.ANY),
            call(mock_cursor, f"roles{db_deploy.SEP}appdbo_role.sql", mock.ANY),
            call(mock_cursor, f"users{db_deploy.SEP}dbo.sql", mock.ANY),
            call(mock_cursor, f"users{db_deploy.SEP}appuser.sql", mock.ANY)
        ])
        self.assertEqual(4, mock_execute_sql_from_file.call_count)
        mock_execute_sql.assert_has_calls([
            call(mock_cursor, f"ALTER USER {db_user} WITH PASSWORD '{db_password}';", mock.ANY),
            call(mock_cursor, f"ALTER USER dbo WITH PASSWORD '{db_password}';", mock.ANY),
        ])
        self.assertEqual(2, mock_execute_sql.call_count)
        mock_con.commit.assert_called_once()
        mock_cursor.close.assert_called_once()

    @patch('db_deploy.execute_sql')
    @patch('db_deploy.execute_sql_from_file')
    @patch('db_deploy.get_cursor')
    def test_create_schema_minimal_path(self,
                                        mock_get_cursor: MagicMock,
                                        mock_execute_sql_from_file: MagicMock,
                                        mock_execute_sql: MagicMock):
        mock_con = Mock()
        mock_cursor = Mock()
        mock_get_cursor.return_value = mock_cursor
        os.environ[db_deploy.OS_ENVIRON_PLATFORM_KEY] = 'NOT AWS'

        db_deploy.create_schema(mock_con)

        mock_get_cursor.assert_called_once_with(mock_con)
        mock_execute_sql.assert_not_called()
        mock_execute_sql_from_file.assert_called_once_with(
            mock_cursor, f"schema{db_deploy.SEP}app.sql", mock.ANY)
        mock_con.commit.assert_called_once()
        mock_cursor.close.assert_called_once()

    @patch('db_deploy.execute_sql')
    @patch('db_deploy.execute_sql_from_file')
    @patch('db_deploy.get_cursor')
    def test_create_schema_aws_auth(self,
                                    mock_get_cursor: MagicMock,
                                    mock_execute_sql_from_file: MagicMock,
                                    mock_execute_sql: MagicMock):
        """
        Same as minimal path, but AWS requires extra session auth.
        """
        mock_con = Mock()
        mock_cursor = Mock()
        mock_get_cursor.return_value = mock_cursor
        os.environ[db_deploy.OS_ENVIRON_PLATFORM_KEY] = 'AWS'

        db_deploy.create_schema(mock_con)

        mock_get_cursor.assert_called_once_with(mock_con)
        mock_execute_sql.assert_called_once_with(mock_cursor, """SET SESSION AUTHORIZATION dbo;""", mock.ANY)
        mock_execute_sql_from_file.assert_called_once_with(
            mock_cursor, f"schema{db_deploy.SEP}app.sql", mock.ANY)
        mock_con.commit.assert_called_once()
        mock_cursor.close.assert_called_once()

    @patch('db_deploy.execute_sql')
    @patch('db_deploy.execute_sql_from_file')
    @patch('db_deploy.get_cursor')
    @patch('db_deploy.get_db_connection')
    @patch('db_deploy.get_file_names_in_dir')
    def test_create_tables_failed_script_does_not_halt(self,
                                                       mock_get_file_names_in_dir: MagicMock,
                                                       mock_get_db_connection: MagicMock,
                                                       mock_get_cursor: MagicMock,
                                                       mock_execute_sql_from_file: MagicMock,
                                                       mock_execute_sql: MagicMock):
        """
        If one script fails, keep going.
        """
        db_host = uuid.uuid4().__str__()
        db_name = uuid.uuid4().__str__()
        db_port = randint(0, 99999).__str__()
        db_user = uuid.uuid4().__str__()
        db_password = uuid.uuid4().__str__()
        ddl_dir = uuid.uuid4().__str__()
        filename1 = uuid.uuid4().__str__()
        filename2 = uuid.uuid4().__str__()
        os.environ[db_deploy.OS_ENVIRON_DDL_DIR_KEY] = ddl_dir + db_deploy.SEP

        mock_get_file_names_in_dir.return_value = [filename1, filename2]
        mock_con = Mock()
        mock_get_db_connection.return_value = mock_con
        mock_cursor = Mock()
        mock_get_cursor.return_value = mock_cursor
        os.environ[db_deploy.OS_ENVIRON_PLATFORM_KEY] = 'AWS'
        mock_execute_sql_from_file.side_effect = [ResourceExists(Exception()), None]  # ResourceExists should NOT halt.

        db_deploy.create_tables(db_host, db_name, db_port, db_user, db_password)

        mock_get_cursor.assert_called_once_with(mock_con)
        mock_execute_sql.assert_called_once_with(mock_cursor, """SET SESSION AUTHORIZATION dbo;""", mock.ANY)
        mock_execute_sql_from_file.assert_has_calls([
            call(mock_cursor, f"tables{db_deploy.SEP}{filename1}", mock.ANY),
            call(mock_cursor, f"tables{db_deploy.SEP}{filename2}", mock.ANY)
        ])
        self.assertEqual(2, mock_execute_sql_from_file.call_count)

        mock_cursor.close.assert_called_once()
        mock_con.close.assert_called_once()

    @patch('db_deploy.walk_wrapper')
    def test_get_file_names_in_dir_filters_out_init(self,
                                                    mock_walk_wrapper: MagicMock):
        """
        Should not return init.sql.
        """
        directory = uuid.uuid4().__str__()
        filename_1 = uuid.uuid4().__str__()
        filename_2 = uuid.uuid4().__str__()

        mock_walk_wrapper.return_value = [(None, None, [filename_1, 'init.sql', filename_2])]

        result = db_deploy.get_file_names_in_dir(directory)

        self.assertEqual({filename_1, filename_2}, set(result))
        mock_walk_wrapper.assert_called_once_with(directory)

    @patch('database.return_connection')
    def test_get_db_connection_minimal_path(self,
                                            mock_return_connection: MagicMock):
        db_host = uuid.uuid4().__str__()
        db_name = uuid.uuid4().__str__()
        db_port = randint(0, 99999).__str__()
        db_user = uuid.uuid4().__str__()
        db_password = uuid.uuid4().__str__()

        mock_con = Mock()
        mock_return_connection.return_value = mock_con

        result = db_deploy.get_db_connection(db_host, db_name, db_port, db_user, db_password)

        self.assertIs(mock_con, result)
        mock_return_connection.assert_called_once_with(
            {"db_host": db_host,
             "db_port": db_port,
             "db_name": db_name,
             "db_user": db_user,
             "db_pw": db_password}
        )

    @patch('database.return_connection')
    def test_get_db_connection_DbError_raises_DatabaseError(self,
                                                            mock_return_connection: MagicMock):
        db_host = uuid.uuid4().__str__()
        db_name = uuid.uuid4().__str__()
        db_port = randint(0, 99999).__str__()
        db_user = uuid.uuid4().__str__()
        db_password = uuid.uuid4().__str__()

        mock_return_connection.side_effect = DbError()

        try:
            db_deploy.get_db_connection(db_host, db_name, db_port, db_user, db_password)
        except db_deploy.DatabaseError:
            mock_return_connection.assert_called_once_with(
                {"db_host": db_host,
                 "db_port": db_port,
                 "db_name": db_name,
                 "db_user": db_user,
                 "db_pw": db_password}
            )
            return
        self.fail('Error not raised.')

    @patch('database.return_cursor')
    def test_get_cursor_minimal_path(self,
                                     mock_return_cursor: MagicMock):
        mock_con = Mock()
        mock_cursor = Mock()
        mock_return_cursor.return_value = mock_cursor

        result = db_deploy.get_cursor(mock_con)

        self.assertIs(mock_cursor, result)
        mock_return_cursor.assert_called_once_with(mock_con)

    @patch('database.return_cursor')
    def test_get_cursor_DbError_raises_DatabaseError(self,
                                                     mock_return_cursor: MagicMock):
        mock_con = Mock()
        mock_return_cursor.side_effect = DbError()

        try:
            db_deploy.get_cursor(mock_con)
        except db_deploy.DatabaseError:
            mock_return_cursor.assert_called_once_with(mock_con)
            return
        self.fail('Error not raised.')

    @patch('database.query_no_params')
    def test_execute_sql_minimal_path(self,
                                      mock_query_no_params: MagicMock):
        sql_stmt = uuid.uuid4().__str__()
        mock_cursor = Mock()

        db_deploy.execute_sql(mock_cursor, sql_stmt, uuid.uuid4().__str__())

        mock_query_no_params.assert_called_once_with(mock_cursor, sql_stmt)

    @patch('database.query_no_params')
    def test_execute_sql_DbError_raises_DatabaseError(self,
                                                      mock_query_no_params: MagicMock):
        sql_stmt = uuid.uuid4().__str__()
        mock_cursor = Mock()
        mock_query_no_params.side_effect = DbError()

        try:
            db_deploy.execute_sql(mock_cursor, sql_stmt, uuid.uuid4().__str__())
        except db_deploy.DatabaseError:
            return
        self.fail('Error not raised.')

    @patch('database.query_from_file')
    def test_execute_sql_from_file_minimal_path(self,
                                                mock_query_from_file: MagicMock):
        sql_file_name = uuid.uuid4().__str__()
        ddl_dir = uuid.uuid4().__str__()
        os.environ[db_deploy.OS_ENVIRON_DDL_DIR_KEY] = ddl_dir + db_deploy.SEP
        mock_cursor = Mock()

        db_deploy.execute_sql_from_file(mock_cursor, sql_file_name, uuid.uuid4().__str__())

        mock_query_from_file.assert_called_once_with(mock_cursor, f"{ddl_dir}{db_deploy.SEP}{sql_file_name}")

    @patch('database.query_from_file')
    def test_execute_sql_from_file_FileNotFound_raises_DatabaseError(self,
                                                                     mock_query_from_file: MagicMock):
        sql_file_name = uuid.uuid4().__str__()
        ddl_dir = uuid.uuid4().__str__()
        os.environ[db_deploy.OS_ENVIRON_DDL_DIR_KEY] = ddl_dir + db_deploy.SEP
        mock_cursor = Mock()
        mock_query_from_file.side_effect = FileNotFoundError()

        try:
            db_deploy.execute_sql_from_file(mock_cursor, sql_file_name, uuid.uuid4().__str__())
        except db_deploy.DatabaseError:
            return
        self.fail('Error not raised.')

    @patch('database.query_from_file')
    def test_execute_sql_from_file_DbError_raises_DatabaseError(self,
                                                                mock_query_from_file: MagicMock):
        sql_file_name = uuid.uuid4().__str__()
        ddl_dir = uuid.uuid4().__str__()
        os.environ[db_deploy.OS_ENVIRON_DDL_DIR_KEY] = ddl_dir + db_deploy.SEP
        mock_cursor = Mock()
        mock_query_from_file.side_effect = DbError(Exception())

        try:
            db_deploy.execute_sql_from_file(mock_cursor, sql_file_name, uuid.uuid4().__str__())
        except db_deploy.DatabaseError:
            return
        self.fail('Error not raised.')

    @patch('db_deploy.task')
    def test_handler_calls_task(self,
                                mock_task: MagicMock):
        db_deploy.handler(None, None)

        mock_task.assert_called_once()


if __name__ == '__main__':
    unittest.main()
