"""
Name: test_migrate_db_v3.py

Description: Runs unit tests for the migrations/migrate_versions_2_to_3/migrate.py
"""

import unittest
from unittest.mock import MagicMock, call, patch

from orca_shared.database.entities import PostgresConnectionInfo

from migrations.migrate_versions_2_to_3 import migrate


class TestMigrateDatabaseLibraries(unittest.TestCase):
    """
    Runs unit tests on the migrate_db functions.
    """

    def setUp(self):
        """
        Set up test.
        """
        # todo: Use randomized values on a per-test basis.
        self.config = PostgresConnectionInfo(  # nosec
            admin_database_name="admin_db",
            admin_username="admin", admin_password="admin123",
            user_username="user56789012", user_password="pass56789012",
            user_database_name="user_db", host="aws.postgresrds.host", port="5432"
        )

    def tearDown(self):
        """
        Tear down test
        """
        self.config = None

    @patch("migrations.migrate_versions_2_to_3.migrate.sql.text")
    @patch("migrations.migrate_versions_2_to_3.migrate.sql.schema_versions_data_sql")
    @patch("migrations.migrate_versions_2_to_3.migrate.sql.add_multipart_chunksize_sql")
    @patch("migrations.migrate_versions_2_to_3.migrate.create_engine")
    @patch("migrations.migrate_versions_2_to_3.migrate.create_admin_uri")
    def test_migrate_versions_2_to_3_happy_path(
        self,
        mock_create_admin_uri: MagicMock,
        mock_create_engine: MagicMock,
        mock_add_multipart_chunksize_sql: MagicMock,
        mock_schema_versions_data: MagicMock,
        mock_text: MagicMock,
    ):
        """
        Tests the migrate_versions_2_to_3 function happy path
        """
        for latest_version in [True, False]:
            with self.subTest(latest_version=latest_version):
                # Run the function
                migrate.migrate_versions_2_to_3(self.config, latest_version)

                # Check that all the functions were called the correct
                # number of times with the proper values
                mock_create_admin_uri.assert_called_once_with(
                    self.config, migrate.LOGGER, self.config.user_database_name
                )
                mock_create_engine.assert_called_once_with(
                    mock_create_admin_uri.return_value, future=True
                )

                # commit block
                mock_add_multipart_chunksize_sql.assert_called_once()

                # Check the text calls occur and in the proper order
                text_calls = [
                    call("SET ROLE orca_dbo;"),
                    call("SET search_path TO orca, public;"),
                ]
                mock_text.assert_has_calls(text_calls, any_order=False)
                self.assertEqual(len(text_calls), mock_text.call_count)

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
                mock_conn_enter = mock_create_engine().connect().__enter__()
                mock_conn_enter.assert_has_calls(execution_order, any_order=False)
                self.assertEqual(len(execution_order), len(mock_conn_enter.method_calls))

            # Reset the mocks for next loop
            mock_text.reset_mock()
            mock_create_admin_uri.reset_mock()
            mock_create_engine.reset_mock()
            mock_add_multipart_chunksize_sql.reset_mock()
            mock_schema_versions_data.reset_mock()
