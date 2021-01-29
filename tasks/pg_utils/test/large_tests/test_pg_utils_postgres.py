"""
Name: test_pg_utils_postgres.py

Description:  Unit tests for requests_db.py.
"""

import datetime
import os
import unittest
from unittest.mock import Mock
import uuid

import boto3
import psycopg2.extras

import database
from database import DbError

UUID1 = str(uuid.uuid4())

class TestDatabase(unittest.TestCase):  #pylint: disable-msg=too-many-public-methods
    """
    TestDatabase.
    """

    def setUp(self):

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
            'db_host': { 'secretsmanager': 'drdb-host' },
            'db_port': { 'env': 'DATABASE_PORT' },
            'db_name': { 'env': 'DATABASE_NAME' },
            'db_user': { 'env': 'DATABASE_USER' },
            'db_pw': { 'secretsmanager': 'drdb-user-pass' }
        }
        self.dbconnect_info = database.read_db_connect_info(db_params)

    def tearDown(self):
        boto3.client = self.mock_boto3
        del os.environ['DATABASE_HOST']
        del os.environ['DATABASE_PORT']
        del os.environ['DATABASE_NAME']
        del os.environ['DATABASE_USER']
        del os.environ['DATABASE_PW']

    # TODO: This test has a happy and sad path, and passes for both.
    # Split into 2 tests
    def test_return_connection(self):
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
        exp_err = ('Database Error. could not translate host name '
                   '"my.db.host.gov" to address: Unknown host\n')
        try:
            con = database.return_connection(db_connect_info)
            self.assertIsNotNone(con)
        except DbError as err:
            self.assertEqual(exp_err, str(err))