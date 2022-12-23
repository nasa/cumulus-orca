import random
import unittest
import uuid
from unittest.mock import patch, MagicMock, Mock

from src.adapters.storage.rdbms import StorageAdapterRDBMS
from src.entities.common import DirectionEnum
from src.entities.internal_reconcile_report import Mismatch


@patch("src.adapters.storage.rdbms.StorageAdapterRDBMS.get_mismatch_page_sql")
@patch("src.adapters.storage.rdbms.create_engine")
class TestRDBMS(unittest.TestCase):
    def test_get_mismatch_page_next_page(
        self,
        mock_create_engine: MagicMock,
        mock_get_mismatch_page_sql: MagicMock,
    ):
        """
        Happy path for getting the next or previous page of results.
        """
        for direction in [DirectionEnum.next, DirectionEnum.previous]:
            with self.subTest(direction=direction):
                mock_user_connection_uri = Mock()

                mock_job_id = Mock()
                mock_cursor_collection_id = Mock()
                mock_cursor_granule_id = Mock()
                mock_cursor_key_path = Mock()
                mock_limit = Mock()
                mock_logger = Mock()

                mismatches = []
                rows = []
                for i in range(0, 3):
                    mismatch = Mismatch(
                        job_id=random.randint(0, 10000),
                        collection_id=uuid.uuid4().__str__(),
                        granule_id=uuid.uuid4().__str__(),
                        filename=uuid.uuid4().__str__(),
                        key_path=uuid.uuid4().__str__(),
                        cumulus_archive_location=uuid.uuid4().__str__(),
                        orca_etag=uuid.uuid4().__str__(),
                        s3_etag=uuid.uuid4().__str__(),
                        orca_last_update=random.randint(0, 10000),
                        s3_last_update=random.randint(0, 10000),
                        orca_size_in_bytes=random.randint(0, 10000),
                        s3_size_in_bytes=random.randint(0, 10000),
                        orca_storage_class=uuid.uuid4().__str__(),
                        s3_storage_class=uuid.uuid4().__str__(),
                        discrepancy_type=uuid.uuid4().__str__(),
                        comment=uuid.uuid4().__str__(),
                    )
                    mismatches.append(mismatch)
                    rows.append(
                        {
                            "job_id": mismatch.job_id,
                            "collection_id": mismatch.collection_id,
                            "granule_id": mismatch.granule_id,
                            "filename": mismatch.filename,
                            "key_path": mismatch.key_path,
                            "cumulus_archive_location": mismatch.cumulus_archive_location,
                            "orca_etag": mismatch.orca_etag,
                            "s3_etag": mismatch.s3_etag,
                            "orca_last_update": mismatch.orca_last_update,
                            "s3_last_update": mismatch.s3_last_update,
                            "orca_size_in_bytes": mismatch.orca_size_in_bytes,
                            "s3_size_in_bytes": mismatch.s3_size_in_bytes,
                            "orca_storage_class": mismatch.orca_storage_class,
                            "s3_storage_class": mismatch.s3_storage_class,
                            "discrepancy_type": mismatch.discrepancy_type,
                            "comment": mismatch.comment
                        }
                    )
                if direction == DirectionEnum.previous:
                    rows.reverse()
                mock_execute = Mock(return_value=rows)
                mock_connection = Mock()
                mock_connection.execute = mock_execute
                mock_exit = Mock(return_value=False)
                mock_enter = Mock()
                mock_enter.__enter__ = Mock(return_value=mock_connection)
                mock_enter.__exit__ = mock_exit
                mock_engine = Mock()
                mock_engine.begin = Mock(return_value=mock_enter)
                mock_create_engine.return_value = mock_engine

                adapter = StorageAdapterRDBMS(mock_user_connection_uri)

                result = adapter.get_mismatch_page(
                    mock_job_id, mock_cursor_collection_id, mock_cursor_granule_id,
                    mock_cursor_key_path,
                    direction, mock_limit, mock_logger
                )
                self.assertEqual(mismatches, result)

                mock_create_engine.assert_called_once_with(mock_user_connection_uri, future=True)
                mock_enter.__enter__.assert_called_once_with()
                mock_execute.assert_called_once_with(
                    mock_get_mismatch_page_sql.return_value,
                    [{
                        "job_id": mock_job_id,
                        "cursor_collection_id": mock_cursor_collection_id,
                        "cursor_granule_id": mock_cursor_granule_id,
                        "cursor_key_path": mock_cursor_key_path,
                        "limit": mock_limit,
                    }],
                )
                mock_exit.assert_called_once_with(None, None, None)
                mock_get_mismatch_page_sql.assert_called_once_with(direction)
            mock_create_engine.reset_mock()
            mock_get_mismatch_page_sql.reset_mock()
