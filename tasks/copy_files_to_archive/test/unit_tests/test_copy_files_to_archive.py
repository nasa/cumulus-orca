"""
Name: test_copy_files_to_archive.py
Description:  Unit tests for copy_files_to_archive.py.
"""
import json
import os
import random
import unittest
import uuid
from random import randint
from unittest import TestCase, mock
from unittest.mock import Mock, call, patch, MagicMock

from botocore.exceptions import ClientError
from s3transfer.constants import MB

import copy_files_to_archive
from test.unit_tests.ConfigCheck import ConfigCheck


class TestCopyFilesToArchive(TestCase):
    """
    Test copy_files_to_archive functionality and business logic.
    """

    @patch.dict(
        os.environ,
        {
            "COPY_RETRIES": "703",
            "COPY_RETRY_SLEEP_SECS": "108.5",
            "DB_QUEUE_URL": "something.blah",
            "DEFAULT_MULTIPART_CHUNKSIZE_MB": "42",
            "RECOVERY_QUEUE_URL": "something_else.blah",
        },
        clear=True,
    )
    @patch("copy_files_to_archive.LOGGER")
    @patch("copy_files_to_archive.task")
    def test_handler_happy_path(
        self,
        mock_task: MagicMock,
        mock_logger: MagicMock,
    ):
        records = Mock()
        event = {"Records": records}

        copy_files_to_archive.handler(event, Mock())

        mock_task.assert_called_with(
            records, 703, 108.5, "something.blah", 42, "something_else.blah"
        )

    @patch.dict(
        os.environ,
        {
            "DB_QUEUE_URL": "something.else",
            "DEFAULT_MULTIPART_CHUNKSIZE_MB": "42",
            "RECOVERY_QUEUE_URL": "someother.queue",
        },
        clear=True,
    )
    @patch("copy_files_to_archive.LOGGER")
    @patch("copy_files_to_archive.task")
    def test_handler_uses_default_retry_settings(
        self, mock_task: MagicMock, mock_logger: MagicMock
    ):
        """
        If retry settings not in os.environ, uses 2 retries and 30 seconds.
        """
        records = Mock()
        event = {"Records": records}

        copy_files_to_archive.handler(event, Mock())

        mock_task.assert_called_with(
            records, 2, 30, "something.else", 42, "someother.queue"
        )

    @patch("time.sleep")
    @patch("copy_files_to_archive.shared_recovery.update_status_for_file")
    @patch("copy_files_to_archive.copy_object")
    @patch("copy_files_to_archive.get_files_from_records")
    @patch("boto3.client")
    def test_task_happy_path(
        self,
        mock_boto3_client: MagicMock,
        mock_get_files_from_records: MagicMock,
        mock_copy_object: MagicMock,
        mock_update_status_for_file: MagicMock,
        mock_sleep: MagicMock,
    ):
        """
        If all files go through without errors, return without sleeps.
        """
        db_queue_url = uuid.uuid4().__str__()
        recovery_queue_url = uuid.uuid4().__str__()
        max_retries = randint(2, 9999)
        retry_sleep_secs = randint(0, 9999)
        default_multipart_chunksize_mb = randint(1, 10000)

        file0_job_id = uuid.uuid4().__str__()
        file0_granule_id = uuid.uuid4().__str__()
        file0_input_filename = uuid.uuid4().__str__()
        file0_source_bucket = uuid.uuid4().__str__()
        file0_source_key = uuid.uuid4().__str__()
        file0_target_bucket = uuid.uuid4().__str__()
        file0_target_key = uuid.uuid4().__str__()
        file0_message_reciept = uuid.uuid4().__str__()

        file1_job_id = uuid.uuid4().__str__()
        file1_granule_id = uuid.uuid4().__str__()
        file1_input_filename = uuid.uuid4().__str__()
        file1_source_bucket = uuid.uuid4().__str__()
        file1_source_key = uuid.uuid4().__str__()
        file1_target_bucket = uuid.uuid4().__str__()
        file1_target_key = uuid.uuid4().__str__()
        file1_multipart_chunksize_mb = randint(1, 10000)
        file1_message_reciept = uuid.uuid4().__str__()

        mock_records = Mock()

        file0 = {
            copy_files_to_archive.INPUT_JOB_ID_KEY: file0_job_id,
            copy_files_to_archive.INPUT_GRANULE_ID_KEY: file0_granule_id,
            copy_files_to_archive.INPUT_FILENAME_KEY: file0_input_filename,
            copy_files_to_archive.FILE_SUCCESS_KEY: False,
            copy_files_to_archive.INPUT_SOURCE_BUCKET_KEY: file0_source_bucket,
            copy_files_to_archive.INPUT_SOURCE_KEY_KEY: file0_source_key,
            copy_files_to_archive.INPUT_TARGET_BUCKET_KEY: file0_target_bucket,
            copy_files_to_archive.INPUT_TARGET_KEY_KEY: file0_target_key,
            copy_files_to_archive.INPUT_MULTIPART_CHUNKSIZE_MB: None,
            copy_files_to_archive.FILE_MESSAGE_RECIEPT: file0_message_reciept,
        }
        file1 = {
            copy_files_to_archive.INPUT_JOB_ID_KEY: file1_job_id,
            copy_files_to_archive.INPUT_GRANULE_ID_KEY: file1_granule_id,
            copy_files_to_archive.INPUT_FILENAME_KEY: file1_input_filename,
            copy_files_to_archive.FILE_SUCCESS_KEY: False,
            copy_files_to_archive.INPUT_SOURCE_BUCKET_KEY: file1_source_bucket,
            copy_files_to_archive.INPUT_SOURCE_KEY_KEY: file1_source_key,
            copy_files_to_archive.INPUT_TARGET_BUCKET_KEY: file1_target_bucket,
            copy_files_to_archive.INPUT_TARGET_KEY_KEY: file1_target_key,
            copy_files_to_archive.INPUT_MULTIPART_CHUNKSIZE_MB: file1_multipart_chunksize_mb,
            copy_files_to_archive.FILE_MESSAGE_RECIEPT: file1_message_reciept,
        }
        mock_get_files_from_records.return_value = [file0, file1]
        mock_copy_object.return_value = None

        copy_files_to_archive.task(
            mock_records,
            max_retries,
            retry_sleep_secs,
            db_queue_url,
            default_multipart_chunksize_mb,
            recovery_queue_url,
        )

        mock_get_files_from_records.assert_called_once_with(mock_records)
        mock_boto3_client.assert_has_calls(
            [
                call("s3"),
                call("sqs"),
            ]
        )
        mock_copy_object.assert_has_calls(
            [
                call(
                    mock_boto3_client.return_value,
                    file0_source_bucket,
                    file0_source_key,
                    file0_target_bucket,
                    default_multipart_chunksize_mb,
                    file0_target_key,
                ),
                call(
                    mock_boto3_client.return_value,
                    file1_source_bucket,
                    file1_source_key,
                    file1_target_bucket,
                    file1_multipart_chunksize_mb,
                    file1_target_key,
                ),
            ]
        )
        self.assertEqual(2, mock_copy_object.call_count)
        mock_update_status_for_file.assert_has_calls(
            [
                call(
                    file0_job_id,
                    file0_granule_id,
                    file0_input_filename,
                    copy_files_to_archive.shared_recovery.OrcaStatus.SUCCESS,
                    None,
                    db_queue_url,
                ),
                call(
                    file1_job_id,
                    file1_granule_id,
                    file1_input_filename,
                    copy_files_to_archive.shared_recovery.OrcaStatus.SUCCESS,
                    None,
                    db_queue_url,
                ),
            ]
        )
        self.assertEqual(2, mock_update_status_for_file.call_count)
        mock_sleep.assert_not_called()

    @patch("copy_files_to_archive.LOGGER")
    @patch("time.sleep")
    @patch("copy_files_to_archive.shared_recovery.update_status_for_file")
    @patch("copy_files_to_archive.copy_object")
    @patch("copy_files_to_archive.get_files_from_records")
    @patch("boto3.client")
    def test_task_retries_failed_files_up_to_retry_limit(
        self,
        mock_boto3_client: MagicMock,
        mock_get_files_from_records: MagicMock,
        mock_copy_object: MagicMock,
        mock_update_status_for_file: MagicMock,
        mock_sleep: MagicMock,
        mock_logger: MagicMock,
    ):
        """
        If one file causes errors during copy,
        retry up to limit then post error status and raise CopyRequestError.
        """
        db_queue_url = uuid.uuid4().__str__()
        max_retries = 2
        retry_sleep_secs = randint(0, 9999)
        multipart_chunksize_mb = randint(1, 10000)
        received_message_queue_url = uuid.uuid4().__str__()

        file0_job_id = uuid.uuid4().__str__()
        file0_granule_id = uuid.uuid4().__str__()
        file0_input_filename = uuid.uuid4().__str__()
        file0_source_bucket = uuid.uuid4().__str__()
        file0_source_key = uuid.uuid4().__str__()
        file0_target_bucket = uuid.uuid4().__str__()
        file0_target_key = uuid.uuid4().__str__()
        file0_message_reciept = uuid.uuid4().__str__()
        error_message = uuid.uuid4().__str__()

        file1_job_id = uuid.uuid4().__str__()
        file1_granule_id = uuid.uuid4().__str__()
        file1_input_filename = uuid.uuid4().__str__()
        file1_source_bucket = uuid.uuid4().__str__()
        file1_source_key = uuid.uuid4().__str__()
        file1_target_bucket = uuid.uuid4().__str__()
        file1_target_key = uuid.uuid4().__str__()
        file1_message_reciept = uuid.uuid4().__str__()

        mock_records = Mock()

        failed_file = {
            copy_files_to_archive.INPUT_JOB_ID_KEY: file0_job_id,
            copy_files_to_archive.INPUT_GRANULE_ID_KEY: file0_granule_id,
            copy_files_to_archive.INPUT_FILENAME_KEY: file0_input_filename,
            copy_files_to_archive.FILE_SUCCESS_KEY: False,
            copy_files_to_archive.INPUT_SOURCE_BUCKET_KEY: file0_source_bucket,
            copy_files_to_archive.INPUT_SOURCE_KEY_KEY: file0_source_key,
            copy_files_to_archive.INPUT_TARGET_BUCKET_KEY: file0_target_bucket,
            copy_files_to_archive.INPUT_TARGET_KEY_KEY: file0_target_key,
            copy_files_to_archive.FILE_MESSAGE_RECIEPT: file0_message_reciept,
        }
        successful_file = {
            copy_files_to_archive.INPUT_JOB_ID_KEY: file1_job_id,
            copy_files_to_archive.INPUT_GRANULE_ID_KEY: file1_granule_id,
            copy_files_to_archive.INPUT_FILENAME_KEY: file1_input_filename,
            copy_files_to_archive.FILE_SUCCESS_KEY: False,
            copy_files_to_archive.INPUT_SOURCE_BUCKET_KEY: file1_source_bucket,
            copy_files_to_archive.INPUT_SOURCE_KEY_KEY: file1_source_key,
            copy_files_to_archive.INPUT_TARGET_BUCKET_KEY: file1_target_bucket,
            copy_files_to_archive.INPUT_TARGET_KEY_KEY: file1_target_key,
            copy_files_to_archive.FILE_MESSAGE_RECIEPT: file1_message_reciept,
        }
        mock_get_files_from_records.return_value = [failed_file, successful_file]
        mock_copy_object.side_effect = [
            error_message,
            None,
            error_message,
            error_message,
        ]

        try:
            copy_files_to_archive.task(
                mock_records,
                max_retries,
                retry_sleep_secs,
                db_queue_url,
                multipart_chunksize_mb,
                received_message_queue_url,
            )
        except copy_files_to_archive.CopyRequestError:
            mock_get_files_from_records.assert_called_once_with(mock_records)
            mock_boto3_client.assert_has_calls(
                [
                    call("s3"),
                    call("sqs"),
                ]
            )
            mock_copy_object.assert_has_calls(
                [
                    call(
                        mock_boto3_client.return_value,
                        file0_source_bucket,
                        file0_source_key,
                        file0_target_bucket,
                        multipart_chunksize_mb,
                        file0_target_key,
                    ),
                    call(
                        mock_boto3_client.return_value,
                        file1_source_bucket,
                        file1_source_key,
                        file1_target_bucket,
                        multipart_chunksize_mb,
                        file1_target_key,
                    ),
                    call(
                        mock_boto3_client.return_value,
                        file0_source_bucket,
                        file0_source_key,
                        file0_target_bucket,
                        multipart_chunksize_mb,
                        file0_target_key,
                    ),
                ]
            )
            self.assertEqual(3, mock_copy_object.call_count)
            mock_update_status_for_file.assert_has_calls(
                [
                    call(
                        file1_job_id,
                        file1_granule_id,
                        file1_input_filename,
                        copy_files_to_archive.shared_recovery.OrcaStatus.SUCCESS,
                        None,
                        db_queue_url,
                    ),
                    call(
                        file0_job_id,
                        file0_granule_id,
                        file0_input_filename,
                        copy_files_to_archive.shared_recovery.OrcaStatus.FAILED,
                        error_message,
                        db_queue_url,
                    ),
                ]
            )
            self.assertEqual(max_retries, mock_update_status_for_file.call_count)
            mock_sleep.assert_has_calls(
                [call(retry_sleep_secs), call(retry_sleep_secs)]
            )
            self.assertEqual(max_retries, mock_sleep.call_count)
            return
        self.fail("Error not raised.")

    @patch("copy_files_to_archive.LOGGER")
    def test_get_files_from_records_adds_success_key(
        self,
        mock_logger: MagicMock,
    ):
        """
        Function should transform json into file dict, and add 'success' key.
        """
        file0 = {
            "job_id": uuid.uuid4().__str__(),
            "granule_id": uuid.uuid4().__str__(),
            "filename": uuid.uuid4().__str__(),
            "source_key": uuid.uuid4().__str__(),
            "target_key": uuid.uuid4().__str__(),
            "restore_destination": uuid.uuid4().__str__(),
            "source_bucket": uuid.uuid4().__str__(),
            "multipart_chunksize_mb": randint(1, 10000),
        }
        file1 = {
            "job_id": uuid.uuid4().__str__(),
            "granule_id": uuid.uuid4().__str__(),
            "filename": uuid.uuid4().__str__(),
            "source_key": uuid.uuid4().__str__(),
            "target_key": uuid.uuid4().__str__(),
            "restore_destination": uuid.uuid4().__str__(),
            "source_bucket": uuid.uuid4().__str__(),
            "multipart_chunksize_mb": None,
        }

        return_message_id_0 = uuid.uuid4().__str__()
        return_message_id_1 = uuid.uuid4().__str__()

        result = copy_files_to_archive.get_files_from_records(
            [
                {
                    copy_files_to_archive.FILE_MESSAGE_RECIEPT: return_message_id_0,
                    "body": json.dumps(file0.copy(), indent=4),
                },
                {
                    copy_files_to_archive.FILE_MESSAGE_RECIEPT: return_message_id_1,
                    "body": json.dumps(file1.copy(), indent=4),
                },
            ]
        )

        file0[copy_files_to_archive.FILE_SUCCESS_KEY] = False
        file0[copy_files_to_archive.FILE_MESSAGE_RECIEPT] = return_message_id_0
        file1[copy_files_to_archive.FILE_SUCCESS_KEY] = False
        file1[copy_files_to_archive.FILE_MESSAGE_RECIEPT] = return_message_id_1

        self.assertEqual([file0, file1], result)

    def test_copy_object_happy_path(self):
        src_bucket_name = uuid.uuid4().__str__()
        src_object_name = uuid.uuid4().__str__()
        dest_bucket_name = uuid.uuid4().__str__()
        multipart_chunksize_mb = randint(1, 10000)
        dest_object_name = uuid.uuid4().__str__()

        mock_s3_cli = Mock()
        config_check = ConfigCheck(multipart_chunksize_mb * MB)
        mock_s3_cli.copy = Mock(return_value=None)
        mock_s3_cli.copy.side_effect = config_check.check_multipart_chunksize

        result = copy_files_to_archive.copy_object(
            mock_s3_cli,
            src_bucket_name,
            src_object_name,
            dest_bucket_name,
            multipart_chunksize_mb,
            dest_object_name,
        )

        mock_s3_cli.copy.assert_called_once_with(
            {"Bucket": src_bucket_name, "Key": src_object_name},
            dest_bucket_name,
            dest_object_name,
            ExtraArgs={},
            Config=mock.ANY,
        )
        self.assertIsNone(result)
        self.assertIsNone(config_check.bad_config)

    def test_copy_object_client_error_returned_as_string(self):
        """
        If copying the object fails, return error as string.
        """
        src_bucket_name = uuid.uuid4().__str__()
        src_object_name = uuid.uuid4().__str__()
        dest_bucket_name = uuid.uuid4().__str__()
        multipart_chunksize_mb = randint(1, 10000)
        dest_object_name = uuid.uuid4().__str__()
        expected_result = uuid.uuid4().__str__()

        mock_s3_cli = Mock()
        error = ClientError({"Error": {}}, "operation name")
        error.__str__ = Mock()
        error.__str__.return_value = expected_result
        mock_s3_cli.copy.side_effect = error

        result = copy_files_to_archive.copy_object(
            mock_s3_cli,
            src_bucket_name,
            src_object_name,
            dest_bucket_name,
            multipart_chunksize_mb,
            dest_object_name,
        )

        mock_s3_cli.copy.assert_called_once_with(
            {"Bucket": src_bucket_name, "Key": src_object_name},
            dest_bucket_name,
            dest_object_name,
            ExtraArgs={},
            Config=mock.ANY,
        )
        self.assertEqual(expected_result, result)


if __name__ == "__main__":
    unittest.main(argv=["start"])
