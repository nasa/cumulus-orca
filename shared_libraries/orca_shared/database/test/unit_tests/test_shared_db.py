"""
Name: test_shared_db.py

Description: Runs unit tests for the shared_db.py library.
"""

import json
import os
import unittest
from unittest.mock import MagicMock, Mock, patch

import boto3
import psycopg2
import sqlalchemy
from moto import mock_secretsmanager
from sqlalchemy.engine import URL

from orca_shared.database import shared_db


class TestSharedDatabaseLibraries(unittest.TestCase):
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
        self.secretstring = """
            {
                "admin_database":"admin_db",
                "admin_password":"admin123",
                "admin_username":"admin",
                "host":"aws.postgresrds.host",
                "port":"5432",
                "user_database":"user_db",
                "user_password":"user123",
                "user_username":"user"
            }
        """
        secret_name = "orcatest-orca-db-login-secret"  # nosec
        self.test_sm.create_secret(
            Name=secret_name, SecretString=self.secretstring
        )
        self.db_connect_info_secret_arn = self.test_sm.describe_secret(
                    SecretId=secret_name
                    )["ARN"]

    def tearDown(self):
        """
        Perform tear down actions
        """
        self.mock_sm.stop()

    @patch.dict(
        os.environ,
        {
            "AWS_REGION": "us-west-2",
        },
        clear=True,
    )
    def test_get_configuration_happy_path(self):
        """
        Testing the rainbows and bunnies path of this call.
        """
        testing_config = shared_db.get_configuration(self.db_connect_info_secret_arn)

        self.assertEqual(json.loads(self.secretstring), testing_config)

    @patch.dict(
        os.environ,
        {
        },
        clear=True,
    )
    def test_get_configuration_no_aws_region(self):
        """
        Validate an error is thrown if AWS_REGION is not set.
        """

        error_message = "Runtime environment variable AWS_REGION is not set."
        with self.assertRaises(Exception) as cm:
            shared_db.get_configuration(self.db_connect_info_secret_arn)
        self.assertEqual(str(cm.exception), error_message)

    @patch.dict(
        os.environ,
        {
            "AWS_REGION": "us-west-2",
        },
        clear=True,
    )
    def test_get_configuration_bad_secret(self):
        """
        Validates a secret is thrown if a secretsmanager ID is invalid.
        """
        secret_key = "orcatest-orca-db-login-secret"  # nosec
        message = "Failed to retrieve secret manager value."

        self.test_sm.delete_secret(SecretId=secret_key, ForceDeleteWithoutRecovery=True)

        # Run the test
        with self.assertRaises(Exception) as cm:
            shared_db.get_configuration(self.db_connect_info_secret_arn)
        self.assertEqual(str(cm.exception), message)

        # Recreate the key
        self.test_sm.create_secret(Name=secret_key, SecretString="Some-Value-Here")

    @patch.dict(
        os.environ,
        {
            "AWS_REGION": "us-west-2",
        },
        clear=True,
    )
    @patch("orca_shared.database.shared_db._create_connection")
    def test_get_admin_connection_database_values(self, mock_connection: MagicMock):
        """
        Tests the function to make sure the correct database value is passed.
        """
        root_db_call = {
            "host": "aws.postgresrds.host",
            "port": "5432",
            "database": "admin_db",
            "username": "admin",
            "password": "admin123",
        }

        user_db_call = {
            "host": "aws.postgresrds.host",
            "port": "5432",
            "database": "orca",
            "username": "admin",
            "password": "admin123",
        }

        config = shared_db.get_configuration(self.db_connect_info_secret_arn)

        _ = shared_db.get_admin_connection(config)
        mock_connection.assert_called_with(**root_db_call)

        _ = shared_db.get_admin_connection(config, "orca")
        mock_connection.assert_called_with(**user_db_call)

    @patch.dict(
        os.environ,
        {
            "AWS_REGION": "us-west-2",
        },
        clear=True,
    )
    @patch("orca_shared.database.shared_db._create_connection")
    def test_get_user_connection_database_values(self, mock_connection: MagicMock):
        """
        Tests the function to make sure the correct database value is passed.
        """
        user_db_call = {
            "host": "aws.postgresrds.host",
            "port": "5432",
            "database": "user_db",
            "username": "user",
            "password": "user123",
        }

        config = shared_db.get_configuration(self.db_connect_info_secret_arn)

        _ = shared_db.get_user_connection(config)
        mock_connection.assert_called_with(**user_db_call)

    @patch.dict(
        os.environ,
        {
            "AWS_REGION": "us-west-2",
        },
        clear=True,
    )
    @patch("orca_shared.database.shared_db.create_engine")
    def test__create_connection_call_values(self, mock_connection: MagicMock):
        """
        Tests the function to make sure the correct database value is passed.
        """
        user_db_call = {
            "host": "aws.postgresrds.host",
            "port": "5432",
            "database": "user_db",
            "username": "user",
            "password": "user123",
        }

        user_db_url = URL.create(drivername="postgresql", **user_db_call)
        _ = shared_db._create_connection(**user_db_call)
        mock_connection.assert_called_once_with(user_db_url, future=True)

    @patch("time.sleep")
    def test_retry_operational_error_happy_path(self, mock_sleep: MagicMock):
        expected_result = Mock()

        @shared_db.retry_operational_error(3)
        def dummy_call():
            return expected_result

        result = dummy_call()

        self.assertEqual(expected_result, result)
        mock_sleep.assert_not_called()

    @patch("time.sleep")
    def test_retry_operational_error_non_operational_error_raises(
        self, mock_sleep: MagicMock
    ):
        """
        If the error raised is not an OperationalError, it should just be raised.
        """

        @shared_db.retry_operational_error(3)
        def dummy_call():
            raise KeyError

        try:
            dummy_call()
        except KeyError:
            mock_sleep.assert_not_called()
            return
        self.fail("Error not raised.")

    @patch("time.sleep")
    def test_retry_operational_error_operational_error_retries_and_raises(
        self, mock_sleep: MagicMock
    ):
        """
        If the error raised is an OperationalError, it should retry up to the maximum allowed.
        """
        max_retries = 16
        # I have not tested that the below is a perfect recreation of an AdminShutdown error.
        expected_error = sqlalchemy.exc.OperationalError(
            Mock(), Mock(), psycopg2.errors.AdminShutdown
        )

        @shared_db.retry_operational_error(max_retries)
        def dummy_call():
            raise expected_error

        try:
            dummy_call()
        except sqlalchemy.exc.OperationalError as caught_error:
            self.assertEqual(expected_error, caught_error)
            self.assertEqual(max_retries, mock_sleep.call_count)
            return
        self.fail("Error not raised.")
