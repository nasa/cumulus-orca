import unittest
from unittest.mock import MagicMock, Mock, patch

from src.adapters.graphql.schemas.queries import Queries


class TestQueries(unittest.TestCase):

    @patch("src.adapters.graphql.schemas.queries.get_phantom_page")
    def test_get_phantom_page_happy_path(
        self,
        mock_get_phantom_page: MagicMock,
    ):
        """
        Parameters should be passed along.
        """
        mock_adapters_storage = MagicMock()

        mock_job_id = Mock()
        mock_page_parameters = Mock()

        # graphql limitations make construction interesting.
        Queries.adapters_storage = mock_adapters_storage
        queries = Queries(adapters_storage=mock_adapters_storage)

        result = queries.get_phantom_page(mock_job_id, mock_page_parameters)

        mock_get_phantom_page.assert_called_once_with(
            mock_job_id, mock_page_parameters,
            mock_adapters_storage.storage_internal_reconciliation,
            mock_adapters_storage.logger_provider.get_logger.return_value
        )
        self.assertEqual(mock_get_phantom_page.return_value, result)

    @patch("src.adapters.graphql.schemas.queries.get_mismatch_page")
    def test_get_mismatch_page_happy_path(
        self,
        mock_get_mismatch_page: MagicMock,
    ):
        """
        Parameters should be passed along.
        """
        mock_adapters_storage = MagicMock()

        mock_job_id = Mock()
        mock_page_parameters = Mock()

        # graphql limitations make construction interesting.
        Queries.adapters_storage = mock_adapters_storage
        queries = Queries(adapters_storage=mock_adapters_storage)

        result = queries.get_mismatch_page(mock_job_id, mock_page_parameters)

        mock_get_mismatch_page.assert_called_once_with(
            mock_job_id, mock_page_parameters,
            mock_adapters_storage.storage_internal_reconciliation,
            mock_adapters_storage.logger_provider.get_logger.return_value
        )
        self.assertEqual(mock_get_mismatch_page.return_value, result)
