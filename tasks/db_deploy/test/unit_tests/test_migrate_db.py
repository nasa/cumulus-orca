"""
Name: test_migrate_db.py

Description: Runs unit tests for the migrate_db.py library.
"""

import unittest
from unittest.mock import Mock, call, patch, MagicMock
import migrate_db, migrate_db_v2, migrate_db_v3, migrate_db_v4


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
            "user_password": "user123",
            "user_username": "user",
        }

    def tearDown(self):
        """
        Tear down test
        """
        self.config = None

    @patch("migrate_db_v2.migrate_versions_1_to_2")
    @patch("migrate_db_v3.migrate_versions_2_to_3")
    @patch("migrate_db_v4.migrate_versions_3_to_4")
    def test_perform_migration_happy_path(
            self,
            mock_migrate_v3_to_v4: MagicMock,
            mock_migrate_v2_to_v3: MagicMock,
            mock_migrate_v1_to_v2: MagicMock,
    ):
        """
        Tests the perform_migration function happy paths
        """
        for version in [1, 2, 3, 4, 5]:
            with self.subTest(version=version):
                migrate_db.perform_migration(version, self.config)

                # Make sure the proper migrations happens.
                # Note that for version 2 and 3 the function is not called so
                # overall through all the tests it is only called once.
                if version < 2:
                    mock_migrate_v1_to_v2.assert_called_once_with(self.config, False)
                else:
                    mock_migrate_v1_to_v2.assert_not_called()

                if version < 3:
                    mock_migrate_v2_to_v3.assert_called_once_with(self.config, False)
                else:
                    mock_migrate_v2_to_v3.assert_not_called()

                if version < 4:
                    mock_migrate_v3_to_v4.assert_called_once_with(self.config, True)
                else:
                    mock_migrate_v3_to_v4.assert_not_called()

                # Reset for next loop
                mock_migrate_v1_to_v2.reset_mock()
                mock_migrate_v2_to_v3.reset_mock()
                mock_migrate_v3_to_v4.reset_mock()

    @patch("migrate_db_v2.schema_versions_data_sql")
    @patch("migrate_db_v2.drop_druser_user_sql")
    @patch("migrate_db_v2.drop_dbo_user_sql")
    @patch("migrate_db_v2.drop_dr_role_sql")
    @patch("migrate_db_v2.drop_drdbo_role_sql")
    @patch("migrate_db_v2.drop_dr_schema_sql")
    @patch("migrate_db_v2.drop_request_status_table_sql")
    @patch("migrate_db_v2.migrate_recovery_file_data_sql")
    @patch("migrate_db_v2.migrate_recovery_job_data_sql")
    @patch("migrate_db_v2.recovery_status_data_sql")
    @patch("migrate_db_v2.recovery_file_table_sql")
    @patch("migrate_db_v2.recovery_job_table_sql")
    @patch("migrate_db_v2.recovery_status_table_sql")
    @patch("migrate_db_v2.schema_versions_table_sql")
    @patch("migrate_db_v2.text")
    @patch("migrate_db_v2.app_user_sql")
    @patch("migrate_db_v2.orca_schema_sql")
    @patch("migrate_db_v2.app_role_sql")
    @patch("migrate_db_v2.dbo_role_sql")
    @patch("migrate_db_v2.get_admin_connection")
    def test_migrate_versions_1_to_2_happy_path(
            self,
            mock_connection: MagicMock,
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
                # Setup the mock object that conn.execute is a part of in
                # the connection with block
                mock_conn_enter = mock_connection().connect().__enter__()

                # Run the function
                migrate_db_v2.migrate_versions_1_to_2(self.config, latest_version)

                # Check that all of the functions were called the correct
                # number of times with the proper values
                mock_connection.assert_any_call(
                    self.config, self.config["user_database"]
                )

                # First commit block
                mock_dbo_role_sql.assert_called_once()
                mock_app_role_sql.assert_called_once()
                mock_orca_schema_sql.assert_called_once()
                mock_app_user_sql.assert_called_once_with(self.config["user_password"])
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
                text_calls = [
                    call("SET ROLE orca_dbo;"),
                    call("SET search_path TO orca, public;"),
                    call("RESET ROLE;"),
                    call("SET search_path TO orca, dr, public;"),
                    call("SET ROLE dbo;"),
                    call("RESET ROLE;"),
                ]
                mock_text.assert_has_calls(text_calls, any_order=False)

                # Validate logic switch and set the execution order
                if latest_version:
                    mock_schema_versions_data.assert_called_once()
                    execution_order = [
                        call.execute(mock_dbo_role_sql()),
                        call.execute(mock_app_role_sql()),
                        call.execute(mock_orca_schema_sql()),
                        call.execute(mock_app_user_sql(self.config["user_password"])),
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
                        call.execute(mock_app_user_sql(self.config["user_password"])),
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
                mock_conn_enter.assert_has_calls(execution_order, any_order=False)

                # Reset the mocks for next loop
                mock_connection.reset_mock()
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

    @patch("migrate_db_v3.text")
    @patch("migrate_db_v3.schema_versions_data_sql")
    @patch("migrate_db_v3.add_multipart_chunksize_sql")
    @patch("migrate_db_v3.get_admin_connection")
    def test_migrate_versions_2_to_3_happy_path(
            self,
            mock_connection: MagicMock,
            mock_add_multipart_chunksize_sql: MagicMock,
            mock_schema_versions_data: MagicMock,
            mock_text: MagicMock
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
                migrate_db_v3.migrate_versions_2_to_3(self.config, latest_version)

                # Check that all of the functions were called the correct
                # number of times with the proper values
                mock_connection.assert_any_call(self.config, self.config["user_database"])

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

    @patch("migrate_db_v4.schema_versions_data_sql")
    @patch("migrate_db_v4.providers_table_sql")
    @patch("migrate_db_v4.collections_table_sql")
    @patch("migrate_db_v4.granules_table_sql")
    @patch("migrate_db_v4.files_table_sql")
    @patch("migrate_db_v4.get_admin_connection")
    @patch("migrate_db_v4.text")
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
