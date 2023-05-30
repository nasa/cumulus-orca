"""
Name: test_migrate.py

Description: Runs unit tests for the migrations/migrate_versions_4_to_5/migrate.py
"""

import unittest
from unittest.mock import MagicMock, call, patch

from orca_shared.database.entities import PostgresConnectionInfo

from migrations.migrate_versions_4_to_5 import migrate


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
        self.orca_buckets = ["orca_worm", "orca_versioned", "orca_special"]

    def tearDown(self):
        """
        Tear down test
        """
        self.config = None
        self.orca_buckets = None

    @patch("migrations.migrate_versions_4_to_5.migrate.sql.schema_versions_data_sql")
    @patch("migrations.migrate_versions_4_to_5.migrate.sql.reconcile_status_table_sql")
    @patch("migrations.migrate_versions_4_to_5.migrate.sql.reconcile_job_table_sql")
    @patch(
        "migrations.migrate_versions_4_to_5.migrate.sql.reconcile_s3_object_table_sql"
    )
    @patch(
        "migrations.migrate_versions_4_to_5.migrate.sql.reconcile_catalog_mismatch_report_table_sql"  # noqa: E501
    )
    @patch(
        "migrations.migrate_versions_4_to_5.migrate.sql.reconcile_orphan_report_table_sql"
    )
    @patch(
        "migrations.migrate_versions_4_to_5.migrate.sql.reconcile_phantom_report_table_sql"
    )
    @patch(
        "migrations.migrate_versions_4_to_5.migrate.sql.reconcile_s3_object_partition_sql"
    )
    @patch("migrations.migrate_versions_4_to_5.migrate.sql.create_extension")
    @patch("migrations.migrate_versions_4_to_5.migrate.create_engine")
    @patch("migrations.migrate_versions_4_to_5.migrate.create_admin_uri")
    @patch("migrations.migrate_versions_4_to_5.migrate.sql.text")
    def test_migrate_versions_4_to_5_happy_path(
        self,
        mock_text: MagicMock,
        mock_create_admin_uri: MagicMock,
        mock_create_engine: MagicMock,
        mock_extension: MagicMock,
        mock_reconcile_s3_object_partition_table: MagicMock,
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
        # Setup
        mock_reconcile_s3_object_partition_table_calls = [
            call(f"reconcile_s3_object_{self.orca_buckets[0]}"),
            call(f"reconcile_s3_object_{self.orca_buckets[1]}"),
            call(f"reconcile_s3_object_{self.orca_buckets[2]}"),
        ]

        for latest_version in [True, False]:
            with self.subTest(latest_version=latest_version):
                # Run the function
                migrate.migrate_versions_4_to_5(
                    self.config, latest_version, self.orca_buckets
                )

                # Check that all the functions were called the correct
                # number of times with the proper values
                mock_create_admin_uri.assert_called_once_with(
                    self.config, migrate.LOGGER, self.config.user_database_name
                )
                mock_create_engine.assert_called_once_with(
                    mock_create_admin_uri.return_value, future=True
                )
                mock_reconcile_status_table.assert_called_once()
                mock_reconcile_job_table.assert_called_once()
                mock_reconcile_s3_object_table.assert_called_once()
                mock_reconcile_s3_object_partition_table.assert_has_calls(
                    mock_reconcile_s3_object_partition_table_calls
                )
                mock_reconcile_catalog_mismatch_report_table.assert_called_once()
                mock_reconcile_orphan_report_table.assert_called_once()
                mock_reconcile_phantom_report_table.assert_called_once()
                mock_extension.assert_called_once()

                # Check the text calls occur and in the proper order
                text_calls = [
                    call("SET ROLE orca_dbo;"),
                    call("SET search_path TO orca, public;"),
                ]
                mock_text.assert_has_calls(text_calls, any_order=False)
                execution_order = [
                    call.execute(mock_extension()),
                    call.execute(mock_text("SET ROLE orca_dbo;")),
                    call.execute(mock_text("SET search_path TO orca, public;")),
                    call.execute(mock_reconcile_status_table()),
                    call.execute(mock_reconcile_job_table()),
                    call.execute(mock_reconcile_s3_object_table()),
                    call.execute(
                        mock_reconcile_s3_object_partition_table(
                            f"reconcile_s3_object_{self.orca_buckets[0]}"
                        ),  # Left hard-coded for backwards compatibility
                        {"bucket_name": self.orca_buckets[0]},
                    ),
                    call.execute(
                        mock_reconcile_s3_object_partition_table(
                            f"reconcile_s3_object_{self.orca_buckets[1]}"
                        ),
                        {"bucket_name": self.orca_buckets[1]},
                    ),
                    call.execute(
                        mock_reconcile_s3_object_partition_table(
                            f"reconcile_s3_object_{self.orca_buckets[2]}"
                        ),
                        {"bucket_name": self.orca_buckets[2]},
                    ),
                    call.execute(mock_reconcile_catalog_mismatch_report_table()),
                    call.execute(mock_reconcile_orphan_report_table()),
                    call.execute(mock_reconcile_phantom_report_table()),
                ]

                # Validate logic switch and set the execution order
                if latest_version:
                    mock_schema_versions_data.assert_called_once()
                    execution_order.append(call.execute(mock_schema_versions_data()))

                else:
                    mock_schema_versions_data.assert_not_called()

                # Add the commit at the end
                execution_order.append(call.commit())

                # Check that items were called in the proper order
                mock_conn_enter = mock_create_engine().connect().__enter__()
                mock_conn_enter.assert_has_calls(execution_order, any_order=False)

            # Reset the mocks for next loop
            mock_create_admin_uri.reset_mock()
            mock_create_engine.reset_mock()
            mock_reconcile_status_table.reset_mock()
            mock_reconcile_job_table.reset_mock()
            mock_reconcile_s3_object_table.reset_mock()
            mock_reconcile_catalog_mismatch_report_table.reset_mock()
            mock_reconcile_orphan_report_table.reset_mock()
            mock_reconcile_phantom_report_table.reset_mock()
            mock_reconcile_s3_object_partition_table.reset_mock()
            mock_extension.reset_mock()
            mock_schema_versions_data.reset_mock()
            mock_text.reset_mock()
