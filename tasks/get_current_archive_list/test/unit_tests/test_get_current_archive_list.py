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
from unittest.mock import Mock, call, patch, MagicMock

from fastjsonschema import JsonSchemaValueException

import get_current_archive_list
from orca_shared.recovery.shared_recovery import OrcaStatus
from orca_shared.recovery import shared_recovery


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

    def test_create_job_happy_path(self):
        pass

    def test_create_job_error_logged_and_raised(self):
        pass

    def test_update_job_with_failure_happy_path(self):
        pass

    def test_update_job_with_failure_error_logged_and_raised(self):
        pass

    def test_truncate_s3_partition_happy_path(self):
        pass

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

    def test_handler_multiple_records_raises_error(self):
        pass

    def test_handler_missing_os_environ_raises_error(self):
        pass

    def test_handler_rejects_bad_input(self):
        pass

    def test_handler_rejects_bad_output(self):
        pass
