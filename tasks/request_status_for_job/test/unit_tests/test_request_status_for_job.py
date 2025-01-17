"""
Name: test_request_status_for_job_unit.py

Description:  Unit tests for request_status_for_job.py.
"""

import copy
import os
import random
import unittest
import uuid
from http import HTTPStatus
from unittest import mock
from unittest.mock import MagicMock, Mock, patch

from sqlalchemy.exc import OperationalError

import request_status_for_job


class TestRequestStatusForJobUnit(
    unittest.TestCase
):  # pylint: disable-msg=too-many-instance-attributes
    """
    TestRequestStatusForJob.
    """

    # noinspection PyPep8Naming
    @patch("request_status_for_job.task")
    @patch("orca_shared.database.shared_db.get_configuration")
    @patch.dict(
        os.environ,
        {"DB_CONNECT_INFO_SECRET_ARN": "test"},
        clear=True,
    )
    def test_handler_happy_path(
        self,
        mock_get_dbconnect_info: MagicMock,
        mock_task: MagicMock,
    ):
        """
        Basic path with all information present.
        """
        job_id = uuid.uuid4().__str__()
        mock_task.return_value = {
            request_status_for_job.OUTPUT_JOB_ID_KEY: job_id,
            request_status_for_job.OUTPUT_GRANULES_KEY: [
                {
                    request_status_for_job.OUTPUT_COLLECTION_ID_KEY: uuid.uuid4().__str__(),
                    request_status_for_job.OUTPUT_GRANULE_ID_KEY: uuid.uuid4().__str__(),
                    request_status_for_job.OUTPUT_STATUS_KEY: "staged",
                }
            ],
            request_status_for_job.OUTPUT_JOB_STATUS_TOTALS_KEY: {
                "pending": random.randint(0, 15),  # nosec
                "staged": random.randint(0, 15),  # nosec
                "success": random.randint(0, 15),  # nosec
                "error": random.randint(0, 15),  # nosec
            },
        }

        event = {request_status_for_job.INPUT_JOB_ID_KEY: job_id}
        context = Mock()

        result = request_status_for_job.handler(event, context)

        mock_task.assert_called_once_with(job_id, mock_get_dbconnect_info.return_value)
        self.assertEqual(mock_task.return_value, result)

    # noinspection PyPep8Naming,PyUnusedLocal
    @patch("request_status_for_job.create_http_error_dict")
    @patch("orca_shared.database.shared_db.get_configuration")
    @patch.dict(
        os.environ,
        {"DB_CONNECT_INFO_SECRET_ARN": "test"},
        clear=True,
    )
    def test_handler_missing_job_id_returns_error_code(
        self,
        mock_get_dbconnect_info: MagicMock,
        mock_create_http_error_dict: MagicMock,
    ):
        """
        If job_id is not present, should return an error dictionary.
        """
        event = {}
        context = Mock()

        result = request_status_for_job.handler(event, context)

        mock_create_http_error_dict.assert_called_once_with(
            "BadRequest",
            HTTPStatus.BAD_REQUEST,
            context.aws_request_id,
            f"data must contain ['{request_status_for_job.OUTPUT_JOB_ID_KEY}'] properties",
        )
        self.assertEqual(mock_create_http_error_dict.return_value, result)

    # noinspection PyPep8Naming,PyUnusedLocal
    @patch("request_status_for_job.create_http_error_dict")
    @patch("request_status_for_job.LOGGER.error")
    @patch("request_status_for_job.task")
    @patch("orca_shared.database.shared_db.get_configuration")
    @patch.dict(
        os.environ,
        {"DB_CONNECT_INFO_SECRET_ARN": "test"},
        clear=True,
    )
    def test_handler_exception_returns_proper_error_code(
        self,
        mock_get_dbconnect_info: MagicMock,
        mock_task: MagicMock,
        mock_logger_error: MagicMock,
        mock_create_http_error_dict: MagicMock,
    ):
        """
        If error is raised, it should be caught and returned in a dictionary.
        """
        job_id = uuid.uuid4().__str__()

        event = {request_status_for_job.INPUT_JOB_ID_KEY: job_id}
        context = Mock()
        database_exception = OperationalError(Mock(), Mock(), Mock())
        exceptions_and_results = [
            (
                database_exception,
                mock.call(
                    "InternalServerError",
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                    context.aws_request_id,
                    str(database_exception),
                ),
            ),
            (
                request_status_for_job.StatusNotFoundException(job_id),
                mock.call(
                    "NotFound",
                    HTTPStatus.NOT_FOUND,
                    context.aws_request_id,
                    f"No granules found for job id '{job_id}'.",
                ),
            ),
        ]

        for exception_and_result in exceptions_and_results:
            with self.subTest(exception_and_result=exception_and_result):
                mock_task.side_effect = exception_and_result[0]

                result = request_status_for_job.handler(event, context)
                # assert_called_once_with does not accept a `call` parameter.
                # Split into two checks.
                mock_create_http_error_dict.assert_has_calls([exception_and_result[1]])
                self.assertEqual(1, mock_create_http_error_dict.call_count)
                self.assertEqual(mock_create_http_error_dict.return_value, result)

            mock_create_http_error_dict.reset_mock()
            mock_task.reset_mock()

    # noinspection PyPep8Naming
    @patch("request_status_for_job.create_http_error_dict")
    @patch("request_status_for_job.task")
    @patch("orca_shared.database.shared_db.get_configuration")
    @patch.dict(
        os.environ,
        {"DB_CONNECT_INFO_SECRET_ARN": "test"},
        clear=True,
    )
    def test_handler_invalid_output_raises_error(
        self,
        mock_get_dbconnect_info: MagicMock,
        mock_task: MagicMock,
        mock_create_http_error_dict: MagicMock,
    ):
        """
        If output is in invalid format, raise error.
        """
        job_id = uuid.uuid4().__str__()
        mock_task.return_value = {
            request_status_for_job.OUTPUT_JOB_ID_KEY: job_id,
            request_status_for_job.OUTPUT_GRANULES_KEY: [
                {
                    request_status_for_job.OUTPUT_COLLECTION_ID_KEY: uuid.uuid4().__str__(),
                    request_status_for_job.OUTPUT_GRANULE_ID_KEY: uuid.uuid4().__str__(),
                    request_status_for_job.OUTPUT_STATUS_KEY: "staged",
                }
            ],
            request_status_for_job.OUTPUT_JOB_STATUS_TOTALS_KEY: {
                "pending": random.randint(0, 15),  # nosec
                "staged": random.randint(0, 15),  # nosec
                "success": random.randint(0, 15),  # nosec
            },
        }

        event = {request_status_for_job.INPUT_JOB_ID_KEY: job_id}
        context = Mock()

        result = request_status_for_job.handler(event, context)

        mock_task.assert_called_once_with(
            job_id,
            mock_get_dbconnect_info.return_value,
        )
        mock_create_http_error_dict.assert_called_once_with(
            "InternalServerError",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            context.aws_request_id,
            f"data.{request_status_for_job.OUTPUT_JOB_STATUS_TOTALS_KEY} "
            f"must contain ['pending', 'staged', 'success', 'error'] properties",
        )
        self.assertEqual(mock_create_http_error_dict.return_value, result)

    @patch("orca_shared.database.shared_db.get_user_connection")
    @patch("request_status_for_job.get_granule_status_entries_for_job")
    @patch("request_status_for_job.get_status_totals_for_job")
    def test_task_happy_path(
        self,
        mock_get_status_totals_for_job: MagicMock,
        mock_get_granule_status_entries_for_job: MagicMock,
        mock_get_user_connection: MagicMock,
    ):
        """
        Basic path with all information present.
        """
        job_id = uuid.uuid4().__str__()
        db_connect_info = Mock()

        mock_get_granule_status_entries_for_job.return_value = [Mock()]

        result = request_status_for_job.task(job_id, db_connect_info)

        mock_get_user_connection.assert_called_once_with(db_connect_info)
        mock_get_granule_status_entries_for_job.assert_called_once_with(
            job_id, mock_get_user_connection.return_value
        )
        mock_get_status_totals_for_job.assert_called_once_with(
            job_id, mock_get_user_connection.return_value
        )

        self.assertEqual(
            {
                request_status_for_job.OUTPUT_JOB_ID_KEY: job_id,
                request_status_for_job.OUTPUT_JOB_STATUS_TOTALS_KEY: mock_get_status_totals_for_job.return_value,  # noqa: E501
                request_status_for_job.OUTPUT_GRANULES_KEY: mock_get_granule_status_entries_for_job.return_value,  # noqa: E501
            },
            result,
        )

    @patch("orca_shared.database.shared_db.get_user_connection")
    @patch("request_status_for_job.get_granule_status_entries_for_job")
    def test_task_no_granules_found_for_job_raises_error(
        self,
        mock_get_granule_status_entries_for_job: MagicMock,
        mock_get_user_connection: MagicMock,
    ):
        """
        If no recovery_job entries exist for the given job_id, raise error.
        """
        job_id = uuid.uuid4().__str__()
        db_connect_info = Mock()

        with self.assertRaises(request_status_for_job.StatusNotFoundException) as cm:
            request_status_for_job.task(job_id, db_connect_info)
        self.assertEqual(job_id, cm.exception.job_id)

        mock_get_user_connection.assert_called_once_with(db_connect_info)
        mock_get_granule_status_entries_for_job.assert_called_once_with(
            job_id, mock_get_user_connection.return_value
        )

    @patch("request_status_for_job.get_granule_status_entries_for_job_sql")
    def test_get_granule_status_entries_for_job_happy_path(self, mock_sql: MagicMock):
        """
        Basic path with all information present.
        """
        job_id = uuid.uuid4().__str__()

        expected_result = [
            {
                request_status_for_job.OUTPUT_COLLECTION_ID_KEY: uuid.uuid4().__str__(),
                request_status_for_job.OUTPUT_GRANULE_ID_KEY: uuid.uuid4().__str__(),
                request_status_for_job.OUTPUT_STATUS_KEY: uuid.uuid4().__str__(),
            },
            {
                request_status_for_job.OUTPUT_COLLECTION_ID_KEY: uuid.uuid4().__str__(),
                request_status_for_job.OUTPUT_GRANULE_ID_KEY: uuid.uuid4().__str__(),
                request_status_for_job.OUTPUT_STATUS_KEY: uuid.uuid4().__str__(),
            },
        ]
        mock_execute_result = Mock()
        mock_execute_result.mappings = Mock(return_value=copy.deepcopy(expected_result))
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
        result = request_status_for_job.get_granule_status_entries_for_job(
            job_id, mock_engine
        )

        mock_connection.execute.assert_called_once_with(
            mock_sql.return_value,
            [{"job_id": job_id}],
        )
        mock_execute_result.mappings.assert_called_once_with()

        self.assertEqual(expected_result, result)

    @patch("request_status_for_job.get_status_totals_for_job_sql")
    def test_get_status_totals_for_job_happy_path(self, mock_sql: MagicMock):
        """
        Basic path with all information present.
        """
        job_id = uuid.uuid4().__str__()

        expected_result = [
            {"value": "success", "total": 5},
            {"value": "future_status", "total": 10},
        ]
        mock_execute_result = Mock()
        mock_execute_result.mappings = Mock(return_value=copy.deepcopy(expected_result))
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

        result = request_status_for_job.get_status_totals_for_job(job_id, mock_engine)

        mock_connection.execute.assert_called_once_with(
            mock_sql.return_value,
            [{"job_id": job_id}],
        )
        mock_execute_result.mappings.assert_called_once_with()

        self.assertEqual({"success": 5, "future_status": 10}, result)

    def test_task_job_id_cannot_be_none(self):
        """
        Raises error if async_operation_id is None.
        """
        try:
            # noinspection PyTypeChecker
            request_status_for_job.task(None, Mock())
        except ValueError:
            return
        self.fail("Error not raised.")

    @patch("request_status_for_job.LOGGER.error")
    def test_create_http_error_dict_happy_path(self, mock_error: MagicMock):
        error_type = uuid.uuid4().__str__()
        http_status_code = random.randint(0, 9999)  # nosec
        request_id = uuid.uuid4().__str__()
        message = uuid.uuid4().__str__()

        result = request_status_for_job.create_http_error_dict(
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

    # Multi-Function Tests:
    @patch("orca_shared.database.shared_db.get_user_connection")
    def test_task_output_json_schema(self, mock_get_user_connection: MagicMock):
        """
        Checks a realistic output against the output.json.
        """
        job_id = uuid.uuid4().__str__()

        db_connect_info = Mock()

        collection_id_0 = uuid.uuid4().__str__()
        collection_id_1 = uuid.uuid4().__str__()

        granule_id_0 = uuid.uuid4().__str__()
        granule_id_1 = uuid.uuid4().__str__()

        mock_execute_result0 = Mock()
        mock_execute_result1 = Mock()
        mock_execute_result0.mappings = Mock(
            return_value=[
                {
                    request_status_for_job.OUTPUT_COLLECTION_ID_KEY: collection_id_0,
                    request_status_for_job.OUTPUT_GRANULE_ID_KEY: granule_id_0,
                    request_status_for_job.OUTPUT_STATUS_KEY: "success",
                },
                {
                    request_status_for_job.OUTPUT_COLLECTION_ID_KEY: collection_id_1,
                    request_status_for_job.OUTPUT_GRANULE_ID_KEY: granule_id_1,
                    request_status_for_job.OUTPUT_STATUS_KEY: "pending",
                },
            ]
        )
        mock_execute_result1.mappings = Mock(
            return_value=[
                {"value": "pending", "total": 5},
                {"value": "success", "total": 2},
                {"value": "staged", "total": 0},
                {"value": "error", "total": 1000},
            ]
        )

        mock_execute = Mock(side_effect=[mock_execute_result0, mock_execute_result1])
        mock_connection = Mock()
        mock_connection.execute = mock_execute
        mock_exit = Mock(return_value=False)
        mock_enter = Mock()
        mock_enter.__enter__ = Mock(return_value=mock_connection)
        mock_enter.__exit__ = mock_exit
        mock_engine = Mock()
        mock_engine.begin = Mock(return_value=mock_enter)
        mock_get_user_connection.return_value = mock_engine

        result = request_status_for_job.task(job_id, db_connect_info)
        self.assertEqual(
            {
                request_status_for_job.OUTPUT_JOB_ID_KEY: job_id,
                request_status_for_job.OUTPUT_GRANULES_KEY: [
                    {
                        request_status_for_job.OUTPUT_COLLECTION_ID_KEY: collection_id_0,
                        request_status_for_job.OUTPUT_GRANULE_ID_KEY: granule_id_0,
                        request_status_for_job.OUTPUT_STATUS_KEY: "success",
                    },
                    {
                        request_status_for_job.OUTPUT_COLLECTION_ID_KEY: collection_id_1,
                        request_status_for_job.OUTPUT_GRANULE_ID_KEY: granule_id_1,
                        request_status_for_job.OUTPUT_STATUS_KEY: "pending",
                    },
                ],
                request_status_for_job.OUTPUT_JOB_STATUS_TOTALS_KEY: {
                    "error": 1000,
                    "pending": 5,
                    "staged": 0,
                    "success": 2,
                },
            },
            result,
        )

        mock_get_user_connection.assert_called_once_with(db_connect_info)
