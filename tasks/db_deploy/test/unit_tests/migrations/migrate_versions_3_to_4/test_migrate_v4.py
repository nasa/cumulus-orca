"""
Name: test_migrate_db_v4.py

Description: Runs unit tests for the migrations/migrate_versions_3_to_4/migrate.py
"""

import unittest
from unittest.mock import MagicMock, call, patch

from orca_shared.database.entities import PostgresConnectionInfo

from migrations.migrate_versions_3_to_4 import migrate


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
            admin_username="admin",
            admin_password="admin123",
            user_username="user56789012",
            user_password="pass56789012",
            user_database_name="user_db",
            host="aws.postgresrds.host",
            port="5432",
        )

    def tearDown(self):
        """
        Tear down test
        """
        self.config = None

    @patch("migrations.migrate_versions_3_to_4.migrate.sql.schema_versions_data_sql")
    @patch("migrations.migrate_versions_3_to_4.migrate.sql.providers_table_sql")
    @patch("migrations.migrate_versions_3_to_4.migrate.sql.collections_table_sql")
    @patch("migrations.migrate_versions_3_to_4.migrate.sql.granules_table_sql")
    @patch("migrations.migrate_versions_3_to_4.migrate.sql.files_table_sql")
    @patch("migrations.migrate_versions_3_to_4.migrate.create_engine")
    @patch("migrations.migrate_versions_3_to_4.migrate.create_admin_uri")
    @patch("migrations.migrate_versions_3_to_4.migrate.sql.text")
    def test_migrate_versions_3_to_4_happy_path(
        self,
        mock_text: MagicMock,
        mock_create_admin_uri: MagicMock,
        mock_create_engine: MagicMock,
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
                # Run the function
                migrate.migrate_versions_3_to_4(self.config, latest_version)

                # Check that all the functions were called the correct
                # number of times with the proper values
                mock_create_admin_uri.assert_called_once_with(
                    self.config, migrate.LOGGER, self.config.user_database_name
                )
                mock_create_engine.assert_called_once_with(
                    mock_create_admin_uri.return_value, future=True
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
                self.assertEqual(len(text_calls), mock_text.call_count)
                execution_order = [
                    call.execute(mock_text("SET ROLE orca_dbo;")),
                    call.execute(mock_text("SET search_path TO orca, public;")),
                    call.execute(mock_providers_table()),
                    call.execute(mock_collections_table()),
                    call.execute(mock_granules_table()),
                    call.execute(mock_files_table()),
                ]
                # Validate logic switch and set the execution order
                if latest_version:
                    execution_order.append(
                        call.execute(mock_schema_versions_data.return_value)
                    )
                    mock_schema_versions_data.assert_called_once_with()

                else:
                    mock_schema_versions_data.assert_not_called()

                execution_order.append(call.commit())

                # Check that items were called in the proper order
                mock_conn_enter = mock_create_engine().connect().__enter__()
                mock_conn_enter.assert_has_calls(execution_order, any_order=False)
                self.assertEqual(
                    len(execution_order), len(mock_conn_enter.method_calls)
                )

            # Reset the mocks for next loop
            mock_create_admin_uri.reset_mock()
            mock_create_engine.reset_mock()
            mock_providers_table.reset_mock()
            mock_collections_table.reset_mock()
            mock_granules_table.reset_mock()
            mock_files_table.reset_mock()
            mock_schema_versions_data.reset_mock()
            mock_text.reset_mock()
