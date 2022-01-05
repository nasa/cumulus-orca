"""
Name: test_request_files.py

Description:  Unit tests for request_files.py.
"""
import json
import os
import random
import unittest
import uuid
from random import randint, uniform
from unittest import mock
from unittest.mock import patch, MagicMock, call, Mock

from orca_shared import shared_recovery
from orca_shared.recovery.shared_recovery import OrcaStatus
from test.request_helpers import LambdaContextMock, create_handler_event

# noinspection PyPackageRequirements
import fastjsonschema as fastjsonschema

# noinspection PyPackageRequirements
from botocore.exceptions import ClientError

import request_files


class TestRequestFiles(unittest.TestCase):
    """
    TestRequestFiles.
    """

    def setUp(self):
        os.environ.pop("CUMULUS_MESSAGE_ADAPTER_DISABLED", None)
        self.maxDiff = None

    def tearDown(self):
        os.environ.pop("PREFIX", None)
        os.environ.pop(request_files.OS_ENVIRON_DB_QUEUE_URL_KEY, None)
        os.environ.pop(request_files.OS_ENVIRON_RESTORE_EXPIRE_DAYS_KEY, None)
        os.environ.pop(request_files.OS_ENVIRON_RESTORE_REQUEST_RETRIES_KEY, None)
        os.environ.pop(request_files.OS_ENVIRON_ORCA_DEFAULT_GLACIER_BUCKET_KEY, None)
        os.environ.pop(request_files.OS_ENVIRON_RESTORE_RETRY_SLEEP_SECS_KEY, None)
        os.environ.pop(request_files.OS_ENVIRON_RESTORE_RETRIEVAL_TYPE_KEY, None)

    @patch("request_files.get_default_glacier_bucket_name")
    @patch("request_files.inner_task")
    def test_task_happy_path(
        self,
        mock_inner_task: MagicMock,
        mock_get_default_glacier_bucket_name: MagicMock,
    ):
        """
        All variables present and valid.
        """
        job_id = uuid.uuid4().__str__()
        config = {
            request_files.CONFIG_JOB_ID_KEY: job_id,
        }
        mock_event = {
            request_files.EVENT_CONFIG_KEY: config,
        }
        max_retries = randint(0, 99)  # nosec
        retry_sleep_secs = uniform(0, 99)  # nosec
        retrieval_type = "Bulk"
        exp_days = randint(0, 99)  # nosec
        db_queue_url = "http://" + uuid.uuid4().__str__() + ".blah"

        os.environ[request_files.OS_ENVIRON_DB_QUEUE_URL_KEY] = db_queue_url
        os.environ[
            request_files.OS_ENVIRON_RESTORE_REQUEST_RETRIES_KEY
        ] = max_retries.__str__()
        os.environ[
            request_files.OS_ENVIRON_RESTORE_RETRY_SLEEP_SECS_KEY
        ] = retry_sleep_secs.__str__()
        os.environ[request_files.OS_ENVIRON_RESTORE_RETRIEVAL_TYPE_KEY] = retrieval_type
        os.environ[
            request_files.OS_ENVIRON_RESTORE_EXPIRE_DAYS_KEY
        ] = exp_days.__str__()

        request_files.task(mock_event, None)

        mock_get_default_glacier_bucket_name.assert_called_once_with(config)
        mock_inner_task.assert_called_once_with(
            {
                request_files.EVENT_CONFIG_KEY: {
                    request_files.CONFIG_ORCA_DEFAULT_BUCKET_OVERRIDE_KEY: mock_get_default_glacier_bucket_name.return_value,
                    request_files.CONFIG_JOB_ID_KEY: job_id,
                },
            },
            max_retries,
            retry_sleep_secs,
            retrieval_type,
            exp_days,
            db_queue_url,
        )

    @patch("request_files.get_default_glacier_bucket_name")
    @patch("request_files.inner_task")
    def test_task_default_for_missing_max_retries(
        self,
        mock_inner_task: MagicMock,
        mock_get_default_glacier_bucket_name: MagicMock,
    ):
        """
        If max_retries missing, use default.
        """
        job_id = uuid.uuid4().__str__()
        config = {
            request_files.CONFIG_JOB_ID_KEY: job_id,
        }
        mock_event = {
            request_files.EVENT_CONFIG_KEY: config,
        }
        retry_sleep_secs = uniform(0, 99)  # nosec
        retrieval_type = "Bulk"
        exp_days = randint(0, 99)  # nosec
        db_queue_url = "http://" + uuid.uuid4().__str__() + ".blah"

        os.environ["DB_QUEUE_URL"] = db_queue_url
        os.environ[
            request_files.OS_ENVIRON_RESTORE_RETRY_SLEEP_SECS_KEY
        ] = retry_sleep_secs.__str__()
        os.environ[request_files.OS_ENVIRON_RESTORE_RETRIEVAL_TYPE_KEY] = retrieval_type
        os.environ[
            request_files.OS_ENVIRON_RESTORE_EXPIRE_DAYS_KEY
        ] = exp_days.__str__()

        request_files.task(mock_event, None)

        mock_get_default_glacier_bucket_name.assert_called_once_with(config)
        mock_inner_task.assert_called_once_with(
            {
                request_files.EVENT_CONFIG_KEY: {
                    request_files.CONFIG_ORCA_DEFAULT_BUCKET_OVERRIDE_KEY: mock_get_default_glacier_bucket_name.return_value,
                    request_files.CONFIG_JOB_ID_KEY: job_id,
                },
            },
            request_files.DEFAULT_MAX_REQUEST_RETRIES,
            retry_sleep_secs,
            retrieval_type,
            exp_days,
            db_queue_url,
        )

    @patch("request_files.get_default_glacier_bucket_name")
    @patch("request_files.inner_task")
    def test_task_default_for_missing_sleep_secs(
        self,
        mock_inner_task: MagicMock,
        mock_get_default_glacier_bucket_name: MagicMock,
    ):
        """
        If sleep_secs missing, use default.
        """
        job_id = uuid.uuid4().__str__()
        config = {
            request_files.CONFIG_JOB_ID_KEY: job_id,
        }
        mock_event = {
            request_files.EVENT_CONFIG_KEY: config,
        }
        max_retries = randint(0, 99)  # nosec
        retrieval_type = "Bulk"
        exp_days = randint(0, 99)  # nosec
        db_queue_url = "http://" + uuid.uuid4().__str__() + ".blah"
        os.environ["DB_QUEUE_URL"] = db_queue_url

        os.environ[
            request_files.OS_ENVIRON_RESTORE_REQUEST_RETRIES_KEY
        ] = max_retries.__str__()
        os.environ[request_files.OS_ENVIRON_RESTORE_RETRIEVAL_TYPE_KEY] = retrieval_type
        os.environ[
            request_files.OS_ENVIRON_RESTORE_EXPIRE_DAYS_KEY
        ] = exp_days.__str__()

        request_files.task(mock_event, None)

        mock_get_default_glacier_bucket_name.assert_called_once_with(config)
        mock_inner_task.assert_called_once_with(
            {
                request_files.EVENT_CONFIG_KEY: {
                    request_files.CONFIG_ORCA_DEFAULT_BUCKET_OVERRIDE_KEY: mock_get_default_glacier_bucket_name.return_value,
                    request_files.CONFIG_JOB_ID_KEY: job_id,
                },
            },
            max_retries,
            request_files.DEFAULT_RESTORE_RETRY_SLEEP_SECS,
            retrieval_type,
            exp_days,
            db_queue_url,
        )

    @patch("request_files.get_default_glacier_bucket_name")
    @patch("request_files.inner_task")
    def test_task_default_for_missing_retrieval_type(
        self,
        mock_inner_task: MagicMock,
        mock_get_default_glacier_bucket_name: MagicMock,
    ):
        """
        If retrieval_type is missing, use default.
        """
        job_id = uuid.uuid4().__str__()
        config = {
            request_files.CONFIG_JOB_ID_KEY: job_id,
        }
        mock_event = {
            request_files.EVENT_CONFIG_KEY: config,
        }
        max_retries = randint(0, 99)  # nosec
        retry_sleep_secs = uniform(0, 99)  # nosec
        exp_days = randint(0, 99)  # nosec
        db_queue_url = "http://" + uuid.uuid4().__str__() + ".blah"
        os.environ["DB_QUEUE_URL"] = db_queue_url

        os.environ[
            request_files.OS_ENVIRON_RESTORE_REQUEST_RETRIES_KEY
        ] = max_retries.__str__()
        os.environ[
            request_files.OS_ENVIRON_RESTORE_RETRY_SLEEP_SECS_KEY
        ] = retry_sleep_secs.__str__()
        os.environ[
            request_files.OS_ENVIRON_RESTORE_EXPIRE_DAYS_KEY
        ] = exp_days.__str__()

        request_files.task(mock_event, None)

        mock_get_default_glacier_bucket_name.assert_called_once_with(config)
        mock_inner_task.assert_called_once_with(
            {
                request_files.EVENT_CONFIG_KEY: {
                    request_files.CONFIG_ORCA_DEFAULT_BUCKET_OVERRIDE_KEY: mock_get_default_glacier_bucket_name.return_value,
                    request_files.CONFIG_JOB_ID_KEY: job_id,
                },
            },
            max_retries,
            retry_sleep_secs,
            request_files.DEFAULT_RESTORE_RETRIEVAL_TYPE,
            exp_days,
            db_queue_url,
        )

    @patch("request_files.get_default_glacier_bucket_name")
    @patch("request_files.inner_task")
    def test_task_default_for_bad_retrieval_type(
        self,
        mock_inner_task: MagicMock,
        mock_get_default_glacier_bucket_name: MagicMock,
    ):
        """
        If retrieval_type is invalid, use default.
        """
        job_id = uuid.uuid4().__str__()
        config = {
            request_files.CONFIG_JOB_ID_KEY: job_id,
        }
        mock_event = {
            request_files.EVENT_CONFIG_KEY: config,
        }
        max_retries = randint(0, 99)  # nosec
        retry_sleep_secs = uniform(0, 99)  # nosec
        retrieval_type = "Nope"
        exp_days = randint(0, 99)  # nosec
        db_queue_url = "http://" + uuid.uuid4().__str__() + ".blah"

        os.environ["DB_QUEUE_URL"] = db_queue_url
        os.environ[
            request_files.OS_ENVIRON_RESTORE_REQUEST_RETRIES_KEY
        ] = max_retries.__str__()
        os.environ[
            request_files.OS_ENVIRON_RESTORE_RETRY_SLEEP_SECS_KEY
        ] = retry_sleep_secs.__str__()
        os.environ[request_files.OS_ENVIRON_RESTORE_RETRIEVAL_TYPE_KEY] = retrieval_type
        os.environ[
            request_files.OS_ENVIRON_RESTORE_EXPIRE_DAYS_KEY
        ] = exp_days.__str__()

        request_files.task(mock_event, None)

        mock_get_default_glacier_bucket_name.assert_called_once_with(config)
        mock_inner_task.assert_called_once_with(
            {
                request_files.EVENT_CONFIG_KEY: {
                    request_files.CONFIG_ORCA_DEFAULT_BUCKET_OVERRIDE_KEY: mock_get_default_glacier_bucket_name.return_value,
                    request_files.CONFIG_JOB_ID_KEY: job_id,
                },
            },
            max_retries,
            retry_sleep_secs,
            request_files.DEFAULT_RESTORE_RETRIEVAL_TYPE,
            exp_days,
            db_queue_url,
        )

    @patch("request_files.get_default_glacier_bucket_name")
    @patch("request_files.inner_task")
    def test_task_default_for_missing_exp_days(
        self,
        mock_inner_task: MagicMock,
        mock_get_default_glacier_bucket_name: MagicMock,
    ):
        """
        Uses default missing_exp_days if needed.
        """
        job_id = uuid.uuid4().__str__()
        config = {
            request_files.CONFIG_JOB_ID_KEY: job_id,
        }
        mock_event = {
            request_files.EVENT_CONFIG_KEY: config,
        }
        max_retries = randint(0, 99)  # nosec
        retry_sleep_secs = uniform(0, 99)  # nosec
        retrieval_type = "Bulk"
        db_queue_url = "http://" + uuid.uuid4().__str__() + ".blah"

        os.environ["DB_QUEUE_URL"] = db_queue_url
        os.environ[
            request_files.OS_ENVIRON_RESTORE_REQUEST_RETRIES_KEY
        ] = max_retries.__str__()
        os.environ[
            request_files.OS_ENVIRON_RESTORE_RETRY_SLEEP_SECS_KEY
        ] = retry_sleep_secs.__str__()
        os.environ[request_files.OS_ENVIRON_RESTORE_RETRIEVAL_TYPE_KEY] = retrieval_type

        request_files.task(mock_event, None)

        mock_get_default_glacier_bucket_name.assert_called_once_with(config)
        mock_inner_task.assert_called_once_with(
            {
                request_files.EVENT_CONFIG_KEY: {
                    request_files.CONFIG_ORCA_DEFAULT_BUCKET_OVERRIDE_KEY: mock_get_default_glacier_bucket_name.return_value,
                    request_files.CONFIG_JOB_ID_KEY: job_id,
                },
            },
            max_retries,
            retry_sleep_secs,
            retrieval_type,
            request_files.DEFAULT_RESTORE_EXPIRE_DAYS,
            db_queue_url,
        )

    @patch("request_files.get_default_glacier_bucket_name")
    @patch("request_files.inner_task")
    def test_task_job_id_missing_generates(
        self,
        mock_inner_task: MagicMock,
        mock_get_default_glacier_bucket_name: MagicMock,
    ):
        """
        If job_id missing, generates a new one.
        """
        config = {
            request_files.CONFIG_JOB_ID_KEY: None,
        }
        mock_event = {
            request_files.EVENT_CONFIG_KEY: config,
        }
        max_retries = randint(0, 99)  # nosec
        retry_sleep_secs = uniform(0, 99)  # nosec
        retrieval_type = "Bulk"
        exp_days = randint(0, 99)  # nosec
        db_queue_url = "http://" + uuid.uuid4().__str__() + ".blah"
        job_id = uuid.uuid4()

        os.environ["DB_QUEUE_URL"] = db_queue_url
        os.environ[
            request_files.OS_ENVIRON_RESTORE_REQUEST_RETRIES_KEY
        ] = max_retries.__str__()
        os.environ[
            request_files.OS_ENVIRON_RESTORE_RETRY_SLEEP_SECS_KEY
        ] = retry_sleep_secs.__str__()
        os.environ[request_files.OS_ENVIRON_RESTORE_RETRIEVAL_TYPE_KEY] = retrieval_type
        os.environ[
            request_files.OS_ENVIRON_RESTORE_EXPIRE_DAYS_KEY
        ] = exp_days.__str__()

        with patch.object(uuid, "uuid4", return_value=job_id):
            request_files.task(mock_event, None)

        mock_get_default_glacier_bucket_name.assert_called_once_with(config)
        mock_inner_task.assert_called_once_with(
            {
                request_files.EVENT_CONFIG_KEY: {
                    request_files.CONFIG_ORCA_DEFAULT_BUCKET_OVERRIDE_KEY: mock_get_default_glacier_bucket_name.return_value,
                    request_files.CONFIG_JOB_ID_KEY: job_id.__str__(),
                },
            },
            max_retries,
            retry_sleep_secs,
            retrieval_type,
            exp_days,
            db_queue_url,
        )

    # noinspection PyUnusedLocal
    @patch("request_files.shared_recovery.create_status_for_job")
    @patch("time.sleep")
    @patch("request_files.process_granule")
    @patch("request_files.object_exists")
    @patch("boto3.client")
    def test_inner_task_happy_path(
            self,
            mock_boto3_client: MagicMock,
            mock_object_exists: MagicMock,
            mock_process_granule: MagicMock,
            mock_sleep: MagicMock,
            mock_create_status_for_job: MagicMock,
    ):
        """
        Basic path with multiple granules.
        """
        glacier_bucket = uuid.uuid4().__str__()
        collection_multipart_chunksize_mb = random.randint(1, 10000)
        file_key_0 = uuid.uuid4().__str__()
        file_key_1 = uuid.uuid4().__str__()
        file_dest_bucket_0 = uuid.uuid4().__str__()
        file_dest_bucket_1 = uuid.uuid4().__str__()
        job_id = uuid.uuid4().__str__()
        granule_id0 = uuid.uuid4().__str__()
        granule_id1 = uuid.uuid4().__str__()
        db_queue_url = "http://" + uuid.uuid4().__str__() + ".blah"
        file_0 = {
            request_files.FILE_KEY_KEY: file_key_0,
            request_files.FILE_DEST_BUCKET_KEY: file_dest_bucket_0,
        }
        expected_file0_output = {
            request_files.FILE_SUCCESS_KEY: False,
            "filename": file_key_0,
            "key_path": file_key_0,
            "restore_destination": file_dest_bucket_0,
            "multipart_chunksize_mb": collection_multipart_chunksize_mb,
            "status_id": OrcaStatus.PENDING.value,
            "request_time": mock.ANY,
            "last_update": mock.ANY,
        }
        file_1 = {
            request_files.FILE_KEY_KEY: file_key_1,
            request_files.FILE_DEST_BUCKET_KEY: file_dest_bucket_1,
        }
        expected_file1_output = {
            request_files.FILE_SUCCESS_KEY: False,
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
            request_files.GRANULE_GRANULE_ID_KEY: granule_id0,
            request_files.GRANULE_KEYS_KEY: [
                file_0,
            ],
        }
        expected_input_granule0 = granule0.copy()
        expected_input_granule0[
            request_files.GRANULE_RECOVER_FILES_KEY
        ] = expected_input_granule_files0

        expected_input_granule_files1 = [
            expected_file1_output,
        ]
        granule1 = {
            request_files.GRANULE_GRANULE_ID_KEY: granule_id1,
            request_files.GRANULE_KEYS_KEY: [
                file_1,
            ],
        }
        expected_input_granule1 = granule1.copy()
        expected_input_granule1[
            request_files.GRANULE_RECOVER_FILES_KEY
        ] = expected_input_granule_files1

        event = {
            request_files.EVENT_CONFIG_KEY: {
                request_files.CONFIG_ORCA_DEFAULT_BUCKET_OVERRIDE_KEY: glacier_bucket,
                request_files.CONFIG_JOB_ID_KEY: job_id,
                request_files.CONFIG_MULTIPART_CHUNKSIZE_MB_KEY: collection_multipart_chunksize_mb,
            },
            request_files.EVENT_INPUT_KEY: {
                request_files.INPUT_GRANULES_KEY: [granule0, granule1]
            },
        }
        max_retries = randint(0, 99)  # nosec
        retry_sleep_secs = randint(0, 99)  # nosec
        retrieval_type = uuid.uuid4().__str__()
        restore_expire_days = randint(0, 99)  # nosec
        mock_s3_cli = mock_boto3_client("s3")

        mock_object_exists.return_value = True

        result = request_files.inner_task(
            event,
            max_retries,
            retry_sleep_secs,
            retrieval_type,
            restore_expire_days,
            db_queue_url,
        )

        mock_create_status_for_job.assert_has_calls([
            call(job_id, granule_id0, glacier_bucket, [{
                "success": False,  # This value is changed by process_granule.
                "filename": file_key_0,
                "key_path": file_key_0,
                "restore_destination": file_dest_bucket_0,
                "multipart_chunksize_mb": collection_multipart_chunksize_mb,
                "status_id": OrcaStatus.PENDING.value,
                "request_time": mock.ANY,
                "last_update": mock.ANY,
            }], db_queue_url),
            call(job_id, granule_id1, glacier_bucket, [{
                "success": False,  # This value is changed by process_granule.
                "filename": file_key_1,
                "key_path": file_key_1,
                "restore_destination": file_dest_bucket_1,
                "multipart_chunksize_mb": collection_multipart_chunksize_mb,
                "status_id": OrcaStatus.PENDING.value,
                "request_time": mock.ANY,
                "last_update": mock.ANY,
            }], db_queue_url)
        ])
        self.assertEqual(2, mock_create_status_for_job.call_count)
        mock_process_granule.assert_has_calls(
            [
                call(
                    mock_s3_cli,
                    expected_input_granule0,
                    glacier_bucket,
                    restore_expire_days,
                    max_retries,
                    retry_sleep_secs,
                    retrieval_type,
                    job_id,
                    db_queue_url,
                ),
                call(
                    mock_s3_cli,
                    expected_input_granule1,
                    glacier_bucket,
                    restore_expire_days,
                    max_retries,
                    retry_sleep_secs,
                    retrieval_type,
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
    @patch("request_files.shared_recovery.create_status_for_job")
    @patch("time.sleep")
    @patch("request_files.process_granule")
    @patch("request_files.object_exists")
    @patch("boto3.client")
    def test_inner_task_error_posting_status_raises(
            self,
            mock_boto3_client: MagicMock,
            mock_object_exists: MagicMock,
            mock_process_granule: MagicMock,
            mock_sleep: MagicMock,
            mock_create_status_for_job: MagicMock,
    ):
        """
        If posting to status DB Queue fails, raise error.
        """
        glacier_bucket = uuid.uuid4().__str__()
        collection_multipart_chunksize_mb = random.randint(1, 10000)
        file_key_0 = uuid.uuid4().__str__()
        file_key_1 = uuid.uuid4().__str__()
        file_dest_bucket_0 = uuid.uuid4().__str__()
        file_dest_bucket_1 = uuid.uuid4().__str__()
        job_id = uuid.uuid4().__str__()
        granule_id0 = uuid.uuid4().__str__()
        granule_id1 = uuid.uuid4().__str__()
        db_queue_url = "http://" + uuid.uuid4().__str__() + ".blah"
        file_0 = {
            request_files.FILE_KEY_KEY: file_key_0,
            request_files.FILE_DEST_BUCKET_KEY: file_dest_bucket_0,
        }
        expected_file0_output = {
            request_files.FILE_SUCCESS_KEY: False,
            "filename": file_key_0,
            "key_path": file_key_0,
            "restore_destination": file_dest_bucket_0,
            "multipart_chunksize_mb": collection_multipart_chunksize_mb,
            "status_id": OrcaStatus.PENDING.value,
            "request_time": mock.ANY,
            "last_update": mock.ANY,
        }
        file_1 = {
            request_files.FILE_KEY_KEY: file_key_1,
            request_files.FILE_DEST_BUCKET_KEY: file_dest_bucket_1,
        }
        expected_file1_output = {
            request_files.FILE_SUCCESS_KEY: False,
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
            request_files.GRANULE_GRANULE_ID_KEY: granule_id0,
            request_files.GRANULE_KEYS_KEY: [
                file_0,
            ],
        }
        expected_input_granule0 = granule0.copy()
        expected_input_granule0[
            request_files.GRANULE_RECOVER_FILES_KEY
        ] = expected_input_granule_files0

        expected_input_granule_files1 = [
            expected_file1_output,
        ]
        granule1 = {
            request_files.GRANULE_GRANULE_ID_KEY: granule_id1,
            request_files.GRANULE_KEYS_KEY: [
                file_1,
            ],
        }
        expected_input_granule1 = granule1.copy()
        expected_input_granule1[
            request_files.GRANULE_RECOVER_FILES_KEY
        ] = expected_input_granule_files1

        event = {
            request_files.EVENT_CONFIG_KEY: {
                request_files.CONFIG_ORCA_DEFAULT_BUCKET_OVERRIDE_KEY: glacier_bucket,
                request_files.CONFIG_JOB_ID_KEY: job_id,
                request_files.CONFIG_MULTIPART_CHUNKSIZE_MB_KEY: collection_multipart_chunksize_mb,
            },
            request_files.EVENT_INPUT_KEY: {
                request_files.INPUT_GRANULES_KEY: [granule0, granule1]
            },
        }
        max_retries = randint(0, 99)  # nosec
        retry_sleep_secs = randint(0, 99)  # nosec
        retrieval_type = uuid.uuid4().__str__()
        restore_expire_days = randint(0, 99)  # nosec
        mock_s3_cli = mock_boto3_client("s3")

        mock_object_exists.return_value = True

        mock_create_status_for_job.side_effect = Exception("mock insert failed error")

        with self.assertRaises(Exception) as cm:
            result = request_files.inner_task(
                event,
                max_retries,
                retry_sleep_secs,
                retrieval_type,
                restore_expire_days,
                db_queue_url,
            )
        self.assertEqual(f"Unable to send message to QUEUE {db_queue_url}", str(cm.exception))

        mock_create_status_for_job.assert_has_calls([
            call(job_id, granule_id0, glacier_bucket, [{
                "success": False,  # This value is changed by process_granule.
                "filename": file_key_0,
                "key_path": file_key_0,
                "restore_destination": file_dest_bucket_0,
                "multipart_chunksize_mb": collection_multipart_chunksize_mb,
                "status_id": OrcaStatus.PENDING.value,
                "request_time": mock.ANY,
                "last_update": mock.ANY,
            }], db_queue_url)
        ] * (max_retries + 1))
        self.assertEqual(max_retries + 1, mock_create_status_for_job.call_count)
        self.assertEqual(0, mock_process_granule.call_count)

    def test_inner_task_missing_glacier_bucket_raises(self):
        try:
            request_files.inner_task(
                {request_files.EVENT_CONFIG_KEY: dict()},
                randint(0, 99),  # nosec
                randint(0, 99),  # nosec
                uuid.uuid4().__str__(),
                randint(0, 99),  # nosec
                "https://db.queue.url",
            )
            self.fail("Error not raised.")
        except request_files.RestoreRequestError:
            pass

    # noinspection PyUnusedLocal
    @patch("request_files.shared_recovery.create_status_for_job")
    @patch("time.sleep")
    @patch("request_files.process_granule")
    @patch("request_files.object_exists")
    @patch("boto3.client")
    def test_inner_task_missing_files_do_not_halt(
        self,
        mock_boto3_client: MagicMock,
        mock_object_exists: MagicMock,
        mock_process_granule: MagicMock,
        mock_sleep: MagicMock,
        mock_create_status_for_job: MagicMock,
    ):
        """
        A return of 'false' from object_exists should ignore the file and continue.
        """
        glacier_bucket = uuid.uuid4().__str__()
        collection_multipart_chunksize_mb = random.randint(1, 10000)
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
            request_files.FILE_KEY_KEY: file_key_0,
            request_files.FILE_DEST_BUCKET_KEY: file_dest_bucket_0,
        }
        expected_file0_output = {
            request_files.FILE_SUCCESS_KEY: False,
            "filename": file_key_0,
            "key_path": file_key_0,
            "restore_destination": file_dest_bucket_0,
            "multipart_chunksize_mb": collection_multipart_chunksize_mb,
            "status_id": OrcaStatus.PENDING.value,
            "request_time": mock.ANY,
            "last_update": mock.ANY,
        }
        file_1 = {
            request_files.FILE_KEY_KEY: file_key_1,
            request_files.FILE_DEST_BUCKET_KEY: file_dest_bucket_1,
        }
        expected_file1_output = {
            request_files.FILE_SUCCESS_KEY: False,
            "filename": file_key_1,
            "key_path": file_key_1,
            "restore_destination": file_dest_bucket_1,
            "multipart_chunksize_mb": collection_multipart_chunksize_mb,
            "status_id": OrcaStatus.PENDING.value,
            "request_time": mock.ANY,
            "last_update": mock.ANY,
        }

        missing_file = {
            request_files.FILE_KEY_KEY: missing_file_key,
            request_files.FILE_DEST_BUCKET_KEY: missing_file_dest_bucket,
            "multipart_chunksize_mb": collection_multipart_chunksize_mb,
        }
        expected_missing_file_output = {
            request_files.FILE_SUCCESS_KEY: True,
            "filename": missing_file_key,
            "key_path": missing_file_key,
            "restore_destination": missing_file_dest_bucket,
            "multipart_chunksize_mb": collection_multipart_chunksize_mb,
            "status_id": OrcaStatus.FAILED.value,
            "request_time": mock.ANY,
            "last_update": mock.ANY,
            "error_message": f"{missing_file_key} does not exist in {glacier_bucket} bucket",
            "completion_time": mock.ANY,
        }

        expected_input_granule_files = [
            expected_file0_output,
            expected_missing_file_output,
            expected_file1_output,
        ]
        granule = {
            request_files.GRANULE_GRANULE_ID_KEY: granule_id,
            request_files.GRANULE_KEYS_KEY: [
                file_0,
                missing_file,
                file_1,
            ],
        }
        expected_input_granule = granule.copy()
        expected_input_granule[
            request_files.GRANULE_RECOVER_FILES_KEY
        ] = expected_input_granule_files
        event = {
            request_files.EVENT_CONFIG_KEY: {
                request_files.CONFIG_ORCA_DEFAULT_BUCKET_OVERRIDE_KEY: glacier_bucket,
                request_files.CONFIG_JOB_ID_KEY: job_id,
                request_files.CONFIG_MULTIPART_CHUNKSIZE_MB_KEY: collection_multipart_chunksize_mb,
            },
            request_files.EVENT_INPUT_KEY: {
                request_files.INPUT_GRANULES_KEY: [granule]
            },
        }
        max_retries = randint(0, 99)  # nosec
        retry_sleep_secs = randint(0, 99)  # nosec
        retrieval_type = uuid.uuid4().__str__()
        restore_expire_days = randint(0, 99)  # nosec
        mock_s3_cli = mock_boto3_client("s3")

        # noinspection PyUnusedLocal
        def object_exists_return_func(
            input_s3_cli, input_glacier_bucket, input_file_key
        ):
            return input_file_key in [file_key_0, file_key_1]

        mock_object_exists.side_effect = object_exists_return_func

        result = request_files.inner_task(
            event,
            max_retries,
            retry_sleep_secs,
            retrieval_type,
            restore_expire_days,
            db_queue_url,
        )

        files_all = [
            {
                "success": False,  # This value is changed by process_granule.
                "filename": file_key_0,
                "key_path": file_key_0,
                "restore_destination": file_dest_bucket_0,
                "multipart_chunksize_mb": collection_multipart_chunksize_mb,
                "status_id": OrcaStatus.PENDING.value,
                "request_time": mock.ANY,
                "last_update": mock.ANY,
            },
            {
                "success": True,  # Set to `True` when not found.
                "filename": missing_file_key,
                "key_path": missing_file_key,
                "restore_destination": missing_file_dest_bucket,
                "multipart_chunksize_mb": collection_multipart_chunksize_mb,
                "status_id": OrcaStatus.FAILED.value,
                "request_time": mock.ANY,
                "last_update": mock.ANY,
                "error_message": f"{missing_file_key} does not exist in {glacier_bucket} bucket",
                "completion_time": mock.ANY,
            },
            {
                "success": False,  # This value is changed by process_granule.
                "filename": file_key_1,
                "key_path": file_key_1,
                "restore_destination": file_dest_bucket_1,
                "multipart_chunksize_mb": collection_multipart_chunksize_mb,
                "status_id": OrcaStatus.PENDING.value,
                "request_time": mock.ANY,
                "last_update": mock.ANY,
            },
        ]
        mock_create_status_for_job.assert_called_once_with(
            job_id, granule_id, glacier_bucket, files_all, db_queue_url
        )
        mock_process_granule.assert_called_once_with(
            mock_s3_cli,
            expected_input_granule,
            glacier_bucket,
            restore_expire_days,
            max_retries,
            retry_sleep_secs,
            retrieval_type,
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
            request_files.OS_ENVIRON_ORCA_DEFAULT_GLACIER_BUCKET_KEY: uuid.uuid4().__str__()
        },
        clear=True,
    )
    def test_get_default_glacier_bucket_name_returns_override_if_present(self):
        bucket = Mock()
        result = request_files.get_default_glacier_bucket_name(
            {request_files.CONFIG_ORCA_DEFAULT_BUCKET_OVERRIDE_KEY: bucket}
        )
        self.assertEqual(bucket, result)

    @patch.dict(
        os.environ,
        {
            request_files.OS_ENVIRON_ORCA_DEFAULT_GLACIER_BUCKET_KEY: uuid.uuid4().__str__()
        },
        clear=True,
    )
    def test_get_default_glacier_bucket_name_returns_default_bucket_if_no_override(
        self,
    ):
        bucket = os.environ[request_files.OS_ENVIRON_ORCA_DEFAULT_GLACIER_BUCKET_KEY]
        result = request_files.get_default_glacier_bucket_name({})
        self.assertEqual(bucket, result)

    @patch.dict(
        os.environ,
        {
            request_files.OS_ENVIRON_ORCA_DEFAULT_GLACIER_BUCKET_KEY: uuid.uuid4().__str__()
        },
        clear=True,
    )
    def test_get_default_glacier_bucket_name_returns_default_bucket_if_none_override(
        self,
    ):
        bucket = os.environ[request_files.OS_ENVIRON_ORCA_DEFAULT_GLACIER_BUCKET_KEY]
        result = request_files.get_default_glacier_bucket_name(
            {
                request_files.CONFIG_ORCA_DEFAULT_BUCKET_OVERRIDE_KEY: None,
            }
        )
        self.assertEqual(bucket, result)

    @patch.dict(
        os.environ,
        {
            request_files.OS_ENVIRON_ORCA_DEFAULT_GLACIER_BUCKET_KEY: uuid.uuid4().__str__()
        },
        clear=True,
    )
    def test_get_default_glacier_bucket_name_returns_env_bucket_if_no_other(self):
        bucket = os.environ[request_files.OS_ENVIRON_ORCA_DEFAULT_GLACIER_BUCKET_KEY]
        result = request_files.get_default_glacier_bucket_name(
            {request_files.CONFIG_ORCA_DEFAULT_BUCKET_OVERRIDE_KEY: None}
        )
        self.assertEqual(bucket, result)

    def test_get_default_glacier_bucket_name_no_bucket_raises_error(self):
        os.environ.pop(request_files.OS_ENVIRON_ORCA_DEFAULT_GLACIER_BUCKET_KEY, None)
        with self.assertRaises(KeyError) as cm:
            request_files.get_default_glacier_bucket_name(
                {request_files.CONFIG_ORCA_DEFAULT_BUCKET_OVERRIDE_KEY: None}
            )
        self.assertEqual("'ORCA_DEFAULT_BUCKET'", str(cm.exception))

    @patch("time.sleep")
    @patch("request_files.restore_object")
    def test_process_granule_minimal_path(
        self, mock_restore_object: MagicMock, mock_sleep: MagicMock
    ):
        mock_s3 = Mock()
        max_retries = randint(10, 999)  # nosec
        glacier_bucket = uuid.uuid4().__str__()
        retry_sleep_secs = randint(0, 99)  # nosec
        retrieval_type = uuid.uuid4().__str__()
        restore_expire_days = randint(0, 99)  # nosec
        granule_id = uuid.uuid4().__str__()
        file_name_0 = uuid.uuid4().__str__()
        dest_bucket_0 = uuid.uuid4().__str__()
        file_name_1 = uuid.uuid4().__str__()
        dest_bucket_1 = uuid.uuid4().__str__()
        job_id = uuid.uuid4().__str__()
        db_queue_url = "http://" + uuid.uuid4().__str__() + ".blah"

        granule = {
            request_files.GRANULE_GRANULE_ID_KEY: granule_id,
            request_files.GRANULE_RECOVER_FILES_KEY: [
                {
                    "success": False,
                    "filename": os.path.basename(file_name_0),
                    "key_path": file_name_0,
                    "restore_destination": dest_bucket_0,
                    "status_id": 1,
                },
                {
                    "success": False,
                    "filename": os.path.basename(file_name_1),
                    "key_path": file_name_1,
                    "restore_destination": dest_bucket_1,
                    "status_id": 1,
                },
            ],
        }

        request_files.process_granule(
            mock_s3,
            granule,
            glacier_bucket,
            restore_expire_days,
            max_retries,
            retry_sleep_secs,
            retrieval_type,
            job_id,
            db_queue_url,
        )

        self.assertTrue(
            granule[request_files.GRANULE_RECOVER_FILES_KEY][0][
                request_files.FILE_SUCCESS_KEY
            ]
        )
        self.assertTrue(
            granule[request_files.GRANULE_RECOVER_FILES_KEY][1][
                request_files.FILE_SUCCESS_KEY
            ]
        )

        mock_restore_object.assert_has_calls(
            [
                call(
                    mock_s3,
                    file_name_0,
                    restore_expire_days,
                    glacier_bucket,
                    1,
                    job_id,
                    retrieval_type,
                ),
                call(
                    mock_s3,
                    file_name_1,
                    restore_expire_days,
                    glacier_bucket,
                    1,
                    job_id,
                    retrieval_type,
                ),
            ]
        )
        self.assertEqual(2, mock_restore_object.call_count)
        mock_sleep.assert_not_called()

    @patch("time.sleep")
    @patch("request_files.restore_object")
    def test_process_granule_one_client_or_key_error_retries(
        self, mock_restore_object: MagicMock, mock_sleep: MagicMock
    ):
        mock_s3 = Mock()
        max_retries = 5
        glacier_bucket = uuid.uuid4().__str__()
        retry_sleep_secs = randint(0, 99)  # nosec
        retrieval_type = uuid.uuid4().__str__()
        restore_expire_days = randint(0, 99)  # nosec
        granule_id = uuid.uuid4().__str__()
        file_name_0 = uuid.uuid4().__str__()
        dest_bucket_0 = uuid.uuid4().__str__()
        job_id = uuid.uuid4().__str__()
        db_queue_url = "http://" + uuid.uuid4().__str__() + ".blah"

        granule = {
            request_files.GRANULE_GRANULE_ID_KEY: granule_id,
            request_files.GRANULE_RECOVER_FILES_KEY: [
                {
                    "filename": os.path.basename(file_name_0),
                    "key_path": file_name_0,
                    "restore_destination": dest_bucket_0,
                    "success": False,
                    "status_id": 1,
                }
            ],
        }

        mock_restore_object.side_effect = [ClientError({}, ""), None]

        request_files.process_granule(
            mock_s3,
            granule,
            glacier_bucket,
            restore_expire_days,
            max_retries,
            retry_sleep_secs,
            retrieval_type,
            job_id,
            db_queue_url,
        )

        self.assertTrue(
            granule[request_files.GRANULE_RECOVER_FILES_KEY][0][
                request_files.FILE_SUCCESS_KEY
            ]
        )
        mock_restore_object.assert_has_calls(
            [
                call(
                    mock_s3,
                    file_name_0,
                    restore_expire_days,
                    glacier_bucket,
                    1,
                    job_id,
                    retrieval_type,
                ),
                call(
                    mock_s3,
                    file_name_0,
                    restore_expire_days,
                    glacier_bucket,
                    2,
                    job_id,
                    retrieval_type,
                ),
            ]
        )
        self.assertEqual(2, mock_restore_object.call_count)
        mock_sleep.assert_has_calls([call(retry_sleep_secs)])
        self.assertEqual(1, mock_sleep.call_count)

    @patch("orca_shared.recovery.shared_recovery.update_status_for_file")
    @patch("time.sleep")
    @patch("request_files.restore_object")
    @patch("cumulus_logger.CumulusLogger.error")
    def test_process_granule_client_errors_retries_until_cap(
        self,
        mock_logger_error: MagicMock,
        mock_restore_object: MagicMock,
        mock_sleep: MagicMock,
        mock_update_status_for_file: MagicMock,
    ):
        mock_s3 = Mock()
        max_retries = randint(3, 20)
        glacier_bucket = uuid.uuid4().__str__()
        retry_sleep_secs = randint(0, 99)  # nosec
        retrieval_type = uuid.uuid4().__str__()
        restore_expire_days = randint(0, 99)  # nosec
        granule_id = uuid.uuid4().__str__()
        file_name_0 = uuid.uuid4().__str__()
        dest_bucket_0 = uuid.uuid4().__str__()
        job_id = uuid.uuid4().__str__()
        db_queue_url = "http://" + uuid.uuid4().__str__() + ".blah"

        granule = {
            request_files.GRANULE_GRANULE_ID_KEY: granule_id,
            request_files.GRANULE_RECOVER_FILES_KEY: [
                {
                    "filename": os.path.basename(file_name_0),
                    "key_path": file_name_0,
                    "restore_destination": dest_bucket_0,
                    "success": False,
                    "status_id": 1,
                },
            ],
        }

        expected_error = ClientError({}, "")
        mock_restore_object.side_effect = expected_error

        try:
            request_files.process_granule(
                mock_s3,
                granule,
                glacier_bucket,
                restore_expire_days,
                max_retries,
                retry_sleep_secs,
                retrieval_type,
                job_id,
                db_queue_url,
            )
            self.fail("Error not Raised.")
        # except request_files.RestoreRequestError:
        except request_files.RestoreRequestError as caught_error:
            self.assertEqual(
                f"One or more files failed to be requested from {glacier_bucket}.",
                str(caught_error),
            )
        self.assertFalse(
            granule[request_files.GRANULE_RECOVER_FILES_KEY][0][
                request_files.FILE_SUCCESS_KEY
            ]
        )

        mock_restore_object.assert_has_calls(
            [
                call(
                    mock_s3,
                    file_name_0,
                    restore_expire_days,
                    glacier_bucket,
                    1,
                    job_id,
                    retrieval_type,
                ),
                call(
                    mock_s3,
                    file_name_0,
                    restore_expire_days,
                    glacier_bucket,
                    2,
                    job_id,
                    retrieval_type,
                ),
                call(
                    mock_s3,
                    file_name_0,
                    restore_expire_days,
                    glacier_bucket,
                    3,
                    job_id,
                    retrieval_type,
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
                    "Failed to restore {file} from {glacier_bucket}. Encountered error [ {err} ].",
                    file=file_name_0,
                    glacier_bucket=glacier_bucket,
                    err=expected_error,
                ),
                call(
                    f"One or more files failed to be requested from {glacier_bucket}.  GRANULE: {{granule}}",
                    granule=json.dumps(granule),
                ),
            ]
        )

    @patch("orca_shared.recovery.shared_recovery.update_status_for_file")
    @patch("time.sleep")
    @patch("request_files.restore_object")
    @patch("cumulus_logger.CumulusLogger.error")
    def test_process_granule_error_when_posting_status_raises_after_retries(
            self,
            mock_logger_error: MagicMock,
            mock_restore_object: MagicMock,
            mock_sleep: MagicMock,
            mock_update_status_for_file: MagicMock,
    ):
        """
        If a file expended all attempts for recovery, and posting to status DB expended all attempts, raise error.
        """
        mock_s3 = Mock()
        max_retries = randint(3, 20)
        glacier_bucket = uuid.uuid4().__str__()
        retry_sleep_secs = randint(0, 99)  # nosec
        retrieval_type = uuid.uuid4().__str__()
        restore_expire_days = randint(0, 99)  # nosec
        granule_id = uuid.uuid4().__str__()
        file_name_0 = uuid.uuid4().__str__()
        dest_bucket_0 = uuid.uuid4().__str__()
        job_id = uuid.uuid4().__str__()
        db_queue_url = "http://" + uuid.uuid4().__str__() + ".blah"

        granule = {
            request_files.GRANULE_GRANULE_ID_KEY: granule_id,
            request_files.GRANULE_RECOVER_FILES_KEY: [
                {
                    "filename": os.path.basename(file_name_0),
                    "key_path": file_name_0,
                    "restore_destination": dest_bucket_0,
                    "success": False,
                    "status_id": 1,
                },
            ],
        }

        expected_error = ClientError({}, "")
        mock_restore_object.side_effect = expected_error

        expected_status_error = Exception(uuid.uuid4().__str__())
        mock_update_status_for_file.side_effect = expected_status_error

        try:
            request_files.process_granule(
                mock_s3,
                granule,
                glacier_bucket,
                restore_expire_days,
                max_retries,
                retry_sleep_secs,
                retrieval_type,
                job_id,
                db_queue_url,
            )
            self.fail("Error not Raised.")
        # except request_files.RestoreRequestError:
        except Exception as caught_error:
            self.assertEqual(
                f"Unable to send message to QUEUE {db_queue_url}",
                str(caught_error),
            )
        self.assertFalse(
            granule[request_files.GRANULE_RECOVER_FILES_KEY][0][
                request_files.FILE_SUCCESS_KEY
            ]
        )

        mock_restore_object.assert_has_calls(
            [
                call(
                    mock_s3,
                    file_name_0,
                    restore_expire_days,
                    glacier_bucket,
                    1,
                    job_id,
                    retrieval_type,
                ),
                call(
                    mock_s3,
                    file_name_0,
                    restore_expire_days,
                    glacier_bucket,
                    2,
                    job_id,
                    retrieval_type,
                ),
                call(
                    mock_s3,
                    file_name_0,
                    restore_expire_days,
                    glacier_bucket,
                    3,
                    job_id,
                    retrieval_type,
                ),
            ]
        )
        mock_update_status_for_file.assert_has_calls([
            call(
                job_id,
                granule_id,
                file_name_0,
                OrcaStatus.FAILED,
                str(expected_error),
                db_queue_url,
            )
        ] * (max_retries + 1))
        self.assertEqual(max_retries + 1, mock_restore_object.call_count)
        self.assertEqual(max_retries + 1, mock_update_status_for_file.call_count)
        mock_sleep.assert_has_calls([call(retry_sleep_secs)] * max_retries * 2)
        mock_logger_error.assert_has_calls(
            [
                call(
                    "Failed to restore {file} from {glacier_bucket}. Encountered error [ {err} ].",
                    file=file_name_0,
                    glacier_bucket=glacier_bucket,
                    err=expected_error,
                ),
                call(
                    f"Ran into error posting to SQS {max_retries + 1} time(s) with exception {{ex}}", ex=str(expected_status_error)
                )
            ], any_order=True
        )

    def test_object_exists_happy_path(self):
        mock_s3_cli = Mock()
        mock_s3_cli.head_object.side_effect = None
        glacier_bucket = uuid.uuid4().__str__()
        file_key = uuid.uuid4().__str__()

        result = request_files.object_exists(mock_s3_cli, glacier_bucket, file_key)
        self.assertTrue(result)

    def test_object_exists_client_error_raised(self):
        expected_error = ClientError(
            {"Error": {"Code": "Teapot", "Message": "test"}}, ""
        )
        mock_s3_cli = Mock()
        mock_s3_cli.head_object.side_effect = expected_error
        glacier_bucket = uuid.uuid4().__str__()
        file_key = uuid.uuid4().__str__()

        try:
            request_files.object_exists(mock_s3_cli, glacier_bucket, file_key)
            self.fail("Error not raised.")
        except ClientError as err:
            self.assertEqual(expected_error, err)

    def test_object_exists_NotFound_returns_false(self):
        expected_error = ClientError(
            {"Error": {"Code": "404", "Message": "Not Found"}}, ""
        )
        mock_s3_cli = Mock()
        mock_s3_cli.head_object.side_effect = expected_error
        glacier_bucket = uuid.uuid4().__str__()
        file_key = uuid.uuid4().__str__()

        result = request_files.object_exists(mock_s3_cli, glacier_bucket, file_key)
        self.assertFalse(result)

    def test_restore_object_happy_path(self):
        glacier_bucket = uuid.uuid4().__str__()
        key = uuid.uuid4().__str__()
        restore_expire_days = randint(0, 99)  # nosec
        retrieval_type = uuid.uuid4().__str__()
        mock_s3_cli = Mock()
        mock_s3_cli.restore_object.return_value = {
            "ResponseMetadata": {"HTTPStatusCode": 202}
        }

        request_files.restore_object(
            mock_s3_cli,
            key,
            restore_expire_days,
            glacier_bucket,
            randint(0, 99),  # nosec
            uuid.uuid4().__str__(),
            retrieval_type,
        )

        mock_s3_cli.restore_object.assert_called_once_with(
            Bucket=glacier_bucket,
            Key=key,
            RestoreRequest={
                "Days": restore_expire_days,
                "GlacierJobParameters": {"Tier": retrieval_type},
            },
        )

    # noinspection PyUnusedLocal
    @patch("cumulus_logger.CumulusLogger.info")
    def test_restore_object_client_error_raises(self, mock_logger_info: MagicMock):
        job_id = uuid.uuid4().__str__()
        glacier_bucket = uuid.uuid4().__str__()
        key = uuid.uuid4().__str__()
        restore_expire_days = randint(0, 99)  # nosec
        retrieval_type = uuid.uuid4().__str__()
        expected_error = ClientError({}, "")
        mock_s3_cli = Mock()
        mock_s3_cli.restore_object.side_effect = expected_error

        try:
            request_files.restore_object(
                mock_s3_cli,
                key,
                restore_expire_days,
                glacier_bucket,
                1,
                job_id,
                retrieval_type,
            )
            self.fail("Error not Raised.")
        except ClientError as error:
            self.assertEqual(expected_error, error)
            mock_s3_cli.restore_object.assert_called_once_with(
                Bucket=glacier_bucket,
                Key=key,
                RestoreRequest={
                    "Days": restore_expire_days,
                    "GlacierJobParameters": {"Tier": retrieval_type},
                },
            )

    # noinspection PyUnusedLocal
    @patch("cumulus_logger.CumulusLogger.info")
    def test_restore_object_200_returned_raises(self, mock_logger_info: MagicMock):
        """
        A 200 indicates that the file is already restored, and thus cannot presently be restored again.
        Should be raised.
        """
        glacier_bucket = uuid.uuid4().__str__()
        key = uuid.uuid4().__str__()
        restore_expire_days = randint(0, 99)  # nosec
        retrieval_type = uuid.uuid4().__str__()
        mock_s3_cli = Mock()
        mock_s3_cli.restore_object.return_value = {
            "ResponseMetadata": {"HTTPStatusCode": 200}
        }

        with self.assertRaises(ClientError) as context:
            request_files.restore_object(
                mock_s3_cli,
                key,
                restore_expire_days,
                glacier_bucket,
                2,
                uuid.uuid4().__str__(),
                retrieval_type,
            )
        self.assertEqual(
            f"An error occurred (HTTPStatus: 200) when calling the restore_object operation: "
            f"File '{key}' in bucket '{glacier_bucket}' has already been recovered.",
            str(context.exception),
        )

    @patch("request_files.task")
    def test_handler_happy_path(self, mock_task: MagicMock):
        """
        Tests that between the handler and CMA, input is translated into what task expects.
        """
        # todo: Remove these hardcoded keys
        file0 = "MOD09GQ___006/2017/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.h5"
        bucket_name = uuid.uuid4().__str__()

        input_event = create_handler_event()
        expected_task_input = {
            "input": input_event["payload"],
            # Values here are based on the event task_config values that are mapped
            "config": {
                request_files.CONFIG_JOB_ID_KEY: None,
                request_files.CONFIG_MULTIPART_CHUNKSIZE_MB_KEY: 750,
                request_files.CONFIG_ORCA_DEFAULT_BUCKET_OVERRIDE_KEY: "lp-sndbx-cumulus-orca"
            },
        }
        mock_task.return_value = {
            "granules": [
                {
                    "granuleId": "some_granule_id",
                    "recover_files": [
                        {
                            "filename": os.path.basename(file0),
                            "key_path": file0,
                            "restore_destination": bucket_name,
                            "success": True,
                            "status_id": 1,
                            "last_update": "2021-01-01T23:53:43.097+00:00",
                            "request_time": "2021-01-01T23:53:43.097+00:00",
                        },
                    ],
                }
            ],
            "asyncOperationId": "some_job_id",
        }
        context = LambdaContextMock()
        result = request_files.handler(input_event, context)
        mock_task.assert_called_once_with(expected_task_input, context)

        self.assertEqual(mock_task.return_value, result["payload"])

    # noinspection PyUnusedLocal
    @patch("request_files.shared_recovery.create_status_for_job")
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
        key0 = {"key": file0, "dest_bucket": protected_bucket_name}
        key1 = {"key": file1, "dest_bucket": protected_bucket_name}
        key2 = {"key": file2, "dest_bucket": public_bucket_name}
        key3 = {"key": file3, "dest_bucket": public_bucket_name}

        os.environ[request_files.OS_ENVIRON_DB_QUEUE_URL_KEY] = "https://db.queue.url"
        job_id = uuid.uuid4().__str__()
        granule_id = "MOD09GQ.A0219114.N5aUCG.006.0656338553321"
        files = [key0, key1, key2, key3]
        input_event = {
            "payload": {"granules": [{"granuleId": granule_id, "keys": files}]},
            "task_config": {
                request_files.CONFIG_ORCA_DEFAULT_BUCKET_OVERRIDE_KEY: "my-dr-fake-glacier-bucket",
                "asyncOperationId": job_id,
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
        result = request_files.handler(input_event, context)

        result_value = result["payload"]

        mock_boto3_client.assert_has_calls([call("s3")])
        mock_s3_cli.head_object.assert_any_call(
            Bucket="my-dr-fake-glacier-bucket", Key=file0
        )
        mock_s3_cli.head_object.assert_any_call(
            Bucket="my-dr-fake-glacier-bucket", Key=file1
        )
        mock_s3_cli.head_object.assert_any_call(
            Bucket="my-dr-fake-glacier-bucket", Key=file2
        )
        mock_s3_cli.head_object.assert_any_call(
            Bucket="my-dr-fake-glacier-bucket", Key=file3
        )
        restore_req_exp = {"Days": 5, "GlacierJobParameters": {"Tier": "Standard"}}

        mock_s3_cli.restore_object.assert_any_call(
            Bucket="my-dr-fake-glacier-bucket",
            Key=file0,
            RestoreRequest=restore_req_exp,
        )
        mock_s3_cli.restore_object.assert_any_call(
            Bucket="my-dr-fake-glacier-bucket",
            Key=file1,
            RestoreRequest=restore_req_exp,
        )
        mock_s3_cli.restore_object.assert_any_call(
            Bucket="my-dr-fake-glacier-bucket",
            Key=file2,
            RestoreRequest=restore_req_exp,
        )
        mock_s3_cli.restore_object.assert_called_with(
            Bucket="my-dr-fake-glacier-bucket",
            Key=file3,
            RestoreRequest=restore_req_exp,
        )

        exp_gran = {
            "granuleId": granule_id,
            "keys": [
                {"dest_bucket": protected_bucket_name, "key": file0},
                {"dest_bucket": protected_bucket_name, "key": file1},
                {"dest_bucket": public_bucket_name, "key": file2},
                {"dest_bucket": public_bucket_name, "key": file3},
            ],
            "recover_files": [
                {
                    "filename": os.path.basename(file0),
                    "key_path": file0,
                    "restore_destination": protected_bucket_name,
                    "success": True,
                    "multipart_chunksize_mb": None,
                    "status_id": 1,
                },
                {
                    "filename": os.path.basename(file1),
                    "key_path": file1,
                    "restore_destination": protected_bucket_name,
                    "success": True,
                    "multipart_chunksize_mb": None,
                    "status_id": 1,
                },
                {
                    "filename": os.path.basename(file2),
                    "key_path": file2,
                    "restore_destination": public_bucket_name,
                    "success": True,
                    "multipart_chunksize_mb": None,
                    "status_id": 1,
                },
                {
                    "filename": os.path.basename(file3),
                    "key_path": file3,
                    "restore_destination": public_bucket_name,
                    "success": True,
                    "multipart_chunksize_mb": None,
                    "status_id": 1,
                },
            ],
        }
        exp_granules = {
            "granules": [exp_gran],
            "asyncOperationId": job_id,
        }

        # Validate the output is correct
        with open("schemas/output.json", "r") as raw_schema:
            schema = json.loads(raw_schema.read())

        validate = fastjsonschema.compile(schema)
        validate(result_value)

        # Check the values of the result less the times since those will never match
        for granule in result_value["granules"]:
            for file in granule["recover_files"]:
                file.pop("request_time", None)
                file.pop("last_update", None)
                file.pop("completion_time", None)

        self.assertEqual(exp_granules, result_value)


if __name__ == "__main__":
    unittest.main(argv=["start"])
