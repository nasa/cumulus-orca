"""
Name: test_request_status_for_job_unit.py

Description:  Unit tests for request_status_for_job.py.
"""
import json
import unittest
import uuid
from http import HTTPStatus
from unittest.mock import patch, MagicMock, Mock

import database
import fastjsonschema as fastjsonschema
import requests_db

import request_status_for_job


class TestRequestStatusForJobUnit(
    unittest.TestCase
):  # pylint: disable-msg=too-many-instance-attributes
    """
    TestRequestStatusForJob.
    """

    # noinspection PyPep8Naming
    @patch("request_status_for_job.task")
    @patch("requests_db.get_dbconnect_info")
    @patch("cumulus_logger.CumulusLogger.setMetadata")
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
        mock_task.assert_called_once_with(job_id, mock_get_dbconnect_info.return_value)
        self.assertEqual(mock_task.return_value, result)

    # noinspection PyPep8Naming
    @patch("requests_db.get_dbconnect_info")
    @patch("cumulus_logger.CumulusLogger.setMetadata")
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
    @patch("request_status_for_job.task")
    @patch("requests_db.get_dbconnect_info")
    @patch("cumulus_logger.CumulusLogger.setMetadata")
    def test_handler_database_error_returns_error_code(
        self,
        mock_setMetadata: MagicMock,
        mock_get_dbconnect_info: MagicMock,
        mock_task: MagicMock,
    ):
        """
        If database error is raised, it should be caught and returned in a dictionary.
        """
        job_id = uuid.uuid4().__str__()

        event = {request_status_for_job.INPUT_JOB_ID_KEY: job_id}
        context = Mock()
        mock_task.side_effect = requests_db.DatabaseError()
        result = request_status_for_job.handler(event, context)
        self.assertEqual(HTTPStatus.INTERNAL_SERVER_ERROR, result["httpStatus"])

    @patch("request_status_for_job.get_granule_status_entries_for_job")
    @patch("request_status_for_job.get_status_totals_for_job")
    def test_task_happy_path(
        self,
        mock_get_status_totals_for_job: MagicMock,
        mock_get_granule_status_entries_for_job: MagicMock,
    ):
        """
        Basic path with all information present.
        """
        job_id = uuid.uuid4().__str__()
        db_connect_info = Mock()

        result = request_status_for_job.task(job_id, db_connect_info)

        mock_get_granule_status_entries_for_job.assert_called_once_with(
            job_id, db_connect_info
        )
        mock_get_status_totals_for_job.assert_called_once_with(job_id, db_connect_info)

        self.assertEqual(
            {
                request_status_for_job.OUTPUT_JOB_ID_KEY: job_id,
                request_status_for_job.OUTPUT_JOB_STATUS_TOTALS_KEY: mock_get_status_totals_for_job.return_value,
                request_status_for_job.OUTPUT_GRANULES_KEY: mock_get_granule_status_entries_for_job.return_value,
            },
            result,
        )

    @patch("database.result_to_json")
    @patch("database.single_query")
    def test_get_granule_status_entries_for_job_happy_path(
        self, mock_single_query: MagicMock, mock_result_to_json: MagicMock
    ):
        """
        Basic path with all information present.
        """
        job_id = uuid.uuid4().__str__()

        db_connect_info = Mock()

        result = request_status_for_job.get_granule_status_entries_for_job(
            job_id, db_connect_info
        )

        mock_single_query.assert_called_once_with(
            f"""
            SELECT
                granule_id as "{request_status_for_job.OUTPUT_GRANULE_ID_KEY}",
                orca_status.value AS "{request_status_for_job.OUTPUT_STATUS_KEY}"
            FROM
                orca_recoveryjob
            JOIN orca_status ON orca_recoveryjob.status_id=orca_status.id
            WHERE
                job_id = %s
            """,
            db_connect_info,
            (job_id,),
        )
        mock_result_to_json.assert_called_once_with(mock_single_query.return_value)

        self.assertEqual(mock_result_to_json.return_value, result)

    @patch("database.single_query")
    def test_get_granule_status_entries_for_job_error_wrapped_in_database_error(
        self, mock_single_query: MagicMock
    ):
        """
        If error is raised when contacting DB, error should be raised as a DatabaseError.
        """
        job_id = uuid.uuid4().__str__()
        db_connect_info = Mock()

        mock_single_query.side_effect = database.DbError()

        with self.assertRaises(request_status_for_job.DatabaseError):
            request_status_for_job.get_granule_status_entries_for_job(
                job_id, db_connect_info
            )

    @patch("database.single_query")
    def test_get_status_totals_for_job_happy_path(self, mock_single_query: MagicMock):
        """
        Basic path with all information present.
        """
        job_id = uuid.uuid4().__str__()
        db_connect_info = Mock()

        mock_single_query.return_value = [
            {"value": "success", "total": 5},
            {"value": "future_status", "total": 10},
        ]

        result = request_status_for_job.get_status_totals_for_job(
            job_id, db_connect_info
        )

        mock_single_query.assert_called_once_with(
            f"""
            with granule_status_count AS (
                SELECT status_id
                    , count(*) as total
                FROM orca_recoveryjob
                WHERE job_id = %s
                GROUP BY status_id
            )
            SELECT value
                , coalesce(total, 0) as total
            FROM orca_status os
            LEFT JOIN granule_status_count gsc ON (gsc.status_id = os.id)""",
            db_connect_info,
            (job_id,),
        )

        self.assertEqual({"success": 5, "future_status": 10}, result)

    @patch("database.single_query")
    def test_get_status_totals_for_job_error_wrapped_in_database_error(
        self, mock_single_query: MagicMock
    ):
        """
        If error is raised when contacting DB, error should be raised as a DatabaseError.
        """
        job_id = uuid.uuid4().__str__()
        db_connect_info = Mock()

        mock_single_query.side_effect = database.DbError()

        with self.assertRaises(request_status_for_job.DatabaseError):
            request_status_for_job.get_status_totals_for_job(job_id, db_connect_info)

    def test_task_job_id_cannot_be_none(self):
        """
        Raises error if async_operation_id is None.
        """
        try:
            request_status_for_job.task(None, Mock())
        except ValueError:
            return
        self.fail("Error not raised.")

    # Multi-Function Tests:
    @patch("database.single_query")
    def test_task_output_json_schema(self, mock_single_query: MagicMock):
        """
        Checks a realistic output against the output.json.
        """
        job_id = uuid.uuid4().__str__()

        db_connect_info = Mock()

        mock_single_query.side_effect = [
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

        result = request_status_for_job.task(job_id, db_connect_info)

        with open("schemas/output.json", "r") as raw_schema:
            schema = json.loads(raw_schema.read())

        validate = fastjsonschema.compile(schema)
        validate(result)
