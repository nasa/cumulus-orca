import random
import unittest
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock, Mock, call, patch

from orca_shared.reconciliation import OrcaStatus

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

    @patch("src.use_cases.internal_reconcile_generation.InternalReconcileGeneration.update_job")
    def test_get_current_archive_list_happy_path(
        self,
        mock_update_job: MagicMock,
    ):
        """
        Should call the underlying storage function.
        """
        mock_report_source = Mock()
        mock_report_cursor = Mock()
        mock_columns_in_csv = Mock()
        mock_csv_file_locations = Mock()
        mock_report_bucket_region = Mock()
        mock_logger = Mock()

        mock_storage = Mock()
        mock_storage.pull_in_inventory_report = Mock()

        InternalReconcileGeneration(mock_storage).get_current_archive_list(
            mock_report_source,
            mock_report_cursor,
            mock_columns_in_csv,
            mock_csv_file_locations,
            mock_report_bucket_region,
            mock_logger,
        )

        mock_storage.pull_in_inventory_report.assert_called_once_with(
            mock_report_source,
            mock_report_cursor,
            mock_columns_in_csv,
            mock_csv_file_locations,
            mock_report_bucket_region,
            mock_logger,
        )

        mock_update_job.assert_called_once_with(mock_report_cursor, OrcaStatus.STAGED, None)

    @patch("src.use_cases.internal_reconcile_generation.InternalReconcileGeneration.update_job")
    def test_get_current_archive_list_error_recorded(
        self,
        mock_update_job: MagicMock,
    ):
        """
        If operation fails, should post an error status update.
        """
        mock_report_source = Mock()
        mock_report_cursor = Mock()
        mock_columns_in_csv = Mock()
        mock_csv_file_locations = Mock()
        mock_report_bucket_region = Mock()
        mock_logger = Mock()
        expected_exception = Exception(uuid.uuid4().__str__())

        mock_storage = Mock()
        mock_storage.pull_in_inventory_report = Mock(side_effect=expected_exception)

        with self.assertRaises(Exception) as cm:
            InternalReconcileGeneration(mock_storage).get_current_archive_list(
                mock_report_source,
                mock_report_cursor,
                mock_columns_in_csv,
                mock_csv_file_locations,
                mock_report_bucket_region,
                mock_logger,
            )

        self.assertEqual(expected_exception, cm.exception)

        mock_storage.pull_in_inventory_report.assert_called_once_with(
            mock_report_source,
            mock_report_cursor,
            mock_columns_in_csv,
            mock_csv_file_locations,
            mock_report_bucket_region,
            mock_logger,
        )
        mock_update_job.assert_called_once_with(
            mock_report_cursor,
            OrcaStatus.ERROR,
            str(expected_exception),
        )

    @patch("src.use_cases.internal_reconcile_generation.InternalReconcileGeneration.update_job")
    def test_perform_orca_reconcile_happy_path(
        self,
        mock_update_job: MagicMock,
    ):
        """
        Should call the underlying storage function.
        """
        mock_report_source = Mock()
        mock_report_cursor = Mock()
        mock_logger = Mock()

        mock_storage = Mock()
        mock_storage.perform_orca_reconcile = Mock()

        InternalReconcileGeneration(mock_storage).perform_orca_reconcile(
            mock_report_source,
            mock_report_cursor,
            mock_logger,
        )

        mock_storage.perform_orca_reconcile.assert_called_once_with(
            mock_report_source,
            mock_report_cursor,
            mock_logger,
        )

        mock_update_job.assert_has_calls([
            call(mock_report_cursor, OrcaStatus.GENERATING_REPORTS, None),
            call(mock_report_cursor, OrcaStatus.SUCCESS, None),
        ])
        self.assertEqual(2, mock_update_job.call_count)

    @patch("src.use_cases.internal_reconcile_generation.InternalReconcileGeneration.update_job")
    def test_perform_orca_reconcile_error_recorded(
        self,
        mock_update_job: MagicMock,
    ):
        """
        If operation fails, should post an error status update.
        """
        mock_report_source = Mock()
        mock_report_cursor = Mock()
        mock_logger = Mock()
        expected_exception = Exception(uuid.uuid4().__str__())

        mock_storage = Mock()
        mock_storage.perform_orca_reconcile = Mock(side_effect=expected_exception)

        with self.assertRaises(Exception) as cm:
            InternalReconcileGeneration(mock_storage).perform_orca_reconcile(
                mock_report_source,
                mock_report_cursor,
                mock_logger,
            )

        self.assertEqual(expected_exception, cm.exception)

        mock_storage.perform_orca_reconcile.assert_called_once_with(
            mock_report_source,
            mock_report_cursor,
            mock_logger,
        )
        mock_update_job.assert_has_calls([
            call(mock_report_cursor, OrcaStatus.GENERATING_REPORTS, None),
            call(mock_report_cursor, OrcaStatus.ERROR, str(expected_exception)),
        ])
        self.assertEqual(2, mock_update_job.call_count)
