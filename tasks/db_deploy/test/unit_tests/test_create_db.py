"""
Name: test_create_db.py

Description: Runs unit tests for the create_db.py library.
"""

import unittest
from unittest.mock import Mock, call, patch, MagicMock
import create_db


class TestCreateDatabseLibraries(unittest.TestCase):
    """
    Test the various functions in the create_db library.
    """

    def setUp(self):
        """
        Set up test.
        """
        self.config = {
            "host": "aws.postgresrds.host",
            "port": "5432",
            "database": "disaster_recovery",
            "root_database": "postgres",
            "app_user": "orcauser",
            "root_user": "postgres",
            "app_user_password": "MySecretUserPassword",
            "root_user_password": "MySecretAdminPassword",
        }

        self.mock_connection = MagicMock()

    def tearDown(self):
        """
        Tear down test
        """
        self.config = None
        self.mock_connection = None

    @patch("create_db.create_recovery_objects")
    @patch("create_db.create_metadata_objects")
    @patch("create_db.set_search_path_and_role")
    @patch("create_db.create_app_schema_role_users")
    @patch("create_db.get_root_connection")
    def test_create_fresh_orca_install_happy_path(
        self,
        mock_connection: MagicMock,
        mock_create_app_schema_roles: MagicMock,
        mock_set_search_path_role: MagicMock,
        mock_create_metadata: MagicMock,
        mock_create_recovery: MagicMock,
    ):
        """
        Tests normal happy path of create_fresh_orca_install function.
        """
        create_db.create_fresh_orca_install(self.config)

        mock_conn_enter = mock_connection().connect().__enter__()

        mock_create_app_schema_roles.assert_called_once_with(
            mock_conn_enter, self.config["app_user_password"]
        )
        mock_set_search_path_role.assert_called_once_with(mock_conn_enter)
        mock_create_metadata.assert_called_once_with(mock_conn_enter)
        mock_create_recovery.assert_called_once_with(mock_conn_enter)

        # Check that commit was called at the end. In this case it is position
        # 4 of the calls (initial call with config, connection call, enter of
        # with loop, commit, then exiting calls).
        mock_call_commit = mock_connection.mock_calls[3]
        mock_commit = call().connect().__enter__().commit()
        self.assertEqual(mock_call_commit, mock_commit)

    @patch("create_db.app_user_sql")
    @patch("create_db.orca_schema_sql")
    @patch("create_db.app_role_sql")
    @patch("create_db.dbo_role_sql")
    def test_create_app_schema_user_role_users_happy_path(
        self,
        mock_dbo_role_sql: MagicMock,
        mock_app_role_sql: MagicMock,
        mock_schema_sql: MagicMock,
        mock_user_sql: MagicMock,
    ):
        """
        Tests happy path of create_app_schema_role_users function.
        """
        create_db.create_app_schema_role_users(
            self.mock_connection, self.config["app_user_password"]
        )

        # Check that SQL called properly
        mock_dbo_role_sql.assert_called_once()
        mock_app_role_sql.assert_called_once()
        mock_schema_sql.assert_called_once()
        mock_user_sql.assert_called_once_with(self.config["app_user_password"])

        # Check SQL called in proper order
        execution_order = [
            call.execute(mock_dbo_role_sql()),
            call.execute(mock_app_role_sql()),
            call.execute(mock_schema_sql()),
            call.execute(mock_user_sql(self.config["app_user_password"])),
        ]

        self.assertEqual(self.mock_connection.mock_calls, execution_order)

    @patch("create_db.text")
    def test_set_search_path_and_role(self, mock_text: MagicMock):
        """
        Tests happy path of set_search_path_and_role function.
        """
        create_db.set_search_path_and_role(self.mock_connection)

        # Check that the two SQL calls are made to text
        mock_text.assert_any_call("SET ROLE orca_dbo;")
        mock_text.assert_any_call("SET search_path TO orca, public;")

        # Check that SQL is called in the proper order
        execution_order = [
            call.execute(mock_text("SET ROLE orca_dbo;")),
            call.execute(mock_text("SET search_path TO orca, public;")),
        ]

        self.assertEqual(self.mock_connection.mock_calls, execution_order)

    @patch("create_db.schema_versions_data_sql")
    @patch("create_db.schema_versions_table_sql")
    def test_create_metadata_objects(
        self,
        mock_schema_versions_table: MagicMock,
        mock_schema_versions_data: MagicMock,
    ):
        """
        Tests happy path of create_metadata_objects function
        """
        create_db.create_metadata_objects(self.mock_connection)

        # Check that the SQL calls were made.
        mock_schema_versions_table.assert_called_once()
        mock_schema_versions_data.assert_called_once()

        # Check that they were called in the proper order
        execution_order = [
            call.execute(mock_schema_versions_table()),
            call.execute(mock_schema_versions_data()),
        ]

        self.assertEqual(self.mock_connection.mock_calls, execution_order)

    @patch("create_db.recovery_file_table_sql")
    @patch("create_db.recovery_job_table_sql")
    @patch("create_db.recovery_status_data_sql")
    @patch("create_db.recovery_status_table_sql")
    def test_create_recovery_objects(
        self,
        mock_recovery_status_table: MagicMock,
        mock_recovery_status_data: MagicMock,
        mock_recovery_job_table: MagicMock,
        mock_recovery_file_table: MagicMock,
    ):
        """
        Tests happy path of the create_recovery_objects function
        """
        create_db.create_recovery_objects(self.mock_connection)

        # Check that the SQL calls were made
        mock_recovery_status_table.assert_called_once()
        mock_recovery_status_data.assert_called_once()
        mock_recovery_job_table.assert_called_once()
        mock_recovery_file_table.assert_called_once()

        # Check that the were called in the proper order
        execution_order = [
            call.execute(mock_recovery_status_table()),
            call.execute(mock_recovery_status_data()),
            call.execute(mock_recovery_job_table()),
            call.execute(mock_recovery_file_table()),
        ]

        self.assertEqual(self.mock_connection.mock_calls, execution_order)
