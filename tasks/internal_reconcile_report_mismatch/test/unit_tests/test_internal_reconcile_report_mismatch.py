"""
Name: test_internal_reconcile_report_mismatch.py
Description:  Unit tests for internal_reconcile_report_mismatch.py.
"""
import os
import random
import unittest
import uuid
from http import HTTPStatus
from unittest.mock import MagicMock, Mock, patch

import internal_reconcile_report_mismatch


class TestInternalReconcileReportMismatch(
    unittest.TestCase
):  # pylint: disable-msg=too-many-instance-attributes
    """
    TestInternalReconcileReportMismatch.
    """

    @patch("internal_reconcile_report_mismatch.task")
    @patch("orca_shared.database.shared_db.get_configuration")
    @patch("internal_reconcile_report_mismatch.check_env_variable")
    def test_handler_happy_path(
        self,
        mock_check_env_variable: MagicMock,
        mock_get_configuration: MagicMock,
        mock_task: MagicMock,
    ):
        """
        Basic path with all information present.
        Should call task.
        """
        page_index = random.randint(0, 999)  # nosec
        job_id = random.randint(0, 999)  # nosec

        event = {"pageIndex": page_index, "jobId": job_id}
        context = Mock()
        mock_task.return_value = {
            internal_reconcile_report_mismatch.OUTPUT_JOB_ID_KEY: job_id,
            internal_reconcile_report_mismatch.OUTPUT_ANOTHER_PAGE_KEY: False,
            internal_reconcile_report_mismatch.OUTPUT_MISMATCHES_KEY: [
                {
                    internal_reconcile_report_mismatch.MISMATCHES_COLLECTION_ID_KEY:
                        uuid.uuid4().__str__(),
                    internal_reconcile_report_mismatch.MISMATCHES_GRANULE_ID_KEY:
                        uuid.uuid4().__str__(),
                    internal_reconcile_report_mismatch.MISMATCHES_FILENAME_KEY:
                        uuid.uuid4().__str__(),
                    internal_reconcile_report_mismatch.MISMATCHES_KEY_PATH_KEY:
                        uuid.uuid4().__str__(),
                    internal_reconcile_report_mismatch.MISMATCHES_CUMULUS_ARCHIVE_LOCATION_KEY:
                        uuid.uuid4().__str__(),
                    internal_reconcile_report_mismatch.MISMATCHES_ORCA_ETAG_KEY:
                        uuid.uuid4().__str__(),
                    internal_reconcile_report_mismatch.MISMATCHES_S3_ETAG_KEY:
                        uuid.uuid4().__str__(),
                    internal_reconcile_report_mismatch.MISMATCHES_ORCA_LAST_UPDATE_KEY:
                        random.randint(0, 999),  # nosec
                    internal_reconcile_report_mismatch.MISMATCHES_S3_LAST_UPDATE_KEY:
                        random.randint(0, 999),  # nosec
                    internal_reconcile_report_mismatch.MISMATCHES_ORCA_SIZE_IN_BYTES_KEY:
                        random.randint(0, 999),  # nosec
                    internal_reconcile_report_mismatch.MISMATCHES_S3_SIZE_IN_BYTES_KEY:
                        random.randint(0, 999),  # nosec
                    internal_reconcile_report_mismatch.MISMATCHES_ORCA_STORAGE_CLASS_KEY:
                        uuid.uuid4().__str__(),
                    internal_reconcile_report_mismatch.MISMATCHES_S3_STORAGE_CLASS_KEY:
                        uuid.uuid4().__str__(),
                    internal_reconcile_report_mismatch.MISMATCHES_DISCREPANCY_TYPE_KEY:
                        uuid.uuid4().__str__(),
                    internal_reconcile_report_mismatch.MISMATCHES_COMMENT_KEY:
                        None
                }
            ],
        }

        result = internal_reconcile_report_mismatch.handler(event, context)

        mock_check_env_variable.assert_called_once_with(
            internal_reconcile_report_mismatch.OS_ENVIRON_DB_CONNECT_INFO_SECRET_ARN_KEY
        )
        mock_get_configuration.assert_called_once_with(
            mock_check_env_variable.return_value
        )
        mock_task.assert_called_once_with(
            job_id,
            page_index,
            mock_get_configuration.return_value,
        )
        self.assertEqual(mock_task.return_value, result)

    # noinspection PyPep8Naming
    @patch("internal_reconcile_report_mismatch.create_http_error_dict")
    @patch("orca_shared.database.shared_db.get_configuration")
    def test_handler_missing_page_index_returns_error(
        self,
        mock_get_configuration: MagicMock,
        mock_create_http_error_dict: MagicMock,
    ):
        """
        page_index should be required by schema.
        """
        job_id = random.randint(0, 999)  # nosec

        event = {
            "pageIndex": None,
            "jobId": job_id,
        }
        context = Mock()
        result = internal_reconcile_report_mismatch.handler(event, context)

        mock_create_http_error_dict.assert_called_once_with(
            "BadRequest",
            HTTPStatus.BAD_REQUEST,
            context.aws_request_id,
            "data.pageIndex must be integer",
        )
        self.assertEqual(mock_create_http_error_dict.return_value, result)

    # noinspection PyPep8Naming
    @patch("internal_reconcile_report_mismatch.create_http_error_dict")
    @patch("internal_reconcile_report_mismatch.task")
    @patch("orca_shared.database.shared_db.get_configuration")
    @patch("internal_reconcile_report_mismatch.check_env_variable")
    def test_handler_bad_output_raises_error(
        self,
        mock_check_env_variable: MagicMock,
        mock_get_configuration: MagicMock,
        mock_task: MagicMock,
        mock_create_http_error_dict: MagicMock,
    ):
        """
        Output validity should be checked, and return an error code if invalid.
        """
        event = {
            "jobId": random.randint(0, 999),  # nosec
            "pageIndex": random.randint(0, 999),  # nosec
        }
        context = Mock()
        mock_task.return_value = {
            internal_reconcile_report_mismatch.OUTPUT_JOB_ID_KEY: random.randint(  # nosec
                0, 999
            ),
            internal_reconcile_report_mismatch.OUTPUT_ANOTHER_PAGE_KEY: False,
            internal_reconcile_report_mismatch.OUTPUT_MISMATCHES_KEY: [
                {
                    internal_reconcile_report_mismatch.MISMATCHES_COLLECTION_ID_KEY:
                        uuid.uuid4().__str__(),
                    internal_reconcile_report_mismatch.MISMATCHES_GRANULE_ID_KEY:
                        uuid.uuid4().__str__(),
                    internal_reconcile_report_mismatch.MISMATCHES_FILENAME_KEY:
                        uuid.uuid4().__str__(),
                    internal_reconcile_report_mismatch.MISMATCHES_KEY_PATH_KEY:
                        uuid.uuid4().__str__(),
                    internal_reconcile_report_mismatch.MISMATCHES_CUMULUS_ARCHIVE_LOCATION_KEY:
                        uuid.uuid4().__str__(),
                    internal_reconcile_report_mismatch.MISMATCHES_ORCA_ETAG_KEY:
                        uuid.uuid4().__str__(),
                    internal_reconcile_report_mismatch.MISMATCHES_S3_ETAG_KEY:
                        uuid.uuid4().__str__(),
                    internal_reconcile_report_mismatch.MISMATCHES_ORCA_LAST_UPDATE_KEY:
                        random.randint(0, 999).__str__(),  # nosec
                    internal_reconcile_report_mismatch.MISMATCHES_S3_LAST_UPDATE_KEY:
                        random.randint(0, 999),  # nosec
                    internal_reconcile_report_mismatch.MISMATCHES_ORCA_SIZE_IN_BYTES_KEY:
                        random.randint(0, 999),  # nosec
                    internal_reconcile_report_mismatch.MISMATCHES_S3_SIZE_IN_BYTES_KEY:
                        random.randint(0, 999),  # nosec
                    internal_reconcile_report_mismatch.MISMATCHES_ORCA_STORAGE_CLASS_KEY:
                        uuid.uuid4().__str__(),
                    internal_reconcile_report_mismatch.MISMATCHES_S3_STORAGE_CLASS_KEY:
                        uuid.uuid4().__str__(),
                    internal_reconcile_report_mismatch.MISMATCHES_DISCREPANCY_TYPE_KEY:
                        uuid.uuid4().__str__(),
                    internal_reconcile_report_mismatch.MISMATCHES_COMMENT_KEY:
                        uuid.uuid4().__str__()
                }
            ],
        }

        result = internal_reconcile_report_mismatch.handler(event, context)
        mock_create_http_error_dict.assert_called_once_with(
            "InternalServerError",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            context.aws_request_id,
            f"data.{internal_reconcile_report_mismatch.OUTPUT_MISMATCHES_KEY}[0]."
            f"{internal_reconcile_report_mismatch.MISMATCHES_ORCA_LAST_UPDATE_KEY} "
            "must be integer",
        )
        self.assertEqual(mock_create_http_error_dict.return_value, result)

    @patch("internal_reconcile_report_mismatch.query_db")
    @patch("orca_shared.database.shared_db.get_user_connection")
    def test_task_happy_path(
        self, mock_get_user_connection: MagicMock, mock_query_db: MagicMock
    ):
        """
        Task should call query_db, and send granules back.
        """
        job_id = random.randint(0, 999)  # nosec
        page_index = Mock()
        db_connect_info = Mock()

        mismatches = []
        for i in range(internal_reconcile_report_mismatch.PAGE_SIZE):
            mismatches.append(Mock)
        mock_query_db.return_value = mismatches

        result = internal_reconcile_report_mismatch.task(
            job_id,
            page_index,
            db_connect_info,
        )

        mock_get_user_connection.assert_called_once_with(db_connect_info)
        mock_query_db.assert_called_once_with(
            mock_get_user_connection.return_value,
            job_id,
            page_index,
        )
        self.assertEqual(
            {
                internal_reconcile_report_mismatch.OUTPUT_JOB_ID_KEY: job_id,
                internal_reconcile_report_mismatch.OUTPUT_ANOTHER_PAGE_KEY: False,
                internal_reconcile_report_mismatch.OUTPUT_MISMATCHES_KEY: mismatches,
            },
            result,
        )

    @patch("internal_reconcile_report_mismatch.query_db")
    @patch("orca_shared.database.shared_db.get_user_connection")
    def test_task_another_page(
        self, mock_get_user_connection: MagicMock, mock_query_db: MagicMock
    ):
        """
        Task should call query_db, and send granules back.
        If there are more granules than PAGE_SIZE, limit them and set "anotherPage" to True
        """
        job_id = random.randint(0, 999)  # nosec
        page_index = Mock()
        db_connect_info = Mock()

        mismatches = []
        for i in range(internal_reconcile_report_mismatch.PAGE_SIZE + 1):
            mismatches.append(Mock)
        mock_query_db.return_value = mismatches

        result = internal_reconcile_report_mismatch.task(
            job_id,
            page_index,
            db_connect_info,
        )

        mock_get_user_connection.assert_called_once_with(db_connect_info)
        mock_query_db.assert_called_once_with(
            mock_get_user_connection.return_value,
            job_id,
            page_index,
        )
        self.assertEqual(
            {
                internal_reconcile_report_mismatch.OUTPUT_JOB_ID_KEY: job_id,
                internal_reconcile_report_mismatch.OUTPUT_ANOTHER_PAGE_KEY: True,
                internal_reconcile_report_mismatch.OUTPUT_MISMATCHES_KEY: mismatches[
                    0: internal_reconcile_report_mismatch.PAGE_SIZE
                ],
            },
            result,
        )

    @patch("internal_reconcile_report_mismatch.get_mismatches_sql")
    def test_query_db_happy_path(self, mock_get_mismatches_sql: MagicMock):
        """
        Should query the db, then format the returned data.
        """
        job_id = random.randint(0, 999)  # nosec
        page_index = Mock()

        collection_id = uuid.uuid4().__str__()
        granule_id = uuid.uuid4().__str__()
        filename = uuid.uuid4().__str__()
        key_path = uuid.uuid4().__str__()
        cumulus_archive_location = uuid.uuid4().__str__()
        orca_etag = uuid.uuid4().__str__()
        s3_etag = uuid.uuid4().__str__()
        orca_last_update = random.randint(0, 999999)  # nosec
        s3_last_update = random.randint(0, 999999)  # nosec
        orca_size_in_bytes = random.randint(0, 999)  # nosec
        s3_size_in_bytes = random.randint(0, 999)  # nosec
        orca_storage_class = uuid.uuid4().__str__()
        s3_storage_class = uuid.uuid4().__str__()
        discrepancy_type = uuid.uuid4().__str__()
        comment = uuid.uuid4().__str__()

        returned_row0 = {
            "collection_id": collection_id,
            "granule_id": granule_id,
            "filename": filename,
            "key_path": key_path,
            "cumulus_archive_location": cumulus_archive_location,
            "orca_etag": orca_etag,
            "s3_etag": s3_etag,
            "orca_last_update": orca_last_update,
            "s3_last_update": s3_last_update,
            "orca_size_in_bytes": orca_size_in_bytes,
            "s3_size_in_bytes": s3_size_in_bytes,
            "orca_storage_class": orca_storage_class,
            "s3_storage_class": s3_storage_class,
            "discrepancy_type": discrepancy_type,
            "comment": comment
        }
        mock_execute_result = Mock()
        mock_execute_result.mappings = Mock(return_value=[returned_row0])
        mock_execute = Mock()
        mock_execute.return_value = mock_execute_result
        mock_connection = Mock()
        mock_connection.execute = mock_execute
        mock_exit = Mock(return_value=False)
        mock_enter = Mock()
        mock_enter.__enter__ = Mock(return_value=mock_connection)
        mock_enter.__exit__ = mock_exit
        mock_engine = Mock()
        mock_engine.begin = Mock(return_value=mock_enter)

        result = internal_reconcile_report_mismatch.query_db(
            mock_engine,
            job_id,
            page_index,
        )

        mock_enter.__enter__.assert_called_once_with()
        mock_execute.assert_called_once_with(
            mock_get_mismatches_sql.return_value,
            [
                {
                    "job_id": job_id,
                    "page_index": page_index,
                    "page_size": internal_reconcile_report_mismatch.PAGE_SIZE,
                }
            ],
        )
        mock_execute_result.mappings.assert_called_once_with()
        mock_exit.assert_called_once_with(None, None, None)
        mock_get_mismatches_sql.assert_called_once_with()
        self.assertEqual(
            [
                {
                    internal_reconcile_report_mismatch.MISMATCHES_COLLECTION_ID_KEY:
                        collection_id,
                    internal_reconcile_report_mismatch.MISMATCHES_GRANULE_ID_KEY:
                        granule_id,
                    internal_reconcile_report_mismatch.MISMATCHES_FILENAME_KEY:
                        filename,
                    internal_reconcile_report_mismatch.MISMATCHES_KEY_PATH_KEY:
                        key_path,
                    internal_reconcile_report_mismatch.MISMATCHES_CUMULUS_ARCHIVE_LOCATION_KEY:
                        cumulus_archive_location,
                    internal_reconcile_report_mismatch.MISMATCHES_ORCA_ETAG_KEY:
                        orca_etag,
                    internal_reconcile_report_mismatch.MISMATCHES_S3_ETAG_KEY:
                        s3_etag,
                    internal_reconcile_report_mismatch.MISMATCHES_ORCA_LAST_UPDATE_KEY:
                        orca_last_update,
                    internal_reconcile_report_mismatch.MISMATCHES_S3_LAST_UPDATE_KEY:
                        s3_last_update,
                    internal_reconcile_report_mismatch.MISMATCHES_ORCA_SIZE_IN_BYTES_KEY:
                        orca_size_in_bytes,
                    internal_reconcile_report_mismatch.MISMATCHES_S3_SIZE_IN_BYTES_KEY:
                        s3_size_in_bytes,
                    internal_reconcile_report_mismatch.MISMATCHES_ORCA_STORAGE_CLASS_KEY:
                        orca_storage_class,
                    internal_reconcile_report_mismatch.MISMATCHES_S3_STORAGE_CLASS_KEY:
                        s3_storage_class,
                    internal_reconcile_report_mismatch.MISMATCHES_DISCREPANCY_TYPE_KEY:
                        discrepancy_type,
                    internal_reconcile_report_mismatch.MISMATCHES_COMMENT_KEY:
                        comment
                }
            ],
            result,
        )

    @patch("internal_reconcile_report_mismatch.get_mismatches_sql")
    def test_query_db_no_rows_happy_path(self, mock_get_mismatches_sql: MagicMock):
        """
        Should query the db, then return an empty array.
        """
        job_id = random.randint(0, 999)  # nosec
        page_index = Mock()

        mock_execute_result = Mock()
        mock_execute_result.mappings = Mock(return_value=[])
        mock_execute = Mock()
        mock_execute.return_value = mock_execute_result
        mock_connection = Mock()
        mock_connection.execute = mock_execute
        mock_exit = Mock(return_value=False)
        mock_enter = Mock()
        mock_enter.__enter__ = Mock(return_value=mock_connection)
        mock_enter.__exit__ = mock_exit
        mock_engine = Mock()
        mock_engine.begin = Mock(return_value=mock_enter)

        result = internal_reconcile_report_mismatch.query_db(
            mock_engine,
            job_id,
            page_index,
        )

        mock_enter.__enter__.assert_called_once_with()
        mock_execute.assert_called_once_with(
            mock_get_mismatches_sql.return_value,
            [
                {
                    "job_id": job_id,
                    "page_index": page_index,
                    "page_size": internal_reconcile_report_mismatch.PAGE_SIZE,
                }
            ],
        )
        mock_execute_result.mappings.assert_called_once_with()
        mock_exit.assert_called_once_with(None, None, None)
        mock_get_mismatches_sql.assert_called_once_with()
        self.assertEqual(
            [],
            result,
        )

    @patch("internal_reconcile_report_mismatch.LOGGER.error")
    def test_create_http_error_dict_happy_path(
            self,
            mock_error: MagicMock
    ):
        error_type = uuid.uuid4().__str__()
        http_status_code = random.randint(0, 9999)  # nosec
        request_id = uuid.uuid4().__str__()
        message = uuid.uuid4().__str__()

        result = internal_reconcile_report_mismatch.create_http_error_dict(
            error_type, http_status_code, request_id, message)

        self.assertEqual({
            "errorType": error_type,
            "httpStatus": http_status_code,
            "requestId": request_id,
            "message": message,
        }, result)

        mock_error.assert_called_once_with(message)

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

        return_value = internal_reconcile_report_mismatch.check_env_variable("ENV_VAR")
        self.assertEqual(os.environ["ENV_VAR"], return_value)

    @patch.dict(
        os.environ,
        {
            "EMPTY_ENV_VAR": "",
        },
        clear=True,
    )
    @patch("internal_reconcile_report_mismatch.LOGGER")
    def test_check_env_variable_empty_and_no_key(self, mock_logger: MagicMock):

        """
        Tests that check_env_variable() raises a KeyError if key ENV_VAR is missing or empty.
        """

        with self.assertRaises(KeyError) as err:
            internal_reconcile_report_mismatch.check_env_variable("EMPTY_ENV_VAR")
        error_message = "Empty value for EMPTY_ENV_VAR"
        self.assertEqual(err.exception.args[0], error_message)
        with self.assertRaises(KeyError):
            internal_reconcile_report_mismatch.check_env_variable("MISSING_ENV_VAR")
        mock_logger.error.assert_called_with(
            "MISSING_ENV_VAR environment value not found."
        )
