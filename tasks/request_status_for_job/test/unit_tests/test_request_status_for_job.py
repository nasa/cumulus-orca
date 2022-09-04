"""
Name: test_request_status_for_job_unit.py

Description:  Unit tests for request_status_for_job.py.
"""
import copy
import json
import os
import random
import unittest
import uuid
from http import HTTPStatus
from unittest import mock
from unittest.mock import MagicMock, Mock, patch

import fastjsonschema as fastjsonschema
import sqlalchemy

import request_status_for_job

# Generating schema validators can take time, so do it once and reuse.
with open("schemas/output.json", "r") as raw_schema:
    _OUTPUT_VALIDATE = fastjsonschema.compile(json.loads(raw_schema.read()))


class TestRequestStatusForJobUnit(
    unittest.TestCase
):  # pylint: disable-msg=too-many-instance-attributes
    """
    TestRequestStatusForJob.
    """

    # noinspection PyPep8Naming
    @patch("request_status_for_job.task")
    @patch("orca_shared.database.shared_db.get_configuration")
    @patch("cumulus_logger.CumulusLogger.setMetadata")
    @patch.dict(
        os.environ,
        {"DB_CONNECT_INFO_SECRET_ARN": "test"},
        clear=True,
    )
    def test_handler_happy_path(
        self,
        mock_setMetadata: MagicMock,
        mock_get_dbconnect_info: MagicMock,
        mock_task: MagicMock,
    ):
        """
        Basic path with all information present.
        """
        job_id = uuid.uuid4().__str__()

        event = {request_status_for_job.INPUT_JOB_ID_KEY: job_id}
        context = Mock()
        result = request_status_for_job.handler(event, context)

        mock_setMetadata.assert_called_once_with(event, context)
        mock_task.assert_called_once_with(
            job_id, mock_get_dbconnect_info.return_value, context.aws_request_id
        )
        self.assertEqual(mock_task.return_value, result)

    # noinspection PyPep8Naming
    @patch("orca_shared.database.shared_db.get_configuration")
    @patch("cumulus_logger.CumulusLogger.setMetadata")
    @patch.dict(
        os.environ,
        {"DB_CONNECT_INFO_SECRET_ARN": "test"},
        clear=True,
    )
    def test_handler_missing_job_id_returns_error_code(
        self, mock_setMetadata: MagicMock, mock_get_dbconnect_info: MagicMock
    ):
        """
        If job_id is not present, should return an error dictionary.
        """
        event = {}
        context = Mock()
        result = request_status_for_job.handler(event, context)
        self.assertEqual(HTTPStatus.BAD_REQUEST, result["httpStatus"])

    # noinspection PyPep8Naming
    @patch("cumulus_logger.CumulusLogger.error")
    @patch("request_status_for_job.task")
    @patch("orca_shared.database.shared_db.get_configuration")
    @patch("cumulus_logger.CumulusLogger.setMetadata")
    @patch.dict(
        os.environ,
        {"DB_CONNECT_INFO_SECRET_ARN": "test"},
        clear=True,
    )
    def test_handler_database_error_returns_error_code(
        self,
        mock_setMetadata: MagicMock,
        mock_get_dbconnect_info: MagicMock,
        mock_task: MagicMock,
        mock_cumulus_logger_error: MagicMock,
    ):
        """
        If database error is raised, it should be caught and returned in a dictionary.
        """
        job_id = uuid.uuid4().__str__()

        event = {request_status_for_job.INPUT_JOB_ID_KEY: job_id}
        context = Mock()
        mock_task.side_effect = sqlalchemy.exc.OperationalError
        result = request_status_for_job.handler(event, context)
        self.assertEqual(HTTPStatus.INTERNAL_SERVER_ERROR, result["httpStatus"])

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
        request_id = uuid.uuid4().__str__()

        mock_get_granule_status_entries_for_job.return_value = [Mock()]

        result = request_status_for_job.task(job_id, db_connect_info, request_id)

        mock_get_user_connection.assert_called_once_with(db_connect_info)
        mock_get_granule_status_entries_for_job.assert_called_once_with(
            job_id, mock_get_user_connection.return_value
        )
        mock_get_status_totals_for_job.assert_called_once_with(
            job_id, mock_get_user_connection.return_value
        )

        self.assertEqual(
            {
                request_status_for_job.OUTPUT_JOB_ID_KEY:
                    job_id,
                request_status_for_job.OUTPUT_JOB_STATUS_TOTALS_KEY:
                    mock_get_status_totals_for_job.return_value,
                request_status_for_job.OUTPUT_GRANULES_KEY:
                    mock_get_granule_status_entries_for_job.return_value,
            },
            result,
        )

    @patch("orca_shared.database.shared_db.get_user_connection")
    @patch("request_status_for_job.create_http_error_dict")
    @patch("request_status_for_job.get_granule_status_entries_for_job")
    def test_task_no_granules_found_for_job_returns_error(
        self,
        mock_get_granule_status_entries_for_job: MagicMock,
        mock_create_http_error_dict: MagicMock,
        mock_get_user_connection: MagicMock,
    ):
        """
        If no recovery_job entries exist for the given job_id, return 404.
        """
        job_id = uuid.uuid4().__str__()
        db_connect_info = Mock()
        request_id = uuid.uuid4().__str__()

        result = request_status_for_job.task(job_id, db_connect_info, request_id)

        mock_get_user_connection.assert_called_once_with(db_connect_info)
        mock_get_granule_status_entries_for_job.assert_called_once_with(
            job_id, mock_get_user_connection.return_value
        )
        mock_create_http_error_dict.assert_called_once_with(
            "NotFound", HTTPStatus.NOT_FOUND, request_id, mock.ANY
        )

        self.assertEqual(mock_create_http_error_dict.return_value, result)

    @patch("request_status_for_job.get_granule_status_entries_for_job_sql")
    def test_get_granule_status_entries_for_job_happy_path(self, mock_sql: MagicMock):
        """
        Basic path with all information present.
        """
        job_id = uuid.uuid4().__str__()

        expected_result = [
            {
                request_status_for_job.OUTPUT_GRANULE_ID_KEY: uuid.uuid4().__str__(),
                request_status_for_job.OUTPUT_STATUS_KEY: uuid.uuid4().__str__(),
            },
            {
                request_status_for_job.OUTPUT_GRANULE_ID_KEY: uuid.uuid4().__str__(),
                request_status_for_job.OUTPUT_STATUS_KEY: uuid.uuid4().__str__(),
            },
        ]
        mock_engine = Mock()
        mock_engine.begin.return_value = Mock()
        mock_connection = Mock()
        mock_connection.execute.return_value = copy.deepcopy(expected_result)
        mock_engine.begin.return_value.__enter__ = Mock()
        mock_engine.begin.return_value.__enter__.return_value = mock_connection
        mock_engine.begin.return_value.__exit__ = Mock(
            return_value=False
        )  # required for "with", but untestable.

        result = request_status_for_job.get_granule_status_entries_for_job(
            job_id, mock_engine
        )

        mock_connection.execute.assert_called_once_with(
            mock_sql.return_value,
            [{"job_id": job_id}],
        )

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
        mock_engine = Mock()
        mock_engine.begin.return_value = Mock()
        mock_connection = Mock()
        mock_connection.execute.return_value = copy.deepcopy(expected_result)
        mock_engine.begin.return_value.__enter__ = Mock()
        mock_engine.begin.return_value.__enter__.return_value = mock_connection
        mock_engine.begin.return_value.__exit__ = Mock(
            return_value=False
        )  # required for "with", but untestable.

        result = request_status_for_job.get_status_totals_for_job(job_id, mock_engine)

        mock_connection.execute.assert_called_once_with(
            mock_sql.return_value,
            [{"job_id": job_id}],
        )

        self.assertEqual({"success": 5, "future_status": 10}, result)

    def test_task_job_id_cannot_be_none(self):
        """
        Raises error if async_operation_id is None.
        """
        try:
            request_status_for_job.task(None, Mock(), Mock())
        except ValueError:
            return
        self.fail("Error not raised.")

    @patch("cumulus_logger.CumulusLogger.error")
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
        request_id = uuid.uuid4().__str__()

        db_connect_info = Mock()

        mock_engine = Mock()
        mock_engine.begin.return_value = Mock()
        mock_connection = Mock()
        mock_connection.execute.side_effect = [
            # granules
            [
                {
                    request_status_for_job.OUTPUT_GRANULE_ID_KEY: uuid.uuid4().__str__(),
                    request_status_for_job.OUTPUT_STATUS_KEY: "success",
                },
                {
                    request_status_for_job.OUTPUT_GRANULE_ID_KEY: uuid.uuid4().__str__(),
                    request_status_for_job.OUTPUT_STATUS_KEY: "pending",
                },
            ],
            # status totals
            [
                {"value": "pending", "total": 5},
                {"value": "success", "total": 2},
                {"value": "staged", "total": 0},
                {"value": "failed", "total": 1000},
            ],
        ]
        mock_engine.begin.return_value.__enter__ = Mock()
        mock_engine.begin.return_value.__enter__.return_value = mock_connection
        mock_engine.begin.return_value.__exit__ = Mock(
            return_value=False
        )  # required for "with", but untestable.
        mock_get_user_connection.return_value = mock_engine

        result = request_status_for_job.task(job_id, db_connect_info, request_id)

        mock_get_user_connection.assert_called_once_with(db_connect_info)
        with open("schemas/output.json", "r") as raw_schema:
            json.loads(raw_schema.read())

        _OUTPUT_VALIDATE(result)
