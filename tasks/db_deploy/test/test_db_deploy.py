"""
Name: test_db_deploy.py

Description:  Unit tests for db_deploy.py.
"""
import os
import unittest
from unittest.mock import Mock
import json
import boto3
import db_config
import db_deploy
from db_deploy import DatabaseError

class TestDbDeploy(unittest.TestCase):
    """
    TestDbDeploy.
    """
    def setUp(self):
        private_config = f"{os.path.realpath(__file__)}".replace(os.path.basename(__file__),
                                                                 'private_config.json')
        db_config.set_env(private_config)
        os.environ["PLATFORM"] = "ONPREM"
        os.environ["DDL_DIR"] = "C:\\devpy\\poswotdr\\database\\ddl\\base\\"
        private_configs = None
        with open(private_config) as private_file:
            private_configs = json.load(private_file)
        os.environ["MASTER_USER_PW"] = private_configs["MASTER_USER_PW"]

    def tearDown(self):
        del os.environ["DATABASE_HOST"]
        del os.environ["DATABASE_PORT"]
        del os.environ["DATABASE_NAME"]
        del os.environ["DATABASE_USER"]
        del os.environ["DATABASE_PW"]
        del os.environ["MASTER_USER_PW"]
        del os.environ["PLATFORM"]

    @staticmethod
    def mock_ssm_get_parameter(n_times):
        """
        mocks the reads from the parameter store for the dbconnect values
        """
        params = []
        db_host = {"Parameter": {"Value": os.environ['DATABASE_HOST']}}
        db_pw = {"Parameter": {"Value": os.environ['DATABASE_PW']}}
        admin_pw = {"Parameter": {"Value": os.environ['MASTER_USER_PW']}}
        loop = 0
        while loop < n_times:
            params.append(db_pw)
            params.append(admin_pw)
            params.append(db_host)
            loop = loop + 1
        ssm_cli = boto3.client('ssm')
        ssm_cli.get_parameter = Mock(side_effect=params)

    def test_handler_drop(self):
        """
        Test db_deploy handler creating database from scratch.
        """
        handler_input_event = {}
        boto3.client = Mock()
        self.mock_ssm_get_parameter(1)
        expected = "database ddl execution complete"
        os.environ["DROP_DATABASE"] = "True"
        try:
            result = db_deploy.handler(handler_input_event, None)
            self.assertEqual(expected, result)
        except DatabaseError as err:
            self.fail(str(err))

    def test_task_no_drop(self):
        """
        Test db_deploy task when database exists
        """
        handler_input_event = {}
        boto3.client = Mock()
        self.mock_ssm_get_parameter(1)
        expected = "database ddl execution complete"
        os.environ["DROP_DATABASE"] = "False"
        del os.environ["DROP_DATABASE"]
        try:
            result = db_deploy.task(handler_input_event, None)
            self.assertEqual(expected, result)
        except DatabaseError as err:
            self.fail(str(err))

    def test_task_no_drop_platform_aws(self):
        """
        Test db_deploy task local with platform=AWS
        """
        handler_input_event = {}
        boto3.client = Mock()
        self.mock_ssm_get_parameter(1)
        expected = "Database Error. permission denied for database disaster_recovery\n"
        os.environ["PLATFORM"] = "AWS"
        try:
            db_deploy.task(handler_input_event, None)
            self.fail("expected DatabaseError")
        except DatabaseError as err:
            self.assertEqual(expected, str(err))

    def test_execute_sql_from_file_exception(self):
        """
        tests an error reading sql from a file.
        """
        con = db_deploy.get_db_connection()
        cur = db_deploy.get_cursor(con)
        sql_file = "my_nonexistent.sql"
        activity = "test file not exists"

        exp_err = "[Errno 2] No such file or directory"
        try:
            db_deploy.execute_sql_from_file(cur, sql_file, activity)
            self.fail("expected DbError")
        except DatabaseError as err:
            self.assertIn(exp_err, str(err))

    def test_execute_sql_exception(self):
        """
        tests an error querying non-existant table.
        """
        con = db_deploy.get_db_connection()
        cur = db_deploy.get_cursor(con)
        activity = "test table no exist"
        sql_stmt = """SELECT * from table_no_exist;"""
        exp_err = 'Database Error. relation "table_no_exist" does not exist'
        try:
            db_deploy.execute_sql(cur, sql_stmt, activity)
            self.fail("expected DbError")
        except DatabaseError as err:
            self.assertIn(exp_err, str(err))
            cur.close()
            con.close()

    def test_get_cursor_exception(self):
        """
        tests an error opening cursor.
        """
        exp_err = "Database Error. 'NoneType' object has no attribute 'cursor'"
        con = None
        try:
            db_deploy.get_cursor(con)
            self.fail("expected DbError")
        except DatabaseError as err:
            self.assertEqual(exp_err, str(err))

    def test_get_db_connnection_exception(self):
        """
        tests an error connecting to database.
        """
        exp_err = 'Database Error. FATAL:  database "dbnoexist" does not exist\n'
        os.environ["DATABASE_NAME"] = "dbnoexist"
        try:
            db_deploy.get_db_connection()
            self.fail("expected DbError")
        except DatabaseError as err:
            self.assertEqual(exp_err, str(err))

    def test_get_files_in_dir(self):
        """
        tests an error getting file list.
        """
        exp_dir = "really*bad$path%name"
        exp_files = []
        file_list = db_deploy.get_file_names_in_dir(exp_dir)
        self.assertEqual(exp_files, file_list)


if __name__ == '__main__':
    unittest.main()
