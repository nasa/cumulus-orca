"""
Name: test_migrate_db_v4.py

Description: Runs unit tests for the migrations/migrate_versions_3_to_4/migrate_db_v4.py
"""

import unittest
from unittest.mock import call, patch, MagicMock
from migrations.migrate_versions_3_to_4 import migrate_db_v4

class TestMigrateDatabaseLibraries(unittest.TestCase):
    """
    Runs unit tests on the migrate_db functions.
    """

    def setUp(self):
        """
        Set up test.
        """
        self.config = {
            "admin_database": "admin_db",
            "admin_password": "admin123",
            "admin_username": "admin",
            "host": "aws.postgresrds.host",
            "port": 5432,
            "user_database": "user_db",
            "user_password": "user123456789",
            "user_username": "user",
        }

    def tearDown(self):
        """
        Tear down test
        """
        self.config = None
    

    @patch("migrations.migrate_versions_3_to_4.migrate_db_v4.sql.schema_versions_data_sql")
    @patch("migrations.migrate_versions_3_to_4.migrate_db_v4.sql.providers_table_sql")
    @patch("migrations.migrate_versions_3_to_4.migrate_db_v4.sql.collections_table_sql")
    @patch("migrations.migrate_versions_3_to_4.migrate_db_v4.sql.granules_table_sql")
    @patch("migrations.migrate_versions_3_to_4.migrate_db_v4.sql.files_table_sql")
    @patch("migrations.migrate_versions_3_to_4.migrate_db_v4.get_admin_connection")
    @patch("migrations.migrate_versions_3_to_4.migrate_db_v4.sql.text")
    def test_migrate_versions_3_to_4_happy_path(
            self,
            mock_text: MagicMock,
            mock_connection: MagicMock,
            mock_files_table: MagicMock,
            mock_granules_table: MagicMock,
            mock_collections_table: MagicMock,
            mock_providers_table: MagicMock,
            mock_schema_versions_data: MagicMock,
    ):
        """
        Tests the migrate_versions_3_to_4 function happy path
        """
        for latest_version in [True, False]:
            with self.subTest(latest_version=latest_version):
                # Setup the mock object that conn.execute is a part of in
                # the connection with block
                mock_conn_enter = mock_connection().connect().__enter__()

                # Run the function
                migrate_db_v4.migrate_versions_3_to_4(self.config, latest_version)

                # Check that all of the functions were called the correct
                # number of times with the proper values
                mock_connection.assert_any_call(
                    self.config, self.config["user_database"]
                )
                mock_providers_table.assert_called_once()
                mock_collections_table.assert_called_once()
                mock_granules_table.assert_called_once()
                mock_files_table.assert_called_once()

                # Check the text calls occur and in the proper order
                text_calls = [
                    call("SET ROLE orca_dbo;"),
                    call("SET search_path TO orca, public;"),
                ]
                mock_text.assert_has_calls(text_calls, any_order=False)
                execution_order = [
                    call.execute(mock_text("SET ROLE orca_dbo;")),
                    call.execute(mock_text("SET search_path TO orca, public;")),
                    call.execute(mock_providers_table()),
                    call.execute(mock_collections_table()),
                    call.execute(mock_granules_table()),
                    call.execute(mock_files_table()),
                    call.commit(),
                ]
                # Validate logic switch and set the execution order
                if latest_version:
                    mock_schema_versions_data.assert_called_once()

                else:
                    mock_schema_versions_data.assert_not_called()

                # Check that items were called in the proper order
                mock_conn_enter.assert_has_calls(execution_order, any_order=False)

                # Reset the mocks for next loop
                mock_connection.reset_mock()
                mock_providers_table.reset_mock()
                mock_collections_table.reset_mock()
                mock_granules_table.reset_mock()
                mock_files_table.reset_mock()
                mock_schema_versions_data.reset_mock()
                mock_text.reset_mock()
