"""
Name: test_requests.py

Description:  Unit tests for requests_db.py.
"""

import datetime
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
import uuid

import boto3
import psycopg2.extras

import database
from database import DbError

UUID1 = str(uuid.uuid4())


class TestDatabase(unittest.TestCase):  # pylint: disable-msg=too-many-public-methods
    """
    TestDatabase.
    """

    def setUp(self):
        # todo: Rework all tests, including wiping this global env and mock setup.
        os.environ['DATABASE_HOST'] = 'localhost'
        os.environ['DATABASE_PORT'] = '5432'
        os.environ['DATABASE_NAME'] = 'postgres'
        os.environ['DATABASE_USER'] = 'postgres'
        os.environ['DATABASE_PW'] = 'postgres'

        self.mock_utcnow = database.get_utc_now_iso
        self.mock_uuid = database.uuid_generator
        self.mock_boto3 = boto3.client
        boto3.client = Mock()
        secretsmanager_cli = boto3.client('secretsmanager')
        db_host = {'SecretString': os.environ['DATABASE_HOST']}
        db_pw = {'SecretString': os.environ['DATABASE_PW']}
        secretsmanager_cli.get_secret_value = Mock(side_effect=[db_host,
                                                                db_pw])
        db_params = {
            'db_host': {'secretsmanager': 'drdb-host'},
            'db_port': {'env': 'DATABASE_PORT'},
            'db_name': {'env': 'DATABASE_NAME'},
            'db_user': {'env': 'DATABASE_USER'},
            'db_pw': {'secretsmanager': 'drdb-user-pass'}
        }
        self.dbconnect_info = database.read_db_connect_info(db_params)

    def tearDown(self):
        boto3.client = self.mock_boto3
        database.get_utc_now_iso = self.mock_utcnow
        database.uuid_generator = self.mock_uuid
        del os.environ['DATABASE_HOST']
        del os.environ['DATABASE_PORT']
        del os.environ['DATABASE_NAME']
        del os.environ['DATABASE_USER']
        del os.environ['DATABASE_PW']

    def test_get_utc_now_iso(self):
        """
        Tests the get_utc_now_iso function
        """
        utc_now_exp = '2019-07-17T17:36:38.494918'
        utc_now_exp = datetime.datetime.utcnow().isoformat()
        database.get_utc_now_iso = Mock(return_value=utc_now_exp)
        self.assertEqual(utc_now_exp, database.get_utc_now_iso())

    # TODO: This doesn't test anything.
    def test_uuid_generator(self):
        """
        Tests the uuid_generator function
        """
        database.uuid_generator = Mock(return_value=UUID1)
        self.assertEqual(UUID1, database.uuid_generator())

    @patch('psycopg2.connect')
    def test_return_connection_missing_port_defaults_to_5432(self,
                                                             mock_connect: MagicMock):
        db_host = uuid.uuid4().__str__()
        db_name = uuid.uuid4().__str__()
        db_user = uuid.uuid4().__str__()
        db_user_pass = uuid.uuid4().__str__()

        dbconnect_info = {
            'db_host': db_host,
            'db_name': db_name,
            'db_user': db_user,
            'db_pw': db_user_pass
        }
        mock_connection = mock_connect.return_value
        result = database.return_connection(dbconnect_info)

        mock_connect.assert_called_once_with(
            host=db_host,
            port=5432,
            database=db_name,
            user=db_user,
            password=db_user_pass
        )
        self.assertEqual(mock_connection, result)

    # todo: More tests.
    @patch('psycopg2.connect')
    def test_return_connection(self,
                               mock_connect: MagicMock):
        """
        Tests getting a database connection
        """
        db_connect_info = {
            'db_host': os.environ['DATABASE_HOST'],
            'db_port': os.environ['DATABASE_PORT'],
            'db_name': os.environ['DATABASE_NAME'],
            'db_user': os.environ['DATABASE_USER'],
            'db_pw': os.environ['DATABASE_PW']
        }
        expected = Mock()
        mock_connect.return_value = expected

        con = database.return_connection(db_connect_info)
        self.assertEqual(expected, con)
        mock_connect.assert_called_once_with(host=db_connect_info['db_host'],
                                             port=db_connect_info['db_port'],
                                             database=db_connect_info['db_name'],
                                             user=db_connect_info['db_user'],
                                             password=db_connect_info['db_pw'])

    def test_single_query_secretsmanager(self):
        """
        Tests the single_query function
        """
        dbconnect_info = {
            'db_host': 'my.db.host.gov',
            'db_port': 5432,
            'db_name': 'postgres',
            'db_user': 'postgres',
            'db_pw': 'secret'
        }
        sql_stmt = 'Select * from mytable'
        exp_err = ('Database Error. could not translate host name "my.db.host.gov" to address: Unknown host\n')
        try:
            database.single_query(sql_stmt, dbconnect_info)
        except DbError as err:
            self.assertEqual(exp_err, str(err))

    @staticmethod
    def build_row(column1, column2, column3):
        """
        builds a row mimicing what would be returned from a call to the db
        """
        row = []
        row.append(('column1', column1))
        row.append(('column2', column2))
        row.append(('column3', column3))
        return row
