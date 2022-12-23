import unittest
from unittest.mock import Mock

from src.use_cases.internal_reconcile_report import InternalReconcileReport


class MyTestCase(unittest.TestCase):
    def test_get_mismatch_page_happy_path(
        self
    ):
        """
        Happy path of getting a page of results from the database and returning the page.
        """
        mock_storage = Mock()
        mock_job_id = Mock()
        mock_page_parameters = Mock()
        mock_logger = Mock()
        InternalReconcileReport(mock_storage)\
            .get_mismatch_page(mock_job_id, mock_page_parameters, mock_logger)
