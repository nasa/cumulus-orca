"""
Name: test_shared_reconciliation.py
Description: Unit tests for shared_reconciliation.py shared library.
"""

import datetime
import unittest
import uuid
from unittest.mock import MagicMock, Mock, patch

from orca_shared.reconciliation import OrcaStatus, shared_reconciliation


class TestSharedReconciliationLibraries(unittest.TestCase):
    """
    Unit tests for the shared_reconciliation library used by ORCA Reconciliation Lambdas.
    """

    @patch("orca_shared.reconciliation.shared_reconciliation.validate_postgres_name")
    def test_get_partition_name_from_bucket_name_happy_path(
        self, mock_validate_name: MagicMock
    ):
        """
        Should replace dashes with underscores.
        Leave this test hardcoded to avoid unintentional deviations from DB.
        """
        result = shared_reconciliation.get_partition_name_from_bucket_name(
            "apple-banana_-lemon"
        )
        expected_result = "reconcile_s3_object_apple_banana__lemon"
        mock_validate_name.assert_called_once_with(
            expected_result,
            f"Partition name '{expected_result}'",
            shared_reconciliation.LOGGER,
        )
        self.assertEqual(expected_result, result)

    @patch("orca_shared.reconciliation.shared_reconciliation.internal_update_job")
    def test_update_job_happy_path(self, mock_internal_update_job: MagicMock):
        """
        Happy path for updating job entry with status.
        """
        mock_error_message = uuid.uuid4().__str__()
        mock_job_id = Mock()
        mock_engine = Mock()

        end_time_present = [OrcaStatus.SUCCESS, OrcaStatus.ERROR]
        for status in OrcaStatus:
            with self.subTest(status=status):
                shared_reconciliation.update_job(
                    mock_job_id,
                    status,
                    mock_error_message if status == OrcaStatus.ERROR else None,
                    mock_engine,
                )

                mock_internal_update_job.assert_called_once_with(
                    mock_job_id,
                    status,
                    unittest.mock.ANY,
                    (
                        unittest.mock.ANY
                        if end_time_present.__contains__(status)
                        else None
                    ),
                    mock_error_message if status == OrcaStatus.ERROR else None,
                    mock_engine,
                )
            mock_internal_update_job.reset_mock()

    @patch("orca_shared.reconciliation.shared_reconciliation.internal_update_job")
    def test_update_job_error_message_required_on_error_status(
        self, mock_internal_update_job: MagicMock
    ):
        """
        Happy path for updating job entry with status.
        """
        mock_job_id = Mock()
        mock_engine = Mock()
        with self.assertRaises(ValueError) as cm:
            shared_reconciliation.update_job(
                mock_job_id,
                OrcaStatus.ERROR,
                None,
                mock_engine,
            )
        self.assertEqual(
            "Error message is required.",
            str(cm.exception),
        )

        mock_internal_update_job.assert_not_called()

    @patch("orca_shared.reconciliation.shared_reconciliation.internal_update_job")
    def test_update_job_error_message_only_valid_on_error_status(
        self, mock_internal_update_job: MagicMock
    ):
        """
        Error message can only be applied on error statuses. Otherwise, raise an error.
        """
        mock_error_message = uuid.uuid4().__str__()
        mock_job_id = Mock()
        mock_engine = Mock()

        for status in OrcaStatus:
            if status == OrcaStatus.ERROR:
                continue
            with self.subTest(status=status):
                with self.assertRaises(ValueError) as cm:
                    shared_reconciliation.update_job(
                        mock_job_id,
                        status,
                        mock_error_message,
                        mock_engine,
                    )
                    self.assertEqual(
                        "Cannot set error message outside of error status entries.",
                        str(cm.exception),
                    )

                    mock_internal_update_job.assert_not_called()

    @patch("orca_shared.reconciliation.shared_reconciliation.update_job_sql")
    def test_internal_update_job_happy_path(
        self,
        mock_update_job_sql: MagicMock,
    ):
        mock_error_message = uuid.uuid4().__str__()
        mock_job_id = Mock()
        mock_execute = Mock()
        mock_connection = Mock()
        mock_connection.execute = mock_execute
        mock_exit = Mock(return_value=False)
        mock_enter = Mock()
        mock_enter.__enter__ = Mock(return_value=mock_connection)
        mock_enter.__exit__ = mock_exit
        mock_engine = Mock()
        mock_engine.begin = Mock(return_value=mock_enter)
        status = OrcaStatus.SUCCESS

        last_update = datetime.datetime.utcnow()
        end_time = datetime.datetime.utcnow()
        shared_reconciliation.internal_update_job(
            mock_job_id,
            status,
            last_update,
            end_time,
            mock_error_message,
            mock_engine,
        )

        mock_enter.__enter__.assert_called_once_with()
        mock_execute.assert_called_once_with(
            mock_update_job_sql.return_value,
            [
                {
                    "id": mock_job_id,
                    "status_id": status.value,
                    "last_update": last_update,
                    "end_time": end_time,
                    "error_message": mock_error_message,
                }
            ],
        )
        mock_exit.assert_called_once_with(None, None, None)
        mock_update_job_sql.assert_called_once_with()

    @patch("orca_shared.reconciliation.shared_reconciliation.LOGGER")
    @patch("orca_shared.reconciliation.shared_reconciliation.update_job_sql")
    def test_internal_update_job_error_logged_and_raised(
        self, mock_update_job_sql: MagicMock, mock_logger: MagicMock
    ):
        """
        Exceptions from Postgres should bubble up.
        """
        expected_exception = Exception(uuid.uuid4().__str__())

        mock_job_id = Mock()
        mock_execute = Mock(side_effect=expected_exception)
        mock_connection = Mock()
        mock_connection.execute = mock_execute
        mock_exit = Mock(return_value=False)
        mock_enter = Mock()
        mock_enter.__enter__ = Mock(return_value=mock_connection)
        mock_enter.__exit__ = mock_exit
        mock_engine = Mock()
        mock_engine.begin = Mock(return_value=mock_enter)
        last_update = datetime.datetime.utcnow()
        end_time = datetime.datetime.utcnow()
        error_message = Mock()

        with self.assertRaises(Exception) as cm:
            shared_reconciliation.internal_update_job(
                mock_job_id,
                OrcaStatus.SUCCESS,
                last_update,
                end_time,
                error_message,
                mock_engine,
            )
        self.assertEqual(expected_exception, cm.exception)

        mock_enter.__enter__.assert_called_once_with()
        mock_execute.assert_called_once_with(
            mock_update_job_sql.return_value,
            [
                {
                    "id": mock_job_id,
                    "status_id": shared_reconciliation.OrcaStatus.SUCCESS.value,
                    "last_update": last_update,
                    "end_time": end_time,
                    "error_message": error_message,
                }
            ],
        )
        mock_exit.assert_called_once_with(
            Exception, expected_exception, unittest.mock.ANY
        )
        mock_update_job_sql.assert_called_once_with()
        mock_logger.error.assert_called_once_with(
            f"Error while updating job '{mock_job_id}': {expected_exception}"
        )
