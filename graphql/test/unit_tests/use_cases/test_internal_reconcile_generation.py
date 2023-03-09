import random
import unittest
from datetime import datetime, timezone
from unittest.mock import Mock, patch, MagicMock

from src.use_cases.internal_reconcile_generation import InternalReconcileGeneration


class TestInternalReconcileGeneration(unittest.TestCase):
    @patch("src.use_cases.internal_reconcile_generation.InternalReconcileReportCreationRecord")
    def test_create_job_happy_path(
        self,
        mock_InternalReconcileReportCreationRecord: MagicMock,
    ):
        """
        Should call the underlying storage function.
        """
        mock_storage = Mock()
        mock_job_cursor = Mock()
        mock_storage.create_job = Mock(return_value=mock_job_cursor)

        mock_report_source = Mock()
        creation_timestamp = random.randint(1000000000, 99999999999)  # nosec
        mock_logger = Mock()

        result = InternalReconcileGeneration(mock_storage).create_job(
            mock_report_source, creation_timestamp, mock_logger
        )

        mock_storage.create_job.assert_called_once_with(
            mock_report_source,
            datetime.utcfromtimestamp(
                creation_timestamp
            ).replace(tzinfo=timezone.utc),
            mock_logger,
        )
        mock_InternalReconcileReportCreationRecord.assert_called_once_with(mock_job_cursor)
        self.assertEqual(mock_InternalReconcileReportCreationRecord.return_value, result)

    def test_update_job_happy_path(
        self,
    ):
        """
        Should call the underlying storage function.
        """
        mock_storage = Mock()
        mock_storage.update_job = Mock()

        mock_report_cursor = Mock()
        mock_status = Mock()
        mock_error_message = Mock()

        InternalReconcileGeneration(mock_storage).update_job(
            mock_report_cursor, mock_status, mock_error_message,
        )

        mock_storage.update_job.assert_called_once_with(
            mock_report_cursor, mock_status, mock_error_message,
        )
