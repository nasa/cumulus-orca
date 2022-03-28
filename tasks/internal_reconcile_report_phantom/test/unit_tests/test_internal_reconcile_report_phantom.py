"""
Name: test_internal_reconcile_report_phantom.py
Description:  Unit tests for internal_reconcile_report_phantom.py.
"""
import random
import unittest
import uuid
from http import HTTPStatus
from unittest.mock import MagicMock, Mock, patch

import internal_reconcile_report_phantom


class TestInternalReconcileReportPhantom(
    unittest.TestCase
):  # pylint: disable-msg=too-many-instance-attributes
    # noinspection PyPep8Naming
    @patch("internal_reconcile_report_phantom.task")
    @patch("orca_shared.database.shared_db.get_configuration")
    @patch("cumulus_logger.CumulusLogger.setMetadata")
    def test_handler_happy_path(
        self,
        mock_setMetadata: MagicMock,
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
            internal_reconcile_report_phantom.OUTPUT_JOB_ID_KEY: job_id,
            internal_reconcile_report_phantom.OUTPUT_ANOTHER_PAGE_KEY: False,
            internal_reconcile_report_phantom.OUTPUT_PHANTOMS_KEY: [
                {
                    internal_reconcile_report_phantom.PHANTOMS_COLLECTION_ID_KEY: uuid.uuid4().__str__(),
                    internal_reconcile_report_phantom.PHANTOMS_GRANULE_ID_KEY: uuid.uuid4().__str__(),
                    internal_reconcile_report_phantom.PHANTOMS_FILENAME_KEY: uuid.uuid4().__str__(),
                    internal_reconcile_report_phantom.PHANTOMS_KEY_PATH_KEY: uuid.uuid4().__str__(),
                    internal_reconcile_report_phantom.PHANTOMS_ORCA_ETAG_KEY: uuid.uuid4().__str__(),
                    internal_reconcile_report_phantom.PHANTOMS_ORCA_LAST_UPDATE_KEY: random.randint(0, 999),  # nosec
                    internal_reconcile_report_phantom.PHANTOMS_ORCA_SIZE_KEY: random.randint(0, 999),  # nosec
                }
            ],
        }

        result = internal_reconcile_report_phantom.handler(event, context)

        mock_setMetadata.assert_called_once_with(event, context)
        mock_task.assert_called_once_with(
            job_id,
            page_index,
            mock_get_configuration.return_value,
        )
        self.assertEqual(mock_task.return_value, result)

    # noinspection PyPep8Naming
    @patch("internal_reconcile_report_phantom.create_http_error_dict")
    @patch("orca_shared.database.shared_db.get_configuration")
    @patch("cumulus_logger.CumulusLogger.setMetadata")
    def test_handler_missing_page_index_returns_error(
        self,
        mock_setMetadata: MagicMock,
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
        result = internal_reconcile_report_phantom.handler(event, context)

        mock_setMetadata.assert_called_once_with(event, context)
        mock_create_http_error_dict.assert_called_once_with(
            "BadRequest",
            HTTPStatus.BAD_REQUEST,
            context.aws_request_id,
            "data.pageIndex must be integer",
        )
        self.assertEqual(mock_create_http_error_dict.return_value, result)

    # noinspection PyPep8Naming
    @patch("internal_reconcile_report_phantom.create_http_error_dict")
    @patch("internal_reconcile_report_phantom.task")
    @patch("orca_shared.database.shared_db.get_configuration")
    @patch("cumulus_logger.CumulusLogger.setMetadata")
    def test_handler_bad_output_raises_error(
        self,
        mock_setMetadata: MagicMock,
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
            internal_reconcile_report_phantom.OUTPUT_JOB_ID_KEY: random.randint(0, 999),  # nosec
            internal_reconcile_report_phantom.OUTPUT_ANOTHER_PAGE_KEY: False,
            internal_reconcile_report_phantom.OUTPUT_PHANTOMS_KEY: [
                {
                    internal_reconcile_report_phantom.PHANTOMS_COLLECTION_ID_KEY: uuid.uuid4().__str__(),
                    internal_reconcile_report_phantom.PHANTOMS_GRANULE_ID_KEY: uuid.uuid4().__str__(),
                    internal_reconcile_report_phantom.PHANTOMS_FILENAME_KEY: uuid.uuid4().__str__(),
                    internal_reconcile_report_phantom.PHANTOMS_KEY_PATH_KEY: uuid.uuid4().__str__(),
                    internal_reconcile_report_phantom.PHANTOMS_ORCA_ETAG_KEY: uuid.uuid4().__str__(),
                    internal_reconcile_report_phantom.PHANTOMS_ORCA_LAST_UPDATE_KEY: random.randint(0, 999).__str__(),  # nosec
                    internal_reconcile_report_phantom.PHANTOMS_ORCA_SIZE_KEY: random.randint(0, 999),  # nosec
                }
            ],
        }

        result = internal_reconcile_report_phantom.handler(event, context)
        mock_create_http_error_dict.assert_called_once_with(
            "InternalServerError",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            context.aws_request_id,
            f"data.{internal_reconcile_report_phantom.OUTPUT_PHANTOMS_KEY}[0]."
            f"{internal_reconcile_report_phantom.PHANTOMS_ORCA_LAST_UPDATE_KEY} must be integer",
        )
        self.assertEqual(mock_create_http_error_dict.return_value, result)

    @patch("internal_reconcile_report_phantom.query_db")
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

        phantoms = []
        for i in range(internal_reconcile_report_phantom.PAGE_SIZE):
            phantoms.append(Mock)
        mock_query_db.return_value = phantoms

        result = internal_reconcile_report_phantom.task(
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
                internal_reconcile_report_phantom.OUTPUT_JOB_ID_KEY: job_id,
                internal_reconcile_report_phantom.OUTPUT_ANOTHER_PAGE_KEY: False,
                internal_reconcile_report_phantom.OUTPUT_PHANTOMS_KEY: phantoms,
            },
            result,
        )

    @patch("internal_reconcile_report_phantom.query_db")
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

        phantoms = []
        for i in range(internal_reconcile_report_phantom.PAGE_SIZE + 1):
            phantoms.append(Mock)
        mock_query_db.return_value = phantoms

        result = internal_reconcile_report_phantom.task(
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
                internal_reconcile_report_phantom.OUTPUT_JOB_ID_KEY: job_id,
                internal_reconcile_report_phantom.OUTPUT_ANOTHER_PAGE_KEY: True,
                internal_reconcile_report_phantom.OUTPUT_PHANTOMS_KEY: phantoms[
                    0 : internal_reconcile_report_phantom.PAGE_SIZE
                ],
            },
            result,
        )

    @patch("internal_reconcile_report_phantom.get_phantoms_sql")
    def test_query_db_happy_path(self, mock_get_phantoms_sql: MagicMock):
        """
        Should query the db, then format the returned data.
        """
        job_id = random.randint(0, 999)  # nosec
        page_index = Mock()

        collection_id = uuid.uuid4().__str__()
        granule_id = uuid.uuid4().__str__()
        filename = uuid.uuid4().__str__()
        key_path = uuid.uuid4().__str__()
        orca_etag = uuid.uuid4().__str__()
        orca_last_update = random.randint(0, 999999)  # nosec
        orca_size = random.randint(0, 999)  # nosec

        returned_row0 = {
            "collection_id": collection_id,
            "granule_id": granule_id,
            "filename": filename,
            "key_path": key_path,
            "orca_etag": orca_etag,
            "orca_last_update": orca_last_update,
            "orca_size": orca_size,
        }
        mock_execute = Mock(return_value=[returned_row0])
        mock_connection = Mock()
        mock_connection.execute = mock_execute
        mock_exit = Mock(return_value=False)
        mock_enter = Mock()
        mock_enter.__enter__ = Mock(return_value=mock_connection)
        mock_enter.__exit__ = mock_exit
        mock_engine = Mock()
        mock_engine.begin = Mock(return_value=mock_enter)

        result = internal_reconcile_report_phantom.query_db(
            mock_engine,
            job_id,
            page_index,
        )

        mock_enter.__enter__.assert_called_once_with()
        mock_execute.assert_called_once_with(
            mock_get_phantoms_sql.return_value,
            [
                {
                    "job_id": job_id,
                    "page_index": page_index,
                    "page_size": internal_reconcile_report_phantom.PAGE_SIZE,
                }
            ],
        )
        mock_exit.assert_called_once_with(None, None, None)
        mock_get_phantoms_sql.assert_called_once_with()
        self.assertEqual(
            [
                {
                    internal_reconcile_report_phantom.PHANTOMS_COLLECTION_ID_KEY: collection_id,
                    internal_reconcile_report_phantom.PHANTOMS_GRANULE_ID_KEY: granule_id,
                    internal_reconcile_report_phantom.PHANTOMS_FILENAME_KEY: filename,
                    internal_reconcile_report_phantom.PHANTOMS_KEY_PATH_KEY: key_path,
                    internal_reconcile_report_phantom.PHANTOMS_ORCA_ETAG_KEY: orca_etag,
                    internal_reconcile_report_phantom.PHANTOMS_ORCA_LAST_UPDATE_KEY: orca_last_update,
                    internal_reconcile_report_phantom.PHANTOMS_ORCA_SIZE_KEY: orca_size,
                }
            ],
            result,
        )
