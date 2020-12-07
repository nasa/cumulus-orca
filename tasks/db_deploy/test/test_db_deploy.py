"""
Name: test_db_deploy.py

Description:  Unit tests for db_deploy.py.
"""
import os
import unittest
import uuid
from unittest.mock import Mock, call
import json
import boto3
import database
import db_config
from psycopg2._psycopg import connection

import db_deploy
from db_deploy import DatabaseError


class TestDbDeploy(unittest.TestCase):
    """
    TestDbDeploy.
    """

    # todo: reinstate commented out tests as large tests
    # todo: Due to the cumbersomeness of mocking order checks, unit tests just make sure functions are hit.
    # todo: Thus, large tests should do checks such as "database does not exist at start" to verify order.

    #    def setUp(self):
    #        private_config = f"{os.path.realpath(__file__)}".replace(os.path.basename(__file__),
    #                                                                 'private_config.json')
    #        db_config.set_env(private_config)
    #        os.environ["PLATFORM"] = "ONPREM"
    #        os.environ["DDL_DIR"] = "C:\\devpy\\poswotdr\\database\\ddl\\base\\"
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
    #        boto3.client = Mock()
    #        self.mock_ssm_get_parameter(1)
    #        expected = "database ddl execution complete"
    #        os.environ["DROP_DATABASE"] = "False"
    #        del os.environ["DROP_DATABASE"]
    #        try:
    #            result = db_deploy.task()
    #            self.assertEqual(expected, result)
    #        except DatabaseError as err:
    #            self.fail(str(err))
    #
    #    def test_task_no_drop_platform_aws(self):
    #        """
    #        Test db_deploy task local with platform=AWS
    #        """
    #        boto3.client = Mock()
    #        self.mock_ssm_get_parameter(1)
    #        expected = "Database Error. permission denied for database disaster_recovery\n"
    #        os.environ["PLATFORM"] = "AWS"
    #        try:
    #            db_deploy.task()
    #            self.fail("expected DatabaseError")
    #        except DatabaseError as err:
    #            self.assertEqual(expected, str(err))
    #
    #    def test_execute_sql_from_file_exception(self):
    #        """
    #        tests an error reading sql from a file.
    #        """
    #        con = db_deploy.get_db_connection()
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
    #        con = db_deploy.get_db_connection()
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
    #    def test_get_db_connection_exception(self):
    #        """
    #        tests an error connecting to database.
    #        """
    #        exp_err = 'Database Error. FATAL:  database "dbnoexist" does not exist\n'
    #        os.environ["DATABASE_NAME"] = "dbnoexist"
    #        try:
    #            db_deploy.get_db_connection()
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
    #        file_list = db_deploy.get_file_names_in_dir(exp_dir)
    #        self.assertEqual(exp_files, file_list)

    def test_task_pulls_correct_environment_variables(self):
        """
        Verifies that environment variables are passed to inner_task correctly.
        """
        db_user_pass = uuid.uuid4().__str__()
        db_admin_pass = uuid.uuid4().__str__()
        db_host = uuid.uuid4().__str__()
        db_name = uuid.uuid4().__str__()
        db_user = uuid.uuid4().__str__()
        db_port = uuid.uuid4().__str__()
        drop_database = 'True'

        ssm_vars = {
            'drdb-user-pass': (db_user_pass, True),
            'drdb-admin-pass': (db_admin_pass, True),
            'drdb-host': (db_host, False)
        }

        boto3.client = Mock()
        ssm = boto3.client('ssm')

        # noinspection PyPep8Naming
        def ssm_return_function(Name, WithDecryption):
            item = ssm_vars[Name]
            if item[1] != WithDecryption:
                raise KeyError
            return {'Parameter': {'Value': item[0]}}

        # parameter = ssm.get_parameter(Name='drdb-user-pass', WithDecryption=True)
        ssm.get_parameter = ssm_return_function

        os.environ[db_deploy.OS_ENVIRON_DATABASE_NAME_KEY] = db_name
        os.environ[db_deploy.OS_ENVIRON_DATABASE_USER_KEY] = db_user
        os.environ[db_deploy.OS_ENVIRON_DATABASE_PORT_KEY] = db_port
        os.environ[db_deploy.OS_ENVIRON_DROP_DATABASE_KEY] = drop_database

        db_deploy.inner_task = Mock(side_effect=None)

        db_deploy.task()

        db_deploy.inner_task.assert_called_once_with(db_host, db_name, db_port, db_user, db_user_pass, db_admin_pass,
                                                     True)

    def test_inner_task_minimal_path(self):
        """
        A basic test of the function that orchestrates db deployment.
        No additional need to create roles and users.
        """
        db_user_pass = uuid.uuid4().__str__()
        db_admin_pass = uuid.uuid4().__str__()
        db_host = uuid.uuid4().__str__()
        db_name = uuid.uuid4().__str__()
        db_user = uuid.uuid4().__str__()
        db_port = uuid.uuid4().__str__()
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

        def mock_get_db_connection(inner_db_host: str, inner_db_name: str, inner_db_port: str, inner_db_user: str,
                                   inner_db_password: str):
            key = (inner_db_host, inner_db_name, inner_db_port, inner_db_user, inner_db_password)
            if key in mock_db_connections.keys():
                return mock_db_connections[key]
            else:
                nonlocal mock_get_db_connection_unmocked_call
                mock_get_db_connection_unmocked_call = key
                return None

        db_deploy.get_db_connection = mock_get_db_connection

        db_created = False
        mock_create_database_unmocked_call = None

        def mock_create_database(inner_connection: connection, inner_drop_database: bool):
            if inner_connection == creation_connection and inner_drop_database == drop_database:
                nonlocal db_created
                db_created = True
                return True, ''
            else:
                nonlocal mock_create_database_unmocked_call
                mock_create_database_unmocked_call = (inner_connection, inner_drop_database)

        db_deploy.create_database = mock_create_database

        db_deploy.create_roles_and_users = Mock()
        db_deploy.create_schema = Mock()
        db_deploy.create_tables = Mock()

        db_deploy.inner_task(db_host, db_name, db_port, db_user, db_user_pass, db_admin_pass, drop_database)
        self.assertTrue(db_created)
        db_deploy.create_roles_and_users.assert_not_called()
        creation_connection.close.assert_called_once()
        db_deploy.create_schema.assert_called_once_with(updating_connection)
        updating_connection.close.assert_called_once()
        db_deploy.create_tables.assert_called_once_with(db_host, db_name, db_port, 'postgres', db_admin_pass)
        self.assertIsNone(mock_get_db_connection_unmocked_call)
        self.assertIsNone(mock_create_database_unmocked_call)
        self.assertTrue(db_created)

    def test_inner_task_db_did_not_exist(self):
        """
        create_database returns that the db did not exist, requiring a call to create_roles_and_users
        """
        db_user_pass = uuid.uuid4().__str__()
        db_admin_pass = uuid.uuid4().__str__()
        db_host = uuid.uuid4().__str__()
        db_name = uuid.uuid4().__str__()
        db_user = uuid.uuid4().__str__()
        db_port = uuid.uuid4().__str__()
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

        def mock_get_db_connection(inner_db_host: str, inner_db_name: str, inner_db_port: str, inner_db_user: str,
                                   inner_db_password: str):
            key = (inner_db_host, inner_db_name, inner_db_port, inner_db_user, inner_db_password)
            if key in mock_db_connections.keys():
                return mock_db_connections[key]
            else:
                nonlocal mock_get_db_connection_unmocked_call
                mock_get_db_connection_unmocked_call = key
                return None

        db_deploy.get_db_connection = mock_get_db_connection

        db_created = False
        mock_create_database_unmocked_call = None

        def mock_create_database(inner_connection: connection, inner_drop_database: bool):
            if inner_connection == creation_connection and inner_drop_database == drop_database:
                nonlocal db_created
                db_created = True
                return False, ''
            else:
                nonlocal mock_create_database_unmocked_call
                mock_create_database_unmocked_call = (inner_connection, inner_drop_database)

        db_deploy.create_database = mock_create_database

        db_deploy.create_roles_and_users = Mock()
        db_deploy.create_schema = Mock()
        db_deploy.create_tables = Mock()

        db_deploy.inner_task(db_host, db_name, db_port, db_user, db_user_pass, db_admin_pass, drop_database)
        self.assertTrue(db_created)
        db_deploy.create_roles_and_users.assert_called_once_with(creation_connection, db_user, db_user_pass)
        creation_connection.close.assert_called_once()
        db_deploy.create_schema.assert_called_once_with(updating_connection)
        updating_connection.close.assert_called_once()
        db_deploy.create_tables.assert_called_once_with(db_host, db_name, db_port, 'postgres', db_admin_pass)
        self.assertIsNone(mock_get_db_connection_unmocked_call)
        self.assertIsNone(mock_create_database_unmocked_call)
        self.assertTrue(db_created)


# todo: more unit tests

if __name__ == '__main__':
    unittest.main()
