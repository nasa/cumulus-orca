"""
Name: test_shared_db.py

Description: Runs unit tests for the shared_db.py library.
"""
from moto import mock_secretsmanager
from sqlalchemy.engine import URL
import boto3
import unittest
from unittest.mock import patch, MagicMock
import os
import json
import shared_db

class TestSharedDatabseLibraries(unittest.TestCase):
    """
    Runs unit tests for all of the functions in the shared_db library.
    """

    # Create the mock instance of secrets manager
    mock_sm = mock_secretsmanager()

    def setUp(self):
        """
        Perform initial setup for test.
        """
        self.mock_sm.start()
        self.test_sm = boto3.client("secretsmanager", region_name="us-west-2")
        self.secretstring = '{"admin_database":"admin_db", "admin_password":"admin123", "admin_username":"admin", "host":"aws.postgresrds.host", "port":5432, "user_database":"user_db", "user_password":"user123", "user_username":"user"}'
        self.test_sm.create_secret(
            Name="orcatest-orca-db-login-secret", SecretString=self.secretstring
        )

    def tearDown(self):
        """
        Perform tear down actions
        """
        self.mock_sm.stop()

    @patch.dict(
        os.environ,
        {
            "PREFIX": "orcatest",
            "AWS_REGION": "us-west-2",
        },
        clear=True,
    )
    def test_get_configuration_happy_path(self):
        """
        Testing the rainbows and bunnies path of this call.
        """
        testing_config = shared_db.get_configuration()

        self.assertEqual(json.loads(self.secretstring), testing_config)

    def test_get_configuration_no_prefix(self):
        """
        Validate an error is thrown if PREFIX is not set.
        """
        error_message = "Environment variable PREFIX is not set."

        with self.assertRaises(Exception) as ex:
            shared_db.get_configuration()
            self.assertEquals(ex.message, error_message)

    @patch.dict(
        os.environ,
        {
            "PREFIX": "orcatest",
        },
        clear=True,
    )
    def test_get_configuration_no_aws_region(self):
        """
        Validate an error is thrown if PREFIX is not set.
        """
        error_message = "Environment variable AWS_REGION is not set."

        with self.assertRaises(Exception) as ex:
            shared_db.get_configuration()
            self.assertEquals(ex.message, error_message)

    @patch.dict(
        os.environ,
        {
            "PREFIX": "orcatest",
            "AWS_REGION": "us-west-2",
        },
        clear=True,
    )
    def test_get_configuration_bad_secret(self):
        """
        Validates a secret is thrown if a secretmanager ID is invalid.
        """
        secret_key = "orcatest-orca-db-login-secret"
        message = "Failed to retrieve secret manager value."

        self.test_sm.delete_secret(SecretId=secret_key, ForceDeleteWithoutRecovery=True)

        # Run the test
        with self.assertRaises(Exception) as ex:
            shared_db.get_configuration()
            self.assertEquals(ex.message, message)

        # Recreate the key
        self.test_sm.create_secret(Name=secret_key, SecretString="Some-Value-Here")

    @patch.dict(
        os.environ,
        {
            "PREFIX": "orcatest",
            "AWS_REGION": "us-west-2",
        },
        clear=True,
    )
    @patch("shared_db._create_connection")
    def test_get_admin_connection_database_values(self, mock_connection: MagicMock):
        """
        Tests the function to make sure the correct database value is passed.
        """
        root_db_call = {
            "host": "aws.postgresrds.host",
            "port": 5432,
            "database": "admin_db",
            "username": "admin",
            "password": "admin123",
        }

        user_db_call = {
            "host": "aws.postgresrds.host",
            "port": 5432,
            "database": "disaster_recovery",
            "username": "admin",
            "password": "admin123",
        }

        config = shared_db.get_configuration()

        root_db_creds = shared_db.get_admin_connection(config)
        mock_connection.assert_called_with(**root_db_call)

        user_db_creds = shared_db.get_admin_connection(config, "disaster_recovery")
        mock_connection.assert_called_with(**user_db_call)

    @patch.dict(
        os.environ,
        {
            "PREFIX": "orcatest",
            "AWS_REGION": "us-west-2",
        },
        clear=True,
    )
    @patch("shared_db._create_connection")
    def test_get_user_connection_database_values(self, mock_connection: MagicMock):
        """
        Tests the function to make sure the correct database value is passed.
        """
        user_db_call = {
            "host": "aws.postgresrds.host",
            "port": 5432,
            "database": "user_db",
            "username": "user",
            "password": "user123",
        }

        config = shared_db.get_configuration()

        user_db_creds = shared_db.get_user_connection(config)
        mock_connection.assert_called_with(**user_db_call)

    @patch.dict(
        os.environ,
        {
            "PREFIX": "orcatest",
            "AWS_REGION": "us-west-2",
        },
        clear=True,
    )
    @patch("shared_db.create_engine")
    def test__create_connection_call_values(self, mock_connection: MagicMock):
        """
        Tests the function to make sure the correct database value is passed.
        """
        user_db_call = {
            "host": "aws.postgresrds.host",
            "port": 5432,
            "database": "user_db",
            "username": "user",
            "password": "user123",
        }

        user_db_url = URL.create(drivername="postgresql", **user_db_call)
        user_db_creds = shared_db._create_connection(**user_db_call)
        mock_connection.assert_called_once_with(user_db_url, future=True)