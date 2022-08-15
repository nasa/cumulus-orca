"""
Name: test_request_status_for_granule_unit.py

Description:  Unit tests for request_status_for_granule.py.
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

import fastjsonschema
import sqlalchemy.exc

import request_status_for_granule

# Generating schema validators can take time, so do it once and reuse.
with open("schemas/output.json", "r") as raw_schema:
    _OUTPUT_VALIDATE = fastjsonschema.compile(json.loads(raw_schema.read()))


class TestRequestStatusForGranuleUnit(
    unittest.TestCase
):  # pylint: disable-msg=too-many-instance-attributes
    """
    TestRequestStatusForGranule.
    """

    # noinspection PyPep8Naming
    @patch("orca_shared.database.shared_db.get_configuration")
    @patch("request_status_for_granule.task")
    @patch("cumulus_logger.CumulusLogger.setMetadata")
    @patch.dict(
        os.environ,
        {"DB_CONNECT_INFO_SECRET_ARN": "test"},
        clear=True,
    )
    def test_handler_happy_path(
        self,
        mock_setMetadata: MagicMock,
        mock_task: MagicMock,
        mock_get_dbconnect_info: MagicMock,
    ):
        """
        Basic path with all information present.
        """
        granule_id = uuid.uuid4().__str__()
        async_operation_id = uuid.uuid4().__str__()

        event = {
            request_status_for_granule.INPUT_GRANULE_ID_KEY: granule_id,
            request_status_for_granule.INPUT_JOB_ID_KEY: async_operation_id,
        }
        context = Mock()
        result = request_status_for_granule.handler(event, context)

        mock_setMetadata.assert_called_once_with(event, context)
        mock_task.assert_called_once_with(
            granule_id,
            mock_get_dbconnect_info.return_value,
            context.aws_request_id,
            async_operation_id,
        )
        self.assertEqual(mock_task.return_value, result)

    @patch("request_status_for_granule.task")
    @patch("orca_shared.database.shared_db.get_configuration")
    @patch.dict(
        os.environ,
        {"DB_CONNECT_INFO_SECRET_ARN": "test"},
        clear=True,
    )
    def test_handler_async_operation_id_defaults_to_none(
        self, mock_get_dbconnect_info: MagicMock, mock_task: MagicMock
    ):
        """
        If asyncOperationId is missing, it should default to null.
        """
        granule_id = uuid.uuid4().__str__()

        event = {request_status_for_granule.INPUT_GRANULE_ID_KEY: granule_id}
        context = Mock()
        result = request_status_for_granule.handler(event, context)

        mock_task.assert_called_once_with(
            granule_id,
            mock_get_dbconnect_info.return_value,
            context.aws_request_id,
            None,
        )
        self.assertEqual(mock_task.return_value, result)

    # noinspection PyPep8Naming
    @patch("cumulus_logger.CumulusLogger.error")
    @patch("orca_shared.database.shared_db.get_configuration")
    @patch("cumulus_logger.CumulusLogger.setMetadata")
    @patch.dict(
        os.environ,
        {"DB_CONNECT_INFO_SECRET_ARN": "test"},
        clear=True,
    )
    def test_handler_missing_granule_id_returns_error_code(
        self,
        mock_setMetadata: MagicMock,
        mock_get_dbconnect_info: MagicMock,
        mock_cumulus_logger_error,
    ):
        """
        If granule_id is missing, error dictionary should be returned.
        """
        async_operation_id = uuid.uuid4().__str__()

        event = {request_status_for_granule.INPUT_JOB_ID_KEY: async_operation_id}
        context = Mock()
        context.aws_request_id = Mock()

        result = request_status_for_granule.handler(event, context)
        self.assertEqual(HTTPStatus.BAD_REQUEST, result["httpStatus"])

    # noinspection PyPep8Naming
    @patch("cumulus_logger.CumulusLogger.error")
    @patch("request_status_for_granule.task")
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
        async_operation_id = uuid.uuid4().__str__()
        granule_id = uuid.uuid4().__str__()

        event = {
            request_status_for_granule.INPUT_JOB_ID_KEY: async_operation_id,
            request_status_for_granule.INPUT_GRANULE_ID_KEY: granule_id,
        }
        context = Mock()
        mock_task.side_effect = sqlalchemy.exc.OperationalError

        result = request_status_for_granule.handler(event, context)
        self.assertEqual(HTTPStatus.INTERNAL_SERVER_ERROR, result["httpStatus"])

    def test_task_granule_id_cannot_be_none(self):
        """
        Raises error if granule_id is None.
        """
        try:
            request_status_for_granule.task(None, uuid.uuid4().__str__(), Mock())
        except ValueError:
            return
        self.fail("Error not raised.")

    @patch("orca_shared.database.shared_db.get_user_connection")
    @patch("request_status_for_granule.get_job_entry_for_granule")
    @patch("request_status_for_granule.get_file_entries_for_granule_in_job")
    def test_task_job_id_present_does_not_re_get(
        self,
        mock_get_file_entries_for_granule_in_job: MagicMock,
        mock_get_job_entry_for_granule: MagicMock,
        mock_get_user_connection: MagicMock,
    ):
        """
        If job_id is given, then it should not take a separate request to get it.
        """
        granule_id = uuid.uuid4().__str__()
        job_id = uuid.uuid4().__str__()
        request_id = uuid.uuid4().__str__()

        db_connect_info = Mock()

        job_entry = {
            request_status_for_granule.OUTPUT_JOB_ID_KEY: job_id,
            request_status_for_granule.OUTPUT_COMPLETION_TIME_KEY: "1999-01-31 09:26:56.66+00:00",
        }
        mock_get_job_entry_for_granule.return_value = copy.deepcopy(job_entry)

        file_entries = [
            {
                request_status_for_granule.OUTPUT_ERROR_MESSAGE_KEY: "Something went boom."
            }
        ]
        mock_get_file_entries_for_granule_in_job.return_value = copy.deepcopy(
            file_entries
        )

        result = request_status_for_granule.task(
            granule_id, db_connect_info, request_id, job_id
        )

        mock_get_file_entries_for_granule_in_job.assert_called_once_with(
            granule_id, job_id, mock_get_user_connection.return_value
        )
        mock_get_job_entry_for_granule.assert_called_once_with(
            granule_id, job_id, mock_get_user_connection.return_value
        )

        expected = job_entry
        expected[request_status_for_granule.OUTPUT_FILES_KEY] = file_entries
        mock_get_user_connection.assert_called_once_with(db_connect_info)
        self.assertEqual(expected, result)

    @patch("orca_shared.database.shared_db.get_user_connection")
    @patch("request_status_for_granule.get_most_recent_job_id_for_granule")
    @patch("request_status_for_granule.get_job_entry_for_granule")
    @patch("request_status_for_granule.get_file_entries_for_granule_in_job")
    def test_task_no_job_id_gets(
        self,
        mock_get_file_entries_for_granule_in_job: MagicMock,
        mock_get_job_entry_for_granule: MagicMock,
        mock_get_most_recent_job_id_for_granule: MagicMock,
        mock_get_user_connection: MagicMock,
    ):
        """
        If job_id is not given, then it should take a separate request to get it.
        """
        granule_id = uuid.uuid4().__str__()
        job_id = uuid.uuid4().__str__()
        request_id = uuid.uuid4().__str__()

        db_connect_info = Mock()

        mock_get_most_recent_job_id_for_granule.return_value = job_id

        job_entry = {
            request_status_for_granule.OUTPUT_JOB_ID_KEY: job_id,
            request_status_for_granule.OUTPUT_COMPLETION_TIME_KEY: None,
        }
        mock_get_job_entry_for_granule.return_value = copy.deepcopy(job_entry)

        file_entries = [{request_status_for_granule.OUTPUT_ERROR_MESSAGE_KEY: None}]
        mock_get_file_entries_for_granule_in_job.return_value = copy.deepcopy(
            file_entries
        )

        result = request_status_for_granule.task(
            granule_id, db_connect_info, request_id, None
        )

        mock_get_most_recent_job_id_for_granule.assert_called_once_with(
            granule_id, mock_get_user_connection.return_value
        )
        mock_get_file_entries_for_granule_in_job.assert_called_once_with(
            granule_id, job_id, mock_get_user_connection.return_value
        )
        mock_get_job_entry_for_granule.assert_called_once_with(
            granule_id, job_id, mock_get_user_connection.return_value
        )

        expected = job_entry
        del expected[request_status_for_granule.OUTPUT_COMPLETION_TIME_KEY]
        expected[request_status_for_granule.OUTPUT_FILES_KEY] = [
            {},
        ]
        mock_get_user_connection.assert_called_once_with(db_connect_info)
        self.assertEqual(expected, result)

    @patch("orca_shared.database.shared_db.get_user_connection")
    @patch("request_status_for_granule.create_http_error_dict")
    @patch("request_status_for_granule.get_most_recent_job_id_for_granule")
    def test_task_no_job_id_job_not_found_returns_error(
        self,
        mock_get_most_recent_job_id_for_granule: MagicMock,
        mock_create_http_error_dict: MagicMock,
        mock_get_user_connection: MagicMock,
    ):
        """
        If job_id is not given, and no valid job id is found, return 404.
        """
        granule_id = uuid.uuid4().__str__()
        request_id = uuid.uuid4().__str__()

        db_connect_info = Mock()

        mock_get_most_recent_job_id_for_granule.return_value = None

        result = request_status_for_granule.task(
            granule_id, db_connect_info, request_id, None
        )

        mock_get_most_recent_job_id_for_granule.assert_called_once_with(
            granule_id, mock_get_user_connection.return_value
        )

        mock_create_http_error_dict.assert_called_once_with(
            "NotFound", HTTPStatus.NOT_FOUND, request_id, mock.ANY
        )
        mock_get_user_connection.assert_called_once_with(db_connect_info)
        self.assertEqual(mock_create_http_error_dict.return_value, result)

    @patch("orca_shared.database.shared_db.get_user_connection")
    @patch("request_status_for_granule.create_http_error_dict")
    @patch("request_status_for_granule.get_job_entry_for_granule")
    def test_task_job_for_granule_and_job_id_not_found_returns_error(
        self,
        mock_get_job_entry_for_granule: MagicMock,
        mock_create_http_error_dict: MagicMock,
        mock_get_user_connection: MagicMock,
    ):
        """
        If the job_id+granule_id does not point to an entry, return 404.
        """
        granule_id = uuid.uuid4().__str__()
        job_id = uuid.uuid4().__str__()
        request_id = uuid.uuid4().__str__()

        db_connect_info = Mock()

        mock_get_job_entry_for_granule.return_value = None

        result = request_status_for_granule.task(
            granule_id, db_connect_info, request_id, job_id
        )

        mock_get_job_entry_for_granule.assert_called_once_with(
            granule_id, job_id, mock_get_user_connection.return_value
        )

        mock_create_http_error_dict.assert_called_once_with(
            "NotFound", HTTPStatus.NOT_FOUND, request_id, mock.ANY
        )
        mock_get_user_connection.assert_called_once_with(db_connect_info)
        self.assertEqual(mock_create_http_error_dict.return_value, result)

    @patch("request_status_for_granule.get_most_recent_job_id_for_granule_sql")
    def test_get_most_recent_job_id_for_granule_happy_path(self, mock_sql: MagicMock):
        """
        Basic path with all information present.
        """
        granule_id = uuid.uuid4().__str__()
        job_id = uuid.uuid4().__str__()

        expected_result = [{"job_id": job_id}]
        mock_engine = Mock()
        mock_engine.begin.return_value = Mock()
        mock_connection = Mock()
        mock_connection.execute.return_value = copy.deepcopy(expected_result)
        mock_engine.begin.return_value.__enter__ = Mock()
        mock_engine.begin.return_value.__enter__.return_value = mock_connection
        mock_engine.begin.return_value.__exit__ = Mock(
            return_value=False
        )  # required for "with", but untestable.

        result = request_status_for_granule.get_most_recent_job_id_for_granule(
            granule_id, mock_engine
        )

        mock_connection.execute.assert_called_once_with(
            mock_sql.return_value,
            [{"granule_id": granule_id}],
        )

        self.assertEqual(job_id, result)

    @patch("request_status_for_granule.get_job_entry_for_granule_sql")
    def test_get_job_entry_for_granule_happy_path(self, mock_sql: MagicMock):
        """
        Basic path with all information present.
        """
        granule_id = uuid.uuid4().__str__()
        job_id = uuid.uuid4().__str__()
        expected_result = {
            request_status_for_granule.OUTPUT_GRANULE_ID_KEY: uuid.uuid4().__str__(),
            request_status_for_granule.OUTPUT_JOB_ID_KEY: uuid.uuid4().__str__(),
            request_status_for_granule.OUTPUT_REQUEST_TIME_KEY: random.randint(  # nosec
                0, 628021800000
            ),
            request_status_for_granule.OUTPUT_COMPLETION_TIME_KEY: random.randint(  # nosec
                0, 628021800000
            ),
        }

        mock_engine = Mock()
        mock_engine.begin.return_value = Mock()
        mock_connection = Mock()
        mock_connection.execute.return_value = [copy.deepcopy(expected_result)]
        mock_engine.begin.return_value.__enter__ = Mock()
        mock_engine.begin.return_value.__enter__.return_value = mock_connection
        mock_engine.begin.return_value.__exit__ = Mock(
            return_value=False
        )  # required for "with", but untestable.

        result = request_status_for_granule.get_job_entry_for_granule(
            granule_id, job_id, mock_engine
        )

        mock_connection.execute.assert_called_once_with(
            mock_sql.return_value,
            [
                {
                    "granule_id": granule_id,
                    "job_id": job_id,
                }
            ],
        )

        self.assertEqual(expected_result, result)

    @patch("request_status_for_granule.get_file_entries_for_granule_in_job_sql")
    def test_get_file_entries_for_granule_in_job_happy_path(self, mock_sql: MagicMock):
        """
        Basic path with all information present.
        """
        granule_id = uuid.uuid4().__str__()
        job_id = uuid.uuid4().__str__()

        expected_result = [
            {
                request_status_for_granule.OUTPUT_FILENAME_KEY: uuid.uuid4().__str__(),
                request_status_for_granule.OUTPUT_RESTORE_DESTINATION_KEY: uuid.uuid4().__str__(),
                request_status_for_granule.OUTPUT_STATUS_KEY: uuid.uuid4().__str__(),
                request_status_for_granule.OUTPUT_ERROR_MESSAGE_KEY: uuid.uuid4().__str__(),
            }
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

        result = request_status_for_granule.get_file_entries_for_granule_in_job(
            granule_id, job_id, mock_engine
        )

        mock_connection.execute.assert_called_once_with(
            mock_sql.return_value,
            [
                {
                    "granule_id": granule_id,
                    "job_id": job_id,
                }
            ],
        )

        self.assertEqual(expected_result, result)

    @patch("cumulus_logger.CumulusLogger.error")
    def test_create_http_error_dict_happy_path(self, mock_error: MagicMock):
        error_type = uuid.uuid4().__str__()
        http_status_code = random.randint(0, 9999)  # nosec
        request_id = uuid.uuid4().__str__()
        message = uuid.uuid4().__str__()

        result = request_status_for_granule.create_http_error_dict(
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
        granule_id = uuid.uuid4().__str__()
        job_id = uuid.uuid4().__str__()
        request_id = uuid.uuid4().__str__()

        db_connect_info = Mock()

        mock_engine = Mock()
        mock_engine.begin.return_value = Mock()
        mock_connection = Mock()
        mock_connection.execute.side_effect = [
            # job
            [
                {
                    request_status_for_granule.OUTPUT_GRANULE_ID_KEY: granule_id,
                    request_status_for_granule.OUTPUT_JOB_ID_KEY: job_id,
                    request_status_for_granule.OUTPUT_REQUEST_TIME_KEY: random.randint(  # nosec
                        0, 628021800000
                    ),
                    request_status_for_granule.OUTPUT_COMPLETION_TIME_KEY: None,
                }
            ],
            # files
            [
                {
                    request_status_for_granule.OUTPUT_FILENAME_KEY: uuid.uuid4().__str__()
                    + ".ext",
                    request_status_for_granule.OUTPUT_RESTORE_DESTINATION_KEY: uuid.uuid4().__str__(),
                    request_status_for_granule.OUTPUT_STATUS_KEY: "failed",
                    request_status_for_granule.OUTPUT_ERROR_MESSAGE_KEY: "some error message",
                },
                {
                    request_status_for_granule.OUTPUT_FILENAME_KEY: uuid.uuid4().__str__()
                    + ".ext",
                    request_status_for_granule.OUTPUT_RESTORE_DESTINATION_KEY: uuid.uuid4().__str__(),
                    request_status_for_granule.OUTPUT_STATUS_KEY: "staged",
                    request_status_for_granule.OUTPUT_ERROR_MESSAGE_KEY: None,
                },
            ],
        ]
        mock_engine.begin.return_value.__enter__ = Mock()
        mock_engine.begin.return_value.__enter__.return_value = mock_connection
        mock_engine.begin.return_value.__exit__ = Mock(
            return_value=False
        )  # required for "with", but untestable.
        mock_get_user_connection.return_value = mock_engine

        result = request_status_for_granule.task(
            granule_id, db_connect_info, request_id, job_id
        )

        mock_get_user_connection.assert_called_once_with(db_connect_info)
        _OUTPUT_VALIDATE(result)
