import os
import random
import unittest
import uuid
from http import HTTPStatus
from unittest.mock import MagicMock, Mock, patch

from src.adapters.api import aws
from src.entities.orphan import OrphanRecord, OrphanRecordFilter, OrphanRecordPage


class TestAWS(unittest.TestCase):
    # tests for check_env_variable copied from https://github.com/nasa/cumulus-orca/pull/260/
    @patch.dict(
        os.environ,
        {
            "ENV_VAR": uuid.uuid4().__str__(),
        },
        clear=True,
    )
    def test_check_env_variable_happy_path(self):
        """
        Happy path for check_env_variable().
        """

        return_value = aws.check_env_variable("ENV_VAR")
        self.assertEqual(os.environ["ENV_VAR"], return_value)

    @patch.dict(
        os.environ,
        {
            "EMPTY_ENV_VAR": "",
        },
        clear=True,
    )
    @patch("src.adapters.api.aws.LOGGER")
    def test_check_env_variable_empty_and_no_key(self, mock_logger: MagicMock):
        """
        Tests that check_env_variable() raises a KeyError if key ENV_VAR is missing or empty.
        """

        with self.assertRaises(KeyError) as err:
            aws.check_env_variable("EMPTY_ENV_VAR")
        error_message = "Empty value for EMPTY_ENV_VAR"
        self.assertEqual(err.exception.args[0], error_message)
        with self.assertRaises(KeyError):
            aws.check_env_variable("MISSING_ENV_VAR")
        mock_logger.error.assert_called_with(
            "MISSING_ENV_VAR environment value not found."
        )

    @patch("src.adapters.api.aws.LOGGER.error")
    def test_create_http_error_dict_happy_path(self, mock_error: MagicMock):
        error_type = uuid.uuid4().__str__()  # nosec
        http_status_code = random.randint(0, 9999)  # nosec
        request_id = uuid.uuid4().__str__()  # nosec
        message = uuid.uuid4().__str__()  # nosec

        result = aws.create_http_error_dict(
            error_type, http_status_code, request_id, message
        )

        self.assertEqual(
            {
                "errorType": error_type,
                "httpStatus": http_status_code,
                "requestId": request_id,
                "message": message,
            },
            result,
        )

        mock_error.assert_called_once_with(message)

    # noinspection PyPep8Naming
    @patch("src.adapters.api.aws.StorageAdapterPostgres")
    @patch("src.adapters.api.aws.get_orphans_page.task")
    @patch("src.adapters.api.aws.create_user_uri")
    @patch("src.adapters.api.aws.get_configuration")
    @patch("src.adapters.api.aws.check_env_variable")
    def test_handler_happy_path(
        self,
        mock_check_env_variable: MagicMock,
        mock_get_configuration: MagicMock,
        mock_create_user_uri: MagicMock,
        mock_task: MagicMock,
        mock_storage_adapter_postgres: MagicMock,
    ):
        """
        Basic path with all information present.
        Should call use_case.
        """
        page_index = random.randint(0, 999)  # nosec
        job_id = random.randint(0, 999)  # nosec

        key_path0 = uuid.uuid4().__str__()
        etag0 = uuid.uuid4().__str__()
        last_update0 = random.randint(0, 99999)  # nosec
        size_in_bytes0 = random.randint(0, 999)  # nosec
        storage_class0 = "GLACIER"

        key_path1 = uuid.uuid4().__str__()
        etag1 = uuid.uuid4().__str__()
        last_update1 = random.randint(0, 99999)  # nosec
        size_in_bytes1 = random.randint(0, 999)  # nosec
        storage_class1 = "DEEP_ARCHIVE"

        another_page = False

        event = {"pageIndex": page_index, "jobId": job_id}
        context = Mock()

        mock_task.return_value = OrphanRecordPage(
            orphans=[
                OrphanRecord(
                    key_path=key_path0,
                    etag=etag0,
                    last_update=last_update0,
                    size_in_bytes=size_in_bytes0,
                    storage_class=storage_class0,
                ),
                OrphanRecord(
                    key_path=key_path1,
                    etag=etag1,
                    last_update=last_update1,
                    size_in_bytes=size_in_bytes1,
                    storage_class=storage_class1,
                ),
            ],
            another_page=another_page,
        )

        result = aws.handler(event, context)

        mock_check_env_variable.assert_called_once_with(
            aws.OS_ENVIRON_DB_CONNECT_INFO_SECRET_ARN_KEY
        )
        mock_get_configuration.assert_called_once_with(
            mock_check_env_variable.return_value, aws.LOGGER
        )
        mock_create_user_uri.assert_called_once_with(
            mock_get_configuration.return_value, aws.LOGGER
        )
        mock_storage_adapter_postgres.assert_called_once_with(
            mock_create_user_uri.return_value
        )
        mock_task.assert_called_once_with(
            OrphanRecordFilter(
                job_id=job_id, page_index=page_index, page_size=aws.PAGE_SIZE
            ),
            mock_storage_adapter_postgres.return_value,
            aws.LOGGER,
        )

        self.assertEqual(
            {
                aws.OUTPUT_JOB_ID_KEY: job_id,
                aws.OUTPUT_ORPHANS_KEY: [
                    {
                        aws.ORPHANS_KEY_PATH_KEY: key_path0,
                        aws.ORPHANS_S3_ETAG_KEY: etag0,
                        aws.ORPHANS_S3_LAST_UPDATE_KEY: last_update0,
                        aws.ORPHANS_S3_SIZE_IN_BYTES_KEY: size_in_bytes0,
                        aws.ORPHANS_STORAGE_CLASS_KEY: storage_class0,
                    },
                    {
                        aws.ORPHANS_KEY_PATH_KEY: key_path1,
                        aws.ORPHANS_S3_ETAG_KEY: etag1,
                        aws.ORPHANS_S3_LAST_UPDATE_KEY: last_update1,
                        aws.ORPHANS_S3_SIZE_IN_BYTES_KEY: size_in_bytes1,
                        aws.ORPHANS_STORAGE_CLASS_KEY: storage_class1,
                    },
                ],
                aws.OUTPUT_ANOTHER_PAGE_KEY: another_page,
            },
            result,
        )

    # noinspection PyPep8Naming
    @patch("src.adapters.api.aws.create_http_error_dict")
    @patch("src.adapters.api.aws.StorageAdapterPostgres")
    @patch("src.adapters.api.aws.get_orphans_page.task")
    def test_handler_missing_page_index_returns_error(
        self,
        mock_task: MagicMock,
        mock_storage_adapter_postgres: MagicMock,
        mock_create_http_error_dict: MagicMock,
    ):
        """
        page_index should be required by schema.
        """
        job_id = random.randint(0, 999)  # nosec

        event = {"jobId": job_id}
        context = Mock()

        result = aws.handler(event, context)

        mock_task.assert_not_called()

        mock_create_http_error_dict.assert_called_once_with(
            "BadRequest",
            HTTPStatus.BAD_REQUEST,
            context.aws_request_id,
            f"data must contain ['{aws.INPUT_JOB_ID_KEY}', "
            f"'{aws.INPUT_PAGE_INDEX_KEY}'] properties",
        )
        self.assertEqual(mock_create_http_error_dict.return_value, result)

    # noinspection PyPep8Naming
    @patch("src.adapters.api.aws.create_http_error_dict")
    @patch("src.adapters.api.aws.StorageAdapterPostgres")
    @patch("src.adapters.api.aws.get_orphans_page.task")
    @patch("src.adapters.api.aws.create_user_uri")
    @patch("src.adapters.api.aws.get_configuration")
    @patch("src.adapters.api.aws.check_env_variable")
    def test_handler_bad_output_raises_error(
        self,
        mock_check_env_variable: MagicMock,
        mock_get_configuration: MagicMock,
        mock_create_user_uri: MagicMock,
        mock_task: MagicMock,
        mock_storage_adapter_postgres: MagicMock,
        mock_create_http_error_dict: MagicMock,
    ):
        """
        Basic path with all information present.
        Should call use_case.
        """
        page_index = random.randint(0, 999)  # nosec
        job_id = random.randint(0, 999)  # nosec

        key_path0 = uuid.uuid4().__str__()
        etag0 = uuid.uuid4().__str__()
        last_update0 = random.randint(0, 99999).__str__()  # nosec
        size_in_bytes0 = random.randint(0, 999)  # nosec
        storage_class0 = "GLACIER"

        another_page = False

        event = {"pageIndex": page_index, "jobId": job_id}
        context = Mock()

        mock_task.return_value = OrphanRecordPage(
            orphans=[
                OrphanRecord(
                    key_path=key_path0,
                    etag=etag0,
                    last_update=last_update0,
                    size_in_bytes=size_in_bytes0,
                    storage_class=storage_class0,
                ),
            ],
            another_page=another_page,
        )

        result = aws.handler(event, context)

        mock_check_env_variable.assert_called_once_with(
            aws.OS_ENVIRON_DB_CONNECT_INFO_SECRET_ARN_KEY
        )
        mock_get_configuration.assert_called_once_with(
            mock_check_env_variable.return_value, aws.LOGGER
        )
        mock_create_user_uri.assert_called_once_with(
            mock_get_configuration.return_value, aws.LOGGER
        )
        mock_storage_adapter_postgres.assert_called_once_with(
            mock_create_user_uri.return_value
        )
        mock_task.assert_called_once_with(
            OrphanRecordFilter(
                job_id=job_id, page_index=page_index, page_size=aws.PAGE_SIZE
            ),
            mock_storage_adapter_postgres.return_value,
            aws.LOGGER,
        )

        mock_create_http_error_dict.assert_called_once_with(
            "InternalServerError",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            context.aws_request_id,
            f"data.{aws.OUTPUT_ORPHANS_KEY}[0]."
            f"{aws.ORPHANS_S3_LAST_UPDATE_KEY} must be integer",
        )
        self.assertEqual(mock_create_http_error_dict.return_value, result)
