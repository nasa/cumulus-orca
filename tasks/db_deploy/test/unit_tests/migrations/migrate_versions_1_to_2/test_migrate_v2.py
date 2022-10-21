"""
Name: test_migrate_db_v2.py

Description: Runs unit tests for the migrations/migrate_versions_1_to_2/migrate.py
"""

import unittest
from unittest.mock import MagicMock, Mock, call, patch

from orca_shared.database.entities import PostgresConnectionInfo

from migrations.migrate_versions_1_to_2 import migrate


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

    @patch("migrations.migrate_versions_1_to_2.migrate.sql.schema_versions_data_sql")
    @patch("migrations.migrate_versions_1_to_2.migrate.sql.drop_druser_user_sql")
    @patch("migrations.migrate_versions_1_to_2.migrate.sql.drop_dbo_user_sql")
    @patch("migrations.migrate_versions_1_to_2.migrate.sql.drop_dr_role_sql")
    @patch("migrations.migrate_versions_1_to_2.migrate.sql.drop_drdbo_role_sql")
    @patch("migrations.migrate_versions_1_to_2.migrate.sql.drop_dr_schema_sql")
    @patch(
        "migrations.migrate_versions_1_to_2.migrate.sql.drop_request_status_table_sql"
    )
    @patch(
        "migrations.migrate_versions_1_to_2.migrate.sql.migrate_recovery_file_data_sql"
    )
    @patch(
        "migrations.migrate_versions_1_to_2.migrate.sql.migrate_recovery_job_data_sql"
    )
    @patch("migrations.migrate_versions_1_to_2.migrate.sql.recovery_status_data_sql")
    @patch("migrations.migrate_versions_1_to_2.migrate.sql.recovery_file_table_sql")
    @patch("migrations.migrate_versions_1_to_2.migrate.sql.recovery_job_table_sql")
    @patch("migrations.migrate_versions_1_to_2.migrate.sql.recovery_status_table_sql")
    @patch("migrations.migrate_versions_1_to_2.migrate.sql.schema_versions_table_sql")
    @patch("migrations.migrate_versions_1_to_2.migrate.sql.text")
    @patch("migrations.migrate_versions_1_to_2.migrate.sql.app_user_sql")
    @patch("migrations.migrate_versions_1_to_2.migrate.sql.orca_schema_sql")
    @patch("migrations.migrate_versions_1_to_2.migrate.sql.app_role_sql")
    @patch("migrations.migrate_versions_1_to_2.migrate.sql.dbo_role_sql")
    @patch("migrations.migrate_versions_1_to_2.migrate.create_engine")
    @patch("migrations.migrate_versions_1_to_2.migrate.create_admin_uri")
    def test_migrate_versions_1_to_2_happy_path(
        self,
        mock_create_admin_uri: MagicMock,
        mock_create_engine: MagicMock,
        mock_dbo_role_sql: MagicMock,
        mock_app_role_sql: MagicMock,
        mock_orca_schema_sql: MagicMock,
        mock_app_user_sql: MagicMock,
        mock_text: MagicMock,
        mock_schema_versions_table: MagicMock,
        mock_recovery_status_table: MagicMock,
        mock_recovery_job_table: MagicMock,
        mock_recovery_file_table: MagicMock,
        mock_recovery_status_data: MagicMock,
        mock_recovery_job_data: MagicMock,
        mock_recovery_file_data: MagicMock,
        mock_drop_request_status_table: MagicMock,
        mock_drop_dr_schema: MagicMock,
        mock_drop_drdbo_role: MagicMock,
        mock_drop_dr_role: MagicMock,
        mock_drop_dbo_user: MagicMock,
        mock_drop_druser_user: MagicMock,
        mock_schema_versions_data: MagicMock,
    ):
        """
        Tests the migrate_versions_1_to_2 function happy path
        """
        for latest_version in [True, False]:
            with self.subTest(latest_version=latest_version):
                # Run the function
                migrate.migrate_versions_1_to_2(self.config, latest_version)

                # Check that all the functions were called the correct
                # number of times with the proper values
                mock_create_admin_uri.assert_called_once_with(
                    self.config, migrate.LOGGER, self.config.user_database_name
                )
                mock_create_engine.assert_called_once_with(
                    mock_create_admin_uri.return_value, future=True
                )

                # First commit block
                # todo: here and elsewhere, checks are not sufficient.
                # assert_called_once should never be used, and all assert_has_calls
                # should be followed by a check on the call count.
                mock_dbo_role_sql.assert_called_once_with(
                    self.config.user_database_name, self.config.admin_username
                )
                mock_app_role_sql.assert_called_once()
                mock_orca_schema_sql.assert_called_once()
                mock_app_user_sql.assert_called_once_with(self.config.user_username)
                mock_schema_versions_table.assert_called_once()
                mock_recovery_status_table.assert_called_once()
                mock_recovery_job_table.assert_called_once()
                mock_recovery_file_table.assert_called_once()

                # Second commit block (migration)
                mock_recovery_status_data.assert_called_once()
                mock_recovery_job_data.assert_called_once()
                mock_recovery_file_data.assert_called_once()
                mock_drop_request_status_table.assert_called_once()
                mock_drop_dr_schema.assert_called_once()
                mock_drop_drdbo_role.assert_called_once()
                mock_drop_dr_role.assert_called_once()
                mock_drop_dbo_user.assert_called_once()
                mock_drop_druser_user.assert_called_once()

                # Check the text calls occur and in the proper order
                mock_text.assert_has_calls(
                    [
                        call("SET ROLE orca_dbo;"),
                        call("SET search_path TO orca, public;"),
                        call("RESET ROLE;"),
                        call("SET search_path TO orca, dr, public;"),
                        call("SET ROLE dbo;"),
                        call("RESET ROLE;"),
                    ]
                )
                self.assertEqual(6, mock_text.call_count)

                # Validate logic switch and set the execution order
                if latest_version:
                    mock_schema_versions_data.assert_called_once()
                    execution_order = [
                        call.execute(mock_dbo_role_sql()),
                        call.execute(mock_app_role_sql()),
                        call.execute(mock_orca_schema_sql()),
                        call.execute(
                            mock_app_user_sql(self.config.user_password),
                            [
                                {
                                    "user_name": self.config.user_username,
                                    "user_password": self.config.user_password,
                                }
                            ],
                        ),
                        call.execute(mock_text("SET ROLE orca_dbo;")),
                        call.execute(mock_text("SET search_path TO orca, public;")),
                        call.execute(mock_schema_versions_table()),
                        call.execute(mock_recovery_status_table()),
                        call.execute(mock_recovery_job_table()),
                        call.execute(mock_recovery_file_table()),
                        call.commit(),
                        call.execute(mock_text("RESET ROLE;")),
                        call.execute(mock_text("SET search_path TO orca, dr, public;")),
                        call.execute(mock_recovery_status_data()),
                        call.execute(mock_recovery_job_data()),
                        call.execute(mock_recovery_file_data()),
                        call.execute(mock_drop_request_status_table()),
                        call.execute(mock_text("SET ROLE dbo;")),
                        call.execute(mock_drop_dr_schema()),
                        call.execute(mock_text("RESET ROLE;")),
                        call.execute(mock_drop_drdbo_role()),
                        call.execute(mock_drop_dr_role()),
                        call.execute(mock_drop_dbo_user()),
                        call.execute(mock_drop_druser_user()),
                        call.execute(mock_schema_versions_data()),
                        call.commit(),
                    ]

                else:
                    mock_schema_versions_data.assert_not_called()
                    execution_order = [
                        call.execute(mock_dbo_role_sql()),
                        call.execute(mock_app_role_sql()),
                        call.execute(mock_orca_schema_sql()),
                        call.execute(
                            mock_app_user_sql(self.config.user_password),
                            [
                                {
                                    "user_name": self.config.user_username,
                                    "user_password": self.config.user_password,
                                }
                            ],
                        ),
                        call.execute(mock_text("SET ROLE orca_dbo;")),
                        call.execute(mock_text("SET search_path TO orca, public;")),
                        call.execute(mock_schema_versions_table()),
                        call.execute(mock_recovery_status_table()),
                        call.execute(mock_recovery_job_table()),
                        call.execute(mock_recovery_file_table()),
                        call.commit(),
                        call.execute(mock_text("RESET ROLE;")),
                        call.execute(mock_text("SET search_path TO orca, dr, public;")),
                        call.execute(mock_recovery_status_data()),
                        call.execute(mock_recovery_job_data()),
                        call.execute(mock_recovery_file_data()),
                        call.execute(mock_drop_request_status_table()),
                        call.execute(mock_text("SET ROLE dbo;")),
                        call.execute(mock_drop_dr_schema()),
                        call.execute(mock_text("RESET ROLE;")),
                        call.execute(mock_drop_drdbo_role()),
                        call.execute(mock_drop_dr_role()),
                        call.execute(mock_drop_dbo_user()),
                        call.execute(mock_drop_druser_user()),
                        call.commit(),
                    ]

                # Check that items were called in the proper order
                mock_conn_enter = mock_create_engine().connect().__enter__()
                mock_conn_enter.assert_has_calls(execution_order, any_order=False)
                self.assertEqual(len(execution_order), len(mock_conn_enter.method_calls))

                # Reset the mocks for next loop
                mock_create_admin_uri.reset_mock()
                mock_create_engine.reset_mock()
                mock_dbo_role_sql.reset_mock()
                mock_app_role_sql.reset_mock()
                mock_orca_schema_sql.reset_mock()
                mock_app_user_sql.reset_mock()
                mock_schema_versions_table.reset_mock()
                mock_recovery_status_table.reset_mock()
                mock_recovery_job_table.reset_mock()
                mock_recovery_file_table.reset_mock()
                mock_recovery_status_data.reset_mock()
                mock_recovery_job_data.reset_mock()
                mock_recovery_file_data.reset_mock()
                mock_drop_request_status_table.reset_mock()
                mock_drop_dr_schema.reset_mock()
                mock_drop_drdbo_role.reset_mock()
                mock_drop_dr_role.reset_mock()
                mock_drop_dbo_user.reset_mock()
                mock_drop_druser_user.reset_mock()
                mock_schema_versions_data.reset_mock()
                mock_text.reset_mock()

    def test_migrate_versions_1_to_2_exceptions(self) -> None:
        """
        Tests that an exception is thrown if the password is not set or is not
        a minimum of 12 characters,
        or if user_name is not set or is over 64 characters.
        """
        # nosec
        bad_passwords = [None, "", "abc123", "1234567890", "AbCdEfG1234"]
        message = "User password must be at least 12 characters long."

        for bad_password in bad_passwords:
            with self.subTest(bad_password=bad_password):
                with self.assertRaises(Exception) as cm:
                    migrate.migrate_versions_1_to_2(
                        PostgresConnectionInfo(
                            admin_database_name=Mock(), admin_username=Mock(),
                            admin_password=Mock(),
                            user_username="orcauser", user_password=bad_password,
                            user_database_name=Mock(), host=Mock(), port=Mock()
                        ),
                        Mock(),
                    )
                self.assertEqual(str(cm.exception), message)

        bad_user_names = [None, ""]
        message = "Username must be non-empty."
        for bad_user_name in bad_user_names:
            with self.subTest(bad_user_name=bad_user_name):
                with self.assertRaises(Exception) as cm:
                    migrate.migrate_versions_1_to_2(
                        PostgresConnectionInfo(  # nosec
                            admin_database_name=Mock(), admin_username=Mock(),
                            admin_password=Mock(),
                            user_username=bad_user_name, user_password="AbCdEfG12345",
                            user_database_name=Mock(), host=Mock(), port=Mock()
                        ),
                        Mock(),
                    )
                self.assertEqual(str(cm.exception), message)

        message = "Username must be less than 64 characters."
        bad_user_name = "".join("a" * 64)
        with self.subTest(bad_user_name=bad_user_name) as _:
            with self.assertRaises(Exception) as cm:
                migrate.migrate_versions_1_to_2(
                    PostgresConnectionInfo(  # nosec
                        admin_database_name=Mock(), admin_username=Mock(),
                        admin_password=Mock(),
                        user_username=bad_user_name, user_password="AbCdEfG12345",
                        user_database_name=Mock(), host=Mock(), port=Mock()
                    ),
                    Mock(),
                )
            self.assertEqual(str(cm.exception), message)
