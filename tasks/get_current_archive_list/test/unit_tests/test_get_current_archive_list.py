"""
Name: test_get_current_archive_list.py

Description:  Unit tests for test_get_current_archive_list.py.
"""
import copy
import os
import random
import unittest
import uuid
from unittest.mock import Mock, patch, MagicMock

from orca_shared.reconciliation import OrcaStatus

import get_current_archive_list


class TestGetCurrentArchiveList(
    unittest.TestCase
):  # pylint: disable-msg=too-many-instance-attributes
    """
    TestGetCurrentArchiveList.
    """

    def test_task_happy_path(self):
        pass

    def test_task_non_manifest_ignored(self):
        pass

    def test_task_error_posted_as_status_update(self):
        pass

    @patch("json.loads")
    @patch("boto3.client")
    def test_get_manifest_happy_path(
            self, mock_client: MagicMock, mock_json_load: MagicMock
    ):
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
    def test_create_job_happy_path(self,
                                   mock_create_job_sql: MagicMock,
                                   ):
        mock_orca_archive_location = Mock()
        mock_inventory_creation_time = Mock()
        mock_job_id = Mock()
        returned_row0 = {"id": mock_job_id}
        mock_execute = Mock(return_value=[returned_row0])
        mock_connection = Mock()
        mock_connection.execute = mock_execute
        mock_exit = Mock(return_value=False)
        mock_enter = Mock()
        mock_enter.__enter__ = Mock(return_value=mock_connection)
        mock_enter.__exit__ = mock_exit
        mock_engine = Mock()
        mock_engine.begin = Mock(return_value=mock_enter)

        result = get_current_archive_list.create_job(mock_orca_archive_location, mock_inventory_creation_time, mock_engine)

        mock_enter.__enter__.assert_called_once_with()
        mock_execute.assert_called_once_with(
            mock_create_job_sql.return_value,
            [
                {
                    "orca_archive_location": mock_orca_archive_location,
                    "inventory_creation_time": mock_inventory_creation_time,
                    "status_id": OrcaStatus.STAGED.value,
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
    def test_create_job_error_logged_and_raised(self,
                                                mock_create_job_sql: MagicMock,
                                                mock_logger: MagicMock
                                                ):
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
            get_current_archive_list.create_job(mock_orca_archive_location, mock_inventory_creation_time,
                                                mock_engine)
        self.assertEqual(expected_exception, cm.exception)

        mock_enter.__enter__.assert_called_once_with()
        mock_execute.assert_called_once_with(
            mock_create_job_sql.return_value,
            [
                {
                    "orca_archive_location": mock_orca_archive_location,
                    "inventory_creation_time": mock_inventory_creation_time,
                    "status_id": OrcaStatus.STAGED.value,
                    "start_time": unittest.mock.ANY,
                    "last_update": unittest.mock.ANY,
                    "end_time": None,
                    "error_message": None,
                }
            ],
        )
        mock_exit.assert_called_once_with(Exception, expected_exception, unittest.mock.ANY)
        mock_create_job_sql.assert_called_once_with()
        mock_logger.error.assert_called_once_with("Error while creating job: {sql_ex}",
                                                  sql_ex=expected_exception)
        pass

    @patch("get_current_archive_list.update_job_sql")
    def test_update_job_with_failure_happy_path(self,
                                                mock_update_job_sql: MagicMock,
                                                ):
        mock_error_message = Mock()
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

        get_current_archive_list.update_job_with_failure(mock_job_id, mock_error_message, mock_engine)

        mock_enter.__enter__.assert_called_once_with()
        mock_execute.assert_called_once_with(
            mock_update_job_sql.return_value,
            [
                {
                    "id": mock_job_id,
                    "status_id": OrcaStatus.ERROR.value,
                    "last_update": unittest.mock.ANY,
                    "end_time": unittest.mock.ANY,
                    "error_message": mock_error_message,
                }
            ],
        )
        mock_exit.assert_called_once_with(None, None, None)
        mock_update_job_sql.assert_called_once_with()

    @patch("get_current_archive_list.LOGGER")
    @patch("get_current_archive_list.update_job_sql")
    def test_update_job_with_failure_error_logged_and_raised(self,
                                                             mock_update_job_sql: MagicMock,
                                                             mock_logger: MagicMock):
        expected_exception = Exception(uuid.uuid4().__str__())

        mock_error_message = Mock()
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
            get_current_archive_list.update_job_with_failure(mock_job_id, mock_error_message, mock_engine)
        self.assertEqual(expected_exception, cm.exception)

        mock_enter.__enter__.assert_called_once_with()
        mock_execute.assert_called_once_with(
            mock_update_job_sql.return_value,
            [
                {
                    "id": mock_job_id,
                    "status_id": OrcaStatus.ERROR.value,
                    "last_update": unittest.mock.ANY,
                    "end_time": unittest.mock.ANY,
                    "error_message": mock_error_message,
                }
            ],
        )
        mock_exit.assert_called_once_with(Exception, expected_exception, unittest.mock.ANY)
        mock_update_job_sql.assert_called_once_with()
        mock_logger.error.assert_called_once_with("Error while updating job '{job_id}': {sql_ex}",
                                                  job_id=mock_job_id,
                                                  sql_ex=expected_exception)

    @patch("get_current_archive_list.get_partition_name_from_bucket_name")
    @patch("get_current_archive_list.truncate_s3_partition_sql")
    def test_truncate_s3_partition_happy_path(self,
                                              mock_truncate_s3_partition_sql: MagicMock,
                                              mock_get_partition_name_from_bucket_name: MagicMock,
                                              ):
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

        get_current_archive_list.truncate_s3_partition(mock_orca_archive_location, mock_engine)

        mock_get_partition_name_from_bucket_name.assert_called_once_with(mock_orca_archive_location)
        mock_enter.__enter__.assert_called_once_with()
        mock_truncate_s3_partition_sql.assert_called_once_with(mock_get_partition_name_from_bucket_name.return_value)
        mock_execute.assert_called_once_with(
            mock_truncate_s3_partition_sql.return_value,
            [
                {}
            ],
        )
        mock_exit.assert_called_once_with(None, None, None)

    def test_truncate_s3_partition_error_logged_and_raised(self):
        pass

    def test_update_job_with_s3_inventory_in_postgres_happy_path(self):
        pass

    def test_update_job_with_s3_inventory_in_postgres_error_logged_and_raised(self):
        pass

    @patch("boto3.resource")
    def test_add_metadata_to_gzip_happy_path(self, mock_boto3_resource: MagicMock):
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
            "StorageClass, blah, Size, Key, Extra, Bucket,LastModifiedDate,ETag"
        )
        self.assertEqual(
            "storage_class text, junk2 text, size_in_bytes bigint, key_path text, junk5 text, orca_archive_location text, last_update timestamptz, etag text",
            result,
        )

    # noinspection PyPep8Naming
    @patch("orca_shared.database.shared_db.get_configuration")
    @patch("get_current_archive_list.LOGGER")
    @patch("get_current_archive_list.task")
    def test_handler_happy_path(self,
                                mock_task: MagicMock,
                                mock_LOGGER: MagicMock,
                                mock_get_configuration: MagicMock):
        expected_result = {get_current_archive_list.OUTPUT_JOB_ID_KEY: random.randint(0, 1000)}
        mock_task.return_value = copy.deepcopy(expected_result)

        mock_context = Mock()
        record = {
            get_current_archive_list.RECORD_S3_KEY: {
                get_current_archive_list.S3_BUCKET_KEY: {get_current_archive_list.BUCKET_NAME_KEY: uuid.uuid4().__str__()},
                get_current_archive_list.S3_OBJECT_KEY: {get_current_archive_list.OBJECT_KEY_KEY: uuid.uuid4().__str__()}
            },
            get_current_archive_list.RECORD_AWS_REGION_KEY: uuid.uuid4().__str__()
        }
        event = {
            get_current_archive_list.EVENT_RECORDS_KEY: [record]
        }

        s3_access_key = uuid.uuid4().__str__()
        s3_secret_key = uuid.uuid4().__str__()

        with patch.dict(
                os.environ, {get_current_archive_list.OS_S3_ACCESS_KEY_KEY: s3_access_key,
                             get_current_archive_list.OS_S3_SECRET_KEY_KEY: s3_secret_key}
        ):
            result = get_current_archive_list.handler(event, mock_context)

        mock_LOGGER.setMetadata.assert_called_once_with(event, mock_context)
        mock_get_configuration.assert_called_once_with()
        mock_task.assert_called_once_with(record, s3_access_key, s3_secret_key, mock_get_configuration.return_value)
        self.assertEqual(expected_result, result)

    # noinspection PyPep8Naming
    @patch("orca_shared.database.shared_db.get_configuration")
    @patch("get_current_archive_list.LOGGER")
    @patch("get_current_archive_list.task")
    def test_handler_multiple_records_raises_error(self,
                                                   mock_task: MagicMock,
                                                   mock_LOGGER: MagicMock,
                                                   mock_get_configuration: MagicMock):
        expected_result = {get_current_archive_list.OUTPUT_JOB_ID_KEY: random.randint(0, 1000)}
        mock_task.return_value = copy.deepcopy(expected_result)

        mock_context = Mock()
        record = {
            get_current_archive_list.RECORD_S3_KEY: {
                get_current_archive_list.S3_BUCKET_KEY: {get_current_archive_list.BUCKET_NAME_KEY: uuid.uuid4().__str__()},
                get_current_archive_list.S3_OBJECT_KEY: {get_current_archive_list.OBJECT_KEY_KEY: uuid.uuid4().__str__()}
            },
            get_current_archive_list.RECORD_AWS_REGION_KEY: uuid.uuid4().__str__()
        }
        event = {
            get_current_archive_list.EVENT_RECORDS_KEY: [record, record]
        }

        s3_access_key = uuid.uuid4().__str__()
        s3_secret_key = uuid.uuid4().__str__()

        with patch.dict(
                os.environ, {get_current_archive_list.OS_S3_ACCESS_KEY_KEY: s3_access_key,
                             get_current_archive_list.OS_S3_SECRET_KEY_KEY: s3_secret_key}
        ):
            with self.assertRaises(ValueError) as cm:
                get_current_archive_list.handler(event, mock_context)

        mock_LOGGER.setMetadata.assert_called_once_with(event, mock_context)
        mock_task.assert_not_called()
        self.assertEqual("Must be passed a single record. Was 2", str(cm.exception))

    @patch("orca_shared.database.shared_db.get_configuration")
    @patch("get_current_archive_list.LOGGER")
    @patch("get_current_archive_list.task")
    def test_handler_missing_os_environ_raises_error(self,
                                                     mock_task: MagicMock,
                                                     mock_LOGGER: MagicMock,
                                                     mock_get_configuration: MagicMock):
        """
        When environment variables are unset or empty strings, should raise KeyError.
        """
        mock_context = Mock()
        record = {
            get_current_archive_list.RECORD_S3_KEY: {
                get_current_archive_list.S3_BUCKET_KEY: {get_current_archive_list.BUCKET_NAME_KEY: uuid.uuid4().__str__()},
                get_current_archive_list.S3_OBJECT_KEY: {get_current_archive_list.OBJECT_KEY_KEY: uuid.uuid4().__str__()}
            },
            get_current_archive_list.RECORD_AWS_REGION_KEY: uuid.uuid4().__str__()
        }
        event = {
            get_current_archive_list.EVENT_RECORDS_KEY: [record]
        }

        s3_access_key = uuid.uuid4().__str__()
        s3_secret_key = uuid.uuid4().__str__()

        for os_environ_key in [get_current_archive_list.OS_S3_ACCESS_KEY_KEY, get_current_archive_list.OS_S3_SECRET_KEY_KEY]:
            with patch.dict(
                    os.environ, {get_current_archive_list.OS_S3_ACCESS_KEY_KEY: s3_access_key,
                                 get_current_archive_list.OS_S3_SECRET_KEY_KEY: s3_secret_key}
            ):
                with self.subTest(os_environ_key=os_environ_key):
                    os.environ[os_environ_key] = ""
                    with self.assertRaises(KeyError) as cm:
                        get_current_archive_list.handler(event, mock_context)

                        mock_LOGGER.setMetadata.assert_called_once_with(event, mock_context)
                        mock_task.assert_not_called()
                        self.assertEqual(f"{os_environ_key} environment variable is not set.",
                                         str(cm.exception))
                        mock_LOGGER.reset_mock()
                    os.environ.pop(os_environ_key)
                    with self.assertRaises(KeyError) as cm:
                        get_current_archive_list.handler(event, mock_context)

                        mock_LOGGER.setMetadata.assert_called_once_with(event, mock_context)
                        mock_task.assert_not_called()
                        self.assertEqual(f"{os_environ_key} environment variable is not set.",
                                         str(cm.exception))
                        mock_LOGGER.reset_mock()

    @patch("orca_shared.database.shared_db.get_configuration")
    @patch("get_current_archive_list.LOGGER")
    @patch("get_current_archive_list.task")
    def test_handler_rejects_bad_input(self,
                                       mock_task: MagicMock,
                                       mock_LOGGER: MagicMock,
                                       mock_get_configuration: MagicMock):
        expected_result = {get_current_archive_list.OUTPUT_JOB_ID_KEY: random.randint(0, 1000)}
        mock_task.return_value = copy.deepcopy(expected_result)

        mock_context = Mock()
        record = {
            get_current_archive_list.RECORD_S3_KEY: {
                get_current_archive_list.S3_OBJECT_KEY: {get_current_archive_list.OBJECT_KEY_KEY: uuid.uuid4().__str__()}
            },
            get_current_archive_list.RECORD_AWS_REGION_KEY: uuid.uuid4().__str__()
        }
        event = {
            get_current_archive_list.EVENT_RECORDS_KEY: [record]
        }

        s3_access_key = uuid.uuid4().__str__()
        s3_secret_key = uuid.uuid4().__str__()

        with patch.dict(
                os.environ, {get_current_archive_list.OS_S3_ACCESS_KEY_KEY: s3_access_key,
                             get_current_archive_list.OS_S3_SECRET_KEY_KEY: s3_secret_key}
        ):
            with self.assertRaises(Exception) as cm:
                get_current_archive_list.handler(event, mock_context)

        mock_LOGGER.setMetadata.assert_called_once_with(event, mock_context)
        mock_task.assert_not_called()
        self.assertEqual(f"data.{get_current_archive_list.EVENT_RECORDS_KEY}[0].{get_current_archive_list.RECORD_S3_KEY} "
                         f"must contain ['{get_current_archive_list.S3_BUCKET_KEY}', "
                         f"'{get_current_archive_list.S3_OBJECT_KEY}'] properties", str(cm.exception))

    @patch("orca_shared.database.shared_db.get_configuration")
    @patch("get_current_archive_list.LOGGER")
    @patch("get_current_archive_list.task")
    def test_handler_rejects_bad_output(self,
                                        mock_task: MagicMock,
                                        mock_LOGGER: MagicMock,
                                        mock_get_configuration: MagicMock):
        expected_result = {}
        mock_task.return_value = copy.deepcopy(expected_result)

        mock_context = Mock()
        record = {
            get_current_archive_list.RECORD_S3_KEY: {
                get_current_archive_list.S3_BUCKET_KEY: {get_current_archive_list.BUCKET_NAME_KEY: uuid.uuid4().__str__()},
                get_current_archive_list.S3_OBJECT_KEY: {get_current_archive_list.OBJECT_KEY_KEY: uuid.uuid4().__str__()}
            },
            get_current_archive_list.RECORD_AWS_REGION_KEY: uuid.uuid4().__str__()
        }
        event = {
            get_current_archive_list.EVENT_RECORDS_KEY: [record]
        }

        s3_access_key = uuid.uuid4().__str__()
        s3_secret_key = uuid.uuid4().__str__()

        with patch.dict(
                os.environ, {get_current_archive_list.OS_S3_ACCESS_KEY_KEY: s3_access_key,
                             get_current_archive_list.OS_S3_SECRET_KEY_KEY: s3_secret_key}
        ):
            with self.assertRaises(Exception) as cm:
                get_current_archive_list.handler(event, mock_context)

        mock_LOGGER.setMetadata.assert_called_once_with(event, mock_context)
        mock_task.assert_called_once_with(record, s3_access_key, s3_secret_key, mock_get_configuration.return_value)
        self.assertEqual(f"data must contain ['{get_current_archive_list.OUTPUT_JOB_ID_KEY}'] properties", str(cm.exception))
