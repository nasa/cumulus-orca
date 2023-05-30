import unittest
from unittest.mock import MagicMock, Mock, call, patch

from src.entities.internal_reconcile_report import Mismatch, Phantom
from src.use_cases.internal_reconcile_report import InternalReconcileReport


class MyTestCase(unittest.TestCase):
    @patch("src.use_cases.internal_reconcile_report.dataclasses.asdict")
    @patch("src.use_cases.internal_reconcile_report.EdgeCursor.encode_cursor")
    @patch("src.use_cases.internal_reconcile_report.EdgeCursor.decode_cursor")
    def test_get_phantom_page_happy_path(
        self,
        mock_decode_cursor: MagicMock,
        mock_encode_cursor: MagicMock,
        mock_asdict: MagicMock,
    ):
        """
        Happy path of getting a page of results from the database and returning the page.
        """
        mock_dict0 = {"key": Mock()}
        mock_dict1 = {"key": Mock()}
        mock_asdict.side_effect = [mock_dict0, mock_dict1]

        mock_start_cursor = Mock()
        mock_end_cursor = Mock()
        mock_encode_cursor.side_effect = [mock_start_cursor, mock_end_cursor]

        phantom0 = Mock()
        phantom1 = Mock()
        phantoms = [phantom0, phantom1]
        mock_storage_get_phantom_page = Mock(return_value=phantoms)
        mock_storage = Mock()
        mock_storage.get_phantom_page = mock_storage_get_phantom_page
        mock_job_id = Mock()
        mock_page_parameters = Mock()
        mock_logger = Mock()

        result = InternalReconcileReport(mock_storage)\
            .get_phantom_page(mock_job_id, mock_page_parameters, mock_logger)

        mock_decode_cursor.assert_called_once_with(mock_page_parameters.cursor, Phantom.Cursor)
        mock_storage_get_phantom_page.assert_called_once_with(
            mock_job_id,
            mock_decode_cursor.return_value.collection_id,
            mock_decode_cursor.return_value.granule_id,
            mock_decode_cursor.return_value.key_path,
            mock_page_parameters.direction,
            mock_page_parameters.limit,
            mock_logger,
        )

        mock_asdict.assert_has_calls([
            call(phantom0.get_cursor()),
            call(phantom1.get_cursor()),
        ])
        self.assertEqual(2, mock_asdict.call_count)
        mock_encode_cursor.assert_has_calls([
            call(**mock_dict0),
            call(**mock_dict1),
        ])
        self.assertEqual(2, mock_encode_cursor.call_count)

        self.assertEqual([phantom0, phantom1], result.items)
        self.assertEqual(mock_start_cursor, result.start_cursor)
        self.assertEqual(mock_end_cursor, result.end_cursor)

    @patch("src.use_cases.internal_reconcile_report.dataclasses.asdict")
    @patch("src.use_cases.internal_reconcile_report.EdgeCursor.encode_cursor")
    @patch("src.use_cases.internal_reconcile_report.EdgeCursor.decode_cursor")
    def test_get_mismatch_page_happy_path(
        self,
        mock_decode_cursor: MagicMock,
        mock_encode_cursor: MagicMock,
        mock_asdict: MagicMock,
    ):
        """
        Happy path of getting a page of results from the database and returning the page.
        """
        mock_dict0 = {"key": Mock()}
        mock_dict1 = {"key": Mock()}
        mock_asdict.side_effect = [mock_dict0, mock_dict1]

        mock_start_cursor = Mock()
        mock_end_cursor = Mock()
        mock_encode_cursor.side_effect = [mock_start_cursor, mock_end_cursor]

        mismatch0 = Mock()
        mismatch1 = Mock()
        mismatches = [mismatch0, mismatch1]
        mock_storage_get_mismatch_page = Mock(return_value=mismatches)
        mock_storage = Mock()
        mock_storage.get_mismatch_page = mock_storage_get_mismatch_page
        mock_job_id = Mock()
        mock_page_parameters = Mock()
        mock_logger = Mock()

        result = InternalReconcileReport(mock_storage)\
            .get_mismatch_page(mock_job_id, mock_page_parameters, mock_logger)

        mock_decode_cursor.assert_called_once_with(mock_page_parameters.cursor, Mismatch.Cursor)
        mock_storage_get_mismatch_page.assert_called_once_with(
            mock_job_id,
            mock_decode_cursor.return_value.collection_id,
            mock_decode_cursor.return_value.granule_id,
            mock_decode_cursor.return_value.key_path,
            mock_page_parameters.direction,
            mock_page_parameters.limit,
            mock_logger,
        )

        mock_asdict.assert_has_calls([
            call(mismatch0.get_cursor()),
            call(mismatch1.get_cursor()),
        ])
        self.assertEqual(2, mock_asdict.call_count)
        mock_encode_cursor.assert_has_calls([
            call(**mock_dict0),
            call(**mock_dict1),
        ])
        self.assertEqual(2, mock_encode_cursor.call_count)

        self.assertEqual([mismatch0, mismatch1], result.items)
        self.assertEqual(mock_start_cursor, result.start_cursor)
        self.assertEqual(mock_end_cursor, result.end_cursor)
