import unittest
from unittest.mock import MagicMock, Mock, patch

from src.adapters.graphql.resolvers import internal_reconcile_report


class TestInternalReconcileReport(unittest.TestCase):
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
