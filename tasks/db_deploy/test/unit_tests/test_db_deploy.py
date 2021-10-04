"""
Name: test_db_deploy.py

Description:  Unit tests for db_deploy.py.
"""
import unittest
import os
from unittest.mock import Mock, call, patch, MagicMock
from moto import mock_secretsmanager
import boto3
import db_deploy
from orca_shared.database import shared_db
from sqlalchemy import text
import json


class TestDbDeployFunctions(unittest.TestCase):
    """
    Tests the db_deploy functions.
    """

    # Create the mock instance of secrets manager
    mock_sm = mock_secretsmanager()

    def setUp(self):
        """
        Perform initial setup for test.
        """
        self.mock_sm.start()
        self.test_sm = boto3.client("secretsmanager", region_name="us-west-2")
        self.config = {
            "admin_database": "admin_db",
            "admin_password": "admin123",
            "admin_username": "admin",
            "host": "aws.postgresrds.host",
            "port": 5432,
            "user_database": "user_db",
            "user_password": "user123",
            "user_username": "user",
        }
        self.secretstring = json.dumps(self.config)
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
    @patch("db_deploy.task")
    def test_handler_happy_path(self, mock_task: MagicMock):
        """
        Does a happy path test. No real logic here as it just sets up the
        Cumulus Logger and the database configuration which are tested in
        other test cases.
        """
        records = {}
        event = {"Records": records}

        db_deploy.handler(event, {})

        mock_task.assert_called_with(json.loads(self.secretstring))

    @patch("db_deploy.create_fresh_orca_install")
    @patch("orca_sql.app_database_comment_sql")
    @patch("orca_sql.app_database_sql")
    @patch("orca_sql.commit_sql")
    @patch("db_deploy.get_admin_connection")
    @patch("db_deploy.app_db_exists")
    def test_task_no_database(
        self, mock_db_exists: MagicMock,
            mock_connection: MagicMock,
            mock_commit_sql: MagicMock,
            mock_app_database_sql: MagicMock,
            mock_app_database_comment_sql: MagicMock,
            mock_create_fresh_orca_install: MagicMock
    ):
        """
        Validates if the ORCA database does not exist, then it is created.
        """
        mock_db_exists.return_value = False

        db_deploy.task(self.config)
        mock_db_exists.assert_called_with(mock_connection().connect().__enter__())
        # Check the text calls occur and in the proper order
        execute_calls = [
            call(mock_commit_sql.return_value),
            call(mock_app_database_sql.return_value),
            call(mock_app_database_comment_sql.return_value)
        ]
        mock_connection().connect().__enter__().execute.assert_has_calls(execute_calls, any_order=False)
        mock_create_fresh_orca_install.assert_called_once_with(self.config)

    @patch("db_deploy.get_admin_connection")
    @patch("db_deploy.create_fresh_orca_install")
    @patch("db_deploy.app_schema_exists")
    @patch("db_deploy.app_db_exists")
    def test_task_no_schema(
        self,
        mock_db_exists: MagicMock,
        mock_schema_exists: MagicMock,
        mock_fresh_install: MagicMock,
        mock_connection: MagicMock,
    ):
        """
        Validates that `create_fresh_orca_install` is called if no ORCA schema
        are present.
        """
        mock_db_exists.return_value = True
        mock_schema_exists.return_value = False

        db_deploy.task(self.config)
        mock_fresh_install.assert_called_with(self.config)

    @patch("db_deploy.get_admin_connection")
    @patch("db_deploy.perform_migration")
    @patch("db_deploy.get_migration_version")
    @patch("db_deploy.app_schema_exists")
    @patch("db_deploy.app_db_exists")
    def test_task_schmea_old_version(
        self,
        mock_db_exists: MagicMock,
        mock_schema_exists: MagicMock,
        mock_migration_version: MagicMock,
        mock_perform_migration: MagicMock,
        mock_connection: MagicMock,
    ):
        """
        Validates that `perform_migration` is called if the current schema
        version is older than the latest version.
        """
        mock_db_exists.return_value = True
        mock_schema_exists.return_value = True
        mock_migration_version.return_value = 1

        db_deploy.task(self.config)
        mock_perform_migration.assert_called_with(1, self.config)

    @patch("db_deploy.get_admin_connection")
    @patch("db_deploy.logger.info")
    @patch("db_deploy.get_migration_version")
    @patch("db_deploy.app_schema_exists")
    @patch("db_deploy.app_db_exists")
    def test_task_schema_current_version(
        self,
        mock_db_exists: MagicMock,
        mock_schema_exists: MagicMock,
        mock_migration_version: MagicMock,
        mock_logger_info: MagicMock,
        mock_connection: MagicMock,
    ):
        """
        validates that no action is taken if the current and latest versions
        are the same.
        """
        mock_db_exists.return_value = True
        mock_schema_exists.return_value = True
        mock_migration_version.return_value = 4
        message = "Current ORCA schema version detected. No migration needed!"

        db_deploy.task(self.config)
        mock_logger_info.assert_called_with(message)

    def test_app_db_exists_happy_path(self):
        """
        Does a happy path test for the function. No real logic to test.
        """
        # Create the mock connection object and the return value
        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchall.return_value = [
            [
                True,
            ],
        ]

        # call the function
        db_exists = db_deploy.app_db_exists(mock_conn)

        self.assertEqual(db_exists, True)

    def test_app_schema_exists_happy_path(self):
        """
        Does a happy path test for the function. No real logic to test.
        """
        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchall.return_value = [
            [
                True,
            ],
        ]

        # call the function
        schema_exists = db_deploy.app_schema_exists(mock_conn)

        self.assertEqual(schema_exists, True)

    def test_app_versions_table_exists_happy_path(self):
        """
        Does a happy path test for the function. No real logic to test.
        """
        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchall.return_value = [
            [
                True,
            ],
        ]

        # call the function
        table_exists = db_deploy.app_version_table_exists(mock_conn)

        self.assertEqual(table_exists, True)

    @patch("db_deploy.app_version_table_exists")
    def test_get_migration_version_happy_path(self, mock_table_exists):
        """
        Does a happy path test for the function. No real logic to test.
        """
        mock_conn = MagicMock()
        table_exists_array = [True, False]
        mock_conn.execute.return_value.fetchall.return_value = [
            [
                4,
            ],
        ]

        for table_exists in table_exists_array:
            with self.subTest(table_exists=table_exists):
                mock_table_exists.return_value = table_exists

                # call the function
                schema_version = db_deploy.get_migration_version(mock_conn)

                if table_exists:
                    self.assertEqual(schema_version, 4)
                else:
                    self.assertEqual(schema_version, 1)
