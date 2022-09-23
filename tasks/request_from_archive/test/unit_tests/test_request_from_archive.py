"""
Name: test_request_from_archive.py

Description:  Unit tests for request_from_archive.py.
"""
import json
import os
import random
import unittest
import uuid
from random import randint, uniform
from test.request_helpers import LambdaContextMock, create_handler_event
from unittest import mock
from unittest.mock import MagicMock, Mock, call, patch

# noinspection PyPackageRequirements
import fastjsonschema as fastjsonschema

# noinspection PyPackageRequirements
from botocore.exceptions import ClientError
from orca_shared.recovery import shared_recovery
from orca_shared.recovery.shared_recovery import OrcaStatus

import request_from_archive

# Generating schema validators can take time, so do it once and reuse.
with open("schemas/output.json", "r") as raw_schema:
    _OUTPUT_VALIDATE = fastjsonschema.compile(json.loads(raw_schema.read()))


class TestRequestFromArchive(unittest.TestCase):
    """
    TestRequestFromArchive.
    """

    def setUp(self):
        os.environ.pop("CUMULUS_MESSAGE_ADAPTER_DISABLED", None)
        self.maxDiff = None

    def tearDown(self):
        os.environ.pop("PREFIX", None)
        os.environ.pop(request_from_archive.OS_ENVIRON_STATUS_UPDATE_QUEUE_URL_KEY, None)
        os.environ.pop(request_from_archive.OS_ENVIRON_RESTORE_EXPIRE_DAYS_KEY, None)
        os.environ.pop(request_from_archive.OS_ENVIRON_RESTORE_REQUEST_RETRIES_KEY, None)
        os.environ.pop(request_from_archive.OS_ENVIRON_ORCA_DEFAULT_ARCHIVE_BUCKET_KEY, None)
        os.environ.pop(request_from_archive.OS_ENVIRON_RESTORE_RETRY_SLEEP_SECS_KEY, None)
        os.environ.pop(request_from_archive.OS_ENVIRON_DEFAULT_RECOVERY_TYPE_KEY, None)

    @patch("request_from_archive.get_default_archive_bucket_name")
    @patch("request_from_archive.inner_task")
    @patch("request_from_archive.get_archive_recovery_type")
    def test_task_happy_path(
        self,
        mock_get_archive_recovery_type: MagicMock,
        mock_inner_task: MagicMock,
        mock_get_default_archive_bucket_name: MagicMock,
    ):
        """
        All variables present and valid.
        """
        job_id = uuid.uuid4().__str__()
        config = {
            request_from_archive.CONFIG_JOB_ID_KEY: job_id,
        }
        mock_event = {
            request_from_archive.EVENT_CONFIG_KEY: config,
        }
        max_retries = randint(0, 99)  # nosec
        retry_sleep_secs = uniform(0, 99)  # nosec
        recovery_type = "Bulk"
        exp_days = randint(0, 99)  # nosec
        db_queue_url = "http://" + uuid.uuid4().__str__() + ".blah"

        os.environ[request_from_archive.OS_ENVIRON_STATUS_UPDATE_QUEUE_URL_KEY] = db_queue_url
        os.environ[
            request_from_archive.OS_ENVIRON_RESTORE_REQUEST_RETRIES_KEY
        ] = max_retries.__str__()
        os.environ[
            request_from_archive.OS_ENVIRON_RESTORE_RETRY_SLEEP_SECS_KEY
        ] = retry_sleep_secs.__str__()
        os.environ[request_from_archive.OS_ENVIRON_DEFAULT_RECOVERY_TYPE_KEY] = recovery_type
        os.environ[
            request_from_archive.OS_ENVIRON_RESTORE_EXPIRE_DAYS_KEY
        ] = exp_days.__str__()

        request_from_archive.task(mock_event, None)

        mock_get_default_archive_bucket_name.assert_called_once_with(config)
        mock_get_archive_recovery_type.assert_called_once_with(config)
        mock_inner_task.assert_called_once_with(
            {
                request_from_archive.EVENT_CONFIG_KEY: {
                    request_from_archive.CONFIG_DEFAULT_BUCKET_OVERRIDE_KEY:
                        mock_get_default_archive_bucket_name.return_value,
                    request_from_archive.CONFIG_JOB_ID_KEY:
                        job_id,
                },
            },
            max_retries,
            retry_sleep_secs,
            mock_get_archive_recovery_type(config),
            exp_days,
            db_queue_url,
        )

    @patch("request_from_archive.get_default_archive_bucket_name")
    @patch("request_from_archive.inner_task")
    @patch("request_from_archive.get_archive_recovery_type")
    def test_task_default_for_missing_max_retries(
        self,
        mock_get_archive_recovery_type: MagicMock,
        mock_inner_task: MagicMock,
        mock_get_default_archive_bucket_name: MagicMock,
    ):
        """
        If max_retries missing, use default.
        """
        job_id = uuid.uuid4().__str__()
        config = {
            request_from_archive.CONFIG_JOB_ID_KEY: job_id,
        }
        mock_event = {
            request_from_archive.EVENT_CONFIG_KEY: config,
        }
        retry_sleep_secs = uniform(0, 99)  # nosec
        recovery_type = "Bulk"
        exp_days = randint(0, 99)  # nosec
        db_queue_url = "http://" + uuid.uuid4().__str__() + ".blah"

        os.environ[request_from_archive.OS_ENVIRON_STATUS_UPDATE_QUEUE_URL_KEY] = db_queue_url
        os.environ[
            request_from_archive.OS_ENVIRON_RESTORE_RETRY_SLEEP_SECS_KEY
        ] = retry_sleep_secs.__str__()
        os.environ[request_from_archive.OS_ENVIRON_DEFAULT_RECOVERY_TYPE_KEY] = recovery_type
        os.environ[
            request_from_archive.OS_ENVIRON_RESTORE_EXPIRE_DAYS_KEY
        ] = exp_days.__str__()

        request_from_archive.task(mock_event, None)

        mock_get_default_archive_bucket_name.assert_called_once_with(config)
        mock_get_archive_recovery_type.assert_called_once_with(config)
        mock_inner_task.assert_called_once_with(
            {
                request_from_archive.EVENT_CONFIG_KEY: {
                    request_from_archive.CONFIG_DEFAULT_BUCKET_OVERRIDE_KEY:
                        mock_get_default_archive_bucket_name.return_value,
                    request_from_archive.CONFIG_JOB_ID_KEY:
                        job_id,
                },
            },
            request_from_archive.DEFAULT_MAX_REQUEST_RETRIES,
            retry_sleep_secs,
            mock_get_archive_recovery_type(config),
            exp_days,
            db_queue_url,
        )

    @patch("request_from_archive.get_default_archive_bucket_name")
    @patch("request_from_archive.inner_task")
    @patch("request_from_archive.get_archive_recovery_type")
    def test_task_default_for_missing_sleep_secs(
        self,
        mock_get_archive_recovery_type: MagicMock,
        mock_inner_task: MagicMock,
        mock_get_default_archive_bucket_name: MagicMock,
    ):
        """
        If sleep_secs missing, use default.
        """
        job_id = uuid.uuid4().__str__()
        config = {
            request_from_archive.CONFIG_JOB_ID_KEY: job_id,
        }
        mock_event = {
            request_from_archive.EVENT_CONFIG_KEY: config,
        }
        max_retries = randint(0, 99)  # nosec
        recovery_type = "Bulk"
        exp_days = randint(0, 99)  # nosec
        db_queue_url = "http://" + uuid.uuid4().__str__() + ".blah"
        os.environ[request_from_archive.OS_ENVIRON_STATUS_UPDATE_QUEUE_URL_KEY] = db_queue_url

        os.environ[
            request_from_archive.OS_ENVIRON_RESTORE_REQUEST_RETRIES_KEY
        ] = max_retries.__str__()
        os.environ[request_from_archive.OS_ENVIRON_DEFAULT_RECOVERY_TYPE_KEY] = recovery_type
        os.environ[
            request_from_archive.OS_ENVIRON_RESTORE_EXPIRE_DAYS_KEY
        ] = exp_days.__str__()

        request_from_archive.task(mock_event, None)

        mock_get_default_archive_bucket_name.assert_called_once_with(config)
        mock_get_archive_recovery_type.assert_called_once_with(config)
        mock_inner_task.assert_called_once_with(
            {
                request_from_archive.EVENT_CONFIG_KEY: {
                    request_from_archive.CONFIG_DEFAULT_BUCKET_OVERRIDE_KEY:
                        mock_get_default_archive_bucket_name.return_value,
                    request_from_archive.CONFIG_JOB_ID_KEY:
                        job_id,
                },
            },
            max_retries,
            request_from_archive.DEFAULT_RESTORE_RETRY_SLEEP_SECS,
            mock_get_archive_recovery_type(config),
            exp_days,
            db_queue_url,
        )

    @patch("request_from_archive.get_default_archive_bucket_name")
    @patch("request_from_archive.inner_task")
    @patch("request_from_archive.get_archive_recovery_type")
    def test_task_default_for_missing_exp_days(
        self,
        mock_get_archive_recovery_type: MagicMock,
        mock_inner_task: MagicMock,
        mock_get_default_archive_bucket_name: MagicMock,
    ):
        """
        Uses default missing_exp_days if needed.
        """
        job_id = uuid.uuid4().__str__()
        config = {
            request_from_archive.CONFIG_JOB_ID_KEY: job_id,
        }
        mock_event = {
            request_from_archive.EVENT_CONFIG_KEY: config,
        }
        max_retries = randint(0, 99)  # nosec
        retry_sleep_secs = uniform(0, 99)  # nosec
        recovery_type = "Bulk"
        db_queue_url = "http://" + uuid.uuid4().__str__() + ".blah"

        os.environ[request_from_archive.OS_ENVIRON_STATUS_UPDATE_QUEUE_URL_KEY] = db_queue_url
        os.environ[
            request_from_archive.OS_ENVIRON_RESTORE_REQUEST_RETRIES_KEY
        ] = max_retries.__str__()
        os.environ[
            request_from_archive.OS_ENVIRON_RESTORE_RETRY_SLEEP_SECS_KEY
        ] = retry_sleep_secs.__str__()
        os.environ[request_from_archive.OS_ENVIRON_DEFAULT_RECOVERY_TYPE_KEY] = recovery_type

        request_from_archive.task(mock_event, None)

        mock_get_default_archive_bucket_name.assert_called_once_with(config)
        mock_get_archive_recovery_type.assert_called_once_with(config)
        mock_inner_task.assert_called_once_with(
            {
                request_from_archive.EVENT_CONFIG_KEY: {
                    request_from_archive.CONFIG_DEFAULT_BUCKET_OVERRIDE_KEY:
                        mock_get_default_archive_bucket_name.return_value,
                    request_from_archive.CONFIG_JOB_ID_KEY:
                        job_id,
                },
            },
            max_retries,
            retry_sleep_secs,
            mock_get_archive_recovery_type(config),
            request_from_archive.DEFAULT_RESTORE_EXPIRE_DAYS,
            db_queue_url,
        )

    @patch("request_from_archive.get_default_archive_bucket_name")
    @patch("request_from_archive.inner_task")
    @patch("request_from_archive.get_archive_recovery_type")
    def test_task_job_id_missing_generates(
        self,
        mock_get_archive_recovery_type: MagicMock,
        mock_inner_task: MagicMock,
        mock_get_default_archive_bucket_name: MagicMock,
    ):
        """
        If job_id missing, generates a new one.
        """
        config = {
            request_from_archive.CONFIG_JOB_ID_KEY: None,
        }
        mock_event = {
            request_from_archive.EVENT_CONFIG_KEY: config,
        }
        max_retries = randint(0, 99)  # nosec
        retry_sleep_secs = uniform(0, 99)  # nosec
        recovery_type = "Bulk"
        exp_days = randint(0, 99)  # nosec
        db_queue_url = "http://" + uuid.uuid4().__str__() + ".blah"
        job_id = uuid.uuid4()

        os.environ[request_from_archive.OS_ENVIRON_STATUS_UPDATE_QUEUE_URL_KEY] = db_queue_url
        os.environ[
            request_from_archive.OS_ENVIRON_RESTORE_REQUEST_RETRIES_KEY
        ] = max_retries.__str__()
        os.environ[
            request_from_archive.OS_ENVIRON_RESTORE_RETRY_SLEEP_SECS_KEY
        ] = retry_sleep_secs.__str__()
        os.environ[request_from_archive.OS_ENVIRON_DEFAULT_RECOVERY_TYPE_KEY] = recovery_type
        os.environ[
            request_from_archive.OS_ENVIRON_RESTORE_EXPIRE_DAYS_KEY
        ] = exp_days.__str__()

        with patch.object(uuid, "uuid4", return_value=job_id):
            request_from_archive.task(mock_event, None)

        mock_get_default_archive_bucket_name.assert_called_once_with(config)
        mock_get_archive_recovery_type.assert_called_once_with(config)
        mock_inner_task.assert_called_once_with(
            {
                request_from_archive.EVENT_CONFIG_KEY: {
                    request_from_archive.CONFIG_DEFAULT_BUCKET_OVERRIDE_KEY:
                        mock_get_default_archive_bucket_name.return_value,
                    request_from_archive.CONFIG_JOB_ID_KEY:
                        job_id.__str__(),
                },
            },
            max_retries,
            retry_sleep_secs,
            mock_get_archive_recovery_type(config),
            exp_days,
            db_queue_url,
        )

    # noinspection PyUnusedLocal
    @patch("request_from_archive.shared_recovery.create_status_for_job")
    @patch("time.sleep")
    @patch("request_from_archive.process_granule")
    @patch("request_from_archive.get_s3_object_information")
    @patch("boto3.client")
    def test_inner_task_happy_path(
        self,
        mock_boto3_client: MagicMock,
        mock_get_s3_object_information: MagicMock,
        mock_process_granule: MagicMock,
        mock_sleep: MagicMock,
        mock_create_status_for_job: MagicMock,
    ):
        """
        Basic path with multiple granules.
        """
        archive_bucket_name = uuid.uuid4().__str__()
        collection_multipart_chunksize_mb = random.randint(1, 10000)  # nosec
        file_key_0 = uuid.uuid4().__str__()
        file_key_1 = uuid.uuid4().__str__()
        file_dest_bucket_0 = uuid.uuid4().__str__()
        file_dest_bucket_1 = uuid.uuid4().__str__()
        job_id = uuid.uuid4().__str__()
        granule_id0 = uuid.uuid4().__str__()
        granule_id1 = uuid.uuid4().__str__()
        db_queue_url = "http://" + uuid.uuid4().__str__() + ".blah"
        file_0 = {
            request_from_archive.FILE_KEY_KEY: file_key_0,
            request_from_archive.FILE_DEST_BUCKET_KEY: file_dest_bucket_0,
        }
        expected_file0_output = {
            request_from_archive.FILE_PROCESSED_KEY: False,
            request_from_archive.FILE_FILENAME_KEY: file_key_0,
            request_from_archive.FILE_KEY_PATH_KEY: file_key_0,
            request_from_archive.FILE_RESTORE_DESTINATION_KEY: file_dest_bucket_0,
            request_from_archive.FILE_MULTIPART_CHUNKSIZE_MB_KEY:
                collection_multipart_chunksize_mb,
            request_from_archive.FILE_STATUS_ID_KEY: OrcaStatus.PENDING.value,
            request_from_archive.FILE_REQUEST_TIME_KEY: mock.ANY,
            request_from_archive.FILE_LAST_UPDATE_KEY: mock.ANY,
        }
        file_1 = {
            request_from_archive.FILE_KEY_KEY: file_key_1,
            request_from_archive.FILE_DEST_BUCKET_KEY: file_dest_bucket_1,
        }
        expected_file1_output = {
            request_from_archive.FILE_PROCESSED_KEY: False,
            request_from_archive.FILE_FILENAME_KEY: file_key_1,
            request_from_archive.FILE_KEY_PATH_KEY: file_key_1,
            request_from_archive.FILE_RESTORE_DESTINATION_KEY: file_dest_bucket_1,
            request_from_archive.FILE_MULTIPART_CHUNKSIZE_MB_KEY:
                collection_multipart_chunksize_mb,
            request_from_archive.FILE_STATUS_ID_KEY: OrcaStatus.PENDING.value,
            request_from_archive.FILE_REQUEST_TIME_KEY: mock.ANY,
            request_from_archive.FILE_LAST_UPDATE_KEY: mock.ANY,
        }

        expected_input_granule_files0 = [
            expected_file0_output,
        ]
        granule0 = {
            request_from_archive.GRANULE_GRANULE_ID_KEY: granule_id0,
            request_from_archive.GRANULE_KEYS_KEY: [
                file_0,
            ],
        }
        expected_input_granule0 = granule0.copy()
        expected_input_granule0[
            request_from_archive.GRANULE_RECOVER_FILES_KEY
        ] = expected_input_granule_files0

        expected_input_granule_files1 = [
            expected_file1_output,
        ]
        granule1 = {
            request_from_archive.GRANULE_GRANULE_ID_KEY: granule_id1,
            request_from_archive.GRANULE_KEYS_KEY: [
                file_1,
            ],
        }
        expected_input_granule1 = granule1.copy()
        expected_input_granule1[
            request_from_archive.GRANULE_RECOVER_FILES_KEY
        ] = expected_input_granule_files1

        event = {
            request_from_archive.EVENT_CONFIG_KEY: {
                request_from_archive.CONFIG_DEFAULT_BUCKET_OVERRIDE_KEY: archive_bucket_name,
                request_from_archive.CONFIG_JOB_ID_KEY: job_id,
                request_from_archive.CONFIG_MULTIPART_CHUNKSIZE_MB_KEY:
                    collection_multipart_chunksize_mb,
            },
            request_from_archive.EVENT_INPUT_KEY: {
                request_from_archive.INPUT_GRANULES_KEY: [granule0, granule1]
            },
        }
        max_retries = randint(0, 99)  # nosec
        retry_sleep_secs = randint(0, 99)  # nosec
        recovery_type = uuid.uuid4().__str__()
        restore_expire_days = randint(0, 99)  # nosec
        mock_s3_cli = mock_boto3_client("s3")

        mock_get_s3_object_information.return_value = {"StorageClass": "GLACIER"}

        result = request_from_archive.inner_task(
            event,
            max_retries,
            retry_sleep_secs,
            recovery_type,
            restore_expire_days,
            db_queue_url,
        )

        # Compare to orca_shared to verify schema.
        mock_create_status_for_job.assert_has_calls(
            [
                call(
                    job_id,
                    granule_id0,
                    archive_bucket_name,
                    [
                        {
                            request_from_archive.FILE_PROCESSED_KEY:
                                False,  # This value is changed by process_granule.
                            shared_recovery.FILENAME_KEY:
                                file_key_0,
                            shared_recovery.KEY_PATH_KEY:
                                file_key_0,
                            shared_recovery.RESTORE_DESTINATION_KEY:
                                file_dest_bucket_0,
                            shared_recovery.MULTIPART_CHUNKSIZE_KEY:
                                collection_multipart_chunksize_mb,
                            shared_recovery.STATUS_ID_KEY:
                                OrcaStatus.PENDING.value,
                            shared_recovery.REQUEST_TIME_KEY:
                                mock.ANY,
                            shared_recovery.LAST_UPDATE_KEY:
                                mock.ANY,
                        }
                    ],
                    db_queue_url,
                ),
                call(
                    job_id,
                    granule_id1,
                    archive_bucket_name,
                    [
                        {
                            request_from_archive.FILE_PROCESSED_KEY:
                                False,  # This value is changed by process_granule.
                            shared_recovery.FILENAME_KEY:
                                file_key_1,
                            shared_recovery.KEY_PATH_KEY:
                                file_key_1,
                            shared_recovery.RESTORE_DESTINATION_KEY:
                                file_dest_bucket_1,
                            shared_recovery.MULTIPART_CHUNKSIZE_KEY:
                                collection_multipart_chunksize_mb,
                            shared_recovery.STATUS_ID_KEY:
                                OrcaStatus.PENDING.value,
                            shared_recovery.REQUEST_TIME_KEY:
                                mock.ANY,
                            shared_recovery.LAST_UPDATE_KEY:
                                mock.ANY,
                        }
                    ],
                    db_queue_url,
                ),
            ]
        )
        self.assertEqual(2, mock_create_status_for_job.call_count)
        mock_process_granule.assert_has_calls(
            [
                call(
                    mock_s3_cli,
                    expected_input_granule0,
                    archive_bucket_name,
                    restore_expire_days,
                    max_retries,
                    retry_sleep_secs,
                    recovery_type,
                    job_id,
                    db_queue_url,
                ),
                call(
                    mock_s3_cli,
                    expected_input_granule1,
                    archive_bucket_name,
                    restore_expire_days,
                    max_retries,
                    retry_sleep_secs,
                    recovery_type,
                    job_id,
                    db_queue_url,
                ),
            ]
        )
        self.assertEqual(2, mock_process_granule.call_count)
        self.assertEqual(
            {
                "granules": [expected_input_granule0, expected_input_granule1],
                "asyncOperationId": job_id,
            },
            result,
        )

    # noinspection PyUnusedLocal
    @patch("request_from_archive.shared_recovery.create_status_for_job")
    @patch("time.sleep")
    @patch("request_from_archive.process_granule")
    @patch("request_from_archive.get_s3_object_information")
    @patch("boto3.client")
    def test_inner_task_expedited_recovery_type_conflicts_with_deep_archive(
        self,
        mock_boto3_client: MagicMock,
        mock_get_s3_object_information: MagicMock,
        mock_process_granule: MagicMock,
        mock_sleep: MagicMock,
        mock_create_status_for_job: MagicMock,
    ):
        """
        If the recovery type is 'Expedited', then files found with storage class
        'DEEP_ARCHIVE' cannot be recovered. Should mark file as processed, and move on.
        """
        archive_bucket_name = uuid.uuid4().__str__()
        collection_multipart_chunksize_mb = random.randint(1, 10000)  # nosec
        file_key_0 = uuid.uuid4().__str__()
        file_key_1 = uuid.uuid4().__str__()
        file_dest_bucket_0 = uuid.uuid4().__str__()
        file_dest_bucket_1 = uuid.uuid4().__str__()
        job_id = uuid.uuid4().__str__()
        granule_id0 = uuid.uuid4().__str__()
        granule_id1 = uuid.uuid4().__str__()
        db_queue_url = "http://" + uuid.uuid4().__str__() + ".blah"
        file_0 = {
            request_from_archive.FILE_KEY_KEY: file_key_0,
            request_from_archive.FILE_DEST_BUCKET_KEY: file_dest_bucket_0,
        }
        file_0_error_message = f"File '{file_key_0}' from bucket '{archive_bucket_name}' " \
                               f"is in storage class 'DEEP_ARCHIVE' " \
                               f"which is incompatible with recovery type 'Expedited'"
        expected_file0_output = {
            request_from_archive.FILE_PROCESSED_KEY: True,
            request_from_archive.FILE_FILENAME_KEY: file_key_0,
            request_from_archive.FILE_KEY_PATH_KEY: file_key_0,
            request_from_archive.FILE_RESTORE_DESTINATION_KEY: file_dest_bucket_0,
            request_from_archive.FILE_MULTIPART_CHUNKSIZE_MB_KEY:
                collection_multipart_chunksize_mb,
            request_from_archive.FILE_STATUS_ID_KEY: OrcaStatus.FAILED.value,
            request_from_archive.FILE_REQUEST_TIME_KEY: mock.ANY,
            request_from_archive.FILE_LAST_UPDATE_KEY: mock.ANY,
            request_from_archive.FILE_ERROR_MESSAGE_KEY: file_0_error_message,
            request_from_archive.FILE_COMPLETION_TIME_KEY: mock.ANY
        }
        file_1 = {
            request_from_archive.FILE_KEY_KEY: file_key_1,
            request_from_archive.FILE_DEST_BUCKET_KEY: file_dest_bucket_1,
        }
        expected_file1_output = {
            request_from_archive.FILE_PROCESSED_KEY: False,
            request_from_archive.FILE_FILENAME_KEY: file_key_1,
            request_from_archive.FILE_KEY_PATH_KEY: file_key_1,
            request_from_archive.FILE_RESTORE_DESTINATION_KEY: file_dest_bucket_1,
            request_from_archive.FILE_MULTIPART_CHUNKSIZE_MB_KEY:
                collection_multipart_chunksize_mb,
            request_from_archive.FILE_STATUS_ID_KEY: OrcaStatus.PENDING.value,
            request_from_archive.FILE_REQUEST_TIME_KEY: mock.ANY,
            request_from_archive.FILE_LAST_UPDATE_KEY: mock.ANY,
        }

        expected_input_granule_files0 = [
            expected_file0_output,
        ]
        granule0 = {
            request_from_archive.GRANULE_GRANULE_ID_KEY: granule_id0,
            request_from_archive.GRANULE_KEYS_KEY: [
                file_0,
            ],
        }
        expected_input_granule0 = granule0.copy()
        expected_input_granule0[
            request_from_archive.GRANULE_RECOVER_FILES_KEY
        ] = expected_input_granule_files0

        expected_input_granule_files1 = [
            expected_file1_output,
        ]
        granule1 = {
            request_from_archive.GRANULE_GRANULE_ID_KEY: granule_id1,
            request_from_archive.GRANULE_KEYS_KEY: [
                file_1,
            ],
        }
        expected_input_granule1 = granule1.copy()
        expected_input_granule1[
            request_from_archive.GRANULE_RECOVER_FILES_KEY
        ] = expected_input_granule_files1

        event = {
            request_from_archive.EVENT_CONFIG_KEY: {
                request_from_archive.CONFIG_DEFAULT_BUCKET_OVERRIDE_KEY: archive_bucket_name,
                request_from_archive.CONFIG_JOB_ID_KEY: job_id,
                request_from_archive.CONFIG_MULTIPART_CHUNKSIZE_MB_KEY:
                    collection_multipart_chunksize_mb,
            },
            request_from_archive.EVENT_INPUT_KEY: {
                request_from_archive.INPUT_GRANULES_KEY: [granule0, granule1]
            },
        }
        max_retries = randint(0, 99)  # nosec
        retry_sleep_secs = randint(0, 99)  # nosec
        recovery_type = "Expedited"
        restore_expire_days = randint(0, 99)  # nosec
        mock_s3_cli = mock_boto3_client("s3")

        mock_get_s3_object_information.side_effect = [
            {"StorageClass": "DEEP_ARCHIVE"},
            {"StorageClass": "GLACIER"},
        ]

        result = request_from_archive.inner_task(
            event,
            max_retries,
            retry_sleep_secs,
            recovery_type,
            restore_expire_days,
            db_queue_url,
        )

        # Compare to orca_shared to verify schema.
        mock_create_status_for_job.assert_has_calls(
            [
                call(
                    job_id,
                    granule_id0,
                    archive_bucket_name,
                    [
                        {
                            request_from_archive.FILE_PROCESSED_KEY:
                                True,
                            shared_recovery.FILENAME_KEY:
                                file_key_0,
                            shared_recovery.KEY_PATH_KEY:
                                file_key_0,
                            shared_recovery.RESTORE_DESTINATION_KEY:
                                file_dest_bucket_0,
                            shared_recovery.MULTIPART_CHUNKSIZE_KEY:
                                collection_multipart_chunksize_mb,
                            shared_recovery.STATUS_ID_KEY:
                                OrcaStatus.FAILED.value,
                            shared_recovery.REQUEST_TIME_KEY:
                                mock.ANY,
                            shared_recovery.LAST_UPDATE_KEY:
                                mock.ANY,
                            shared_recovery.ERROR_MESSAGE_KEY:
                                file_0_error_message,
                            shared_recovery.COMPLETION_TIME_KEY:
                                mock.ANY,
                        }
                    ],
                    db_queue_url,
                ),
                call(
                    job_id,
                    granule_id1,
                    archive_bucket_name,
                    [
                        {
                            request_from_archive.FILE_PROCESSED_KEY:
                                False,  # This value is changed by process_granule.
                            shared_recovery.FILENAME_KEY:
                                file_key_1,
                            shared_recovery.KEY_PATH_KEY:
                                file_key_1,
                            shared_recovery.RESTORE_DESTINATION_KEY:
                                file_dest_bucket_1,
                            shared_recovery.MULTIPART_CHUNKSIZE_KEY:
                                collection_multipart_chunksize_mb,
                            shared_recovery.STATUS_ID_KEY:
                                OrcaStatus.PENDING.value,
                            shared_recovery.REQUEST_TIME_KEY:
                                mock.ANY,
                            shared_recovery.LAST_UPDATE_KEY:
                                mock.ANY,
                        }
                    ],
                    db_queue_url,
                ),
            ]
        )
        self.assertEqual(2, mock_create_status_for_job.call_count)
        mock_process_granule.assert_has_calls(
            [
                call(
                    mock_s3_cli,
                    expected_input_granule0,
                    archive_bucket_name,
                    restore_expire_days,
                    max_retries,
                    retry_sleep_secs,
                    recovery_type,
                    job_id,
                    db_queue_url,
                ),
                call(
                    mock_s3_cli,
                    expected_input_granule1,
                    archive_bucket_name,
                    restore_expire_days,
                    max_retries,
                    retry_sleep_secs,
                    recovery_type,
                    job_id,
                    db_queue_url,
                ),
            ]
        )
        self.assertEqual(2, mock_process_granule.call_count)
        self.assertEqual(
            {
                "granules": [expected_input_granule0, expected_input_granule1],
                "asyncOperationId": job_id,
            },
            result,
        )

    # noinspection PyUnusedLocal
    @patch("request_from_archive.shared_recovery.create_status_for_job")
    @patch("time.sleep")
    @patch("request_from_archive.process_granule")
    @patch("request_from_archive.get_s3_object_information")
    @patch("boto3.client")
    def test_inner_task_error_posting_status_raises(
        self,
        mock_boto3_client: MagicMock,
        mock_get_s3_object_information: MagicMock,
        mock_process_granule: MagicMock,
        mock_sleep: MagicMock,
        mock_create_status_for_job: MagicMock,
    ):
        """
        If posting to status DB Queue fails, raise error.
        """
        archive_bucket_name = uuid.uuid4().__str__()
        collection_multipart_chunksize_mb = random.randint(1, 10000)  # nosec
        file_key_0 = uuid.uuid4().__str__()
        file_key_1 = uuid.uuid4().__str__()
        file_dest_bucket_0 = uuid.uuid4().__str__()
        file_dest_bucket_1 = uuid.uuid4().__str__()
        job_id = uuid.uuid4().__str__()
        granule_id0 = uuid.uuid4().__str__()
        granule_id1 = uuid.uuid4().__str__()
        db_queue_url = "http://" + uuid.uuid4().__str__() + ".blah"
        file_0 = {
            request_from_archive.FILE_KEY_KEY: file_key_0,
            request_from_archive.FILE_DEST_BUCKET_KEY: file_dest_bucket_0,
        }
        expected_file0_output = {
            request_from_archive.FILE_PROCESSED_KEY: False,
            request_from_archive.FILE_FILENAME_KEY: file_key_0,
            request_from_archive.FILE_KEY_PATH_KEY: file_key_0,
            request_from_archive.FILE_RESTORE_DESTINATION_KEY: file_dest_bucket_0,
            request_from_archive.FILE_MULTIPART_CHUNKSIZE_MB_KEY:
                collection_multipart_chunksize_mb,
            request_from_archive.FILE_STATUS_ID_KEY: OrcaStatus.PENDING.value,
            "request_time": mock.ANY,
            "last_update": mock.ANY,
        }
        file_1 = {
            request_from_archive.FILE_KEY_KEY: file_key_1,
            request_from_archive.FILE_DEST_BUCKET_KEY: file_dest_bucket_1,
        }
        expected_file1_output = {
            request_from_archive.FILE_PROCESSED_KEY: False,
            "filename": file_key_1,
            "key_path": file_key_1,
            "restore_destination": file_dest_bucket_1,
            "multipart_chunksize_mb": collection_multipart_chunksize_mb,
            "status_id": OrcaStatus.PENDING.value,
            "request_time": mock.ANY,
            "last_update": mock.ANY,
        }

        expected_input_granule_files0 = [
            expected_file0_output,
        ]
        granule0 = {
            request_from_archive.GRANULE_GRANULE_ID_KEY: granule_id0,
            request_from_archive.GRANULE_KEYS_KEY: [
                file_0,
            ],
        }
        expected_input_granule0 = granule0.copy()
        expected_input_granule0[
            request_from_archive.GRANULE_RECOVER_FILES_KEY
        ] = expected_input_granule_files0

        expected_input_granule_files1 = [
            expected_file1_output,
        ]
        granule1 = {
            request_from_archive.GRANULE_GRANULE_ID_KEY: granule_id1,
            request_from_archive.GRANULE_KEYS_KEY: [
                file_1,
            ],
        }
        expected_input_granule1 = granule1.copy()
        expected_input_granule1[
            request_from_archive.GRANULE_RECOVER_FILES_KEY
        ] = expected_input_granule_files1

        event = {
            request_from_archive.EVENT_CONFIG_KEY: {
                request_from_archive.CONFIG_DEFAULT_BUCKET_OVERRIDE_KEY: archive_bucket_name,
                request_from_archive.CONFIG_JOB_ID_KEY: job_id,
                request_from_archive.CONFIG_MULTIPART_CHUNKSIZE_MB_KEY:
                    collection_multipart_chunksize_mb,
            },
            request_from_archive.EVENT_INPUT_KEY: {
                request_from_archive.INPUT_GRANULES_KEY: [granule0, granule1]
            },
        }
        max_retries = randint(0, 99)  # nosec
        retry_sleep_secs = randint(0, 99)  # nosec
        recovery_type = uuid.uuid4().__str__()
        restore_expire_days = randint(0, 99)  # nosec

        mock_get_s3_object_information.return_value = {"StorageClass": "DEEP_ARCHIVE"}

        mock_create_status_for_job.side_effect = Exception("mock insert failed error")

        with self.assertRaises(Exception) as cm:
            request_from_archive.inner_task(
                event,
                max_retries,
                retry_sleep_secs,
                recovery_type,
                restore_expire_days,
                db_queue_url,
            )
        self.assertEqual(
            f"Unable to send message to QUEUE '{db_queue_url}'", str(cm.exception)
        )

        # Compare to orca_shared to verify schema.
        mock_create_status_for_job.assert_has_calls(
            [
                call(
                    job_id,
                    granule_id0,
                    archive_bucket_name,
                    [
                        {
                            request_from_archive.FILE_PROCESSED_KEY:
                            False,  # This value is changed by process_granule.
                            shared_recovery.FILENAME_KEY:
                            file_key_0,
                            shared_recovery.KEY_PATH_KEY:
                            file_key_0,
                            shared_recovery.RESTORE_DESTINATION_KEY:
                            file_dest_bucket_0,
                            shared_recovery.MULTIPART_CHUNKSIZE_KEY:
                                collection_multipart_chunksize_mb,
                            shared_recovery.STATUS_ID_KEY:
                                OrcaStatus.PENDING.value,
                            shared_recovery.REQUEST_TIME_KEY:
                                mock.ANY,
                            shared_recovery.LAST_UPDATE_KEY:
                                mock.ANY,
                        }
                    ],
                    db_queue_url,
                )
            ]
            * (max_retries + 1)
        )
        self.assertEqual(max_retries + 1, mock_create_status_for_job.call_count)
        self.assertEqual(0, mock_process_granule.call_count)

    def test_inner_task_missing_archive_bucket_name_raises(self):
        try:
            request_from_archive.inner_task(
                {request_from_archive.EVENT_CONFIG_KEY: dict()},
                randint(0, 99),  # nosec
                randint(0, 99),  # nosec
                uuid.uuid4().__str__(),
                randint(0, 99),  # nosec
                "https://db.queue.url",
            )
            self.fail("Error not raised.")
        except request_from_archive.RestoreRequestError:
            pass

    # noinspection PyUnusedLocal
    @patch("request_from_archive.shared_recovery.create_status_for_job")
    @patch("time.sleep")
    @patch("request_from_archive.process_granule")
    @patch("request_from_archive.get_s3_object_information")
    @patch("boto3.client")
    def test_inner_task_missing_files_do_not_halt(
        self,
        mock_boto3_client: MagicMock,
        mock_get_s3_object_information: MagicMock,
        mock_process_granule: MagicMock,
        mock_sleep: MagicMock,
        mock_create_status_for_job: MagicMock,
    ):
        """
        A return of None from get_s3_object_information should ignore the file and continue.
        """
        archive_bucket_name = uuid.uuid4().__str__()
        collection_multipart_chunksize_mb = random.randint(1, 10000)  # nosec
        file_key_0 = uuid.uuid4().__str__()
        file_key_1 = uuid.uuid4().__str__()
        missing_file_key = uuid.uuid4().__str__()
        file_dest_bucket_0 = uuid.uuid4().__str__()
        file_dest_bucket_1 = uuid.uuid4().__str__()
        missing_file_dest_bucket = uuid.uuid4().__str__()
        job_id = uuid.uuid4().__str__()
        granule_id = uuid.uuid4().__str__()
        db_queue_url = "http://" + uuid.uuid4().__str__() + ".blah"
        file_0 = {
            request_from_archive.FILE_KEY_KEY: file_key_0,
            request_from_archive.FILE_DEST_BUCKET_KEY: file_dest_bucket_0,
        }
        expected_file0_output = {
            request_from_archive.FILE_PROCESSED_KEY: False,
            request_from_archive.FILE_FILENAME_KEY: file_key_0,
            request_from_archive.FILE_KEY_PATH_KEY: file_key_0,
            request_from_archive.FILE_RESTORE_DESTINATION_KEY: file_dest_bucket_0,
            request_from_archive.FILE_MULTIPART_CHUNKSIZE_MB_KEY:
                collection_multipart_chunksize_mb,
            request_from_archive.FILE_STATUS_ID_KEY: OrcaStatus.PENDING.value,
            request_from_archive.FILE_REQUEST_TIME_KEY: mock.ANY,
            request_from_archive.FILE_LAST_UPDATE_KEY: mock.ANY,
        }
        file_1 = {
            request_from_archive.FILE_KEY_KEY: file_key_1,
            request_from_archive.FILE_DEST_BUCKET_KEY: file_dest_bucket_1,
        }
        expected_file1_output = {
            request_from_archive.FILE_PROCESSED_KEY: False,
            request_from_archive.FILE_FILENAME_KEY: file_key_1,
            request_from_archive.FILE_KEY_PATH_KEY: file_key_1,
            request_from_archive.FILE_RESTORE_DESTINATION_KEY: file_dest_bucket_1,
            request_from_archive.FILE_MULTIPART_CHUNKSIZE_MB_KEY:
                collection_multipart_chunksize_mb,
            request_from_archive.FILE_STATUS_ID_KEY: OrcaStatus.PENDING.value,
            request_from_archive.FILE_REQUEST_TIME_KEY: mock.ANY,
            request_from_archive.FILE_LAST_UPDATE_KEY: mock.ANY,
        }

        missing_file = {
            request_from_archive.FILE_KEY_KEY: missing_file_key,
            request_from_archive.FILE_DEST_BUCKET_KEY: missing_file_dest_bucket,
            request_from_archive.FILE_MULTIPART_CHUNKSIZE_MB_KEY:
                collection_multipart_chunksize_mb,
        }
        expected_missing_file_output = {
            request_from_archive.FILE_PROCESSED_KEY:
                True,
            request_from_archive.FILE_FILENAME_KEY:
                missing_file_key,
            request_from_archive.FILE_KEY_PATH_KEY:
                missing_file_key,
            request_from_archive.FILE_RESTORE_DESTINATION_KEY:
                missing_file_dest_bucket,
            request_from_archive.FILE_MULTIPART_CHUNKSIZE_MB_KEY:
                collection_multipart_chunksize_mb,
            request_from_archive.FILE_STATUS_ID_KEY:
                OrcaStatus.FAILED.value,
            request_from_archive.FILE_REQUEST_TIME_KEY:
                mock.ANY,
            request_from_archive.FILE_LAST_UPDATE_KEY:
                mock.ANY,
            request_from_archive.FILE_ERROR_MESSAGE_KEY:
                f"'{missing_file_key}' does not exist in '{archive_bucket_name}' bucket",
            request_from_archive.FILE_COMPLETION_TIME_KEY:
                mock.ANY,
        }

        expected_input_granule_files = [
            expected_file0_output,
            expected_missing_file_output,
            expected_file1_output,
        ]
        granule = {
            request_from_archive.GRANULE_GRANULE_ID_KEY: granule_id,
            request_from_archive.GRANULE_KEYS_KEY: [
                file_0,
                missing_file,
                file_1,
            ],
        }
        expected_input_granule = granule.copy()
        expected_input_granule[
            request_from_archive.GRANULE_RECOVER_FILES_KEY
        ] = expected_input_granule_files
        event = {
            request_from_archive.EVENT_CONFIG_KEY: {
                request_from_archive.CONFIG_DEFAULT_BUCKET_OVERRIDE_KEY: archive_bucket_name,
                request_from_archive.CONFIG_JOB_ID_KEY: job_id,
                request_from_archive.CONFIG_MULTIPART_CHUNKSIZE_MB_KEY:
                    collection_multipart_chunksize_mb,
            },
            request_from_archive.EVENT_INPUT_KEY: {
                request_from_archive.INPUT_GRANULES_KEY: [granule]
            },
        }
        max_retries = randint(0, 99)  # nosec
        retry_sleep_secs = randint(0, 99)  # nosec
        recovery_type = uuid.uuid4().__str__()
        restore_expire_days = randint(0, 99)  # nosec
        mock_s3_cli = mock_boto3_client("s3")

        # noinspection PyUnusedLocal
        def get_s3_object_information_return_func(
            input_s3_cli, input_archive_bucket_name, input_file_key
        ):
            if input_file_key in [file_key_0, file_key_1]:
                return {"StorageClass": "DEEP_ARCHIVE"}
            else:
                return None

        mock_get_s3_object_information.side_effect = (
            get_s3_object_information_return_func
        )

        result = request_from_archive.inner_task(
            event,
            max_retries,
            retry_sleep_secs,
            recovery_type,
            restore_expire_days,
            db_queue_url,
        )

        mock_create_status_for_job.assert_called_once_with(
            job_id,
            granule_id,
            archive_bucket_name,
            # Compare to orca_shared to verify schema.
            [
                {
                    request_from_archive.FILE_PROCESSED_KEY:
                        False,  # This value is changed by process_granule.
                    shared_recovery.FILENAME_KEY:
                        file_key_0,
                    shared_recovery.KEY_PATH_KEY:
                        file_key_0,
                    shared_recovery.RESTORE_DESTINATION_KEY:
                        file_dest_bucket_0,
                    shared_recovery.MULTIPART_CHUNKSIZE_KEY:
                        collection_multipart_chunksize_mb,
                    shared_recovery.STATUS_ID_KEY:
                        OrcaStatus.PENDING.value,
                    shared_recovery.REQUEST_TIME_KEY:
                        mock.ANY,
                    shared_recovery.LAST_UPDATE_KEY:
                        mock.ANY,
                },
                {
                    request_from_archive.FILE_PROCESSED_KEY:
                        True,  # Set to `True` when not found.
                    shared_recovery.FILENAME_KEY:
                        missing_file_key,
                    shared_recovery.KEY_PATH_KEY:
                        missing_file_key,
                    shared_recovery.RESTORE_DESTINATION_KEY:
                        missing_file_dest_bucket,
                    shared_recovery.MULTIPART_CHUNKSIZE_KEY:
                        collection_multipart_chunksize_mb,
                    shared_recovery.STATUS_ID_KEY:
                        OrcaStatus.FAILED.value,
                    shared_recovery.REQUEST_TIME_KEY:
                        mock.ANY,
                    shared_recovery.LAST_UPDATE_KEY:
                        mock.ANY,
                    shared_recovery.ERROR_MESSAGE_KEY:
                        f"'{missing_file_key}' does not exist in '{archive_bucket_name}' bucket",
                    shared_recovery.COMPLETION_TIME_KEY:
                        mock.ANY,
                },
                {
                    request_from_archive.FILE_PROCESSED_KEY:
                        False,  # This value is changed by process_granule.
                    shared_recovery.FILENAME_KEY:
                        file_key_1,
                    shared_recovery.KEY_PATH_KEY:
                        file_key_1,
                    shared_recovery.RESTORE_DESTINATION_KEY:
                        file_dest_bucket_1,
                    shared_recovery.MULTIPART_CHUNKSIZE_KEY:
                        collection_multipart_chunksize_mb,
                    shared_recovery.STATUS_ID_KEY:
                        OrcaStatus.PENDING.value,
                    shared_recovery.REQUEST_TIME_KEY:
                        mock.ANY,
                    shared_recovery.LAST_UPDATE_KEY:
                        mock.ANY,
                },
            ],
            db_queue_url,
        )
        mock_process_granule.assert_called_once_with(
            mock_s3_cli,
            expected_input_granule,
            archive_bucket_name,
            restore_expire_days,
            max_retries,
            retry_sleep_secs,
            recovery_type,
            job_id,
            db_queue_url,
        )
        self.assertEqual(
            {
                "granules": [expected_input_granule],
                "asyncOperationId": job_id,
            },
            result,
        )

    @patch.dict(
        os.environ,
        {
            request_from_archive.OS_ENVIRON_ORCA_DEFAULT_ARCHIVE_BUCKET_KEY: uuid.uuid4().__str__()
        },
        clear=True,
    )
    def test_get_default_archive_bucket_name_returns_override_if_present(self):
        bucket = Mock()
        result = request_from_archive.get_default_archive_bucket_name(
            {request_from_archive.CONFIG_DEFAULT_BUCKET_OVERRIDE_KEY: bucket}
        )
        self.assertEqual(bucket, result)

    @patch.dict(
        os.environ,
        {
            request_from_archive.OS_ENVIRON_ORCA_DEFAULT_ARCHIVE_BUCKET_KEY: uuid.uuid4().__str__()
        },
        clear=True,
    )
    def test_get_default_archive_bucket_name_returns_default_bucket_if_no_override(
        self,
    ):
        bucket = os.environ[request_from_archive.OS_ENVIRON_ORCA_DEFAULT_ARCHIVE_BUCKET_KEY]
        result = request_from_archive.get_default_archive_bucket_name({})
        self.assertEqual(bucket, result)

    @patch.dict(
        os.environ,
        {
            request_from_archive.OS_ENVIRON_ORCA_DEFAULT_ARCHIVE_BUCKET_KEY: uuid.uuid4().__str__()
        },
        clear=True,
    )
    def test_get_default_archive_bucket_name_returns_default_bucket_if_none_override(
        self,
    ):
        bucket = os.environ[request_from_archive.OS_ENVIRON_ORCA_DEFAULT_ARCHIVE_BUCKET_KEY]
        result = request_from_archive.get_default_archive_bucket_name(
            {
                request_from_archive.CONFIG_DEFAULT_BUCKET_OVERRIDE_KEY: None,
            }
        )
        self.assertEqual(bucket, result)

    @patch.dict(
        os.environ,
        {
            request_from_archive.OS_ENVIRON_ORCA_DEFAULT_ARCHIVE_BUCKET_KEY: uuid.uuid4().__str__()
        },
        clear=True,
    )
    def test_get_default_archive_bucket_name_returns_env_bucket_if_no_other(self):
        bucket = os.environ[request_from_archive.OS_ENVIRON_ORCA_DEFAULT_ARCHIVE_BUCKET_KEY]
        result = request_from_archive.get_default_archive_bucket_name(
            {request_from_archive.CONFIG_DEFAULT_BUCKET_OVERRIDE_KEY: None}
        )
        self.assertEqual(bucket, result)

    def test_get_default_archive_bucket_name_no_bucket_raises_error(self):
        os.environ.pop(request_from_archive.OS_ENVIRON_ORCA_DEFAULT_ARCHIVE_BUCKET_KEY, None)
        with self.assertRaises(KeyError) as cm:
            request_from_archive.get_default_archive_bucket_name(
                {request_from_archive.CONFIG_DEFAULT_BUCKET_OVERRIDE_KEY: None}
            )
        self.assertEqual("'ORCA_DEFAULT_BUCKET'", str(cm.exception))

    @patch.dict(
        os.environ,
        {},
        clear=True,
    )
    def test_get_archive_recovery_no_value_defaults_to_standard(self):
        """
        If no values are present, return "Standard"
        """
        config = {request_from_archive.CONFIG_DEFAULT_RECOVERY_TYPE_OVERRIDE_KEY: None}
        result = request_from_archive.get_archive_recovery_type(config)
        self.assertEqual(
            "Standard", result
        )

    @patch.dict(
        os.environ,
        {request_from_archive.OS_ENVIRON_DEFAULT_RECOVERY_TYPE_KEY: "Bulk"},
        clear=True,
    )
    def test_get_archive_recovery_type_valid_config_overrides(self):
        """
        Returns the value in config if valid, overriding other values.
        """
        config = {request_from_archive.CONFIG_DEFAULT_RECOVERY_TYPE_OVERRIDE_KEY: "Bulk"}
        result = request_from_archive.get_archive_recovery_type(config)
        self.assertEqual(
            result, config[request_from_archive.CONFIG_DEFAULT_RECOVERY_TYPE_OVERRIDE_KEY]
        )

    @patch("cumulus_logger.CumulusLogger.error")
    def test_get_archive_recovery_type_invalid_config_raises_valueerror(
        self, mock_logger_error: MagicMock
    ):
        """
        Raises ValueError if invalid config value.
        """
        recovery_type = uuid.uuid4().__str__()  # nosec
        config = {request_from_archive.CONFIG_DEFAULT_RECOVERY_TYPE_OVERRIDE_KEY: recovery_type}
        with self.assertRaises(ValueError) as ve:
            request_from_archive.get_archive_recovery_type(config)
        self.assertEqual(
            f"Invalid restore type value of '{recovery_type}'.",
            ve.exception.args[0],
        )
        mock_logger_error.assert_called_once_with(
            f"Invalid restore type value of "
            f"'{config[request_from_archive.CONFIG_DEFAULT_RECOVERY_TYPE_OVERRIDE_KEY]}'."
        )

    @patch.dict(
        os.environ,
        {request_from_archive.OS_ENVIRON_DEFAULT_RECOVERY_TYPE_KEY: "Bulk"},
        clear=True,
    )
    def test_get_archive_recovery_type_env_variable_valid(self):
        """
        Returns the value in env variable if valid and config is None.
        """
        config = {request_from_archive.CONFIG_DEFAULT_RECOVERY_TYPE_OVERRIDE_KEY: None}
        result = request_from_archive.get_archive_recovery_type(config)
        self.assertEqual(
            result, os.environ[request_from_archive.OS_ENVIRON_DEFAULT_RECOVERY_TYPE_KEY]
        )

    @patch("cumulus_logger.CumulusLogger.error")
    @patch.dict(
        os.environ,
        {request_from_archive.OS_ENVIRON_DEFAULT_RECOVERY_TYPE_KEY: "Nope"},
        clear=True,
    )
    def test_get_archive_recovery_type_env_variable_invalid_raises_valueerror(
        self, mock_logger_error: MagicMock
    ):
        """
        Returns ValueError if the value in env variable if invalid and config is None.
        """
        config = {request_from_archive.CONFIG_DEFAULT_RECOVERY_TYPE_OVERRIDE_KEY: None}
        with self.assertRaises(ValueError) as ve:
            request_from_archive.get_archive_recovery_type(config)
        self.assertEqual(
            f"Invalid restore type value of "
            f"'{os.environ[request_from_archive.OS_ENVIRON_DEFAULT_RECOVERY_TYPE_KEY]}'.",
            ve.exception.args[0],
        )
        mock_logger_error.assert_called_once_with(
            f"Invalid restore type value of "
            f"'{os.environ[request_from_archive.OS_ENVIRON_DEFAULT_RECOVERY_TYPE_KEY]}'."
        )

    @patch("time.sleep")
    @patch("request_from_archive.restore_object")
    def test_process_granule_minimal_path(
        self, mock_restore_object: MagicMock, mock_sleep: MagicMock
    ):
        mock_s3 = Mock()
        max_retries = randint(10, 999)  # nosec
        archive_bucket_name = uuid.uuid4().__str__()
        retry_sleep_secs = randint(0, 99)  # nosec
        recovery_type = uuid.uuid4().__str__()
        restore_expire_days = randint(0, 99)  # nosec
        granule_id = uuid.uuid4().__str__()
        file_name_0 = uuid.uuid4().__str__()
        dest_bucket_0 = uuid.uuid4().__str__()
        file_name_1 = uuid.uuid4().__str__()
        dest_bucket_1 = uuid.uuid4().__str__()
        job_id = uuid.uuid4().__str__()
        db_queue_url = "http://" + uuid.uuid4().__str__() + ".blah"

        granule = {
            request_from_archive.GRANULE_GRANULE_ID_KEY: granule_id,
            request_from_archive.GRANULE_RECOVER_FILES_KEY: [
                {
                    request_from_archive.FILE_PROCESSED_KEY: False,
                    request_from_archive.FILE_FILENAME_KEY: os.path.basename(file_name_0),
                    request_from_archive.FILE_KEY_PATH_KEY: file_name_0,
                    request_from_archive.FILE_RESTORE_DESTINATION_KEY: dest_bucket_0,
                    request_from_archive.FILE_STATUS_ID_KEY: 1,
                },
                {
                    request_from_archive.FILE_PROCESSED_KEY: False,
                    request_from_archive.FILE_FILENAME_KEY: os.path.basename(file_name_1),
                    request_from_archive.FILE_KEY_PATH_KEY: file_name_1,
                    request_from_archive.FILE_RESTORE_DESTINATION_KEY: dest_bucket_1,
                    request_from_archive.FILE_STATUS_ID_KEY: 1,
                },
            ],
        }

        request_from_archive.process_granule(
            mock_s3,
            granule,
            archive_bucket_name,
            restore_expire_days,
            max_retries,
            retry_sleep_secs,
            recovery_type,
            job_id,
            db_queue_url,
        )

        self.assertTrue(
            granule[request_from_archive.GRANULE_RECOVER_FILES_KEY][0][
                request_from_archive.FILE_PROCESSED_KEY
            ]
        )
        self.assertTrue(
            granule[request_from_archive.GRANULE_RECOVER_FILES_KEY][1][
                request_from_archive.FILE_PROCESSED_KEY
            ]
        )

        mock_restore_object.assert_has_calls(
            [
                call(
                    mock_s3,
                    file_name_0,
                    restore_expire_days,
                    archive_bucket_name,
                    1,
                    job_id,
                    recovery_type,
                ),
                call(
                    mock_s3,
                    file_name_1,
                    restore_expire_days,
                    archive_bucket_name,
                    1,
                    job_id,
                    recovery_type,
                ),
            ]
        )
        self.assertEqual(2, mock_restore_object.call_count)
        mock_sleep.assert_not_called()

    @patch("time.sleep")
    @patch("request_from_archive.restore_object")
    def test_process_granule_one_client_or_key_error_retries(
        self, mock_restore_object: MagicMock, mock_sleep: MagicMock
    ):
        mock_s3 = Mock()
        max_retries = 5
        archive_bucket_name = uuid.uuid4().__str__()
        retry_sleep_secs = randint(0, 99)  # nosec
        recovery_type = uuid.uuid4().__str__()
        restore_expire_days = randint(0, 99)  # nosec
        granule_id = uuid.uuid4().__str__()
        file_name_0 = uuid.uuid4().__str__()
        dest_bucket_0 = uuid.uuid4().__str__()
        job_id = uuid.uuid4().__str__()
        db_queue_url = "http://" + uuid.uuid4().__str__() + ".blah"

        granule = {
            request_from_archive.GRANULE_GRANULE_ID_KEY: granule_id,
            request_from_archive.GRANULE_RECOVER_FILES_KEY: [
                {
                    request_from_archive.FILE_FILENAME_KEY: os.path.basename(file_name_0),
                    request_from_archive.FILE_KEY_PATH_KEY: file_name_0,
                    request_from_archive.FILE_RESTORE_DESTINATION_KEY: dest_bucket_0,
                    request_from_archive.FILE_PROCESSED_KEY: False,
                    request_from_archive.FILE_STATUS_ID_KEY: 1,
                }
            ],
        }

        mock_restore_object.side_effect = [ClientError({}, ""), None]

        request_from_archive.process_granule(
            mock_s3,
            granule,
            archive_bucket_name,
            restore_expire_days,
            max_retries,
            retry_sleep_secs,
            recovery_type,
            job_id,
            db_queue_url,
        )

        self.assertTrue(
            granule[request_from_archive.GRANULE_RECOVER_FILES_KEY][0][
                request_from_archive.FILE_PROCESSED_KEY
            ]
        )
        mock_restore_object.assert_has_calls(
            [
                call(
                    mock_s3,
                    file_name_0,
                    restore_expire_days,
                    archive_bucket_name,
                    1,
                    job_id,
                    recovery_type,
                ),
                call(
                    mock_s3,
                    file_name_0,
                    restore_expire_days,
                    archive_bucket_name,
                    2,
                    job_id,
                    recovery_type,
                ),
            ]
        )
        self.assertEqual(2, mock_restore_object.call_count)
        mock_sleep.assert_has_calls([call(retry_sleep_secs)])
        self.assertEqual(1, mock_sleep.call_count)

    @patch("orca_shared.recovery.shared_recovery.update_status_for_file")
    @patch("time.sleep")
    @patch("request_from_archive.restore_object")
    @patch("cumulus_logger.CumulusLogger.error")
    def test_process_granule_client_errors_retries_until_cap(
        self,
        mock_logger_error: MagicMock,
        mock_restore_object: MagicMock,
        mock_sleep: MagicMock,
        mock_update_status_for_file: MagicMock,
    ):
        mock_s3 = Mock()
        max_retries = randint(3, 20)  # nosec
        archive_bucket_name = uuid.uuid4().__str__()
        retry_sleep_secs = randint(0, 99)  # nosec
        recovery_type = uuid.uuid4().__str__()
        restore_expire_days = randint(0, 99)  # nosec
        granule_id = uuid.uuid4().__str__()
        file_name_0 = uuid.uuid4().__str__()
        dest_bucket_0 = uuid.uuid4().__str__()
        job_id = uuid.uuid4().__str__()
        db_queue_url = "http://" + uuid.uuid4().__str__() + ".blah"

        granule = {
            request_from_archive.GRANULE_GRANULE_ID_KEY: granule_id,
            request_from_archive.GRANULE_RECOVER_FILES_KEY: [
                {
                    request_from_archive.FILE_FILENAME_KEY: os.path.basename(file_name_0),
                    request_from_archive.FILE_KEY_PATH_KEY: file_name_0,
                    request_from_archive.FILE_RESTORE_DESTINATION_KEY: dest_bucket_0,
                    request_from_archive.FILE_PROCESSED_KEY: False,
                    request_from_archive.FILE_STATUS_ID_KEY: 1,
                },
            ],
        }

        expected_error = ClientError({}, "")
        mock_restore_object.side_effect = expected_error

        try:
            request_from_archive.process_granule(
                mock_s3,
                granule,
                archive_bucket_name,
                restore_expire_days,
                max_retries,
                retry_sleep_secs,
                recovery_type,
                job_id,
                db_queue_url,
            )
            self.fail("Error not Raised.")
        # except request_from_archive.RestoreRequestError:
        except request_from_archive.RestoreRequestError as caught_error:
            self.assertEqual(
                f"One or more files failed to be requested from '{archive_bucket_name}'.",
                str(caught_error),
            )
        self.assertFalse(
            granule[request_from_archive.GRANULE_RECOVER_FILES_KEY][0][
                request_from_archive.FILE_PROCESSED_KEY
            ]
        )

        mock_restore_object.assert_has_calls(
            [
                call(
                    mock_s3,
                    file_name_0,
                    restore_expire_days,
                    archive_bucket_name,
                    1,
                    job_id,
                    recovery_type,
                ),
                call(
                    mock_s3,
                    file_name_0,
                    restore_expire_days,
                    archive_bucket_name,
                    2,
                    job_id,
                    recovery_type,
                ),
                call(
                    mock_s3,
                    file_name_0,
                    restore_expire_days,
                    archive_bucket_name,
                    3,
                    job_id,
                    recovery_type,
                ),
            ]
        )
        self.assertEqual(max_retries + 1, mock_restore_object.call_count)
        mock_sleep.assert_has_calls([call(retry_sleep_secs)] * max_retries)
        mock_update_status_for_file.assert_called_once_with(
            job_id,
            granule_id,
            file_name_0,
            OrcaStatus.FAILED,
            str(expected_error),
            db_queue_url,
        )
        mock_logger_error.assert_has_calls(
            [
                call(
                    f"Failed to restore '{file_name_0}' from "
                    f"'{archive_bucket_name}'. Encountered error '{str(expected_error)}'."
                ),
                call(
                    f"One or more files failed to be requested from "
                    f"'{archive_bucket_name}'. GRANULE: {json.dumps(granule)}",
                ),
            ]
        )

    @patch("orca_shared.recovery.shared_recovery.update_status_for_file")
    @patch("time.sleep")
    @patch("request_from_archive.restore_object")
    @patch("cumulus_logger.CumulusLogger.error")
    def test_process_granule_error_when_posting_status_raises_after_retries(
        self,
        mock_logger_error: MagicMock,
        mock_restore_object: MagicMock,
        mock_sleep: MagicMock,
        mock_update_status_for_file: MagicMock,
    ):
        """
        If a file expended all attempts for recovery, and posting to
        status DB expended all attempts, raise error.
        """
        mock_s3 = Mock()
        max_retries = randint(3, 20)  # nosec
        archive_bucket_name = uuid.uuid4().__str__()
        retry_sleep_secs = randint(0, 99)  # nosec
        recovery_type = uuid.uuid4().__str__()
        restore_expire_days = randint(0, 99)  # nosec
        granule_id = uuid.uuid4().__str__()
        file_name_0 = uuid.uuid4().__str__()
        dest_bucket_0 = uuid.uuid4().__str__()
        job_id = uuid.uuid4().__str__()
        db_queue_url = "http://" + uuid.uuid4().__str__() + ".blah"

        granule = {
            request_from_archive.GRANULE_GRANULE_ID_KEY: granule_id,
            request_from_archive.GRANULE_RECOVER_FILES_KEY: [
                {
                    request_from_archive.FILE_FILENAME_KEY: os.path.basename(file_name_0),
                    request_from_archive.FILE_KEY_PATH_KEY: file_name_0,
                    request_from_archive.FILE_RESTORE_DESTINATION_KEY: dest_bucket_0,
                    request_from_archive.FILE_PROCESSED_KEY: False,
                    request_from_archive.FILE_STATUS_ID_KEY: 1,
                },
            ],
        }

        expected_error = ClientError({}, "")
        mock_restore_object.side_effect = expected_error

        expected_status_error = Exception(uuid.uuid4().__str__())
        mock_update_status_for_file.side_effect = expected_status_error

        try:
            request_from_archive.process_granule(
                mock_s3,
                granule,
                archive_bucket_name,
                restore_expire_days,
                max_retries,
                retry_sleep_secs,
                recovery_type,
                job_id,
                db_queue_url,
            )
            self.fail("Error not Raised.")
        # except request_from_archive.RestoreRequestError:
        except Exception as caught_error:
            self.assertEqual(
                f"Unable to send message to QUEUE '{db_queue_url}'",
                str(caught_error),
            )
        self.assertFalse(
            granule[request_from_archive.GRANULE_RECOVER_FILES_KEY][0][
                request_from_archive.FILE_PROCESSED_KEY
            ]
        )

        mock_restore_object.assert_has_calls(
            [
                call(
                    mock_s3,
                    file_name_0,
                    restore_expire_days,
                    archive_bucket_name,
                    1,
                    job_id,
                    recovery_type,
                ),
                call(
                    mock_s3,
                    file_name_0,
                    restore_expire_days,
                    archive_bucket_name,
                    2,
                    job_id,
                    recovery_type,
                ),
                call(
                    mock_s3,
                    file_name_0,
                    restore_expire_days,
                    archive_bucket_name,
                    3,
                    job_id,
                    recovery_type,
                ),
            ]
        )
        mock_update_status_for_file.assert_has_calls(
            [
                call(
                    job_id,
                    granule_id,
                    file_name_0,
                    OrcaStatus.FAILED,
                    str(expected_error),
                    db_queue_url,
                )
            ]
            * (max_retries + 1)
        )
        self.assertEqual(max_retries + 1, mock_restore_object.call_count)
        self.assertEqual(max_retries + 1, mock_update_status_for_file.call_count)
        mock_sleep.assert_has_calls([call(retry_sleep_secs)] * max_retries * 2)
        # The following does not check all error messages. Do not implement a call count check.
        mock_logger_error.assert_has_calls(
            [
                call(
                    f"Failed to restore '{file_name_0}' from "
                    f"'{archive_bucket_name}'. Encountered error '{str(expected_error)}'."
                ),
                call(
                    f"Ran into error posting to SQS {max_retries + 1} time(s) "
                    f"with exception '{str(expected_status_error)}'"
                ),
            ],
            any_order=True,
        )

    def test_get_s3_object_information_happy_path(self):
        mock_s3_cli = Mock()
        mock_s3_cli.head_object.side_effect = None
        archive_bucket_name = uuid.uuid4().__str__()
        file_key = uuid.uuid4().__str__()

        result = request_from_archive.get_s3_object_information(
            mock_s3_cli, archive_bucket_name, file_key
        )
        self.assertEqual(mock_s3_cli.head_object.return_value, result)

    def test_get_s3_object_information_client_error_raised(self):
        expected_error = ClientError(
            {"Error": {"Code": "Teapot", "Message": "test"}}, ""
        )
        mock_s3_cli = Mock()
        mock_s3_cli.head_object.side_effect = expected_error
        archive_bucket_name = uuid.uuid4().__str__()
        file_key = uuid.uuid4().__str__()

        try:
            request_from_archive.get_s3_object_information(
                mock_s3_cli, archive_bucket_name, file_key
            )
            self.fail("Error not raised.")
        except ClientError as err:
            self.assertEqual(expected_error, err)

    def test_get_s3_object_information_NotFound_returns_none(self):
        expected_error = ClientError(
            {"Error": {"Code": "404", "Message": "Not Found"}}, ""
        )
        mock_s3_cli = Mock()
        mock_s3_cli.head_object.side_effect = expected_error
        archive_bucket_name = uuid.uuid4().__str__()
        file_key = uuid.uuid4().__str__()

        result = request_from_archive.get_s3_object_information(
            mock_s3_cli, archive_bucket_name, file_key
        )
        self.assertIsNone(result)

    def test_restore_object_happy_path(self):
        archive_bucket_name = uuid.uuid4().__str__()
        key = uuid.uuid4().__str__()
        restore_expire_days = randint(0, 99)  # nosec
        recovery_type = uuid.uuid4().__str__()
        mock_s3_cli = Mock()
        mock_s3_cli.restore_object.return_value = {
            "ResponseMetadata": {"HTTPStatusCode": 202}
        }

        request_from_archive.restore_object(
            mock_s3_cli,
            key,
            restore_expire_days,
            archive_bucket_name,
            randint(0, 99),  # nosec
            uuid.uuid4().__str__(),
            recovery_type,
        )

        mock_s3_cli.restore_object.assert_called_once_with(
            Bucket=archive_bucket_name,
            Key=key,
            RestoreRequest={
                "Days": restore_expire_days,
                "GlacierJobParameters": {"Tier": recovery_type},
            },
        )

    # noinspection PyUnusedLocal
    @patch("cumulus_logger.CumulusLogger.info")
    def test_restore_object_client_error_raises(self, mock_logger_info: MagicMock):
        job_id = uuid.uuid4().__str__()
        archive_bucket_name = uuid.uuid4().__str__()
        key = uuid.uuid4().__str__()
        restore_expire_days = randint(0, 99)  # nosec
        recovery_type = uuid.uuid4().__str__()
        expected_error = ClientError({}, "")
        mock_s3_cli = Mock()
        mock_s3_cli.restore_object.side_effect = expected_error

        try:
            request_from_archive.restore_object(
                mock_s3_cli,
                key,
                restore_expire_days,
                archive_bucket_name,
                1,
                job_id,
                recovery_type,
            )
            self.fail("Error not Raised.")
        except ClientError as error:
            self.assertEqual(expected_error, error)
            mock_s3_cli.restore_object.assert_called_once_with(
                Bucket=archive_bucket_name,
                Key=key,
                RestoreRequest={
                    "Days": restore_expire_days,
                    "GlacierJobParameters": {"Tier": recovery_type},
                },
            )

    # noinspection PyUnusedLocal
    @patch("cumulus_logger.CumulusLogger.info")
    def test_restore_object_200_returned_raises(self, mock_logger_info: MagicMock):
        """
        A 200 indicates that the file is already restored,  and thus cannot
        presently be restored again. Should be raised.
        """
        archive_bucket_name = uuid.uuid4().__str__()
        key = uuid.uuid4().__str__()
        restore_expire_days = randint(0, 99)  # nosec
        recovery_type = uuid.uuid4().__str__()
        mock_s3_cli = Mock()
        mock_s3_cli.restore_object.return_value = {
            "ResponseMetadata": {"HTTPStatusCode": 200}
        }

        with self.assertRaises(ClientError) as context:
            request_from_archive.restore_object(
                mock_s3_cli,
                key,
                restore_expire_days,
                archive_bucket_name,
                2,
                uuid.uuid4().__str__(),
                recovery_type,
            )
        self.assertEqual(
            f"An error occurred (HTTPStatus: 200) when calling the restore_object operation: "
            f"File '{key}' in bucket '{archive_bucket_name}' has already been recovered.",
            str(context.exception),
        )

    @patch("request_from_archive.task")
    def test_handler_happy_path(self, mock_task: MagicMock):
        """
        Tests that between the handler and CMA, input is translated into what task expects.
        """
        # todo: Remove these hardcoded keys
        file0 = "MOD09GQ___006/2017/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.h5"
        bucket_name = uuid.uuid4().__str__()

        input_event = create_handler_event()
        expected_task_input = {
            request_from_archive.EVENT_INPUT_KEY: input_event["payload"],
            # Values here are based on the event task_config values that are mapped
            request_from_archive.EVENT_CONFIG_KEY: {
                request_from_archive.CONFIG_JOB_ID_KEY: None,
                request_from_archive.CONFIG_MULTIPART_CHUNKSIZE_MB_KEY: 750,
                request_from_archive.CONFIG_DEFAULT_BUCKET_OVERRIDE_KEY: "lp-sndbx-cumulus-orca",
                request_from_archive.CONFIG_DEFAULT_RECOVERY_TYPE_OVERRIDE_KEY: None,
            },
        }
        mock_task.return_value = {
            "granules": [
                {
                    request_from_archive.GRANULE_GRANULE_ID_KEY: "some_granule_id",
                    request_from_archive.GRANULE_RECOVER_FILES_KEY: [
                        {
                            request_from_archive.FILE_FILENAME_KEY: os.path.basename(file0),
                            request_from_archive.FILE_KEY_PATH_KEY: file0,
                            request_from_archive.FILE_RESTORE_DESTINATION_KEY: bucket_name,
                            request_from_archive.FILE_PROCESSED_KEY: True,
                            request_from_archive.FILE_STATUS_ID_KEY: 1,
                            request_from_archive.FILE_LAST_UPDATE_KEY:
                                "2021-01-01T23:53:43.097+00:00",
                            request_from_archive.FILE_REQUEST_TIME_KEY:
                                "2021-01-01T23:53:43.097+00:00",
                        },
                    ],
                }
            ],
            "asyncOperationId": "some_job_id",
        }
        context = LambdaContextMock()
        result = request_from_archive.handler(input_event, context)
        mock_task.assert_called_once_with(expected_task_input, context)

        self.assertEqual(mock_task.return_value, result["payload"])

    # noinspection PyUnusedLocal
    @patch("request_from_archive.shared_recovery.create_status_for_job")
    @patch("boto3.client")
    def test_handler_output_json_schema(
        self,
        mock_boto3_client: MagicMock,
        mock_create_status_for_job: MagicMock,
    ):
        """
        A full run through with multiple files to verify output schema.
        Does NOT presently check side effects. Should not currently count for coverage.
        """
        # todo: Remove these hardcoded keys
        file0 = "MOD09GQ___006/2017/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.h5"
        file1 = "MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.h5.met"
        file2 = "MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321_ndvi.jpg"
        file3 = "MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml"
        protected_bucket_name = "sndbx-cumulus-protected"
        public_bucket_name = "sndbx-cumulus-public"
        key0 = {
            request_from_archive.FILE_KEY_KEY: file0,
            request_from_archive.FILE_DEST_BUCKET_KEY: protected_bucket_name,
        }
        key1 = {
            request_from_archive.FILE_KEY_KEY: file1,
            request_from_archive.FILE_DEST_BUCKET_KEY: protected_bucket_name,
        }
        key2 = {
            request_from_archive.FILE_KEY_KEY: file2,
            request_from_archive.FILE_DEST_BUCKET_KEY: public_bucket_name,
        }
        key3 = {
            request_from_archive.FILE_KEY_KEY: file3,
            request_from_archive.FILE_DEST_BUCKET_KEY: public_bucket_name,
        }

        os.environ[
            request_from_archive.OS_ENVIRON_STATUS_UPDATE_QUEUE_URL_KEY
        ] = "https://db.queue.url"
        job_id = uuid.uuid4().__str__()
        granule_id = "MOD09GQ.A0219114.N5aUCG.006.0656338553321"
        files = [key0, key1, key2, key3]
        input_event = {
            "payload": {
                request_from_archive.INPUT_GRANULES_KEY: [
                    {
                        request_from_archive.GRANULE_GRANULE_ID_KEY: granule_id,
                        request_from_archive.GRANULE_KEYS_KEY: files,
                    }
                ]
            },
            "task_config": {
                request_from_archive.CONFIG_DEFAULT_BUCKET_OVERRIDE_KEY:
                    "my-dr-fake-archive-bucket",
                request_from_archive.CONFIG_JOB_ID_KEY: job_id,
                request_from_archive.CONFIG_DEFAULT_RECOVERY_TYPE_OVERRIDE_KEY: "Standard",
            },
        }

        mock_s3_cli = mock_boto3_client("s3")
        mock_s3_cli.restore_object.side_effect = [
            {"ResponseMetadata": {"HTTPStatusCode": 202}},
            {"ResponseMetadata": {"HTTPStatusCode": 202}},
            {"ResponseMetadata": {"HTTPStatusCode": 202}},
            {"ResponseMetadata": {"HTTPStatusCode": 202}},
        ]

        context = LambdaContextMock()
        result = request_from_archive.handler(input_event, context)

        result_value = result["payload"]

        mock_boto3_client.assert_has_calls([call("s3")])
        mock_s3_cli.head_object.assert_any_call(
            Bucket="my-dr-fake-archive-bucket", Key=file0
        )
        mock_s3_cli.head_object.assert_any_call(
            Bucket="my-dr-fake-archive-bucket", Key=file1
        )
        mock_s3_cli.head_object.assert_any_call(
            Bucket="my-dr-fake-archive-bucket", Key=file2
        )
        mock_s3_cli.head_object.assert_any_call(
            Bucket="my-dr-fake-archive-bucket", Key=file3
        )
        restore_req_exp = {"Days": 5, "GlacierJobParameters": {"Tier": "Standard"}}

        mock_s3_cli.restore_object.assert_any_call(
            Bucket="my-dr-fake-archive-bucket",
            Key=file0,
            RestoreRequest=restore_req_exp,
        )
        mock_s3_cli.restore_object.assert_any_call(
            Bucket="my-dr-fake-archive-bucket",
            Key=file1,
            RestoreRequest=restore_req_exp,
        )
        mock_s3_cli.restore_object.assert_any_call(
            Bucket="my-dr-fake-archive-bucket",
            Key=file2,
            RestoreRequest=restore_req_exp,
        )
        mock_s3_cli.restore_object.assert_called_with(
            Bucket="my-dr-fake-archive-bucket",
            Key=file3,
            RestoreRequest=restore_req_exp,
        )

        expected_granule = {
            request_from_archive.GRANULE_GRANULE_ID_KEY: granule_id,
            request_from_archive.GRANULE_KEYS_KEY: [
                {
                    request_from_archive.FILE_DEST_BUCKET_KEY: protected_bucket_name,
                    request_from_archive.FILE_KEY_KEY: file0,
                },
                {
                    request_from_archive.FILE_DEST_BUCKET_KEY: protected_bucket_name,
                    request_from_archive.FILE_KEY_KEY: file1,
                },
                {
                    request_from_archive.FILE_DEST_BUCKET_KEY: public_bucket_name,
                    request_from_archive.FILE_KEY_KEY: file2,
                },
                {
                    request_from_archive.FILE_DEST_BUCKET_KEY: public_bucket_name,
                    request_from_archive.FILE_KEY_KEY: file3,
                },
            ],
            request_from_archive.GRANULE_RECOVER_FILES_KEY: [
                {
                    request_from_archive.FILE_FILENAME_KEY: os.path.basename(file0),
                    request_from_archive.FILE_KEY_PATH_KEY: file0,
                    request_from_archive.FILE_RESTORE_DESTINATION_KEY: protected_bucket_name,
                    request_from_archive.FILE_PROCESSED_KEY: True,
                    request_from_archive.FILE_MULTIPART_CHUNKSIZE_MB_KEY: None,
                    request_from_archive.FILE_STATUS_ID_KEY: 1,
                },
                {
                    request_from_archive.FILE_FILENAME_KEY: os.path.basename(file1),
                    request_from_archive.FILE_KEY_PATH_KEY: file1,
                    request_from_archive.FILE_RESTORE_DESTINATION_KEY: protected_bucket_name,
                    request_from_archive.FILE_PROCESSED_KEY: True,
                    request_from_archive.FILE_MULTIPART_CHUNKSIZE_MB_KEY: None,
                    request_from_archive.FILE_STATUS_ID_KEY: 1,
                },
                {
                    request_from_archive.FILE_FILENAME_KEY: os.path.basename(file2),
                    request_from_archive.FILE_KEY_PATH_KEY: file2,
                    request_from_archive.FILE_RESTORE_DESTINATION_KEY: public_bucket_name,
                    request_from_archive.FILE_PROCESSED_KEY: True,
                    request_from_archive.FILE_MULTIPART_CHUNKSIZE_MB_KEY: None,
                    request_from_archive.FILE_STATUS_ID_KEY: 1,
                },
                {
                    request_from_archive.FILE_FILENAME_KEY: os.path.basename(file3),
                    request_from_archive.FILE_KEY_PATH_KEY: file3,
                    request_from_archive.FILE_RESTORE_DESTINATION_KEY: public_bucket_name,
                    request_from_archive.FILE_PROCESSED_KEY: True,
                    request_from_archive.FILE_MULTIPART_CHUNKSIZE_MB_KEY: None,
                    request_from_archive.FILE_STATUS_ID_KEY: 1,
                },
            ],
        }
        expected_result = {
            "granules": [expected_granule],
            "asyncOperationId": job_id,
        }

        # Validate the output is correct
        _OUTPUT_VALIDATE(result_value)

        # Check the values of the result less the times since those will never match
        for granule in result_value["granules"]:
            for file in granule[request_from_archive.GRANULE_RECOVER_FILES_KEY]:
                file.pop(request_from_archive.FILE_REQUEST_TIME_KEY, None)
                file.pop(request_from_archive.FILE_LAST_UPDATE_KEY, None)
                file.pop(request_from_archive.FILE_COMPLETION_TIME_KEY, None)

        self.assertEqual(expected_result, result_value)


if __name__ == "__main__":
    unittest.main(argv=["start"])
