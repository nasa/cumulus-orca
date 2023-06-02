"""
Name: test_request_status_for_granule_unit.py

Description:  Unit tests for request_status_for_granule.py.
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

import request_status_for_granule


class TestRequestStatusForGranuleUnit(
    unittest.TestCase
):  # pylint: disable-msg=too-many-instance-attributes
    """
    TestRequestStatusForGranule.
    """

    # noinspection PyPep8Naming
    @patch("orca_shared.database.shared_db.get_configuration")
    @patch("request_status_for_granule.task")
    @patch.dict(
        os.environ,
        {"DB_CONNECT_INFO_SECRET_ARN": "test"},
        clear=True,
    )
    def test_handler_happy_path(
        self,
        mock_task: MagicMock,
        mock_get_dbconnect_info: MagicMock,
    ):
        """
        Basic path with all information present.
        """
        collection_id = uuid.uuid4().__str__()
        granule_id = uuid.uuid4().__str__()
        async_operation_id = uuid.uuid4().__str__()
        mock_task.return_value = {
            request_status_for_granule.OUTPUT_COLLECTION_ID_KEY: collection_id,
            request_status_for_granule.OUTPUT_GRANULE_ID_KEY: granule_id,
            request_status_for_granule.OUTPUT_JOB_ID_KEY: async_operation_id,
            request_status_for_granule.OUTPUT_FILES_KEY: [
                {
                    request_status_for_granule.OUTPUT_FILENAME_KEY:
                        uuid.uuid4().__str__(),  # nosec
                    request_status_for_granule.OUTPUT_RESTORE_DESTINATION_KEY:
                        uuid.uuid4().__str__(),  # nosec
                    request_status_for_granule.OUTPUT_STATUS_KEY:
                        "staged",
                }
            ],
            request_status_for_granule.OUTPUT_REQUEST_TIME_KEY:
                random.randint(0, 9999999),  # nosec
        }

        event = {
            request_status_for_granule.INPUT_COLLECTION_ID_KEY: collection_id,
            request_status_for_granule.INPUT_GRANULE_ID_KEY: granule_id,
            request_status_for_granule.INPUT_JOB_ID_KEY: async_operation_id,
        }
        context = Mock()

        result = request_status_for_granule.handler(event, context)

        mock_task.assert_called_once_with(
            collection_id,
            granule_id,
            mock_get_dbconnect_info.return_value,
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
        collection_id = uuid.uuid4().__str__()
        granule_id = uuid.uuid4().__str__()

        event = {
            request_status_for_granule.INPUT_COLLECTION_ID_KEY: collection_id,
            request_status_for_granule.INPUT_GRANULE_ID_KEY: granule_id,
        }
        context = Mock()
        mock_task.return_value = {
            request_status_for_granule.OUTPUT_COLLECTION_ID_KEY: collection_id,
            request_status_for_granule.OUTPUT_GRANULE_ID_KEY: granule_id,
            request_status_for_granule.OUTPUT_JOB_ID_KEY: uuid.uuid4().__str__(),  # nosec
            request_status_for_granule.OUTPUT_FILES_KEY: [
                {
                    request_status_for_granule.OUTPUT_FILENAME_KEY:
                        uuid.uuid4().__str__(),  # nosec
                    request_status_for_granule.OUTPUT_RESTORE_DESTINATION_KEY:
                        uuid.uuid4().__str__(),  # nosec
                    request_status_for_granule.OUTPUT_STATUS_KEY:
                        "staged",
                }
            ],
            request_status_for_granule.OUTPUT_REQUEST_TIME_KEY:
                random.randint(0, 9999999),  # nosec
        }

        result = request_status_for_granule.handler(event, context)

        mock_task.assert_called_once_with(
            collection_id,
            granule_id,
            mock_get_dbconnect_info.return_value,
            None,
        )
        self.assertEqual(mock_task.return_value, result)

    # noinspection PyPep8Naming
    @patch("request_status_for_granule.create_http_error_dict")
    @patch("request_status_for_granule.LOGGER.error")
    @patch("orca_shared.database.shared_db.get_configuration")
    @patch.dict(
        os.environ,
        {"DB_CONNECT_INFO_SECRET_ARN": "test"},
        clear=True,
    )
    def test_handler_missing_granule_id_returns_error_code(
        self,
        mock_get_dbconnect_info: MagicMock,
        mock_logger_error,
        mock_create_http_error_dict: MagicMock,
    ):
        """
        If granule_id is missing, error dictionary should be returned.
        """
        async_operation_id = uuid.uuid4().__str__()

        event = {
            request_status_for_granule.INPUT_COLLECTION_ID_KEY: uuid.uuid4().__str__(),
            request_status_for_granule.INPUT_JOB_ID_KEY: async_operation_id,
        }
        context = Mock()
        context.aws_request_id = Mock()

        result = request_status_for_granule.handler(event, context)
        mock_create_http_error_dict.assert_called_once_with(
            "BadRequest",
            HTTPStatus.BAD_REQUEST,
            context.aws_request_id,
            f"data must contain ['{request_status_for_granule.OUTPUT_COLLECTION_ID_KEY}', "
            f"'{request_status_for_granule.OUTPUT_GRANULE_ID_KEY}'] properties")
        self.assertEqual(mock_create_http_error_dict.return_value, result)

    # noinspection PyPep8Naming
    @patch("request_status_for_granule.create_http_error_dict")
    @patch("request_status_for_granule.LOGGER.error")
    @patch("request_status_for_granule.task")
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
        async_operation_id = uuid.uuid4().__str__()
        collection_id = uuid.uuid4().__str__()
        granule_id = uuid.uuid4().__str__()

        event = {
            request_status_for_granule.INPUT_JOB_ID_KEY: async_operation_id,
            request_status_for_granule.INPUT_COLLECTION_ID_KEY: collection_id,
            request_status_for_granule.INPUT_GRANULE_ID_KEY: granule_id,
        }
        context = Mock()

        database_exception = OperationalError(Mock(), Mock(), Mock())
        exceptions_and_results = [
            (
                database_exception,
                mock.call(
                    "InternalServerError",
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                    context.aws_request_id,
                    str(database_exception)
                )
            ),
            (
                request_status_for_granule.JobGranuleCombinationNotFoundException(
                    async_operation_id, collection_id, granule_id),
                mock.call(
                    "NotFound",
                    HTTPStatus.NOT_FOUND,
                    context.aws_request_id,
                    f"No job found for collection '{collection_id}' granule '{granule_id}' "
                    f"job '{async_operation_id}'."
                )
            ),
            (
                request_status_for_granule.JobNotFoundException(
                    collection_id,
                    granule_id
                ),
                mock.call(
                    "NotFound",
                    HTTPStatus.NOT_FOUND,
                    context.aws_request_id,
                    f"No job for collection '{collection_id}' granule '{granule_id}'.",
                )
            ),
        ]

        for exception_and_result in exceptions_and_results:
            with self.subTest(exception_and_result=exception_and_result):
                mock_task.side_effect = exception_and_result[0]

                result = request_status_for_granule.handler(event, context)
                # assert_called_once_with does not accept a `call` parameter.
                # Split into two checks.
                mock_create_http_error_dict.assert_has_calls(
                    [exception_and_result[1]]
                )
                self.assertEqual(1, mock_create_http_error_dict.call_count)
                self.assertEqual(mock_create_http_error_dict.return_value, result)

            mock_create_http_error_dict.reset_mock()
            mock_task.reset_mock()

    # noinspection PyPep8Naming
    @patch("request_status_for_granule.create_http_error_dict")
    @patch("orca_shared.database.shared_db.get_configuration")
    @patch("request_status_for_granule.task")
    @patch.dict(
        os.environ,
        {"DB_CONNECT_INFO_SECRET_ARN": "test"},
        clear=True,
    )
    def test_handler_invalid_output_raises_error(
        self,
        mock_task: MagicMock,
        mock_get_dbconnect_info: MagicMock,
        mock_create_http_error_dict: MagicMock,
    ):
        """
        If output is in invalid format, raise error.
        """
        collection_id = uuid.uuid4().__str__()
        granule_id = uuid.uuid4().__str__()
        async_operation_id = uuid.uuid4().__str__()
        mock_task.return_value = {
            request_status_for_granule.OUTPUT_COLLECTION_ID_KEY: collection_id,
            request_status_for_granule.OUTPUT_GRANULE_ID_KEY: granule_id,
            request_status_for_granule.OUTPUT_JOB_ID_KEY: async_operation_id,
            request_status_for_granule.OUTPUT_FILES_KEY: [
                {
                    request_status_for_granule.OUTPUT_FILENAME_KEY:
                        uuid.uuid4().__str__(),  # nosec
                    request_status_for_granule.OUTPUT_RESTORE_DESTINATION_KEY:
                        uuid.uuid4().__str__(),  # nosec
                    request_status_for_granule.OUTPUT_STATUS_KEY:
                        "apples",
                }
            ],
            request_status_for_granule.OUTPUT_REQUEST_TIME_KEY:
                random.randint(0, 9999999),  # nosec
        }

        event = {
            request_status_for_granule.INPUT_COLLECTION_ID_KEY: collection_id,
            request_status_for_granule.INPUT_GRANULE_ID_KEY: granule_id,
            request_status_for_granule.INPUT_JOB_ID_KEY: async_operation_id,
        }
        context = Mock()

        result = request_status_for_granule.handler(event, context)

        mock_task.assert_called_once_with(
            collection_id,
            granule_id,
            mock_get_dbconnect_info.return_value,
            async_operation_id,
        )
        mock_create_http_error_dict.assert_called_once_with(
            "InternalServerError",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            context.aws_request_id,
            f"data.{request_status_for_granule.OUTPUT_FILES_KEY}[0]."
            f"{request_status_for_granule.OUTPUT_STATUS_KEY} "
            f"must match pattern ^(pending|success|error|staged)$")
        self.assertEqual(mock_create_http_error_dict.return_value, result)

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
        collection_id = uuid.uuid4().__str__()
        granule_id = uuid.uuid4().__str__()
        job_id = uuid.uuid4().__str__()

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
            collection_id, granule_id, db_connect_info, job_id
        )

        mock_get_file_entries_for_granule_in_job.assert_called_once_with(
            collection_id, granule_id, job_id, mock_get_user_connection.return_value
        )
        mock_get_job_entry_for_granule.assert_called_once_with(
            collection_id, granule_id, job_id, mock_get_user_connection.return_value
        )

        expected = job_entry
        # noinspection PyTypeChecker
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
        collection_id = uuid.uuid4().__str__()
        granule_id = uuid.uuid4().__str__()
        job_id = uuid.uuid4().__str__()

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
            collection_id, granule_id, db_connect_info, None
        )

        mock_get_most_recent_job_id_for_granule.assert_called_once_with(
            collection_id, granule_id, mock_get_user_connection.return_value
        )
        mock_get_file_entries_for_granule_in_job.assert_called_once_with(
            collection_id, granule_id, job_id, mock_get_user_connection.return_value
        )
        mock_get_job_entry_for_granule.assert_called_once_with(
            collection_id, granule_id, job_id, mock_get_user_connection.return_value
        )

        expected = job_entry
        del expected[request_status_for_granule.OUTPUT_COMPLETION_TIME_KEY]
        # noinspection PyTypeChecker
        expected[request_status_for_granule.OUTPUT_FILES_KEY] = [
            {},
        ]
        mock_get_user_connection.assert_called_once_with(db_connect_info)
        self.assertEqual(expected, result)

    @patch("orca_shared.database.shared_db.get_user_connection")
    @patch("request_status_for_granule.get_most_recent_job_id_for_granule")
    def test_task_no_job_id_job_not_found_raises_error(
        self,
        mock_get_most_recent_job_id_for_granule: MagicMock,
        mock_get_user_connection: MagicMock,
    ):
        """
        If job_id is not given, and no valid job id is found, raise error.
        """
        collection_id = uuid.uuid4().__str__()
        granule_id = uuid.uuid4().__str__()

        db_connect_info = Mock()

        mock_get_most_recent_job_id_for_granule.return_value = None

        with self.assertRaises(request_status_for_granule.JobNotFoundException) as cm:
            request_status_for_granule.task(
                collection_id, granule_id, db_connect_info, None
            )
        self.assertEqual(collection_id, cm.exception.collection_id)
        self.assertEqual(granule_id, cm.exception.granule_id)

        mock_get_most_recent_job_id_for_granule.assert_called_once_with(
            collection_id, granule_id, mock_get_user_connection.return_value
        )
        mock_get_user_connection.assert_called_once_with(db_connect_info)

    @patch("orca_shared.database.shared_db.get_user_connection")
    @patch("request_status_for_granule.get_job_entry_for_granule")
    def test_task_job_for_granule_and_job_id_not_found_raises_error(
        self,
        mock_get_job_entry_for_granule: MagicMock,
        mock_get_user_connection: MagicMock,
    ):
        """
        If the job_id+granule_id does not point to an entry, raise error.
        """
        collection_id = uuid.uuid4().__str__()
        granule_id = uuid.uuid4().__str__()
        job_id = uuid.uuid4().__str__()

        db_connect_info = Mock()

        mock_get_job_entry_for_granule.return_value = None

        with self.assertRaises(request_status_for_granule.JobGranuleCombinationNotFoundException) \
                as cm:
            request_status_for_granule.task(
                collection_id, granule_id, db_connect_info, job_id
            )
        self.assertEqual(collection_id, cm.exception.collection_id)
        self.assertEqual(granule_id, cm.exception.granule_id)
        self.assertEqual(job_id, cm.exception.job_id)

        mock_get_job_entry_for_granule.assert_called_once_with(
            collection_id, granule_id, job_id, mock_get_user_connection.return_value
        )

        mock_get_user_connection.assert_called_once_with(db_connect_info)

    @patch("request_status_for_granule.get_most_recent_job_id_for_granule_sql")
    def test_get_most_recent_job_id_for_granule_happy_path(self, mock_sql: MagicMock):
        """
        Basic path with all information present.
        """
        collection_id = uuid.uuid4().__str__()
        granule_id = uuid.uuid4().__str__()
        job_id = uuid.uuid4().__str__()

        expected_result = {"job_id": job_id}

        mock_execute_result = Mock()
        mock_execute_result.mappings = Mock(return_value=copy.deepcopy([expected_result]))
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

        result = request_status_for_granule.get_most_recent_job_id_for_granule(
            collection_id, granule_id, mock_engine
        )

        mock_connection.execute.assert_called_once_with(
            mock_sql.return_value,
            [{"collection_id": collection_id, "granule_id": granule_id}],
        )
        mock_execute_result.mappings.assert_called_once_with()

        self.assertEqual(job_id, result)

    @patch("request_status_for_granule.get_job_entry_for_granule_sql")
    def test_get_job_entry_for_granule_happy_path(self, mock_sql: MagicMock):
        """
        Basic path with all information present.
        """
        collection_id = uuid.uuid4().__str__()
        granule_id = uuid.uuid4().__str__()
        job_id = uuid.uuid4().__str__()
        expected_result = {
            request_status_for_granule.OUTPUT_COLLECTION_ID_KEY: uuid.uuid4().__str__(),
            request_status_for_granule.OUTPUT_GRANULE_ID_KEY: uuid.uuid4().__str__(),
            request_status_for_granule.OUTPUT_JOB_ID_KEY: uuid.uuid4().__str__(),
            request_status_for_granule.OUTPUT_REQUEST_TIME_KEY: random.randint(  # nosec
                0, 628021800000
            ),
            request_status_for_granule.OUTPUT_COMPLETION_TIME_KEY: random.randint(  # nosec
                0, 628021800000
            ),
        }

        mock_execute_result = Mock()
        mock_execute_result.mappings = Mock(return_value=copy.deepcopy([expected_result]))
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

        result = request_status_for_granule.get_job_entry_for_granule(
            collection_id, granule_id, job_id, mock_engine
        )

        mock_connection.execute.assert_called_once_with(
            mock_sql.return_value,
            [
                {
                    "collection_id": collection_id,
                    "granule_id": granule_id,
                    "job_id": job_id,
                }
            ],
        )
        mock_execute_result.mappings.assert_called_once_with()

        self.assertEqual(expected_result, result)

    @patch("request_status_for_granule.get_file_entries_for_granule_in_job_sql")
    def test_get_file_entries_for_granule_in_job_happy_path(self, mock_sql: MagicMock):
        """
        Basic path with all information present.
        """
        collection_id = uuid.uuid4().__str__()
        granule_id = uuid.uuid4().__str__()
        job_id = uuid.uuid4().__str__()

        expected_result = [{
                request_status_for_granule.OUTPUT_FILENAME_KEY: uuid.uuid4().__str__(),
                request_status_for_granule.OUTPUT_RESTORE_DESTINATION_KEY: uuid.uuid4().__str__(),
                request_status_for_granule.OUTPUT_STATUS_KEY: uuid.uuid4().__str__(),
                request_status_for_granule.OUTPUT_ERROR_MESSAGE_KEY: uuid.uuid4().__str__(),
            }]

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

        result = request_status_for_granule.get_file_entries_for_granule_in_job(
            collection_id, granule_id, job_id, mock_engine
        )

        mock_connection.execute.assert_called_once_with(
            mock_sql.return_value,
            [
                {
                    "collection_id": collection_id,
                    "granule_id": granule_id,
                    "job_id": job_id,
                }
            ],
        )
        mock_execute_result.mappings.assert_called_once_with()

        self.assertEqual(expected_result, result)

    @patch("request_status_for_granule.LOGGER.error")
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
    def test_handler_output_json_schema(self, mock_get_user_connection: MagicMock):
        """
        Checks a realistic output against the output.json.
        """
        collection_id = uuid.uuid4().__str__()
        granule_id = uuid.uuid4().__str__()
        job_id = uuid.uuid4().__str__()
        request_time = random.randint(0, 628021800000)  # nosec

        filename_0 = uuid.uuid4().__str__() + ".ext"
        restore_destination_0 = uuid.uuid4().__str__()
        status_0 = "error"
        error_0 = uuid.uuid4().__str__()  # nosec

        filename_1 = uuid.uuid4().__str__() + ".ext"
        restore_destination_1 = uuid.uuid4().__str__()
        status_1 = "staged"
        error_1 = None

        db_connect_info = Mock()

        mock_execute_result0 = Mock()
        mock_execute_result1 = Mock()
        mock_execute_result0.mappings = Mock(
            return_value=[
                    {
                        request_status_for_granule.OUTPUT_COLLECTION_ID_KEY: collection_id,
                        request_status_for_granule.OUTPUT_GRANULE_ID_KEY: granule_id,
                        request_status_for_granule.OUTPUT_JOB_ID_KEY: job_id,
                        request_status_for_granule.OUTPUT_REQUEST_TIME_KEY: request_time,
                        request_status_for_granule.OUTPUT_COMPLETION_TIME_KEY: None,
                    }
                ]
            )
        mock_execute_result1.mappings = Mock(
            return_value=[
                {
                    request_status_for_granule.OUTPUT_FILENAME_KEY:
                        filename_0,
                    request_status_for_granule.OUTPUT_RESTORE_DESTINATION_KEY:
                        restore_destination_0,
                    request_status_for_granule.OUTPUT_STATUS_KEY:
                        status_0,
                    request_status_for_granule.OUTPUT_ERROR_MESSAGE_KEY:
                        error_0,
                },
                {
                    request_status_for_granule.OUTPUT_FILENAME_KEY:
                        filename_1,
                    request_status_for_granule.OUTPUT_RESTORE_DESTINATION_KEY:
                        restore_destination_1,
                    request_status_for_granule.OUTPUT_STATUS_KEY:
                        status_1,
                    request_status_for_granule.OUTPUT_ERROR_MESSAGE_KEY:
                        error_1,
                }
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

        result = request_status_for_granule.task(
            collection_id, granule_id, db_connect_info, job_id
        )

        self.assertEqual(
            {
                request_status_for_granule.OUTPUT_COLLECTION_ID_KEY: collection_id,
                request_status_for_granule.OUTPUT_GRANULE_ID_KEY: granule_id,
                request_status_for_granule.OUTPUT_JOB_ID_KEY: job_id,
                request_status_for_granule.OUTPUT_FILES_KEY: [
                    {
                        request_status_for_granule.OUTPUT_FILENAME_KEY: filename_0,
                        request_status_for_granule.OUTPUT_ERROR_MESSAGE_KEY: error_0,
                        request_status_for_granule.OUTPUT_RESTORE_DESTINATION_KEY:
                            restore_destination_0,
                        request_status_for_granule.OUTPUT_STATUS_KEY: status_0,
                    },
                    {
                        request_status_for_granule.OUTPUT_FILENAME_KEY: filename_1,
                        request_status_for_granule.OUTPUT_RESTORE_DESTINATION_KEY:
                            restore_destination_1,
                        request_status_for_granule.OUTPUT_STATUS_KEY: status_1,
                    }
                ],
                request_status_for_granule.OUTPUT_REQUEST_TIME_KEY: request_time,
            },
            result)

        mock_get_user_connection.assert_called_once_with(db_connect_info)
