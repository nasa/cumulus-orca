"""
Name: test_shared_reconciliation.py
Description: Unit tests for shared_reconciliation.py shared library.
"""
import unittest
import uuid
from unittest.mock import patch, MagicMock, Mock

from orca_shared.reconciliation import shared_reconciliation, OrcaStatus


class TestSharedReconciliationLibraries(unittest.TestCase):
    """
    Unit tests for the shared_reconciliation library used by ORCA Reconciliation Lambdas.
    """

    def test_get_partition_name_from_bucket_name_happy_path(self):
        """
        Should replace dashes with underscores.
        """
        result = shared_reconciliation.get_partition_name_from_bucket_name("apple-banana_-lemon")
        self.assertEqual("reconcile_s3_object_apple_banana__lemon", result)

    def test_get_partition_name_from_bucket_name_rejects_non_alphanumeric(self):
        """
        Should replace dashes with underscores.
        """
        for error_case in ["a a", "a!a"]:
            with self.subTest(error_case=error_case):
                with self.assertRaises(Exception) as cm:
                    shared_reconciliation.get_partition_name_from_bucket_name(error_case)
                self.assertEqual(f"'reconcile_s3_object_{error_case}' is not a valid partition name.", str(cm.exception))

    @patch("orca_shared.reconciliation.shared_reconciliation.update_job_sql")
    def test_update_job_happy_path(
        self,
        mock_update_job_sql: MagicMock,
    ):
        """
        Happy path for updating job entry with failure status and error message.
        """
        mock_error_message = Mock()
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

        end_time_present = [
            OrcaStatus.SUCCESS,
            OrcaStatus.ERROR
        ]
        for status in OrcaStatus:
            with self.subTest(status=status):
                now = uuid.uuid4().__str__()
                shared_reconciliation.update_job(
                    mock_job_id, status, now, mock_error_message, mock_engine, Mock()
                )

            mock_enter.__enter__.assert_called_once_with()
            mock_execute.assert_called_once_with(
                mock_update_job_sql.return_value,
                [
                    {
                        "id": mock_job_id,
                        "status_id": status.value,
                        "last_update": now,
                        "end_time": now if end_time_present.__contains__(status) else None,
                        "error_message": mock_error_message,
                    }
                ],
            )
            mock_exit.assert_called_once_with(None, None, None)
            mock_update_job_sql.assert_called_once_with()
            mock_execute.reset_mock()
            mock_exit.reset_mock()
            mock_enter.reset_mock()
            mock_update_job_sql.reset_mock()

    @patch("orca_shared.reconciliation.shared_reconciliation.update_job_sql")
    def test_update_job_error_logged_and_raised(
        self, mock_update_job_sql: MagicMock
    ):
        """
        Exceptions from Postgres should bubble up.
        """
        expected_exception = Exception(uuid.uuid4().__str__())

        mock_error_message = Mock()
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
        mock_logger = Mock()
        now = uuid.uuid4().__str__()

        with self.assertRaises(Exception) as cm:
            shared_reconciliation.update_job(
                mock_job_id, OrcaStatus.SUCCESS, now, mock_error_message, mock_engine, mock_logger
            )
        self.assertEqual(expected_exception, cm.exception)

        mock_enter.__enter__.assert_called_once_with()
        mock_execute.assert_called_once_with(
            mock_update_job_sql.return_value,
            [
                {
                    "id": mock_job_id,
                    "status_id": shared_reconciliation.OrcaStatus.SUCCESS.value,
                    "last_update": now,
                    "end_time": now,
                    "error_message": mock_error_message,
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
