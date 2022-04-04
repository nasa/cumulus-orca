"""
Name: test_get_current_archive_list.py

Description:  Unit tests for test_get_current_archive_list.py.
"""
import copy
import datetime
import json
import os
import random
import unittest
import uuid
from unittest.mock import MagicMock, Mock, call, patch

from orca_shared.reconciliation import OrcaStatus

import get_current_archive_list


class TestGetCurrentArchiveList(
    unittest.TestCase
):  # pylint: disable-msg=too-many-instance-attributes
    """
    TestGetCurrentArchiveList.
    """

    @patch("get_current_archive_list.update_job_with_s3_inventory_in_postgres")
    @patch("get_current_archive_list.truncate_s3_partition")
    @patch("get_current_archive_list.get_manifest")
    @patch("get_current_archive_list.create_job")
    @patch("orca_shared.database.shared_db.get_admin_connection")
    @patch("orca_shared.database.shared_db.get_user_connection")
    def test_task_happy_path(
        self,
        mock_get_user_connection: MagicMock,
        mock_get_admin_connection: MagicMock,
        mock_create_job: MagicMock,
        mock_get_manifest: MagicMock,
        mock_truncate_s3_partition: MagicMock,
        mock_update_job_with_s3_inventory_in_postgres: MagicMock,
    ):
        """
        Happy path that gets the manifest and triggers the various DB tasks.
        """
        mock_s3_access_key = Mock()
        mock_s3_secret_key = Mock()
        mock_user_database = Mock()
        manifest_key_path = (
            uuid.uuid4().__str__() + "/" + uuid.uuid4().__str__() + "/manifest.json"
        )
        mock_report_bucket_name = Mock()
        mock_report_bucket_aws_region = Mock()
        db_connect_info = {"user_database": mock_user_database}
        mock_orca_archive_location = Mock()
        mock_manifest_file_schema = Mock()
        manifest_file_keys = [Mock(), Mock()]
        mock_get_manifest.return_value = {
            get_current_archive_list.MANIFEST_SOURCE_BUCKET_KEY: mock_orca_archive_location,
            get_current_archive_list.MANIFEST_FILES_KEY: [
                {get_current_archive_list.FILES_KEY_KEY: manifest_file_key}
                for manifest_file_key in manifest_file_keys
            ],
            get_current_archive_list.MANIFEST_FILE_SCHEMA_KEY: mock_manifest_file_schema,
            get_current_archive_list.MANIFEST_CREATION_TIMESTAMP_KEY: "1643760000000",
        }
        mock_job_id = Mock()
        mock_create_job.return_value = mock_job_id

        result = get_current_archive_list.task(
            mock_report_bucket_aws_region,
            mock_report_bucket_name,
            manifest_key_path,
            mock_s3_access_key,
            mock_s3_secret_key,
            copy.copy(db_connect_info),
        )

        mock_get_manifest.assert_called_once_with(
            manifest_key_path, mock_report_bucket_name, mock_report_bucket_aws_region
        )
        mock_get_user_connection.assert_called_once_with(db_connect_info)
        mock_get_admin_connection.assert_called_once_with(
            db_connect_info, mock_user_database
        )
        mock_create_job.assert_called_once_with(
            mock_orca_archive_location,
            datetime.datetime(2022, 2, 2, 0, 0, 0, tzinfo=datetime.timezone.utc),
            mock_get_user_connection.return_value,
        )
        mock_truncate_s3_partition.assert_called_once_with(
            mock_orca_archive_location, mock_get_admin_connection.return_value
        )
        mock_update_job_with_s3_inventory_in_postgres.assert_called_once_with(
            mock_s3_access_key,
            mock_s3_secret_key,
            mock_report_bucket_name,
            mock_report_bucket_aws_region,
            manifest_file_keys,
            mock_manifest_file_schema,
            mock_job_id,
            mock_get_admin_connection.return_value,
        )

        self.assertEqual(
            {
                get_current_archive_list.OUTPUT_JOB_ID_KEY: mock_job_id,
                get_current_archive_list.OUTPUT_ORCA_ARCHIVE_LOCATION_KEY: mock_orca_archive_location,
            },
            result,
        )

    @patch("get_current_archive_list.LOGGER")
    @patch("get_current_archive_list.update_job_with_s3_inventory_in_postgres")
    @patch("get_current_archive_list.truncate_s3_partition")
    @patch("get_current_archive_list.get_manifest")
    @patch("get_current_archive_list.create_job")
    @patch("orca_shared.database.shared_db.get_admin_connection")
    @patch("orca_shared.database.shared_db.get_user_connection")
    def test_task_non_manifest_ignored(
        self,
        mock_get_user_connection: MagicMock,
        mock_get_admin_connection: MagicMock,
        mock_create_job: MagicMock,
        mock_get_manifest: MagicMock,
        mock_truncate_s3_partition: MagicMock,
        mock_update_job_with_s3_inventory_in_postgres: MagicMock,
        mock_logger: MagicMock,
    ):
        """
        Only manifest.json files should trigger deeper processing. Otherwise, return {job_id: None}
        """
        mock_s3_access_key = Mock()
        mock_s3_secret_key = Mock()
        mock_user_database = Mock()
        manifest_key_path = (
            uuid.uuid4().__str__() + "/" + uuid.uuid4().__str__() + "/blah.json"
        )
        mock_report_bucket_name = Mock()
        mock_report_bucket_aws_region = Mock()
        db_connect_info = {"user_database": mock_user_database}

        with self.assertRaises(Exception) as cm:
            get_current_archive_list.task(
                mock_report_bucket_aws_region,
                mock_report_bucket_name,
                manifest_key_path,
                mock_s3_access_key,
                mock_s3_secret_key,
                copy.copy(db_connect_info),
            )
        self.assertEqual(
            "Illegal file 'blah.json'. Must be 'manifest.json'", str(cm.exception)
        )
        mock_logger.error.assert_called_once_with(
            "Illegal file 'blah.json'. Must be 'manifest.json'"
        )

        mock_get_manifest.assert_not_called()
        mock_get_user_connection.assert_not_called()
        mock_get_admin_connection.assert_not_called()
        mock_create_job.assert_not_called()
        mock_truncate_s3_partition.assert_not_called()
        mock_update_job_with_s3_inventory_in_postgres.assert_not_called()

    @patch("get_current_archive_list.LOGGER")
    @patch("get_current_archive_list.update_job")
    @patch("get_current_archive_list.update_job_with_s3_inventory_in_postgres")
    @patch("get_current_archive_list.truncate_s3_partition")
    @patch("get_current_archive_list.get_manifest")
    @patch("get_current_archive_list.create_job")
    @patch("orca_shared.database.shared_db.get_admin_connection")
    @patch("orca_shared.database.shared_db.get_user_connection")
    def test_task_error_posted_as_status_update(
        self,
        mock_get_user_connection: MagicMock,
        mock_get_admin_connection: MagicMock,
        mock_create_job: MagicMock,
        mock_get_manifest: MagicMock,
        mock_truncate_s3_partition: MagicMock,
        mock_update_job_with_s3_inventory_in_postgres: MagicMock,
        mock_update_job: MagicMock,
        mock_logger: MagicMock,
    ):
        """
        Errors should be written to status entries.
        """
        expected_exception = Exception(uuid.uuid4().__str__())

        mock_s3_access_key = Mock()
        mock_s3_secret_key = Mock()
        mock_user_database = Mock()
        manifest_key_path = (
            uuid.uuid4().__str__() + "/" + uuid.uuid4().__str__() + "/manifest.json"
        )
        mock_report_bucket_name = Mock()
        mock_report_bucket_aws_region = Mock()
        db_connect_info = {"user_database": mock_user_database}
        mock_orca_archive_location = Mock()
        mock_manifest_file_schema = Mock()
        manifest_file_keys = [Mock(), Mock()]
        mock_get_manifest.return_value = {
            get_current_archive_list.MANIFEST_SOURCE_BUCKET_KEY: mock_orca_archive_location,
            get_current_archive_list.MANIFEST_FILES_KEY: [
                {get_current_archive_list.FILES_KEY_KEY: manifest_file_key}
                for manifest_file_key in manifest_file_keys
            ],
            get_current_archive_list.MANIFEST_FILE_SCHEMA_KEY: mock_manifest_file_schema,
            get_current_archive_list.MANIFEST_CREATION_TIMESTAMP_KEY: "1643760000000",
        }
        mock_job_id = Mock()
        mock_create_job.return_value = mock_job_id
        mock_truncate_s3_partition.side_effect = expected_exception

        with self.assertRaises(Exception) as cm:
            get_current_archive_list.task(
                mock_report_bucket_aws_region,
                mock_report_bucket_name,
                manifest_key_path,
                mock_s3_access_key,
                mock_s3_secret_key,
                copy.copy(db_connect_info),
            )
        self.assertEqual(expected_exception, cm.exception)

        mock_get_manifest.assert_called_once_with(
            manifest_key_path, mock_report_bucket_name, mock_report_bucket_aws_region
        )
        mock_get_user_connection.assert_called_once_with(db_connect_info)
        mock_get_admin_connection.assert_called_once_with(
            db_connect_info, mock_user_database
        )
        mock_create_job.assert_called_once_with(
            mock_orca_archive_location,
            datetime.datetime(2022, 2, 2, 0, 0, 0, tzinfo=datetime.timezone.utc),
            mock_get_user_connection.return_value,
        )
        mock_truncate_s3_partition.assert_called_once_with(
            mock_orca_archive_location, mock_get_admin_connection.return_value
        )
        mock_update_job_with_s3_inventory_in_postgres.assert_not_called()

        mock_logger.error.assert_called_once_with(
            f"Encountered a fatal error: {expected_exception}"
        )
        mock_update_job.assert_called_once_with(
            mock_job_id,
            OrcaStatus.ERROR,
            str(expected_exception),
            mock_get_user_connection.return_value,
        )

    @patch("json.loads")
    @patch("boto3.client")
    def test_get_manifest_happy_path(
        self, mock_client: MagicMock, mock_json_load: MagicMock
    ):
        """
        Happy path for getting and parsing manifest.
        """
        mock_file_data = Mock()
        mock_file_body = Mock()
        mock_file_body.read.return_value = mock_file_data
        mock_s3_client = mock_client.return_value
        mock_s3_client.get_object.return_value = {"Body": mock_file_body}
        manifest_key_path = Mock()
        report_bucket_name = Mock()
        report_bucket_region = Mock()

        result = get_current_archive_list.get_manifest(
            manifest_key_path, report_bucket_name, report_bucket_region
        )

        mock_client.assert_called_once_with("s3", region_name=report_bucket_region)
        mock_s3_client.get_object.assert_called_once_with(
            Bucket=report_bucket_name, Key=manifest_key_path
        )
        mock_file_body.read.assert_called_once_with()
        mock_file_data.decode.assert_called_once_with("utf-8")
        mock_json_load.assert_called_once_with(mock_file_data.decode.return_value)
        self.assertEqual(mock_json_load.return_value, result)

    @patch("get_current_archive_list.create_job_sql")
    def test_create_job_happy_path(
        self,
        mock_create_job_sql: MagicMock,
    ):
        """
        Happy path for creating job entry.
        """
        mock_orca_archive_location = Mock()
        mock_inventory_creation_time = Mock()
        mock_job_id = Mock()
        returned_rows = Mock()
        returned_rows.fetchone = Mock(return_value={"id": mock_job_id})
        mock_execute = Mock(return_value=returned_rows)
        mock_connection = Mock()
        mock_connection.execute = mock_execute
        mock_exit = Mock(return_value=False)
        mock_enter = Mock()
        mock_enter.__enter__ = Mock(return_value=mock_connection)
        mock_enter.__exit__ = mock_exit
        mock_engine = Mock()
        mock_engine.begin = Mock(return_value=mock_enter)

        result = get_current_archive_list.create_job(
            mock_orca_archive_location, mock_inventory_creation_time, mock_engine
        )

        mock_enter.__enter__.assert_called_once_with()
        mock_execute.assert_called_once_with(
            mock_create_job_sql.return_value,
            [
                {
                    "orca_archive_location": mock_orca_archive_location,
                    "inventory_creation_time": mock_inventory_creation_time,
                    "status_id": OrcaStatus.GETTING_S3_LIST.value,
                    "start_time": unittest.mock.ANY,
                    "last_update": unittest.mock.ANY,
                    "end_time": None,
                    "error_message": None,
                }
            ],
        )
        mock_exit.assert_called_once_with(None, None, None)
        mock_create_job_sql.assert_called_once_with()
        self.assertEqual(
            mock_job_id,
            result,
        )

    @patch("get_current_archive_list.LOGGER")
    @patch("get_current_archive_list.create_job_sql")
    def test_create_job_error_logged_and_raised(
        self, mock_create_job_sql: MagicMock, mock_logger: MagicMock
    ):
        """
        Exceptions from Postgres should bubble up.
        """
        expected_exception = Exception(uuid.uuid4().__str__())

        mock_orca_archive_location = Mock()
        mock_inventory_creation_time = Mock()
        mock_execute = Mock(side_effect=expected_exception)
        mock_connection = Mock()
        mock_connection.execute = mock_execute
        mock_exit = Mock(return_value=False)
        mock_enter = Mock()
        mock_enter.__enter__ = Mock(return_value=mock_connection)
        mock_enter.__exit__ = mock_exit
        mock_engine = Mock()
        mock_engine.begin = Mock(return_value=mock_enter)

        with self.assertRaises(Exception) as cm:
            get_current_archive_list.create_job(
                mock_orca_archive_location, mock_inventory_creation_time, mock_engine
            )
        self.assertEqual(expected_exception, cm.exception)

        mock_enter.__enter__.assert_called_once_with()
        mock_execute.assert_called_once_with(
            mock_create_job_sql.return_value,
            [
                {
                    "orca_archive_location": mock_orca_archive_location,
                    "inventory_creation_time": mock_inventory_creation_time,
                    "status_id": OrcaStatus.GETTING_S3_LIST.value,
                    "start_time": unittest.mock.ANY,
                    "last_update": unittest.mock.ANY,
                    "end_time": None,
                    "error_message": None,
                }
            ],
        )
        mock_exit.assert_called_once_with(
            Exception, expected_exception, unittest.mock.ANY
        )
        mock_create_job_sql.assert_called_once_with()
        mock_logger.error.assert_called_once_with(
            f"Error while creating job: {expected_exception}"
        )

    @patch("get_current_archive_list.get_partition_name_from_bucket_name")
    @patch("get_current_archive_list.truncate_s3_partition_sql")
    def test_truncate_s3_partition_happy_path(
        self,
        mock_truncate_s3_partition_sql: MagicMock,
        mock_get_partition_name_from_bucket_name: MagicMock,
    ):
        """
        Happy path for truncating the partition in postgres
        """
        mock_orca_archive_location = Mock()
        mock_execute = Mock()
        mock_connection = Mock()
        mock_connection.execute = mock_execute
        mock_exit = Mock(return_value=False)
        mock_enter = Mock()
        mock_enter.__enter__ = Mock(return_value=mock_connection)
        mock_enter.__exit__ = mock_exit
        mock_engine = Mock()
        mock_engine.begin = Mock(return_value=mock_enter)

        get_current_archive_list.truncate_s3_partition(
            mock_orca_archive_location, mock_engine
        )

        mock_get_partition_name_from_bucket_name.assert_called_once_with(
            mock_orca_archive_location
        )
        mock_enter.__enter__.assert_called_once_with()
        mock_truncate_s3_partition_sql.assert_called_once_with(
            mock_get_partition_name_from_bucket_name.return_value
        )
        mock_execute.assert_called_once_with(
            mock_truncate_s3_partition_sql.return_value,
            [{}],
        )
        mock_exit.assert_called_once_with(None, None, None)

    @patch("get_current_archive_list.LOGGER")
    @patch("get_current_archive_list.get_partition_name_from_bucket_name")
    @patch("get_current_archive_list.truncate_s3_partition_sql")
    def test_truncate_s3_partition_error_logged_and_raised(
        self,
        mock_truncate_s3_partition_sql: MagicMock,
        mock_get_partition_name_from_bucket_name: MagicMock,
        mock_logger: MagicMock,
    ):
        """
        Exceptions from Postgres should bubble up.
        """
        expected_exception = Exception(uuid.uuid4().__str__())

        mock_orca_archive_location = Mock()
        mock_execute = Mock(side_effect=expected_exception)
        mock_connection = Mock()
        mock_connection.execute = mock_execute
        mock_exit = Mock(return_value=False)
        mock_enter = Mock()
        mock_enter.__enter__ = Mock(return_value=mock_connection)
        mock_enter.__exit__ = mock_exit
        mock_engine = Mock()
        mock_engine.begin = Mock(return_value=mock_enter)

        with self.assertRaises(Exception) as cm:
            get_current_archive_list.truncate_s3_partition(
                mock_orca_archive_location, mock_engine
            )
        self.assertEqual(expected_exception, cm.exception)

        mock_get_partition_name_from_bucket_name.assert_called_once_with(
            mock_orca_archive_location
        )
        mock_enter.__enter__.assert_called_once_with()
        mock_truncate_s3_partition_sql.assert_called_once_with(
            mock_get_partition_name_from_bucket_name.return_value
        )
        mock_execute.assert_called_once_with(
            mock_truncate_s3_partition_sql.return_value,
            [{}],
        )
        mock_exit.assert_called_once_with(
            Exception, expected_exception, unittest.mock.ANY
        )
        mock_logger.error.assert_called_once_with(
            f"Error while truncating bucket '{mock_orca_archive_location}': {expected_exception}"
        )

    @patch("orca_shared.reconciliation.shared_reconciliation.update_job")
    @patch("get_current_archive_list.translate_s3_import_to_partitioned_data_sql")
    @patch("get_current_archive_list.trigger_csv_load_from_s3_sql")
    @patch("get_current_archive_list.add_metadata_to_gzip")
    @patch("get_current_archive_list.create_temporary_table_sql")
    @patch("get_current_archive_list.generate_temporary_s3_column_list")
    def test_update_job_with_s3_inventory_in_postgres_happy_path(
        self,
        mock_generate_temporary_s3_column_list: MagicMock,
        mock_create_temporary_table_sql: MagicMock,
        mock_add_metadata_to_gzip: MagicMock,
        mock_trigger_csv_load_from_s3_sql: MagicMock,
        mock_translate_s3_import_to_partitioned_data_sql: MagicMock,
        mock_update_job: MagicMock,
    ):
        """
        Happy path for pulling s3 inventory csv into postgres.
        Should perform each operation in a single transaction.
        """
        mock_s3_access_key = Mock()
        mock_s3_secret_key = Mock()
        mock_report_bucket_name = Mock()
        mock_report_bucket_region = Mock()
        mock_csv_key_paths = [
            uuid.uuid4().__str__() + ".csv.gz",
            uuid.uuid4().__str__() + ".csv.gz",
        ]
        mock_manifest_file_schema = Mock()
        mock_job_id = Mock()
        mock_execute = Mock()
        mock_connection = Mock()
        mock_connection.execute = mock_execute
        mock_exit = Mock(return_value=False)
        mock_enter = Mock()
        mock_enter.__enter__ = Mock(return_value=mock_connection)
        mock_enter.__exit__ = mock_exit
        mock_engine = Mock()
        mock_engine.begin = Mock(return_value=mock_enter)

        get_current_archive_list.update_job_with_s3_inventory_in_postgres(
            mock_s3_access_key,
            mock_s3_secret_key,
            mock_report_bucket_name,
            mock_report_bucket_region,
            mock_csv_key_paths,
            mock_manifest_file_schema,
            mock_job_id,
            mock_engine,
        )

        mock_generate_temporary_s3_column_list.assert_called_once_with(
            mock_manifest_file_schema
        )
        mock_enter.__enter__.assert_called_once_with()
        mock_add_metadata_to_gzip.assert_has_calls(
            [
                call(mock_report_bucket_name, mock_csv_key_path)
                for mock_csv_key_path in mock_csv_key_paths
            ]
        )
        self.assertEqual(len(mock_csv_key_paths), mock_add_metadata_to_gzip.call_count)
        mock_trigger_csv_load_from_s3_sql.assert_has_calls(
            [call() for mock_csv_key_path in mock_csv_key_paths]
        )
        self.assertEqual(
            len(mock_csv_key_paths), mock_trigger_csv_load_from_s3_sql.call_count
        )
        mock_translate_s3_import_to_partitioned_data_sql.assert_called_once_with()
        mock_update_job.assert_called_once_with(
            mock_job_id,
            OrcaStatus.STAGED,
            None,
            mock_engine,
        )
        mock_execute.assert_has_calls(
            [
                call(mock_create_temporary_table_sql.return_value, [{}]),
            ]
        )
        mock_execute.assert_has_calls(
            [
                call(
                    mock_trigger_csv_load_from_s3_sql.return_value,
                    [
                        {
                            "report_bucket_name": mock_report_bucket_name,
                            "csv_key_path": mock_csv_key_path,
                            "report_bucket_region": mock_report_bucket_region,
                            "s3_access_key": mock_s3_access_key,
                            "s3_secret_key": mock_s3_secret_key,
                        }
                    ],
                )
                for mock_csv_key_path in mock_csv_key_paths
            ]
        )
        mock_execute.assert_has_calls(
            [
                call(
                    mock_translate_s3_import_to_partitioned_data_sql.return_value,
                    [{"job_id": mock_job_id}],
                )
            ]
        )
        self.assertEqual(len(mock_csv_key_paths) + 2, mock_execute.call_count)
        mock_exit.assert_called_once_with(None, None, None)

    @patch("get_current_archive_list.LOGGER")
    @patch("orca_shared.reconciliation.shared_reconciliation.update_job")
    @patch("get_current_archive_list.get_partition_name_from_bucket_name")
    @patch("get_current_archive_list.translate_s3_import_to_partitioned_data_sql")
    @patch("get_current_archive_list.trigger_csv_load_from_s3_sql")
    @patch("get_current_archive_list.add_metadata_to_gzip")
    @patch("get_current_archive_list.create_temporary_table_sql")
    @patch("get_current_archive_list.generate_temporary_s3_column_list")
    def test_update_job_with_s3_inventory_in_postgres_error_logged_and_raised(
        self,
        mock_generate_temporary_s3_column_list: MagicMock,
        mock_create_temporary_table_sql: MagicMock,
        mock_add_metadata_to_gzip: MagicMock,
        mock_trigger_csv_load_from_s3_sql: MagicMock,
        mock_translate_s3_import_to_partitioned_data_sql: MagicMock,
        mock_get_partition_name_from_bucket_name: MagicMock,
        mock_update_job: MagicMock,
        mock_logger: MagicMock,
    ):
        """
        Exceptions from Postgres should bubble up.
        """
        expected_exception = Exception(uuid.uuid4().__str__())
        mock_s3_access_key = Mock()
        mock_s3_secret_key = Mock()
        mock_report_bucket_name = Mock()
        mock_report_bucket_region = Mock()
        mock_csv_key_paths = [
            uuid.uuid4().__str__() + ".csv.gz",
            uuid.uuid4().__str__() + ".csv.gz",
        ]
        mock_manifest_file_schema = Mock()
        mock_job_id = Mock()
        mock_execute = Mock(side_effect=expected_exception)
        mock_connection = Mock()
        mock_connection.execute = mock_execute
        mock_exit = Mock(return_value=False)
        mock_enter = Mock()
        mock_enter.__enter__ = Mock(return_value=mock_connection)
        mock_enter.__exit__ = mock_exit
        mock_engine = Mock()
        mock_engine.begin = Mock(return_value=mock_enter)

        with self.assertRaises(Exception) as cm:
            get_current_archive_list.update_job_with_s3_inventory_in_postgres(
                mock_s3_access_key,
                mock_s3_secret_key,
                mock_report_bucket_name,
                mock_report_bucket_region,
                mock_csv_key_paths,
                mock_manifest_file_schema,
                mock_job_id,
                mock_engine,
            )
        self.assertEqual(expected_exception, cm.exception)

        mock_generate_temporary_s3_column_list.assert_called_once_with(
            mock_manifest_file_schema
        )
        mock_enter.__enter__.assert_called_once_with()
        mock_execute.assert_called_once_with(
            mock_create_temporary_table_sql.return_value, [{}]
        )
        mock_exit.assert_called_once_with(
            Exception, expected_exception, unittest.mock.ANY
        )
        mock_logger.error.assert_called_once_with(
            f"Error while processing job '{mock_job_id}': {expected_exception}"
        )

    @patch("get_current_archive_list.LOGGER")
    @patch("orca_shared.reconciliation.shared_reconciliation.update_job")
    @patch("get_current_archive_list.get_partition_name_from_bucket_name")
    @patch("get_current_archive_list.translate_s3_import_to_partitioned_data_sql")
    @patch("get_current_archive_list.trigger_csv_load_from_s3_sql")
    @patch("get_current_archive_list.add_metadata_to_gzip")
    @patch("get_current_archive_list.create_temporary_table_sql")
    @patch("get_current_archive_list.generate_temporary_s3_column_list")
    def test_update_job_with_s3_inventory_in_postgres_non_csv_gzip_raises_error(
        self,
        mock_generate_temporary_s3_column_list: MagicMock,
        mock_create_temporary_table_sql: MagicMock,
        mock_add_metadata_to_gzip: MagicMock,
        mock_trigger_csv_load_from_s3_sql: MagicMock,
        mock_translate_s3_import_to_partitioned_data_sql: MagicMock,
        mock_get_partition_name_from_bucket_name: MagicMock,
        mock_update_job: MagicMock,
        mock_logger: MagicMock,
    ):
        """
        If AWS starts giving us non-csv.gz files, we should raise an error.
        """
        mock_s3_access_key = Mock()
        mock_s3_secret_key = Mock()
        mock_report_bucket_name = Mock()
        mock_report_bucket_region = Mock()
        bad_csv_key_path = uuid.uuid4().__str__() + ".csv"
        mock_csv_key_paths = [bad_csv_key_path]
        mock_manifest_file_schema = Mock()
        mock_job_id = Mock()
        mock_execute = Mock()
        mock_connection = Mock()
        mock_connection.execute = mock_execute
        mock_exit = Mock(return_value=False)
        mock_enter = Mock()
        mock_enter.__enter__ = Mock(return_value=mock_connection)
        mock_enter.__exit__ = mock_exit
        mock_engine = Mock()
        mock_engine.begin = Mock(return_value=mock_enter)

        with self.assertRaises(Exception) as cm:
            get_current_archive_list.update_job_with_s3_inventory_in_postgres(
                mock_s3_access_key,
                mock_s3_secret_key,
                mock_report_bucket_name,
                mock_report_bucket_region,
                mock_csv_key_paths,
                mock_manifest_file_schema,
                mock_job_id,
                mock_engine,
            )
        self.assertEqual(
            f"Cannot handle file extension on '{bad_csv_key_path}'", str(cm.exception)
        )

        mock_generate_temporary_s3_column_list.assert_called_once_with(
            mock_manifest_file_schema
        )
        mock_execute.assert_called_once_with(
            mock_create_temporary_table_sql.return_value, [{}]
        )
        mock_exit.assert_called_once_with(
            Exception, unittest.mock.ANY, unittest.mock.ANY
        )
        mock_logger.error.assert_called_once_with(
            f"Error while processing job '{mock_job_id}': {cm.exception}"
        )

    @patch("boto3.resource")
    def test_add_metadata_to_gzip_happy_path(self, mock_boto3_resource: MagicMock):
        """
        Happy path for adding missing metadata to AWS Inventory csv.gz files.
        """
        mock_s3_object = mock_boto3_resource.return_value.Object.return_value
        mock_s3_object.content_encoding = None
        mock_report_bucket_name = Mock()
        mock_gzip_key_path = Mock()
        get_current_archive_list.add_metadata_to_gzip(
            mock_report_bucket_name, mock_gzip_key_path
        )

        mock_boto3_resource.assert_called_once_with("s3")
        mock_boto3_resource.return_value.Object.assert_called_once_with(
            mock_report_bucket_name, mock_gzip_key_path
        )
        mock_s3_object.copy_from.assert_called_once_with(
            CopySource={"Bucket": mock_report_bucket_name, "Key": mock_gzip_key_path},
            Metadata=mock_s3_object.metadata,
            MetadataDirective="REPLACE",
            ContentEncoding="gzip",
        )

    @patch("boto3.resource")
    def test_add_metadata_to_gzip_already_present_does_not_copy(
        self, mock_boto3_resource: MagicMock
    ):
        """
        If metadata is already present, do not add.
        """
        mock_s3_object = mock_boto3_resource.return_value.Object.return_value
        mock_s3_object.content_encoding = Mock()
        mock_report_bucket_name = Mock()
        mock_gzip_key_path = Mock()
        get_current_archive_list.add_metadata_to_gzip(
            mock_report_bucket_name, mock_gzip_key_path
        )

        mock_boto3_resource.assert_called_once_with("s3")
        mock_boto3_resource.return_value.Object.assert_called_once_with(
            mock_report_bucket_name, mock_gzip_key_path
        )
        mock_s3_object.copy_from.assert_not_called()

    def test_generate_temporary_s3_column_list_happy_path(self):
        """
        Should properly translate columns to orca DB format.
        Must add extra columns for extra columns.
        """
        result = get_current_archive_list.generate_temporary_s3_column_list(
            "IsDeleteMarker,StorageClass, blah, Size, Key, IsLatest,Extra, Bucket,LastModifiedDate,ETag"
        )
        self.assertEqual(
            "delete_flag bool, storage_class text, junk2 text, size_in_bytes bigint, key_path text, is_latest bool, "
            "junk6 text, orca_archive_location text, last_update timestamptz, etag text",
            result,
        )

    @patch("boto3.client")
    def test_get_s3_credentials_from_secrets_manager_happy_path(
        self, mock_client: MagicMock
    ):
        """
        Happy path for pulling secret values from secretsmanager
        """
        mock_db_connect_info_secret_arn = Mock()
        region = uuid.uuid4().__str__()
        s3_access_key = uuid.uuid4().__str__()
        s3_secret_key = uuid.uuid4().__str__()

        mock_secrets_manager = mock_client.return_value
        mock_secrets_manager.get_secret_value.return_value = {
            "SecretString": json.dumps(
                {
                    get_current_archive_list.S3_ACCESS_CREDENTIALS_ACCESS_KEY_KEY: s3_access_key,
                    get_current_archive_list.S3_ACCESS_CREDENTIALS_SECRET_KEY_KEY: s3_secret_key,
                }
            )
        }

        with patch.dict(
            os.environ,
            {"AWS_REGION": region},
        ):
            (
                result_access_key,
                result_secret_key,
            ) = get_current_archive_list.get_s3_credentials_from_secrets_manager(
                mock_db_connect_info_secret_arn
            )

        mock_client.assert_called_once_with("secretsmanager", region_name=region)
        mock_secrets_manager.get_secret_value.assert_called_once_with(
            SecretId=mock_db_connect_info_secret_arn
        )
        self.assertEqual(s3_access_key, result_access_key)
        self.assertEqual(s3_secret_key, result_secret_key)

    @patch("boto3.client")
    def test_get_s3_credentials_from_secrets_manager_missing_values_raises_error(
        self, mock_client: MagicMock
    ):
        """
        When returns are unset or empty strings, should raise KeyError.
        """
        mock_db_connect_info_secret_arn = Mock()
        s3_access_key = uuid.uuid4().__str__()
        s3_secret_key = uuid.uuid4().__str__()
        region = uuid.uuid4().__str__()

        mock_secrets_manager = mock_client.return_value

        with patch.dict(
            os.environ,
            {"AWS_REGION": region},
        ):
            for secret_key in [
                get_current_archive_list.S3_ACCESS_CREDENTIALS_ACCESS_KEY_KEY,
                get_current_archive_list.S3_ACCESS_CREDENTIALS_SECRET_KEY_KEY,
            ]:
                values = {
                    get_current_archive_list.S3_ACCESS_CREDENTIALS_ACCESS_KEY_KEY: s3_access_key,
                    get_current_archive_list.S3_ACCESS_CREDENTIALS_SECRET_KEY_KEY: s3_secret_key,
                }
                with self.subTest(secret_key=secret_key):
                    values[secret_key] = ""
                    mock_secrets_manager.get_secret_value.return_value = {
                        "SecretString": json.dumps(values)
                    }
                    with self.assertRaises(ValueError) as cm:
                        get_current_archive_list.get_s3_credentials_from_secrets_manager(
                            mock_db_connect_info_secret_arn
                        )
                    self.assertEqual(
                        f"{secret_key} secret is not set.",
                        str(cm.exception),
                    )
                    values.pop(secret_key)
                    mock_secrets_manager.get_secret_value.return_value = {
                        "SecretString": json.dumps(values)
                    }
                    with self.assertRaises(ValueError) as cm:
                        get_current_archive_list.get_s3_credentials_from_secrets_manager(
                            mock_db_connect_info_secret_arn
                        )
                    self.assertEqual(
                        f"{secret_key} secret is not set.",
                        str(cm.exception),
                    )

    @patch("boto3.client")
    def test_get_message_from_queue_happy_path(self, mock_client: MagicMock):
        """
        Happy path for pulling a message from the internal report queue.
        """
        report_bucket_aws_region = uuid.uuid4().__str__()
        report_bucket_name = uuid.uuid4().__str__()
        manifest_key_path = uuid.uuid4().__str__()
        expected_record = {
            get_current_archive_list.RECORD_REPORT_BUCKET_REGION_KEY: report_bucket_aws_region,
            get_current_archive_list.RECORD_MANIFEST_KEY_KEY: manifest_key_path,
            get_current_archive_list.RECORD_REPORT_BUCKET_NAME_KEY: report_bucket_name,
        }
        expected_receipt_handle = uuid.uuid4().__str__()

        mock_client.return_value.receive_message.return_value = {
            get_current_archive_list.MESSAGES_KEY: [
                {
                    "Body": json.dumps(expected_record),
                    "ReceiptHandle": expected_receipt_handle,
                }
            ]
        }

        mock_internal_report_queue_url = Mock()

        result = get_current_archive_list.get_message_from_queue(
            mock_internal_report_queue_url
        )

        self.assertEqual(report_bucket_aws_region, result.report_bucket_region)
        self.assertEqual(report_bucket_name, result.report_bucket_name)
        self.assertEqual(manifest_key_path, result.manifest_key)
        self.assertEqual(expected_receipt_handle, result.message_receipt_handle)

        mock_client.assert_called_once_with("sqs")
        mock_client.return_value.receive_message.assert_called_once_with(
            QueueUrl=mock_internal_report_queue_url,
            MaxNumberOfMessages=1,
        )

    @patch("boto3.client")
    def test_get_message_from_queue_rejects_bad_json_format(
        self, mock_client: MagicMock
    ):
        """
        If the body is not in the correct format, should raise an error.
        """
        report_bucket_aws_region = uuid.uuid4().__str__()
        report_bucket_name = uuid.uuid4().__str__()
        expected_record = {
            get_current_archive_list.RECORD_REPORT_BUCKET_REGION_KEY: report_bucket_aws_region,
            get_current_archive_list.RECORD_REPORT_BUCKET_NAME_KEY: report_bucket_name,
        }
        expected_receipt_handle = uuid.uuid4().__str__()

        mock_client.return_value.receive_message.return_value = {
            get_current_archive_list.MESSAGES_KEY: [
                {
                    "Body": json.dumps(expected_record),
                    "ReceiptHandle": expected_receipt_handle,
                }
            ]
        }

        mock_internal_report_queue_url = Mock()

        with self.assertRaises(ValueError) as cm:
            get_current_archive_list.get_message_from_queue(
                mock_internal_report_queue_url
            )
        self.assertEqual(
            f"data must contain ['{get_current_archive_list.RECORD_REPORT_BUCKET_REGION_KEY}', "
            f"'{get_current_archive_list.RECORD_REPORT_BUCKET_NAME_KEY}', "
            f"'{get_current_archive_list.RECORD_MANIFEST_KEY_KEY}'] properties",
            str(cm.exception),
        )

    # noinspection PyPep8Naming
    @patch("get_current_archive_list.get_message_from_queue")
    @patch("orca_shared.database.shared_db.get_configuration")
    @patch("get_current_archive_list.get_s3_credentials_from_secrets_manager")
    @patch("get_current_archive_list.LOGGER")
    @patch("get_current_archive_list.task")
    @patch.dict(
        os.environ,
        {
            "DB_CONNECT_INFO_SECRET_ARN": "dummy_secret_arn"
        },
        clear=True,
     )
    def test_handler_happy_path(
        self,
        mock_task: MagicMock,
        mock_LOGGER: MagicMock,
        mock_get_s3_credentials_from_secrets_manager: MagicMock,
        mock_get_configuration: MagicMock,
        mock_get_message_from_queue: MagicMock,
    ):
        """
        Happy path for handler assembling information to call Task.
        """
        db_connect_info_secret_arn = uuid.uuid4().__str__()
        mock_report_bucket_aws_region = Mock()
        mock_report_bucket_name = Mock()
        mock_manifest_key_path = Mock()
        receipt_handle = uuid.uuid4().__str__()
        expected_result = {
            get_current_archive_list.OUTPUT_JOB_ID_KEY: random.randint(  # nosec
                0, 1000
            ),
            get_current_archive_list.OUTPUT_ORCA_ARCHIVE_LOCATION_KEY: uuid.uuid4().__str__(),  # nosec
        }
        mock_task.return_value = copy.deepcopy(expected_result)
        expected_result[
            get_current_archive_list.OUTPUT_RECEIPT_HANDLE_KEY
        ] = receipt_handle

        mock_context = Mock()
        mock_get_message_from_queue.return_value = get_current_archive_list.MessageData(
            mock_report_bucket_aws_region,
            mock_report_bucket_name,
            mock_manifest_key_path,
            receipt_handle,
        )

        s3_access_key = uuid.uuid4().__str__()
        s3_secret_key = uuid.uuid4().__str__()

        mock_get_s3_credentials_from_secrets_manager.return_value = (
            s3_access_key,
            s3_secret_key,
        )
        event = Mock()

        report_queue_url = uuid.uuid4().__str__()
        with patch.dict(
            os.environ,
            {
                get_current_archive_list.OS_ENVIRON_S3_CREDENTIALS_SECRET_ARN_KEY: db_connect_info_secret_arn,
                get_current_archive_list.OS_ENVIRON_INTERNAL_REPORT_QUEUE_URL_KEY: report_queue_url,
            },
        ):
            result = get_current_archive_list.handler(event, mock_context)

        mock_LOGGER.setMetadata.assert_called_once_with(event, mock_context)
        mock_get_s3_credentials_from_secrets_manager.assert_called_once_with(db_connect_info_secret_arn)
        mock_get_configuration.assert_called_once_with(os.environ["DB_CONNECT_INFO_SECRET_ARN"])
        mock_get_message_from_queue.assert_called_once_with(report_queue_url)
        mock_task.assert_called_once_with(
            mock_report_bucket_aws_region,
            mock_report_bucket_name,
            mock_manifest_key_path,
            s3_access_key,
            s3_secret_key,
            mock_get_configuration.return_value,
        )
        self.assertEqual(expected_result, result)

    @patch("get_current_archive_list.get_message_from_queue")
    @patch("orca_shared.database.shared_db.get_configuration")
    @patch("get_current_archive_list.get_s3_credentials_from_secrets_manager")
    @patch("get_current_archive_list.LOGGER")
    @patch("get_current_archive_list.task")
    @patch.dict(
        os.environ,
        {
            "DB_CONNECT_INFO_SECRET_ARN": "test"
        },
        clear=True,
     )
    def test_handler_rejects_bad_output(
        self,
        mock_task: MagicMock,
        mock_LOGGER: MagicMock,
        mock_get_s3_credentials_from_secrets_manager: MagicMock,
        mock_get_configuration: MagicMock,
        mock_get_message_from_queue: MagicMock,
    ):
        """
        Violating output.json schema should raise an error.
        """
        db_connect_info_secret_arn = uuid.uuid4().__str__()
        mock_report_bucket_aws_region = Mock()
        mock_report_bucket_name = Mock()
        mock_manifest_key_path = Mock()
        expected_result = {}
        mock_task.return_value = copy.deepcopy(expected_result)
        receipt_handle = uuid.uuid4().__str__()

        mock_context = Mock()
        mock_get_message_from_queue.return_value = get_current_archive_list.MessageData(
            mock_report_bucket_aws_region,
            mock_report_bucket_name,
            mock_manifest_key_path,
            receipt_handle,
        )

        s3_access_key = uuid.uuid4().__str__()
        s3_secret_key = uuid.uuid4().__str__()

        mock_get_s3_credentials_from_secrets_manager.return_value = (
            s3_access_key,
            s3_secret_key,
        )
        with self.assertRaises(Exception) as cm:
            event = Mock()

            report_queue_url = uuid.uuid4().__str__()
            with patch.dict(
                os.environ,
                {
                    get_current_archive_list.OS_ENVIRON_S3_CREDENTIALS_SECRET_ARN_KEY: db_connect_info_secret_arn,
                    get_current_archive_list.OS_ENVIRON_INTERNAL_REPORT_QUEUE_URL_KEY: report_queue_url,
                },
            ):
                get_current_archive_list.handler(event, mock_context)

        mock_LOGGER.setMetadata.assert_called_once_with(event, mock_context)
        mock_get_message_from_queue.assert_called_once_with(report_queue_url)
        mock_task.assert_called_once_with(
            mock_report_bucket_aws_region,
            mock_report_bucket_name,
            mock_manifest_key_path,
            s3_access_key,
            s3_secret_key,
            mock_get_configuration.return_value,
        )
        self.assertEqual(
            f"data must contain ['{get_current_archive_list.OUTPUT_JOB_ID_KEY}', "
            f"'{get_current_archive_list.OUTPUT_ORCA_ARCHIVE_LOCATION_KEY}'] properties",
            str(cm.exception),
        )
