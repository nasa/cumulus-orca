"""
Name: test_shared_db.py

Description: Runs unit tests for the shared_db.py library.
"""
import os
import unittest
from unittest.mock import MagicMock, patch

import boto3
from moto import mock_secretsmanager
from sqlalchemy.engine import URL

from orca_shared.database import shared_db


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
        self.test_sm.create_secret(
            Name="orcatest-drdb-host", SecretString="aws.postgresrds.host"
        )
        self.test_sm.create_secret(
            Name="orcatest-drdb-admin-pass", SecretString="MySecretAdminPassword"
        )
        self.test_sm.create_secret(
            Name="orcatest-drdb-user-pass", SecretString="MySecretUserPassword"
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
            "DATABASE_NAME": "disaster_recovery",
            "DATABASE_PORT": "5432",
            "APPLICATION_USER": "orcauser",
            "ADMIN_USER": "postgres",
            "ADMIN_DATABASE": "postgres",
            "AWS_REGION": "us-west-2",
        },
        clear=True,
    )
    def test_get_configuration_happy_path(self):
        """
        Testing the rainbows and bunnies path of this call.
        """
        check_config = {
            "host": "aws.postgresrds.host",
            "port": "5432",
            "database": "disaster_recovery",
            "admin_database": "postgres",
            "app_user": "orcauser",
            "admin_user": "postgres",
            "app_user_password": "MySecretUserPassword",
            "admin_user_password": "MySecretAdminPassword",
        }

        testing_config = shared_db.get_configuration()

        for key in check_config:
            self.assertIn(key, testing_config)
            self.assertEqual(check_config[key], testing_config[key])

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
            "DATABASE_NAME": "disaster_recovery",
            "DATABASE_PORT": "5432",
            "APPLICATION_USER": "orcauser",
            "ADMIN_USER": "postgres",
            "ADMIN_DATABASE": "postgres",
            "AWS_REGION": "us-west-2",
        },
        clear=True,
    )
    def test_get_configuration_bad_env_required(self):
        """
        Validate an error is thrown if an expected environment variable is not
        is not set.
        """
        env_names = [
            "DATABASE_NAME",
            "DATABASE_PORT",
            "APPLICATION_USER",
        ]
        env_bad_values = [None, ""]

        for name in env_names:
            good_value = os.getenv(name)
            for bad_value in env_bad_values:
                with self.subTest(
                    name=name, bad_value=bad_value, good_value=good_value
                ):
                    # Set the variable to the bad value and create the message
                    if bad_value is None:
                        del os.environ[name]
                    else:
                        os.environ[name] = bad_value

                    message = f"Environment variable {name} is not set and is required"

                    # Run the test
                    with self.assertRaises(Exception) as ex:
                        shared_db.get_configuration()
                        self.assertEquals(ex.message, message)

                    # Reset the value
                    os.environ[name] = good_value

    @patch.dict(
        os.environ,
        {
            "PREFIX": "orcatest",
            "DATABASE_NAME": "disaster_recovery",
            "DATABASE_PORT": "5432",
            "APPLICATION_USER": "orcauser",
            "ADMIN_USER": "postgres",
            "ADMIN_DATABASE": "postgres",
            "AWS_REGION": "us-west-2",
        },
        clear=True,
    )
    @patch("orca_shared.database.shared_db.logger")
    def test_get_configuration_bad_env_optional(self, mock_logger: MagicMock):
        """
        Validate an error is thrown if an expected environment variable is not
        is not set.
        """
        env_names = [
            "ADMIN_USER",
            "ADMIN_DATABASE",
        ]
        env_bad_values = [None, ""]

        for name in env_names:
            good_value = os.getenv(name)
            for bad_value in env_bad_values:
                with self.subTest(
                    name=name, bad_value=bad_value, good_value=good_value
                ):

                    # Set the variable to the bad value and create the message
                    if bad_value is None:
                        del os.environ[name]
                    else:
                        os.environ[name] = bad_value

                    message = f"Setting variable {name} value to postgres"

                    # Run the test
                    test_config = shared_db.get_configuration()

                    # Check log message and default value set
                    mock_logger.info.assert_called_with(message)
                    self.assertEqual(test_config[name.lower()], "postgres")

                    # Reset the value for the next loop
                    os.environ[name] = good_value

    @patch.dict(
        os.environ,
        {
            "PREFIX": "orcatest",
            "DATABASE_NAME": "disaster_recovery",
            "DATABASE_PORT": "5432",
            "APPLICATION_USER": "orcauser",
            "ADMIN_USER": "postgres",
            "ADMIN_DATABASE": "postgres",
            "AWS_REGION": "us-west-2",
        },
        clear=True,
    )
    def test_get_configuration_bad_secret(self):
        """
        Validates a secret is thrown if a secretmanager ID is invalid.
        """
        secret_keys = [
            "orcatest-drdb-host",
            "orcatest-drdb-admin-pass",
            "orcatest-drdb-user-pass",
        ]
        message = "Failed to retrieve secret manager value."

        for secret_key in secret_keys:
            with self.subTest(secret_key=secret_key):
                # Delete the key
                self.test_sm.delete_secret(
                    SecretId=secret_key, ForceDeleteWithoutRecovery=True
                )

                # Run the test
                with self.assertRaises(Exception) as ex:
                    shared_db.get_configuration()
                    self.assertEquals(ex.message, message)

                # Recreate the key
                self.test_sm.create_secret(
                    Name=secret_key, SecretString="Some-Value-Here"
                )

    @patch.dict(
        os.environ,
        {
            "PREFIX": "orcatest",
            "DATABASE_NAME": "disaster_recovery",
            "DATABASE_PORT": "5432",
            "APPLICATION_USER": "orcauser",
            "ADMIN_USER": "postgres",
            "ADMIN_DATABASE": "postgres",
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
            "database": "postgres",
            "username": "postgres",
            "password": "MySecretAdminPassword",
        }

        user_db_call = {
            "host": "aws.postgresrds.host",
            "port": "5432",
            "database": "disaster_recovery",
            "username": "postgres",
            "password": "MySecretAdminPassword",
        }

        config = shared_db.get_configuration()

        _ = shared_db.get_admin_connection(config)
        mock_connection.assert_called_with(**root_db_call)

        _ = shared_db.get_admin_connection(config, "disaster_recovery")
        mock_connection.assert_called_with(**user_db_call)

    @patch.dict(
        os.environ,
        {
            "PREFIX": "orcatest",
            "DATABASE_NAME": "disaster_recovery",
            "DATABASE_PORT": "5432",
            "APPLICATION_USER": "orcauser",
            "ADMIN_USER": "postgres",
            "ADMIN_DATABASE": "postgres",
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
            "database": "disaster_recovery",
            "username": "orcauser",
            "password": "MySecretUserPassword",
        }

        config = shared_db.get_configuration()

        _ = shared_db.get_user_connection(config)
        mock_connection.assert_called_with(**user_db_call)

    @patch.dict(
        os.environ,
        {
            "PREFIX": "orcatest",
            "DATABASE_NAME": "disaster_recovery",
            "DATABASE_PORT": "5432",
            "APPLICATION_USER": "orcauser",
            "ADMIN_USER": "postgres",
            "ADMIN_DATABASE": "postgres",
            "AWS_REGION": "us-west-2",
        },
        clear=True,
    )
    @patch("orca_shared.database.shared_db.create_engine")
    def test_create_connection_call_values(self, mock_connection: MagicMock):
        """
        Tests the function to make sure the correct database value is passed.
        """
        user_db_call = {
            "host": "aws.postgresrds.host",
            "port": "5432",
            "database": "disaster_recovery",
            "username": "orcauser",
            "password": "MySecretUserPassword",
        }

        user_db_url = URL.create(drivername="postgresql", **user_db_call)

        _ = shared_db._create_connection(**user_db_call)
        mock_connection.assert_called_once_with(user_db_url, future=True)
