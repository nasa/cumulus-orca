"""
Name: test_request_files.py

Description:  Unit tests for request_files.py.
"""
import json
import os
import unittest
import uuid
from random import randint, uniform
from unittest import mock
from unittest.mock import patch, MagicMock, call, Mock

from orca_shared.shared_recovery import OrcaStatus
from test.request_helpers import LambdaContextMock, create_handler_event

# noinspection PyPackageRequirements
import fastjsonschema as fastjsonschema
from botocore.exceptions import ClientError

import request_files

# noinspection PyPackageRequirements

FILE1 = "MOD09GQ___006/2017/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.h5"
FILE2 = "MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.h5.met"
FILE3 = "MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321_ndvi.jpg"
FILE4 = "MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml"
PROTECTED_BUCKET = "sndbx-cumulus-protected"
PUBLIC_BUCKET = "sndbx-cumulus-public"
KEY1 = {"key": FILE1, "dest_bucket": PROTECTED_BUCKET}
KEY2 = {"key": FILE2, "dest_bucket": PROTECTED_BUCKET}
KEY3 = {"key": FILE3, "dest_bucket": PUBLIC_BUCKET}
KEY4 = {"key": FILE4, "dest_bucket": PUBLIC_BUCKET}


class TestRequestFiles(unittest.TestCase):
    """
    TestRequestFiles.
    """

    def setUp(self):
        # todo: These values should NOT be hard-coded as present for every test.
        os.environ[request_files.OS_ENVIRON_DB_QUEUE_URL_KEY] = "https://db.queue.url"
        os.environ[request_files.OS_ENVIRON_RESTORE_EXPIRE_DAYS_KEY] = "5"
        os.environ[request_files.OS_ENVIRON_RESTORE_REQUEST_RETRIES_KEY] = "2"
        os.environ[
            request_files.OS_ENVIRON_ORCA_DEFAULT_GLACIER_BUCKET_KEY
        ] = "default_glacier_bucket"
        os.environ["PREFIX"] = uuid.uuid4().__str__()
        os.environ.pop("CUMULUS_MESSAGE_ADAPTER_DISABLED", None)
        self.context = LambdaContextMock()
        self.maxDiff = None

    def tearDown(self):
        os.environ.pop("PREFIX", None)
        os.environ.pop(request_files.OS_ENVIRON_RESTORE_EXPIRE_DAYS_KEY, None)
        os.environ.pop(request_files.OS_ENVIRON_RESTORE_REQUEST_RETRIES_KEY, None)
        os.environ.pop(request_files.OS_ENVIRON_RESTORE_RETRY_SLEEP_SECS_KEY, None)
        os.environ.pop(request_files.OS_ENVIRON_RESTORE_RETRIEVAL_TYPE_KEY, None)
        os.environ.pop(request_files.OS_ENVIRON_DB_QUEUE_URL_KEY, None)

    @patch("request_files.inner_task")
    def test_task_happy_path(self, mock_inner_task: MagicMock):
        """
        All variables present and valid.
        """
        job_id = uuid.uuid4().__str__()
        glacier_bucket = uuid.uuid4().__str__()
        mock_event = {
            request_files.EVENT_CONFIG_KEY: {
                request_files.CONFIG_GLACIER_BUCKET_KEY: glacier_bucket,
                request_files.CONFIG_JOB_ID_KEY: job_id,
            },
        }
        max_retries = randint(0, 99)  # nosec
        retry_sleep_secs = uniform(0, 99)  # nosec
        retrieval_type = "Bulk"
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

        mock_inner_task.assert_called_once_with(
            {
                request_files.EVENT_CONFIG_KEY: {
                    request_files.CONFIG_GLACIER_BUCKET_KEY: glacier_bucket,
                    request_files.CONFIG_JOB_ID_KEY: job_id,
                },
            },
            max_retries,
            retry_sleep_secs,
            retrieval_type,
            exp_days,
            db_queue_url,
        )

    @patch("request_files.inner_task")
    def test_task_default_for_missing_max_retries(self, mock_inner_task: MagicMock):
        """
        If max_retries missing, use default.
        """
        job_id = uuid.uuid4().__str__()
        glacier_bucket = uuid.uuid4().__str__()
        mock_event = {
            request_files.EVENT_CONFIG_KEY: {
                request_files.CONFIG_GLACIER_BUCKET_KEY: glacier_bucket,
                request_files.CONFIG_JOB_ID_KEY: job_id,
            },
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

        mock_inner_task.assert_called_once_with(
            {
                request_files.EVENT_CONFIG_KEY: {
                    request_files.CONFIG_GLACIER_BUCKET_KEY: glacier_bucket,
                    request_files.CONFIG_JOB_ID_KEY: job_id,
                },
            },
            request_files.DEFAULT_MAX_REQUEST_RETRIES,
            retry_sleep_secs,
            retrieval_type,
            exp_days,
            db_queue_url,
        )

    @patch("request_files.inner_task")
    def test_task_default_for_missing_sleep_secs(self, mock_inner_task: MagicMock):
        """
        If sleep_secs missing, use default.
        """
        job_id = uuid.uuid4().__str__()
        glacier_bucket = uuid.uuid4().__str__()
        mock_event = {
            request_files.EVENT_CONFIG_KEY: {
                request_files.CONFIG_GLACIER_BUCKET_KEY: glacier_bucket,
                request_files.CONFIG_JOB_ID_KEY: job_id,
            },
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

        mock_inner_task.assert_called_once_with(
            {
                request_files.EVENT_CONFIG_KEY: {
                    request_files.CONFIG_GLACIER_BUCKET_KEY: glacier_bucket,
                    request_files.CONFIG_JOB_ID_KEY: job_id,
                },
            },
            max_retries,
            request_files.DEFAULT_RESTORE_RETRY_SLEEP_SECS,
            retrieval_type,
            exp_days,
            db_queue_url,
        )

    @patch("request_files.inner_task")
    def test_task_default_for_missing_retrieval_type(self, mock_inner_task: MagicMock):
        """
        If retrieval_type is missing, use default.
        """
        job_id = uuid.uuid4().__str__()
        glacier_bucket = uuid.uuid4().__str__()
        mock_event = {
            request_files.EVENT_CONFIG_KEY: {
                request_files.CONFIG_GLACIER_BUCKET_KEY: glacier_bucket,
                request_files.CONFIG_JOB_ID_KEY: job_id,
            },
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

        mock_inner_task.assert_called_once_with(
            {
                request_files.EVENT_CONFIG_KEY: {
                    request_files.CONFIG_GLACIER_BUCKET_KEY: glacier_bucket,
                    request_files.CONFIG_JOB_ID_KEY: job_id,
                },
            },
            max_retries,
            retry_sleep_secs,
            request_files.DEFAULT_RESTORE_RETRIEVAL_TYPE,
            exp_days,
            db_queue_url,
        )

    @patch("request_files.inner_task")
    def test_task_default_for_bad_retrieval_type(self, mock_inner_task: MagicMock):
        """
        If retrieval_type is invalid, use default.
        """
        job_id = uuid.uuid4().__str__()
        glacier_bucket = uuid.uuid4().__str__()
        mock_event = {
            request_files.EVENT_CONFIG_KEY: {
                request_files.CONFIG_GLACIER_BUCKET_KEY: glacier_bucket,
                request_files.CONFIG_JOB_ID_KEY: job_id,
            },
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

        mock_inner_task.assert_called_once_with(
            {
                request_files.EVENT_CONFIG_KEY: {
                    request_files.CONFIG_GLACIER_BUCKET_KEY: glacier_bucket,
                    request_files.CONFIG_JOB_ID_KEY: job_id,
                },
            },
            max_retries,
            retry_sleep_secs,
            request_files.DEFAULT_RESTORE_RETRIEVAL_TYPE,
            exp_days,
            db_queue_url,
        )

    @patch("request_files.inner_task")
    def test_task_default_for_missing_exp_days(self, mock_inner_task: MagicMock):
        """
        Uses default missing_exp_days if needed.
        """
        job_id = uuid.uuid4().__str__()
        glacier_bucket = uuid.uuid4().__str__()
        mock_event = {
            request_files.EVENT_CONFIG_KEY: {
                request_files.CONFIG_GLACIER_BUCKET_KEY: glacier_bucket,
                request_files.CONFIG_JOB_ID_KEY: job_id,
            },
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

        mock_inner_task.assert_called_once_with(
            {
                request_files.EVENT_CONFIG_KEY: {
                    request_files.CONFIG_GLACIER_BUCKET_KEY: glacier_bucket,
                    request_files.CONFIG_JOB_ID_KEY: job_id,
                },
            },
            max_retries,
            retry_sleep_secs,
            retrieval_type,
            request_files.DEFAULT_RESTORE_EXPIRE_DAYS,
            db_queue_url,
        )

    @patch("request_files.inner_task")
    def test_task_job_id_missing_generates(self, mock_inner_task: MagicMock):
        """
        If job_id missing, generates a new one.
        """
        glacier_bucket = uuid.uuid4().__str__()
        mock_event = {
            request_files.EVENT_CONFIG_KEY: {
                request_files.CONFIG_GLACIER_BUCKET_KEY: glacier_bucket,
                request_files.CONFIG_JOB_ID_KEY: None,
            },
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

        mock_inner_task.assert_called_once_with(
            {
                request_files.EVENT_CONFIG_KEY: {
                    request_files.CONFIG_GLACIER_BUCKET_KEY: glacier_bucket,
                    request_files.CONFIG_JOB_ID_KEY: job_id.__str__(),
                },
            },
            max_retries,
            retry_sleep_secs,
            retrieval_type,
            exp_days,
            db_queue_url,
        )

    @patch("request_files.inner_task")
    def test_task_glacier_bucket_missing_uses_default(self, mock_inner_task: MagicMock):
        """
        If glacier_bucket is missing, use default from env.
        """
        job_id = uuid.uuid4().__str__()
        glacier_bucket = uuid.uuid4().__str__()
        mock_event = {
            request_files.EVENT_CONFIG_KEY: {request_files.CONFIG_JOB_ID_KEY: job_id},
        }
        os.environ[
            request_files.OS_ENVIRON_ORCA_DEFAULT_GLACIER_BUCKET_KEY
        ] = glacier_bucket
        max_retries = randint(0, 99)  # nosec
        retry_sleep_secs = uniform(0, 99)  # nosec
        retrieval_type = "Bulk"
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

        with patch.object(uuid, "uuid4", return_value=job_id):
            request_files.task(mock_event, None)

        mock_inner_task.assert_called_once_with(
            {
                request_files.EVENT_CONFIG_KEY: {
                    request_files.CONFIG_GLACIER_BUCKET_KEY: glacier_bucket,
                    request_files.CONFIG_JOB_ID_KEY: job_id.__str__(),
                },
            },
            max_retries,
            retry_sleep_secs,
            retrieval_type,
            exp_days,
            db_queue_url,
        )

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
            "status_id": OrcaStatus.PENDING.value,
            "request_time": mock.ANY,
            "last_update": mock.ANY,
        }

        missing_file = {
            request_files.FILE_KEY_KEY: missing_file_key,
            request_files.FILE_DEST_BUCKET_KEY: missing_file_dest_bucket,
        }
        expected_missing_file_output = {
            request_files.FILE_SUCCESS_KEY: True,
            "filename": missing_file_key,
            "key_path": missing_file_key,
            "restore_destination": missing_file_dest_bucket,
            "status_id": OrcaStatus.FAILED.value,
            "request_time": mock.ANY,
            "last_update": mock.ANY,
            "error_message": f"{missing_file_key} does not exist in S3 bucket",
            "completion_time": mock.ANY
        }

        expected_input_granule_files = [expected_file0_output, expected_missing_file_output, expected_file1_output]
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
                request_files.CONFIG_GLACIER_BUCKET_KEY: glacier_bucket,
                request_files.CONFIG_JOB_ID_KEY: job_id
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
                "success": False,
                "filename": file_key_0,
                "key_path": file_key_0,
                "restore_destination": file_dest_bucket_0,
                "status_id": OrcaStatus.PENDING.value,
                "request_time": mock.ANY,
                "last_update": mock.ANY,
            },
            {
                "success": True,
                "filename": missing_file_key,
                "key_path": missing_file_key,
                "restore_destination": missing_file_dest_bucket,
                "status_id": OrcaStatus.FAILED.value,
                "request_time": mock.ANY,
                "last_update": mock.ANY,
                "error_message": f"{missing_file_key} does not exist in S3 bucket",
                "completion_time": mock.ANY
            },
            {
                "success": False,
                "filename": file_key_1,
                "key_path": file_key_1,
                "restore_destination": file_dest_bucket_1,
                "status_id": OrcaStatus.PENDING.value,
                "request_time": mock.ANY,
                "last_update": mock.ANY,
            },
        ]
        mock_create_status_for_job.assert_called_once_with(
            job_id, granule_id, glacier_bucket, files_all, db_queue_url
        )
        mock_process_granule.assert_has_calls(
            [
                call(
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
            ]
        )
        self.assertEqual(
            1, mock_process_granule.call_count
        )  # I'm hoping that we can remove the 'one granule' limit.
        self.assertEqual(
            {
                "granules": [expected_input_granule],
                "asyncOperationId": job_id,
            },
            result,
        )

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
    def test_process_granule_one_client_error_retries(
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
        files = [
            {
                "filename": file_name_0,
                "key_path": file_name_0,
                "restore_destination": dest_bucket_0,
                "status_id": OrcaStatus.PENDING.value,
                "error_message": None,
                "request_time": mock.ANY,
                "last_update": mock.ANY,
                "completion_time": None,
            },
        ]
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
        mock_sleep.assert_called_once_with(retry_sleep_secs)

    @patch("time.sleep")
    @patch("request_files.restore_object")
    @patch("cumulus_logger.CumulusLogger.error")
    def test_process_granule_client_errors_retries_until_cap(
        self,
        mock_logger_error: MagicMock,
        mock_restore_object: MagicMock,
        mock_sleep: MagicMock,
    ):
        mock_s3 = Mock()
        max_retries = randint(3, 20)  # nosec
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

        mock_restore_object.side_effect = ClientError({}, "")

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
        except Exception:
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

    @patch("cumulus_logger.CumulusLogger.info")
    def test_restore_object_happy_path(self, mock_logger_info: MagicMock):
        glacier_bucket = uuid.uuid4().__str__()
        key = uuid.uuid4().__str__()
        restore_expire_days = randint(0, 99)  # nosec
        retrieval_type = uuid.uuid4().__str__()
        mock_s3_cli = Mock()

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
    @patch("cumulus_logger.CumulusLogger.error")
    @patch("cumulus_logger.CumulusLogger.info")
    def test_restore_object_client_error_last_attempt_logs_and_raises(
        self, mock_logger_info: MagicMock, mock_logger_error: MagicMock
    ):
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
                2,
                uuid.uuid4().__str__(),
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
    @patch("cumulus_logger.CumulusLogger.error")
    @patch("cumulus_logger.CumulusLogger.info")
    def test_restore_object_log_to_db_fails_does_not_halt(
        self, mock_logger_info: MagicMock, mock_logger_error: MagicMock
    ):
        glacier_bucket = uuid.uuid4().__str__()
        key = uuid.uuid4().__str__()
        restore_expire_days = randint(0, 99)  # nosec
        retrieval_type = uuid.uuid4().__str__()
        mock_s3_cli = Mock()

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

    # The below are legacy tests that don't strictly check request_files.py on its own. Remove/adjust as needed.
    @patch("request_files.task")
    def test_handler_happy_path(self, mock_task: MagicMock):
        """
        Tests that between the handler and CMA, input is translated into what task expects.
        """
        input_event = create_handler_event()
        expected_task_input = {
            "input": input_event["payload"],
            "config": {"glacier-bucket": "podaac-sndbx-cumulus-glacier"},
        }
        mock_task.return_value = {
            "granules": [
                {
                    "granuleId": "some_granule_id",
                    "recover_files": [
                        {
                            "filename": os.path.basename(FILE1),
                            "key_path": FILE1,
                            "restore_destination": PROTECTED_BUCKET,
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
        result = request_files.handler(input_event, self.context)
        mock_task.assert_called_once_with(expected_task_input, self.context)

        self.assertEqual(mock_task.return_value, result["payload"])

    @patch("request_files.shared_recovery.post_entry_to_queue")
    @patch("boto3.client")
    @patch("cumulus_logger.CumulusLogger.info")
    def test_task_one_granule_4_files_success(
        self,
        mock_logger_info: MagicMock,
        mock_boto3_client: MagicMock,
        mock_post_entry_to_queue: MagicMock,
    ):
        """
        Test four files for one granule - successful
        """
        granule_id = "MOD09GQ.A0219114.N5aUCG.006.0656338553321"
        files = [KEY1, KEY2, KEY3, KEY4]
        input_event = {
            "input": {"granules": [{"granuleId": granule_id, "keys": files}]},
            "config": {
                "glacier-bucket": "my-dr-fake-glacier-bucket",
                "asyncOperationId": uuid.uuid4().__str__(),
            },
        }

        mock_s3_cli = mock_boto3_client("s3")
        mock_s3_cli.restore_object.side_effect = [None, None, None, None]

        result = request_files.task(input_event, self.context)

        mock_boto3_client.assert_has_calls([call("s3")])
        mock_s3_cli.head_object.assert_any_call(
            Bucket="my-dr-fake-glacier-bucket", Key=FILE1
        )
        mock_s3_cli.head_object.assert_any_call(
            Bucket="my-dr-fake-glacier-bucket", Key=FILE2
        )
        mock_s3_cli.head_object.assert_any_call(
            Bucket="my-dr-fake-glacier-bucket", Key=FILE3
        )
        mock_s3_cli.head_object.assert_any_call(
            Bucket="my-dr-fake-glacier-bucket", Key=FILE4
        )
        restore_req_exp = {"Days": 5, "GlacierJobParameters": {"Tier": "Standard"}}

        mock_s3_cli.restore_object.assert_any_call(
            Bucket="my-dr-fake-glacier-bucket",
            Key=FILE1,
            RestoreRequest=restore_req_exp,
        )
        mock_s3_cli.restore_object.assert_any_call(
            Bucket="my-dr-fake-glacier-bucket",
            Key=FILE2,
            RestoreRequest=restore_req_exp,
        )
        mock_s3_cli.restore_object.assert_any_call(
            Bucket="my-dr-fake-glacier-bucket",
            Key=FILE3,
            RestoreRequest=restore_req_exp,
        )
        mock_s3_cli.restore_object.assert_called_with(
            Bucket="my-dr-fake-glacier-bucket",
            Key=FILE4,
            RestoreRequest=restore_req_exp,
        )

        exp_gran = {
            "granuleId": granule_id,
            "keys": self.get_expected_keys(),
            "recover_files": self.get_expected_files(),
        }
        exp_granules = {
            "granules": [exp_gran],
            "asyncOperationId": input_event["config"]["asyncOperationId"],
        }

        # Check the values of the result less the times since those will never match
        result_value = result.copy()
        for granule in result_value["granules"]:
            for file in granule["recover_files"]:
                file.pop("request_time", None)
                file.pop("last_update", None)
                file.pop("completion_time", None)

        self.assertEqual(exp_granules, result_value)
        mock_post_entry_to_queue.assert_called_once()

    @staticmethod
    def get_expected_files():
        """
        builds a list of expected files
        """
        return [
            {
                "filename": os.path.basename(FILE1),
                "key_path": FILE1,
                "restore_destination": PROTECTED_BUCKET,
                "success": True,
                "status_id": 1,
            },
            {
                "filename": os.path.basename(FILE2),
                "key_path": FILE2,
                "restore_destination": PROTECTED_BUCKET,
                "success": True,
                "status_id": 1,
            },
            {
                "filename": os.path.basename(FILE3),
                "key_path": FILE3,
                "restore_destination": PUBLIC_BUCKET,
                "success": True,
                "status_id": 1,
            },
            {
                "filename": os.path.basename(FILE4),
                "key_path": FILE4,
                "restore_destination": PUBLIC_BUCKET,
                "success": True,
                "status_id": 1,
            },
        ]

    @staticmethod
    def get_expected_keys():
        """
        Builds a list of expected keys
        """
        return [
            {"dest_bucket": PROTECTED_BUCKET, "key": FILE1},
            {"dest_bucket": PROTECTED_BUCKET, "key": FILE2},
            {"dest_bucket": PUBLIC_BUCKET, "key": FILE3},
            {"dest_bucket": PUBLIC_BUCKET, "key": FILE4},
        ]

    # todo: single_query is not called in code. Replace with higher-level checks.
    @patch("request_files.shared_recovery.post_entry_to_queue")
    @patch("boto3.client")
    @patch("cumulus_logger.CumulusLogger.error")
    @patch("cumulus_logger.CumulusLogger.info")
    def test_task_one_granule_1_file_db_error(
        self,
        mock_logger_info: MagicMock,
        mock_logger_error: MagicMock,
        mock_boto3_client: MagicMock,
        mock_post_entry_to_queue: MagicMock,
    ):
        """
        Test one file for one granule - db error inserting status
        """
        granule_id = "MOD09GQ.A0219114.N5aUCG.006.0656338553321"
        input_event = {
            "input": {"granules": [{"granuleId": granule_id, "keys": [KEY1]}]},
            "config": {
                "glacier-bucket": "my-dr-fake-glacier-bucket",
                "asyncOperationId": uuid.uuid4().__str__(),
            },
        }

        mock_s3_cli = mock_boto3_client("s3")
        mock_s3_cli.restore_object.side_effect = [None]
        mock_post_entry_to_queue.side_effect = [Exception("mock insert failed error")]
        try:
            result = request_files.task(input_event, self.context)
        except Exception as err:
            mock_post_entry_to_queue.assert_called()
            return
        self.fail(f"failed post to status queue should throw exception.")

    @patch("request_files.shared_recovery.post_entry_to_queue")
    @patch("boto3.client")
    @patch("cumulus_logger.CumulusLogger.info")
    def test_task_file_not_in_glacier(
        self,
        mock_logger_info: MagicMock,
        mock_boto3_client: MagicMock,
        mock_post_entry_to_queue: MagicMock,
    ):
        """
        Test a file that is not in glacier.
        # todo: Expand test descriptions.
        """
        dest_bucket = uuid.uuid4().__str__()
        file1 = "MOD09GQ___006/2017/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.xyz"
        granule_id = "MOD09GQ.A0219114.N5aUCG.006.0656338553321.xyz"
        event = {
            "input": {
                "granules": [
                    {
                        "granuleId": granule_id,
                        "keys": [{"key": file1, "dest_bucket": dest_bucket}],
                    }
                ]
            },
            "config": {
                "glacier-bucket": "my-bucket",
                "asyncOperationId": uuid.uuid4().__str__(),
            },
        }
        mock_s3_cli = mock_boto3_client("s3")
        # todo: Verify the below with a real-world db. If not the same, fix request_files.object_exists
        mock_s3_cli.head_object.side_effect = [
            ClientError(
                {"Error": {"Code": "404", "Message": "Not Found"}}, "head_object"
            )
        ]
        result = request_files.task(event, self.context)

        # todo: Kill all of this,
        #  or at least use the actual bucket values for the individual files instead of copy/paste.
        expected_granules = {
            "granules": [
                {
                    "granuleId": granule_id,
                    "keys": [{"dest_bucket": dest_bucket, "key": file1}],
                    "recover_files": [
                        {
                            "success": True,
                            "filename": granule_id,
                            "key_path": file1,
                            "restore_destination": dest_bucket,
                            "status_id": OrcaStatus.FAILED.value,
                            "error_message": f"{file1} does not exist in S3 bucket",
                            "request_time": mock.ANY,
                            "last_update": mock.ANY,
                            "completion_time": mock.ANY,
                        }
                    ],
                }
            ],
            "asyncOperationId": event["config"]["asyncOperationId"],
        }
        self.assertEqual(expected_granules, result)
        mock_boto3_client.assert_called_with("s3")
        mock_s3_cli.head_object.assert_called_with(Bucket="my-bucket", Key=file1)

    @patch("request_files.shared_recovery.post_entry_to_queue")
    @patch("boto3.client")
    def test_task_no_retries_env_var(
        self, mock_boto3_client: MagicMock, mock_post_entry_to_queue: MagicMock
    ):
        """
        Test environment var RESTORE_REQUEST_RETRIES not set - use default.
        """
        del os.environ["RESTORE_REQUEST_RETRIES"]
        granule_id = "MOD09GQ.A0219114.N5aUCG.006.0656338553321"
        # todo: Reduce string copy/paste for test values here and elsewhere.
        event = {
            "input": {"granules": [{"granuleId": granule_id, "keys": [KEY1]}]},
            "config": {
                "glacier-bucket": "some_bucket",
                "asyncOperationId": uuid.uuid4().__str__(),
            },
        }

        mock_s3_cli = mock_boto3_client("s3")
        mock_s3_cli.restore_object.side_effect = [None]

        exp_granules = {
            "granules": [
                {
                    "granuleId": granule_id,
                    "keys": [{"key": FILE1, "dest_bucket": PROTECTED_BUCKET}],
                    "recover_files": [
                        {
                            "filename": os.path.basename(FILE1),
                            "key_path": FILE1,
                            "restore_destination": PROTECTED_BUCKET,
                            "success": True,
                            "status_id": 1,
                        },
                    ],
                }
            ],
            "asyncOperationId": event["config"]["asyncOperationId"],
        }
        result = request_files.task(event, self.context)
        os.environ[
            "RESTORE_REQUEST_RETRIES"
        ] = "2"  # todo: This test claims 'no_retries'

        # Check the values of the result less the times since those will never match
        result_value = result.copy()
        for granule in result_value["granules"]:
            for file in granule["recover_files"]:
                file.pop("request_time", None)
                file.pop("last_update", None)
                file.pop("completion_time", None)

        self.assertEqual(exp_granules, result_value)

        mock_boto3_client.assert_called_with("s3")
        mock_s3_cli.head_object.assert_called_with(Bucket="some_bucket", Key=FILE1)
        restore_req_exp = {"Days": 5, "GlacierJobParameters": {"Tier": "Standard"}}
        mock_s3_cli.restore_object.assert_called_with(
            Bucket="some_bucket", Key=FILE1, RestoreRequest=restore_req_exp
        )
        mock_post_entry_to_queue.assert_called()

    # todo: single_query is not called in code. Replace with higher-level checks.
    @patch("request_files.shared_recovery.post_entry_to_queue")
    @patch("boto3.client")
    @patch("cumulus_logger.CumulusLogger.info")
    def test_task_no_expire_days_env_var(
        self,
        mock_logger_info: MagicMock,
        mock_boto3_client: MagicMock,
        mock_post_entry_to_queue: MagicMock,
    ):
        """
        Test environment var RESTORE_EXPIRE_DAYS not set - use default.
        """
        del os.environ["RESTORE_EXPIRE_DAYS"]
        os.environ["RESTORE_RETRIEVAL_TYPE"] = "Expedited"
        granule_id = "MOD09GQ.A0219114.N5aUCG.006.0656338553321"
        event = {
            "config": {
                "glacier-bucket": "some_bucket",
                "asyncOperationId": uuid.uuid4().__str__(),
            },
            "input": {"granules": [{"granuleId": granule_id, "keys": [KEY1]}]},
        }

        mock_s3_cli = mock_boto3_client("s3")
        # mock_s3_cli.head_object = Mock()  # todo: Look into why this line was in so many tests without asserts.
        mock_s3_cli.restore_object.side_effect = [None]
        exp_granules = {
            "granules": [
                {
                    "granuleId": granule_id,
                    "keys": [{"key": FILE1, "dest_bucket": PROTECTED_BUCKET}],
                    "recover_files": [
                        {
                            "filename": os.path.basename(FILE1),
                            "key_path": FILE1,
                            "restore_destination": PROTECTED_BUCKET,
                            "success": True,
                            "status_id": 1,
                        },
                    ],
                }
            ],
            "asyncOperationId": event["config"]["asyncOperationId"],
        }

        result = request_files.task(event, self.context)

        # Check the values of the result less the times since those will never match
        result_value = result.copy()
        for granule in result_value["granules"]:
            for file in granule["recover_files"]:
                file.pop("request_time", None)
                file.pop("last_update", None)
                file.pop("completion_time", None)

        self.assertEqual(exp_granules, result_value)
        os.environ["RESTORE_EXPIRE_DAYS"] = "3"  # todo: Why is this set here?
        del os.environ["RESTORE_RETRIEVAL_TYPE"]
        mock_boto3_client.assert_called_with("s3")
        mock_s3_cli.head_object.assert_called_with(Bucket="some_bucket", Key=FILE1)
        restore_req_exp = {"Days": 5, "GlacierJobParameters": {"Tier": "Expedited"}}
        mock_s3_cli.restore_object.assert_called_with(
            Bucket="some_bucket", Key=FILE1, RestoreRequest=restore_req_exp
        )
        self.assertEqual(1, mock_post_entry_to_queue.call_count)

    @patch("request_files.shared_recovery.post_entry_to_queue")
    @patch("boto3.client")
    @patch("cumulus_logger.CumulusLogger.error")
    @patch("cumulus_logger.CumulusLogger.info")
    def test_task_client_error_one_file(
        self,
        mock_logger_info: MagicMock,
        mock_logger_error: MagicMock,
        mock_boto3_client: MagicMock,
        mock_post_entry_to_queue: MagicMock,
    ):
        """
        Test retries for restore error for one file.
        """
        event = {
            "config": {
                "glacier-bucket": "some_bucket",
                "asyncOperationId": uuid.uuid4().__str__(),
            },
            "input": {
                "granules": [
                    {
                        "granuleId": "MOD09GQ.A0219114.N5aUCG.006.0656338553321",
                        "keys": [KEY1],
                    }
                ]
            },
        }

        os.environ[
            "RESTORE_RETRY_SLEEP_SECS"
        ] = ".5"  # todo: This is not reset between tests
        mock_s3_cli = mock_boto3_client("s3")
        mock_s3_cli.restore_object.side_effect = [
            ClientError({"Error": {"Code": "NoSuchBucket"}}, "restore_object"),
            ClientError({"Error": {"Code": "NoSuchBucket"}}, "restore_object"),
            ClientError({"Error": {"Code": "NoSuchBucket"}}, "restore_object"),
        ]
        os.environ[
            "RESTORE_RETRIEVAL_TYPE"
        ] = "Standard"  # todo: This is not reset between tests

        exp_gran = {
            "granuleId": "MOD09GQ.A0219114.N5aUCG.006.0656338553321",
            "keys": [{"key": FILE1, "dest_bucket": PROTECTED_BUCKET}],
            "recover_files": [
                {
                    "key": FILE1,
                    "dest_bucket": PROTECTED_BUCKET,
                    "success": False,
                    "err_msg": "An error occurred (NoSuchBucket) when calling the restore_object operation: Unknown",
                }
            ],
        }
        exp_err = "One or more files failed to be requested from {bucket}.".format(
            bucket=event["config"]["glacier-bucket"]
        )
        try:
            request_files.task(event, self.context)
            self.fail("RestoreRequestError expected")
        except request_files.RestoreRequestError as err:
            self.assertEqual(exp_err, str(err))
        del os.environ["RESTORE_RETRY_SLEEP_SECS"]
        del os.environ["RESTORE_RETRIEVAL_TYPE"]
        mock_boto3_client.assert_called_with("s3")
        mock_s3_cli.head_object.assert_called_with(Bucket="some_bucket", Key=FILE1)
        restore_req_exp = {"Days": 5, "GlacierJobParameters": {"Tier": "Standard"}}
        mock_s3_cli.restore_object.assert_any_call(
            Bucket="some_bucket", Key=FILE1, RestoreRequest=restore_req_exp
        )

    @patch("request_files.shared_recovery.post_entry_to_queue")
    @patch("boto3.client")
    @patch("cumulus_logger.CumulusLogger.error")
    @patch("cumulus_logger.CumulusLogger.info")
    def test_task_client_error_3_times(
        self,
        mock_logger_info: MagicMock,
        mock_logger_error: MagicMock,
        mock_boto3_client: MagicMock,
        mock_post_entry_to_queue: MagicMock,
    ):
        """
        Test three files, two successful, one errors on all retries and fails.
        """
        keys = [KEY1, KEY3, KEY4]

        event = {
            "config": {
                "glacier-bucket": "some_bucket",
                "asyncOperationId": uuid.uuid4().__str__(),
            }
        }
        gran = {"granuleId": "MOD09GQ.A0219114.N5aUCG.006.0656338553321", "keys": keys}

        event["input"] = {"granules": [gran]}
        mock_s3_cli = mock_boto3_client("s3")
        mock_s3_cli.restore_object.side_effect = [
            None,
            ClientError({"Error": {"Code": "NoSuchBucket"}}, "restore_object"),
            None,
            ClientError({"Error": {"Code": "NoSuchBucket"}}, "restore_object"),
            ClientError({"Error": {"Code": "NoSuchKey"}}, "restore_object"),
        ]

        exp_gran = {
            "granuleId": gran["granuleId"],
            "keys": self.get_exp_keys_3_errs(),
            "recover_files": self.get_exp_files_3_errs(),
        }
        exp_err = "One or more files failed to be requested from {bucket}.".format(
            bucket=event["config"]["glacier-bucket"]
        )
        try:
            request_files.task(event, self.context)
            self.fail("RestoreRequestError expected")
        except request_files.RestoreRequestError as err:
            self.assertEqual(exp_err, str(err))

        mock_boto3_client.assert_called_with("s3")
        mock_s3_cli.head_object.assert_any_call(Bucket="some_bucket", Key=FILE1)
        mock_s3_cli.restore_object.assert_any_call(
            Bucket="some_bucket",
            Key=FILE1,
            RestoreRequest={"Days": 5, "GlacierJobParameters": {"Tier": "Standard"}},
        )
        mock_post_entry_to_queue.assert_called()  # 5 times # todo: No..?

    @staticmethod
    def get_exp_files_3_errs():
        """
        builds list of expected files for test case
        """
        return [
            {
                "key": FILE1,
                "dest_bucket": PROTECTED_BUCKET,
                "success": True,
                "err_msg": "",
            },
            {
                "key": FILE3,
                "dest_bucket": PUBLIC_BUCKET,
                "success": False,
                "err_msg": "An error occurred (NoSuchKey) when calling the restore_object "
                "operation: Unknown",
            },
            {
                "key": FILE4,
                "dest_bucket": PUBLIC_BUCKET,
                "success": True,
                "err_msg": "",
            },
        ]

    @staticmethod
    def get_exp_keys_3_errs():
        """
        builds list of expected files for test case
        """
        return [
            {"key": FILE1, "dest_bucket": PROTECTED_BUCKET},
            {"key": FILE3, "dest_bucket": PUBLIC_BUCKET},
            {"key": FILE4, "dest_bucket": PUBLIC_BUCKET},
        ]

    # todo: single_query is not called in code. Replace with higher-level checks.
    @patch("request_files.shared_recovery.post_entry_to_queue")
    @patch("boto3.client")
    @patch("cumulus_logger.CumulusLogger.error")
    @patch("cumulus_logger.CumulusLogger.info")
    def test_task_client_error_2_times(
        self,
        mock_logger_info: MagicMock,
        mock_logger_error: MagicMock,
        mock_boto3_client: MagicMock,
        mock_post_entry_to_queue: MagicMock,
    ):
        """
        Test two files, first successful, second has two errors, then success.
        """
        event = {
            "config": {
                "glacier-bucket": "some_bucket",
                "asyncOperationId": uuid.uuid4().__str__(),
            }
        }
        gran = {}
        granule_id = "MOD09GQ.A0219114.N5aUCG.006.0656338553321"
        gran["granuleId"] = granule_id
        keys = [KEY1, KEY2]
        gran["keys"] = keys
        event["input"] = {"granules": [gran]}
        mock_s3_cli = mock_boto3_client("sqs")

        mock_s3_cli.restore_object.side_effect = [
            None,
            ClientError({"Error": {"Code": "NoSuchBucket"}}, "restore_object"),
            ClientError({"Error": {"Code": "NoSuchBucket"}}, "restore_object"),
            None,
        ]

        exp_granules = {
            "granules": [
                {
                    "granuleId": granule_id,
                    "keys": [
                        {"key": FILE1, "dest_bucket": PROTECTED_BUCKET},
                        {"key": FILE2, "dest_bucket": PROTECTED_BUCKET},
                    ],
                    "recover_files": [
                        {
                            "filename": os.path.basename(FILE1),
                            "key_path": FILE1,
                            "restore_destination": PROTECTED_BUCKET,
                            "success": True,
                            "status_id": 1,
                        },
                        {
                            "error_message": "An error occurred (NoSuchBucket) when calling the restore_object operation: Unknown",
                            "filename": os.path.basename(FILE2),
                            "key_path": FILE2,
                            "restore_destination": PROTECTED_BUCKET,
                            "success": True,
                            "status_id": 1,
                        },
                    ],
                }
            ],
            "asyncOperationId": event["config"]["asyncOperationId"],
        }

        result = request_files.task(event, self.context)
        # Check the values of the result less the times since those will never match
        result_value = result.copy()
        for granule in result_value["granules"]:
            for file in granule["recover_files"]:
                file.pop("request_time", None)
                file.pop("last_update", None)
                file.pop("completion_time", None)

        self.assertEqual(exp_granules, result_value)

        mock_boto3_client.assert_has_calls([call("sqs")])
        mock_s3_cli.restore_object.assert_any_call(
            Bucket="some_bucket",
            Key=FILE1,
            RestoreRequest={"Days": 5, "GlacierJobParameters": {"Tier": "Standard"}},
        )
        mock_post_entry_to_queue.assert_called()  # 4 times # todo: No..?

    @patch("request_files.shared_recovery.post_entry_to_queue")
    @patch("boto3.client")
    @patch("cumulus_logger.CumulusLogger.info")
    def test_task_output_json_schema(
        self,
        mock_logger_info: MagicMock,
        mock_boto3_client: MagicMock,
        mock_post_entry_to_queue: MagicMock,
    ):
        """
        Test four files for one granule - successful. Check against output schema.
        """
        granule_id = "MOD09GQ.A0219114.N5aUCG.006.0656338553321"
        files = [KEY1, KEY2, KEY3, KEY4]
        input_event = {
            "input": {"granules": [{"granuleId": granule_id, "keys": files}]},
            "config": {
                "glacier-bucket": "my-dr-fake-glacier-bucket",
                "asyncOperationId": uuid.uuid4().__str__(),
            },
        }

        mock_s3_cli = mock_boto3_client("s3")
        mock_s3_cli.restore_object.side_effect = [None, None, None, None]

        result = request_files.task(input_event, self.context)

        mock_boto3_client.assert_has_calls([call("s3")])
        mock_s3_cli.head_object.assert_any_call(
            Bucket="my-dr-fake-glacier-bucket", Key=FILE1
        )
        mock_s3_cli.head_object.assert_any_call(
            Bucket="my-dr-fake-glacier-bucket", Key=FILE2
        )
        mock_s3_cli.head_object.assert_any_call(
            Bucket="my-dr-fake-glacier-bucket", Key=FILE3
        )
        mock_s3_cli.head_object.assert_any_call(
            Bucket="my-dr-fake-glacier-bucket", Key=FILE4
        )
        restore_req_exp = {"Days": 5, "GlacierJobParameters": {"Tier": "Standard"}}

        mock_s3_cli.restore_object.assert_any_call(
            Bucket="my-dr-fake-glacier-bucket",
            Key=FILE1,
            RestoreRequest=restore_req_exp,
        )
        mock_s3_cli.restore_object.assert_any_call(
            Bucket="my-dr-fake-glacier-bucket",
            Key=FILE2,
            RestoreRequest=restore_req_exp,
        )
        mock_s3_cli.restore_object.assert_any_call(
            Bucket="my-dr-fake-glacier-bucket",
            Key=FILE3,
            RestoreRequest=restore_req_exp,
        )
        mock_s3_cli.restore_object.assert_called_with(
            Bucket="my-dr-fake-glacier-bucket",
            Key=FILE4,
            RestoreRequest=restore_req_exp,
        )

        exp_gran = {
            "granuleId": granule_id,
            "keys": self.get_expected_keys(),
            "recover_files": self.get_expected_files(),
        }
        exp_granules = {
            "granules": [exp_gran],
            "asyncOperationId": input_event["config"]["asyncOperationId"],
        }

        # Validate the output is correct
        with open("schemas/output.json", "r") as raw_schema:
            schema = json.loads(raw_schema.read())

        validate = fastjsonschema.compile(schema)
        validate(result)

        # Check the values of the result less the times since those will never match
        result_value = result.copy()
        for granule in result_value["granules"]:
            for file in granule["recover_files"]:
                file.pop("request_time", None)
                file.pop("last_update", None)
                file.pop("completion_time", None)

        self.assertEqual(exp_granules, result_value)
        mock_post_entry_to_queue.assert_called_once()


if __name__ == "__main__":
    unittest.main(argv=["start"])
