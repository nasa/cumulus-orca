import random
import unittest
import uuid
from inspect import getmembers, isabstract
from unittest.mock import MagicMock, Mock, patch

from sqlalchemy.sql.elements import TextClause

from src.adapters.storage import rdbms
from src.adapters.storage.rdbms import StorageAdapterPostgres, StorageAdapterRDBMS
from src.entities.orphan import OrphanRecord, OrphanRecordFilter, OrphanRecordPage


class TestRDBMS(unittest.TestCase):
    @patch("src.adapters.storage.rdbms.StorageAdapterRDBMS.get_orphans_sql")
    @patch("sqlalchemy.engine.create.create_engine")
    def test_get_orphans_page_happy_path(
            self,
            mock_create_engine: MagicMock,
            mock_get_orphans_sql: MagicMock,
    ):
        """
        Should set up an engine, and use it to retrieve a page of orphan reports.
        """
        connection_uri = Mock()
        job_id = Mock()
        page_index = Mock()
        page_size = random.randint(1, 999)  # nosec

        key_path = uuid.uuid4().__str__()
        etag = uuid.uuid4().__str__()
        last_update = random.randint(0, 999999)  # nosec
        size_in_bytes = random.randint(0, 999)  # nosec
        storage_class = uuid.uuid4().__str__()  # nosec

        returned_row0 = {
            "key_path": key_path,
            "etag": etag,
            "last_update": last_update,
            "size_in_bytes": size_in_bytes,
            "storage_class": storage_class
        }
        mock_execute_result = Mock()
        mock_execute_result.mappings = Mock(return_value=[returned_row0])
        mock_execute = Mock()
        mock_execute.return_value = mock_execute_result
        mock_connection = Mock()
        mock_connection.execute = mock_execute
        mock_exit = Mock(return_value=False)
        mock_enter = Mock()
        mock_enter.__enter__ = Mock(return_value=mock_connection)
        mock_enter.__exit__ = mock_exit
        mock_engine = Mock()
        mock_engine.begin = Mock(return_value=mock_enter)
        mock_create_engine.return_value = mock_engine

        storage_adapter = rdbms.StorageAdapterRDBMS(connection_uri)

        mock_create_engine.assert_called_once_with(connection_uri, future=True)

        LOGGER = Mock()

        result = storage_adapter.get_orphans_page(
            OrphanRecordFilter(job_id=job_id, page_index=page_index, page_size=page_size),
            LOGGER
        )

        mock_enter.__enter__.assert_called_once_with()
        mock_execute.assert_called_once_with(
            mock_get_orphans_sql.return_value,
            [
                {
                    "job_id": job_id,
                    "page_index": page_index,
                    "page_size": page_size,
                }
            ],
        )
        mock_execute_result.mappings.assert_called_once_with()
        mock_exit.assert_called_once_with(None, None, None)
        mock_get_orphans_sql.assert_called_once_with()
        self.assertEqual(
            OrphanRecordPage(
                orphans=[
                    OrphanRecord(
                        key_path=key_path,
                        etag=etag,
                        last_update=last_update,
                        size_in_bytes=size_in_bytes,
                        storage_class=storage_class,
                    )
                ],
                another_page=False),
            result
        )

    @patch("src.adapters.storage.rdbms.StorageAdapterPostgres.get_orphans_sql")
    @patch("sqlalchemy.engine.create.create_engine")
    def test_get_orphans_page_no_rows_happy_path(
            self,
            mock_create_engine: MagicMock,
            mock_get_orphans_sql: MagicMock,
    ):
        """
        Should query the db, then return an empty array.
        """
        connection_uri = Mock()
        job_id = Mock()
        page_index = Mock()
        page_size = random.randint(1, 999)  # nosec
        mock_execute_result = Mock()
        mock_execute_result.mappings = Mock(return_value=[])
        mock_execute = Mock()
        mock_execute.return_value = mock_execute_result
        mock_connection = Mock()
        mock_connection.execute = mock_execute
        mock_exit = Mock(return_value=False)
        mock_enter = Mock()
        mock_enter.__enter__ = Mock(return_value=mock_connection)
        mock_enter.__exit__ = mock_exit
        mock_engine = Mock()
        mock_engine.begin = Mock(return_value=mock_enter)
        mock_create_engine.return_value = mock_engine

        storage_adapter = rdbms.StorageAdapterPostgres(connection_uri)
        mock_create_engine.assert_called_once_with(connection_uri, future=True)

        LOGGER = Mock()

        result = storage_adapter.get_orphans_page(
            OrphanRecordFilter(job_id=job_id, page_index=page_index, page_size=page_size),
            LOGGER
        )

        mock_enter.__enter__.assert_called_once_with()
        mock_execute.assert_called_once_with(
            mock_get_orphans_sql.return_value,
            [
                {
                    "job_id": job_id,
                    "page_index": page_index,
                    "page_size": page_size,
                }
            ],
        )
        mock_execute_result.mappings.assert_called_once_with()
        mock_exit.assert_called_once_with(None, None, None)
        mock_get_orphans_sql.assert_called_once_with()
        self.assertEqual(
            OrphanRecordPage(
                orphans=[
                ],
                another_page=False),
            result
        )

    @patch("src.adapters.storage.rdbms.StorageAdapterRDBMS.get_orphans_sql")
    @patch("sqlalchemy.engine.create.create_engine")
    def test_get_orphans_page_extra_results_pages(
            self,
            mock_create_engine: MagicMock,
            mock_get_orphans_sql: MagicMock,
    ):
        """
        If the results exceed page-size,
        should return up to page-size results, and set another_page = True
        """
        connection_uri = Mock()
        job_id = Mock()
        page_index = Mock()
        page_size = 1

        key_path = uuid.uuid4().__str__()
        etag = uuid.uuid4().__str__()
        last_update = random.randint(0, 999999)  # nosec
        size_in_bytes = random.randint(0, 999)  # nosec
        storage_class = uuid.uuid4().__str__()

        returned_row0 = {
            "key_path": key_path,
            "etag": etag,
            "last_update": last_update,
            "size_in_bytes": size_in_bytes,
            "storage_class": storage_class
        }
        returned_row1 = {
            "key_path": uuid.uuid4().__str__(),
            "etag": uuid.uuid4().__str__(),
            "last_update": random.randint(0, 999999),  # nosec
            "size_in_bytes": random.randint(0, 999),  # nosec
            "storage_class": uuid.uuid4().__str__()
        }
        mock_execute_result = Mock()
        mock_execute_result.mappings = Mock(return_value=[returned_row0, returned_row1])
        mock_execute = Mock()
        mock_execute.return_value = mock_execute_result
        mock_connection = Mock()
        mock_connection.execute = mock_execute
        mock_exit = Mock(return_value=False)
        mock_enter = Mock()
        mock_enter.__enter__ = Mock(return_value=mock_connection)
        mock_enter.__exit__ = mock_exit
        mock_engine = Mock()
        mock_engine.begin = Mock(return_value=mock_enter)
        mock_create_engine.return_value = mock_engine

        storage_adapter = rdbms.StorageAdapterRDBMS(connection_uri)
        mock_create_engine.assert_called_once_with(connection_uri, future=True)

        LOGGER = Mock()

        result = storage_adapter.get_orphans_page(
            OrphanRecordFilter(job_id=job_id, page_index=page_index, page_size=page_size),
            LOGGER
        )

        mock_enter.__enter__.assert_called_once_with()
        mock_execute.assert_called_once_with(
            mock_get_orphans_sql.return_value,
            [
                {
                    "job_id": job_id,
                    "page_index": page_index,
                    "page_size": page_size,
                }
            ],
        )
        mock_execute_result.mappings.assert_called_once_with()
        mock_exit.assert_called_once_with(None, None, None)
        mock_get_orphans_sql.assert_called_once_with()
        self.assertEqual(
            OrphanRecordPage(
                orphans=[
                    OrphanRecord(
                        key_path=key_path,
                        etag=etag,
                        last_update=last_update,
                        size_in_bytes=size_in_bytes,
                        storage_class=storage_class,
                    )
                ],
                another_page=True),
            result
        )

    def test_StorageAdapterPostgres_implements_sql(
            self,
    ):
        """
        Should implement the StorageAdapterRDBMS and associated SQL.
        """
        self.assertTrue(issubclass(StorageAdapterPostgres, StorageAdapterRDBMS))

        for name, function in getmembers(StorageAdapterRDBMS, isabstract):
            with self.subTest(function=function):
                implementation = getattr(StorageAdapterPostgres, name)
                self.assertEqual(type(function()), TextClause)
                self.assertEqual(type(implementation()), TextClause)
