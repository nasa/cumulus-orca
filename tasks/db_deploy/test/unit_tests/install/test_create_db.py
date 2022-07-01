"""
Name: test_create_db.py

Description: Runs unit tests for the create_db.py library.
"""

import unittest
from unittest.mock import MagicMock, Mock, call, patch

from install import create_db


class TestCreateDatabaseLibraries(unittest.TestCase):
    """
    Test the various functions in the create_db library.
    """

    def setUp(self):
        """
        Set up test.
        """
        # todo: Use randomized values on a per-test basis.
        self.config = {
            "admin_database": "admin_db",
            "admin_password": "admin123",
            "admin_username": "admin",
            "host": "aws.postgresrds.host",
            "port": 5432,
            "user_database": "user_db",
            "user_password": "pass56789012",
            "user_username": "user56789012",
        }

        self.mock_connection = MagicMock()
        self.orca_buckets = ["orca_worm", "orca_versioned", "orca_special"]

    def tearDown(self):
        """
        Tear down test
        """
        self.config = None
        self.mock_connection = None
        self.orca_buckets = None

    @patch("install.create_db.create_recovery_objects")
    @patch("install.create_db.create_metadata_objects")
    @patch("install.create_db.create_inventory_objects")
    @patch("install.create_db.create_internal_reconciliation_objects")
    @patch("install.create_db.set_search_path_and_role")
    @patch("install.create_db.create_app_schema_role_users")
    @patch("install.create_db.get_admin_connection")
    def test_create_fresh_orca_install_happy_path(
        self,
        mock_connection: MagicMock,
        mock_create_app_schema_roles: MagicMock,
        mock_set_search_path_role: MagicMock,
        mock_create_internal_reconciliation_objects: MagicMock,
        mock_create_inventory_objects: MagicMock,
        mock_create_metadata: MagicMock,
        mock_create_recovery: MagicMock,
    ):
        """
        Tests normal happy path of create_fresh_orca_install function.
        """
        # Call
        create_db.create_fresh_orca_install(self.config, self.orca_buckets)

        mock_conn_enter = mock_connection().connect().__enter__()

        # Check
        mock_create_app_schema_roles.assert_called_once_with(
            mock_conn_enter,
            self.config["user_username"],
            self.config["user_password"],
            self.config["user_database"],
            self.config["admin_username"],
        )
        mock_set_search_path_role.assert_called_once_with(mock_conn_enter)
        mock_create_inventory_objects.assert_called_once_with(mock_conn_enter)
        mock_create_metadata.assert_called_once_with(mock_conn_enter)
        mock_create_recovery.assert_called_once_with(mock_conn_enter)
        mock_create_internal_reconciliation_objects.assert_called_once_with(
            mock_conn_enter, self.orca_buckets
        )

        # Check that commit was called at the end. In this case it is position
        # 4 of the calls (initial call with config, connection call, enter of
        # with loop, commit, then exiting calls).
        mock_call_commit = mock_connection.mock_calls[3]
        mock_commit = call().connect().__enter__().commit()
        self.assertEqual(mock_call_commit, mock_commit)

    @patch("install.orca_sql.app_database_comment_sql")
    @patch("install.orca_sql.app_database_sql")
    @patch("install.orca_sql.commit_sql")
    @patch("install.create_db.get_admin_connection")
    def test_create_database_happy_path(
        self,
        mock_connection: MagicMock,
        mock_commit_sql: MagicMock,
        mock_app_database_sql: MagicMock,
        mock_app_database_comment_sql: MagicMock,
    ):
        """
        Tests normal happy path of create_database function.
        """
        create_db.create_database(self.config)

        mock_app_database_sql.assert_called_once_with(
            self.config["user_database"], self.config["admin_username"]
        )
        mock_connection().connect().__enter__().execute.assert_has_calls(
            [
                call(mock_commit_sql.return_value),
                call(mock_app_database_sql.return_value),
                call(mock_app_database_comment_sql.return_value),
            ],
            any_order=True,
        )

    @patch("install.create_db.sql.create_extension")
    @patch("install.create_db.sql.app_user_sql")
    @patch("install.create_db.sql.orca_schema_sql")
    @patch("install.create_db.sql.app_role_sql")
    @patch("install.create_db.sql.dbo_role_sql")
    def test_create_app_schema_role_users_happy_path(
        self,
        mock_dbo_role_sql: MagicMock,
        mock_app_role_sql: MagicMock,
        mock_schema_sql: MagicMock,
        mock_user_sql: MagicMock,
        mock_extension_sql: MagicMock,
    ):
        """
        Tests happy path of create_app_schema_role_users function.
        """
        create_db.create_app_schema_role_users(
            self.mock_connection,
            self.config["user_username"],
            self.config["user_password"],
            self.config["user_database"],
            self.config["admin_username"],
        )

        # Check that SQL called properly
        mock_dbo_role_sql.assert_called_once_with(
            self.config["user_database"], self.config["admin_username"]
        )
        mock_app_role_sql.assert_called_once()
        mock_schema_sql.assert_called_once()
        mock_user_sql.assert_called_once_with(
            self.config["user_username"],
        )
        mock_extension_sql.assert_called_once()

        # Check SQL called in proper order
        # todo: here and elsewhere, checks are not sufficient. assert_called_once should never be used, and all assert_has_calls should be followed by a check on the call count.
        self.mock_connection.assert_has_calls(
            [
                call.execute(mock_dbo_role_sql()),
                call.execute(mock_app_role_sql()),
                call.execute(mock_schema_sql()),
                call.execute(
                    mock_user_sql(self.config["user_password"]),
                    [
                        {
                            "user_name": self.config["user_username"],
                            "user_password": self.config["user_password"],
                        }
                    ],
                ),
                call.execute(mock_extension_sql()),
            ]
        )

    def test_create_app_schema_role_users_exceptions(self) -> None:
        """
        Tests that an exception is thrown if the password is not set or is not
        a minimum of 12 characters,
        or if user_name is not set or is over 64 characters.
        """
        bad_passwords = [None, "", "abc123", "1234567890", "AbCdEfG1234"]
        message = "User password must be at least 12 characters long."

        for bad_password in bad_passwords:
            with self.subTest(bad_password=bad_password):
                with self.assertRaises(Exception) as cm:
                    create_db.create_app_schema_role_users(
                        Mock(), "orcauser", bad_password, Mock(), Mock()
                    )
                self.assertEqual(str(cm.exception), message)

        bad_user_names = [None, ""]
        message = "Username must be non-empty."
        for bad_user_name in bad_user_names:
            with self.subTest(bad_user_name=bad_user_name):
                with self.assertRaises(Exception) as cm:
                    create_db.create_app_schema_role_users(
                        Mock(), bad_user_name, "AbCdEfG12345", Mock(), Mock()
                    )
                self.assertEqual(str(cm.exception), message)

        message = "Username must be less than 64 characters."
        bad_user_name = "".join("a" * 64)
        with self.subTest(bad_user_name=bad_user_name) as cm:
            with self.assertRaises(Exception) as cm:
                create_db.create_app_schema_role_users(
                    Mock(), bad_user_name, "AbCdEfG12345", Mock(), Mock()
                )
            self.assertEqual(str(cm.exception), message)

    @patch("install.create_db.sql.text")
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

    @patch("install.create_db.sql.schema_versions_data_sql")
    @patch("install.create_db.sql.schema_versions_table_sql")
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

    @patch("install.create_db.sql.recovery_file_table_sql")
    @patch("install.create_db.sql.recovery_job_table_sql")
    @patch("install.create_db.sql.recovery_status_data_sql")
    @patch("install.create_db.sql.recovery_status_table_sql")
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

    @patch("install.create_db.sql.providers_table_sql")
    @patch("install.create_db.sql.collections_table_sql")
    @patch("install.create_db.sql.granules_table_sql")
    @patch("install.create_db.sql.files_table_sql")
    def test_create_inventory_objects(
        self,
        mock_files_table: MagicMock,
        mock_granules_table: MagicMock,
        mock_collections_table: MagicMock,
        mock_providers_table: MagicMock,
    ):
        """
        Tests happy path of the create_inventory_objects function
        """
        create_db.create_inventory_objects(self.mock_connection)

        # Check that the SQL calls were made
        mock_providers_table.assert_called_once()
        mock_collections_table.assert_called_once()
        mock_granules_table.assert_called_once()
        mock_files_table.assert_called_once()

        # Check that they were called in the proper order
        execution_order = [
            call.execute(mock_providers_table()),
            call.execute(mock_collections_table()),
            call.execute(mock_granules_table()),
            call.execute(mock_files_table()),
        ]

        self.assertEqual(self.mock_connection.mock_calls, execution_order)

    @patch("install.create_db.sql.reconcile_status_table_sql")
    @patch("install.create_db.sql.reconcile_job_table_sql")
    @patch("install.create_db.sql.reconcile_s3_object_table_sql")
    @patch("install.create_db.sql.reconcile_catalog_mismatch_report_table_sql")
    @patch("install.create_db.sql.reconcile_orphan_report_table_sql")
    @patch("install.create_db.sql.reconcile_phantom_report_table_sql")
    @patch("install.create_db.sql.reconcile_s3_object_partition_sql")
    @patch("install.create_db.sql.create_extension")
    def test_create_internal_reconciliation_objects_happy_path(
        self,
        mock_extension: MagicMock,
        mock_reconcile_s3_object_partition_table: MagicMock,
        mock_reconcile_phantom_report_table: MagicMock,
        mock_reconcile_orphan_report_table: MagicMock,
        mock_reconcile_catalog_mismatch_report_table: MagicMock,
        mock_reconcile_s3_object_table: MagicMock,
        mock_reconcile_job_table: MagicMock,
        mock_reconcile_status_table: MagicMock,
    ):
        """
        Tests happy path of the create_internal_reconciliation_objects function
        """
        create_db.create_internal_reconciliation_objects(
            self.mock_connection, self.orca_buckets
        )
        mock_reconcile_s3_object_partition_table_calls = [
            call(f"reconcile_s3_object_{self.orca_buckets[0]}"),
            call(f"reconcile_s3_object_{self.orca_buckets[1]}"),
            call(f"reconcile_s3_object_{self.orca_buckets[2]}"),
        ]

        # Check that the SQL calls were made
        mock_reconcile_status_table.assert_called_once()
        mock_reconcile_job_table.assert_called_once()
        mock_reconcile_s3_object_table.assert_called_once()
        mock_reconcile_s3_object_partition_table.assert_has_calls(
            mock_reconcile_s3_object_partition_table_calls
        )
        mock_reconcile_catalog_mismatch_report_table.assert_called_once()
        mock_reconcile_orphan_report_table.assert_called_once()
        mock_reconcile_phantom_report_table.assert_called_once()

        # Check that they were called in the proper order
        execution_order = [
            call.execute(mock_reconcile_status_table()),
            call.execute(mock_reconcile_job_table()),
            call.execute(mock_reconcile_s3_object_table()),
            call.execute(
                mock_reconcile_s3_object_partition_table(
                    f"reconcile_s3_object_{self.orca_buckets[0]}"
                ),
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

        self.assertListEqual(self.mock_connection.mock_calls, execution_order)
