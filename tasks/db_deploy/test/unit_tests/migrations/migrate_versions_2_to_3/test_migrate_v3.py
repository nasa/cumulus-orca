"""
Name: test_migrate_db_v3.py

Description: Runs unit tests for the migrations/migrate_versions_2_to_3/migrate.py
"""

import unittest
from unittest.mock import MagicMock, call, patch

from migrations.migrate_versions_2_to_3 import migrate


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

    @patch("migrations.migrate_versions_2_to_3.migrate.sql.text")
    @patch("migrations.migrate_versions_2_to_3.migrate.sql.schema_versions_data_sql")
    @patch("migrations.migrate_versions_2_to_3.migrate.sql.add_multipart_chunksize_sql")
    @patch("migrations.migrate_versions_2_to_3.migrate.get_admin_connection")
    def test_migrate_versions_2_to_3_happy_path(
        self,
        mock_connection: MagicMock,
        mock_add_multipart_chunksize_sql: MagicMock,
        mock_schema_versions_data: MagicMock,
        mock_text: MagicMock,
    ):
        """
        Tests the migrate_versions_2_to_3 function happy path
        """
        for latest_version in [True, False]:
            with self.subTest(latest_version=latest_version):
                # Setup the mock object that conn.execute is a part of in
                # the connection with block
                mock_conn_enter = mock_connection().connect().__enter__()

                # Run the function
                migrate.migrate_versions_2_to_3(self.config, latest_version)

                # Check that all of the functions were called the correct
                # number of times with the proper values
                mock_connection.assert_any_call(
                    self.config, self.config["user_database"]
                )

                # commit block
                mock_add_multipart_chunksize_sql.assert_called_once()

                # Check the text calls occur and in the proper order
                text_calls = [
                    call("SET ROLE orca_dbo;"),
                    call("SET search_path TO orca, public;"),
                ]
                mock_text.assert_has_calls(text_calls, any_order=False)

                # Validate logic switch and set the execution order
                if latest_version:
                    mock_schema_versions_data.assert_called_once()
                    execution_order = [
                        call.execute(mock_text("SET ROLE orca_dbo;")),
                        call.execute(mock_text("SET search_path TO orca, public;")),
                        call.execute(mock_add_multipart_chunksize_sql()),
                        call.execute(mock_schema_versions_data()),
                        call.commit(),
                    ]

                else:
                    mock_schema_versions_data.assert_not_called()
                    execution_order = [
                        call.execute(mock_text("SET ROLE orca_dbo;")),
                        call.execute(mock_text("SET search_path TO orca, public;")),
                        call.execute(mock_add_multipart_chunksize_sql()),
                        call.commit(),
                    ]

                # Check that items were called in the proper order
                mock_conn_enter.assert_has_calls(execution_order, any_order=False)

                # Reset the mocks for next loop
                mock_connection.reset_mock()
                mock_add_multipart_chunksize_sql.reset_mock()
                mock_schema_versions_data.reset_mock()
