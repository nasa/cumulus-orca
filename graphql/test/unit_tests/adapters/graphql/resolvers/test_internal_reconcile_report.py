import unittest
from unittest.mock import MagicMock, Mock, patch

from src.adapters.graphql.resolvers import internal_reconcile_report
from src.entities.internal_reconcile_report import InternalReconcileReportCursor


class TestInternalReconcileReport(unittest.TestCase):
    @patch("src.adapters.graphql.resolvers.internal_reconcile_report.InternalReconcileGeneration")
    def test_create_job_happy_path(
        self,
        mock_use_case: MagicMock,
    ):
        """
        Arguments should be passed along.
        """
        mock_report_source = Mock()
        mock_creation_timestamp = Mock()
        mock_storage_irr = Mock()
        mock_logger = Mock()

        result = \
            internal_reconcile_report.create_job(mock_report_source, mock_creation_timestamp,
                                                 mock_storage_irr, mock_logger)

        mock_use_case.assert_called_once_with(mock_storage_irr)
        mock_use_case.return_value.create_job.assert_called_once_with(
            mock_report_source, mock_creation_timestamp, mock_logger)
        self.assertEqual(mock_use_case.return_value.create_job.return_value, result)

    @patch("src.adapters.graphql.resolvers.internal_reconcile_report"
           ".InternalServerErrorGraphqlType")
    @patch("src.adapters.graphql.resolvers.internal_reconcile_report.InternalReconcileGeneration")
    def test_create_job_error_wrapped(
        self,
        mock_use_case: MagicMock,
        mock_error: MagicMock,
    ):
        """
        When an error is raised, wrap in InternalServerErrorGraphqlType
        """
        mock_report_source = Mock()
        mock_creation_timestamp = Mock()
        mock_storage_irr = Mock()
        mock_logger = Mock()
        mock_exception = Exception()

        mock_use_case.side_effect = mock_exception

        result = \
            internal_reconcile_report.create_job(mock_report_source, mock_creation_timestamp,
                                                 mock_storage_irr, mock_logger)

        mock_use_case.assert_called_once_with(mock_storage_irr)
        mock_use_case.return_value.create_job.assert_not_called()
        mock_error.assert_called_once_with(mock_exception)
        self.assertEqual(mock_error.return_value, result)

    @patch("src.adapters.graphql.resolvers.internal_reconcile_report.InternalReconcileGeneration")
    @patch("src.adapters.graphql.resolvers.internal_reconcile_report.EdgeCursor.decode_cursor")
    def test_update_job_happy_path(
        self,
        mock_decode_cursor: MagicMock,
        mock_use_case: MagicMock,
    ):
        """
        Arguments should be passed along.
        """
        mock_report_cursor = Mock()
        mock_status = Mock()
        mock_error_message = Mock()
        mock_storage_irr = Mock()

        result = \
            internal_reconcile_report.update_job(mock_report_cursor, mock_status,
                                                 mock_error_message,
                                                 mock_storage_irr,
                                                 Mock())

        mock_decode_cursor.assert_called_once_with(mock_report_cursor,
                                                   InternalReconcileReportCursor)
        mock_use_case.assert_called_once_with(mock_storage_irr)
        mock_use_case.return_value.update_job.assert_called_once_with(
            mock_decode_cursor.return_value, mock_status, mock_error_message)
        self.assertEqual(None, result)

    @patch("src.adapters.graphql.resolvers.internal_reconcile_report"
           ".InternalServerErrorGraphqlType")
    @patch("src.adapters.graphql.resolvers.internal_reconcile_report.InternalReconcileGeneration")
    @patch("src.adapters.graphql.resolvers.internal_reconcile_report.EdgeCursor.decode_cursor")
    def test_update_job_error_wrapped(
        self,
        mock_decode_cursor: MagicMock,
        mock_use_case: MagicMock,
        mock_error: MagicMock,
    ):
        """
        When an error is raised, wrap in InternalServerErrorGraphqlType
        """
        mock_report_cursor = Mock()
        mock_status = Mock()
        mock_error_message = Mock()
        mock_storage_irr = Mock()
        mock_exception = Exception()
        mock_logger = Mock()
        mock_logger.error = Mock()

        mock_use_case.side_effect = mock_exception

        result = \
            internal_reconcile_report.update_job(mock_report_cursor, mock_status,
                                                 mock_error_message,
                                                 mock_storage_irr,
                                                 mock_logger)

        mock_decode_cursor.assert_called_once_with(mock_report_cursor,
                                                   InternalReconcileReportCursor)
        mock_use_case.assert_called_once_with(mock_storage_irr)
        mock_use_case.return_value.update_job.assert_not_called()
        mock_error.assert_called_once_with(mock_exception)
        mock_logger.error.assert_called_once_with(mock_exception)
        self.assertEqual(mock_error.return_value, result)

    @patch("src.adapters.graphql.resolvers.internal_reconcile_report.InternalReconcileGeneration")
    @patch("src.adapters.graphql.resolvers.internal_reconcile_report.EdgeCursor.decode_cursor")
    def test_get_current_archive_list_happy_path(
        self,
        mock_decode_cursor: MagicMock,
        mock_use_case: MagicMock,
    ):
        """
        Arguments should be passed along.
        """
        mock_report_source = Mock()
        mock_report_cursor = Mock()
        mock_columns_in_csv = Mock()
        mock_csv_file_locations = Mock()
        mock_report_bucket_region = Mock()
        mock_storage_irr = Mock()
        mock_logger = Mock()

        result = \
            internal_reconcile_report.get_current_archive_list(
                mock_report_source,
                mock_report_cursor,
                mock_columns_in_csv,
                mock_csv_file_locations,
                mock_report_bucket_region,
                mock_storage_irr,
                mock_logger,
            )

        mock_decode_cursor.assert_called_once_with(mock_report_cursor,
                                                   InternalReconcileReportCursor)
        mock_use_case.assert_called_once_with(mock_storage_irr)
        mock_use_case.return_value.get_current_archive_list.assert_called_once_with(
            mock_report_source,
            mock_decode_cursor.return_value,
            mock_columns_in_csv,
            mock_csv_file_locations,
            mock_report_bucket_region,
            mock_logger,
        )
        self.assertEqual(None, result)

    @patch("src.adapters.graphql.resolvers.internal_reconcile_report"
           ".InternalServerErrorGraphqlType")
    @patch("src.adapters.graphql.resolvers.internal_reconcile_report.InternalReconcileGeneration")
    @patch("src.adapters.graphql.resolvers.internal_reconcile_report.EdgeCursor.decode_cursor")
    def test_get_current_archive_list_error_wrapped(
        self,
        mock_decode_cursor: MagicMock,
        mock_use_case: MagicMock,
        mock_error: MagicMock,
    ):
        """
        When an error is raised, wrap in InternalServerErrorGraphqlType
        """
        mock_exception = Exception()
        mock_use_case.side_effect = mock_exception

        mock_report_source = Mock()
        mock_report_cursor = Mock()
        mock_columns_in_csv = Mock()
        mock_csv_file_locations = Mock()
        mock_report_bucket_region = Mock()
        mock_storage_irr = Mock()
        mock_logger = Mock()

        result = \
            internal_reconcile_report.get_current_archive_list(
                mock_report_source,
                mock_report_cursor,
                mock_columns_in_csv,
                mock_csv_file_locations,
                mock_report_bucket_region,
                mock_storage_irr,
                mock_logger,
            )

        mock_decode_cursor.assert_called_once_with(mock_report_cursor,
                                                   InternalReconcileReportCursor)
        mock_use_case.assert_called_once_with(mock_storage_irr)
        mock_use_case.return_value.update_job.assert_not_called()
        mock_error.assert_called_once_with(mock_exception)
        self.assertEqual(mock_error.return_value, result)

    @patch("src.adapters.graphql.resolvers.internal_reconcile_report.InternalReconcileGeneration")
    @patch("src.adapters.graphql.resolvers.internal_reconcile_report.EdgeCursor.decode_cursor")
    def test_perform_orca_reconcile_happy_path(
        self,
        mock_decode_cursor: MagicMock,
        mock_use_case: MagicMock,
    ):
        """
        Arguments should be passed along.
        """
        mock_report_source = Mock()
        mock_report_cursor = Mock()
        mock_storage_irr = Mock()
        mock_logger = Mock()

        result = \
            internal_reconcile_report.perform_orca_reconcile(
                mock_report_source,
                mock_report_cursor,
                mock_storage_irr,
                mock_logger,
            )

        mock_decode_cursor.assert_called_once_with(mock_report_cursor,
                                                   InternalReconcileReportCursor)
        mock_use_case.assert_called_once_with(mock_storage_irr)
        mock_use_case.return_value.perform_orca_reconcile.assert_called_once_with(
            mock_report_source,
            mock_decode_cursor.return_value,
            mock_logger,
        )
        self.assertEqual(None, result)

    @patch("src.adapters.graphql.resolvers.internal_reconcile_report"
           ".InternalServerErrorGraphqlType")
    @patch("src.adapters.graphql.resolvers.internal_reconcile_report.InternalReconcileGeneration")
    def test_perform_orca_reconcile_error_wrapped(
        self,
        mock_use_case: MagicMock,
        mock_error: MagicMock,
    ):
        """
        When an error is raised, wrap in InternalServerErrorGraphqlType
        """
        mock_exception = Exception()
        mock_use_case.side_effect = mock_exception

        mock_report_source = Mock()
        mock_report_cursor = Mock()
        mock_storage_irr = Mock()
        mock_logger = Mock()

        result = \
            internal_reconcile_report.perform_orca_reconcile(
                mock_report_source,
                mock_report_cursor,
                mock_storage_irr,
                mock_logger,
            )

        mock_use_case.assert_called_once_with(mock_storage_irr)
        mock_use_case.return_value.update_job.assert_not_called()
        mock_error.assert_called_once_with(mock_exception)
        self.assertEqual(mock_error.return_value, result)

    @patch("src.adapters.graphql.resolvers.internal_reconcile_report.InternalReconcileReport")
    def test_get_phantom_page_happy_path(
        self,
        mock_use_case: MagicMock,
    ):
        """
        Arguments should be passed along.
        """
        mock_job_id = Mock()
        mock_page_parameters = Mock()
        mock_storage_irr = Mock()
        mock_logger = Mock()

        result = \
            internal_reconcile_report.get_phantom_page(mock_job_id, mock_page_parameters,
                                                       mock_storage_irr, mock_logger)

        mock_use_case.assert_called_once_with(mock_storage_irr)
        mock_use_case.return_value.get_phantom_page.assert_called_once_with(
            mock_job_id, mock_page_parameters, mock_logger)
        self.assertEqual(mock_use_case.return_value.get_phantom_page.return_value, result)

    @patch("src.adapters.graphql.resolvers.internal_reconcile_report"
           ".InternalServerErrorGraphqlType")
    @patch("src.adapters.graphql.resolvers.internal_reconcile_report.InternalReconcileReport")
    def test_get_phantom_page_error_wrapped(
        self,
        mock_use_case: MagicMock,
        mock_error: MagicMock,
    ):
        """
        When an error is raised, wrap in InternalServerErrorGraphqlType
        """
        mock_job_id = Mock()
        mock_page_parameters = Mock()
        mock_storage_irr = Mock()
        mock_logger = Mock()
        mock_exception = Exception()

        mock_use_case.side_effect = mock_exception

        result = \
            internal_reconcile_report.get_phantom_page(mock_job_id, mock_page_parameters,
                                                       mock_storage_irr, mock_logger)

        mock_use_case.assert_called_once_with(mock_storage_irr)
        mock_use_case.return_value.get_phantom_page.assert_not_called()
        mock_error.assert_called_once_with(mock_exception)
        self.assertEqual(mock_error.return_value, result)

    @patch("src.adapters.graphql.resolvers.internal_reconcile_report.InternalReconcileReport")
    def test_get_mismatch_page_happy_path(
        self,
        mock_use_case: MagicMock,
    ):
        """
        Arguments should be passed along.
        """
        mock_job_id = Mock()
        mock_page_parameters = Mock()
        mock_storage_irr = Mock()
        mock_logger = Mock()

        result = \
            internal_reconcile_report.get_mismatch_page(mock_job_id, mock_page_parameters,
                                                        mock_storage_irr, mock_logger)

        mock_use_case.assert_called_once_with(mock_storage_irr)
        mock_use_case.return_value.get_mismatch_page.assert_called_once_with(
            mock_job_id, mock_page_parameters, mock_logger)
        self.assertEqual(mock_use_case.return_value.get_mismatch_page.return_value, result)

    @patch("src.adapters.graphql.resolvers.internal_reconcile_report"
           ".InternalServerErrorGraphqlType")
    @patch("src.adapters.graphql.resolvers.internal_reconcile_report.InternalReconcileReport")
    def test_get_mismatch_page_error_wrapped(
        self,
        mock_use_case: MagicMock,
        mock_error: MagicMock,
    ):
        """
        When an error is raised, wrap in InternalServerErrorGraphqlType
        """
        mock_job_id = Mock()
        mock_page_parameters = Mock()
        mock_storage_irr = Mock()
        mock_logger = Mock()
        mock_exception = Exception()

        mock_use_case.side_effect = mock_exception

        result = \
            internal_reconcile_report.get_mismatch_page(mock_job_id, mock_page_parameters,
                                                        mock_storage_irr, mock_logger)

        mock_use_case.assert_called_once_with(mock_storage_irr)
        mock_use_case.return_value.get_mismatch_page.assert_not_called()
        mock_error.assert_called_once_with(mock_exception)
        self.assertEqual(mock_error.return_value, result)
