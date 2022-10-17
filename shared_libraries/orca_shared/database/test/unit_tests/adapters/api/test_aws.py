import os
import unittest
from unittest.mock import Mock, patch

import boto3
from moto import mock_secretsmanager

from orca_shared.database.adapters.api import aws
from orca_shared.database.entities import PostgresConnectionInfo


class TestAWS(unittest.TestCase):
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

    @patch.dict(
        os.environ,
        {
            "AWS_REGION": "us-west-2",
        },
        clear=True,
    )
    def test_get_configuration_happy_path(self):
        """
        Get secret value and return data class.
        """

        testing_config = aws.get_configuration(self.db_connect_info_secret_arn, LOGGER=Mock())

        self.assertEqual(PostgresConnectionInfo(  # nosec
            admin_database_name="admin_db",
            admin_password="admin123",
            admin_username="admin",
            host="aws.postgresrds.host",
            port="5432",
            user_database_name="user_db",
            user_password="user123",
            user_username="user",
        ), testing_config)

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
            aws.get_configuration(self.db_connect_info_secret_arn, LOGGER=Mock())
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
            aws.get_configuration(self.db_connect_info_secret_arn, LOGGER=Mock())
        self.assertEqual(str(cm.exception), message)
