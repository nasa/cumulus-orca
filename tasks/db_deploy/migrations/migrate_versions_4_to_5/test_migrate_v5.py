"""
Name: test_migrate.py

Description: Runs unit tests for the migrations/migrate_versions_4_to_5/migrate.py
"""

import unittest
from unittest.mock import call, patch, MagicMock
from migrations.migrate_versions_4_to_5 import migrate

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
    

    @patch("migrations.migrate_versions_4_to_5.migrate.sql.schema_versions_data_sql")
    @patch("migrations.migrate_versions_4_to_5.migrate.sql.reconcile_status_table_sql")
    @patch("migrations.migrate_versions_4_to_5.migrate.sql.reconcile_job_table_sql")
    @patch("migrations.migrate_versions_4_to_5.migrate.sql.reconcile_s3_object_table_sql")
    @patch("migrations.migrate_versions_4_to_5.migrate.sql.reconcile_catalog_mismatch_report_table_sql")
    @patch("migrations.migrate_versions_4_to_5.migrate.sql.reconcile_orphan_report_table_sql")
    @patch("migrations.migrate_versions_4_to_5.migrate.sql.reconcile_phantom_report_table_sql")
    @patch("migrations.migrate_versions_4_to_5.migrate.get_admin_connection")
    @patch("migrations.migrate_versions_4_to_5.migrate.sql.text")
    def test_migrate_versions_4_to_5_happy_path(
            self,
            mock_text: MagicMock,
            mock_connection: MagicMock,
            mock_reconcile_phantom_report_table: MagicMock,
            mock_reconcile_orphan_report_table: MagicMock,
            mock_reconcile_catalog_mismatch_report_table: MagicMock,
            mock_reconcile_s3_object_table: MagicMock,
            mock_reconcile_job_table: MagicMock,
            mock_reconcile_status_table: MagicMock,
            mock_schema_versions_data: MagicMock,
    ):
        """
        Tests the migrate_versions_4_to_5 function happy path
        """
        for latest_version in [True, False]:
            with self.subTest(latest_version=latest_version):
                # Setup the mock object that conn.execute is a part of in
                # the connection with block
                mock_conn_enter = mock_connection().connect().__enter__()

                # Run the function
                migrate.migrate_versions_4_to_5(self.config, latest_version)

                # Check that all of the functions were called the correct
                # number of times with the proper values
                mock_connection.assert_any_call(
                    self.config, self.config["user_database"]
                )
                mock_reconcile_status_table.assert_called_once()
                mock_reconcile_job_table.assert_called_once()
                mock_reconcile_s3_object_table.assert_called_once()
                mock_reconcile_catalog_mismatch_report_table.assert_called_once()
                mock_reconcile_orphan_report_table.assert_called_once()
                mock_reconcile_phantom_report_table.assert_called_once()

                # Check the text calls occur and in the proper order
                text_calls = [
                    call("SET ROLE orca_dbo;"),
                    call("SET search_path TO orca, public;"),
                ]
                mock_text.assert_has_calls(text_calls, any_order=False)
                execution_order = [
                    call.execute(mock_text("SET ROLE orca_dbo;")),
                    call.execute(mock_text("SET search_path TO orca, public;")),
                    call.execute(mock_reconcile_status_table()),
                    call.execute(mock_reconcile_job_table()),
                    call.execute(mock_reconcile_s3_object_table()),
                    call.execute(mock_reconcile_catalog_mismatch_report_table()),
                    call.execute(mock_reconcile_orphan_report_table()),
                    call.execute(mock_reconcile_phantom_report_table()),
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
                mock_reconcile_status_table.reset_mock()
                mock_reconcile_job_table.reset_mock()
                mock_reconcile_s3_object_table.reset_mock()
                mock_reconcile_catalog_mismatch_report_table.reset_mock()
                mock_reconcile_orphan_report_table.reset_mock()
                mock_reconcile_phantom_report_table.reset_mock()
                mock_schema_versions_data.reset_mock()
                mock_text.reset_mock()
