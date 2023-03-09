import random
import unittest
import uuid
from unittest.mock import MagicMock, Mock, patch, call

from orca_shared.reconciliation import OrcaStatus

from src.adapters.storage.internal_reconciliation_rdbms import \
    InternalReconciliationStorageAdapterRDBMS
from src.adapters.storage.internal_reconciliation_s3 import AWSS3FileLocation
from src.entities.common import DirectionEnum
from src.entities.internal_reconcile_report import Mismatch, Phantom, InternalReconcileReportCursor


class TestInternalReconciliationStorageAdapterRDBMS(unittest.TestCase):
    @patch("src.adapters.storage.internal_reconciliation_rdbms."
           "InternalReconciliationStorageAdapterRDBMS.create_job_sql")
    @patch("src.adapters.storage.internal_reconciliation_rdbms.create_engine")
    def test_create_job_happy_path(
        self,
        mock_create_engine: MagicMock,
        mock_create_job_sql: MagicMock,
    ):
        """
        Happy path for creating job.
        """
        mock_logger = Mock()

        mock_user_connection_uri = Mock()
        mock_admin_connection_uri = Mock()
        mock_s3_access_key = Mock()
        mock_s3_secret_key = Mock()

        mock_orca_archive_location = Mock()
        mock_inventory_creation_time = Mock()
        mock_job_id = random.randint(0, 9999999)  # nosec
        returned_rows = Mock()
        returned_rows.fetchone = Mock(return_value={"id": mock_job_id})
        mock_execute = Mock(return_value=returned_rows)
        mock_connection = Mock()
        mock_connection.execute = mock_execute
        mock_exit = Mock(return_value=False)
        mock_enter = Mock()
        mock_enter.__enter__ = Mock(return_value=mock_connection)
        mock_enter.__exit__ = mock_exit
        mock_engine = Mock()
        mock_engine.begin = Mock(return_value=mock_enter)
        mock_create_engine.side_effect = [mock_engine, Mock()]

        adapter = InternalReconciliationStorageAdapterRDBMS(
            mock_user_connection_uri,
            mock_admin_connection_uri,
            mock_s3_access_key,
            mock_s3_secret_key,
        )

        result = adapter.create_job(
            mock_orca_archive_location, mock_inventory_creation_time, mock_logger
        )
        self.assertEqual(mock_job_id, result.job_id)

        mock_create_engine.assert_has_calls([
            call(mock_user_connection_uri, future=True),
            call(mock_admin_connection_uri, future=True)
        ])
        self.assertEqual(2, mock_create_engine.call_count)
        self.assertEqual(mock_engine, adapter.user_engine)

        mock_enter.__enter__.assert_called_once_with()
        mock_execute.assert_called_once_with(
            mock_create_job_sql.return_value,
            [
                {
                    "orca_archive_location": mock_orca_archive_location,
                    "inventory_creation_time": mock_inventory_creation_time,
                    "status_id": OrcaStatus.GETTING_S3_LIST.value,
                    "start_time": unittest.mock.ANY,
                    "last_update": unittest.mock.ANY,
                    "end_time": None,
                    "error_message": None,
                }
            ],
        )
        mock_exit.assert_called_once_with(None, None, None)
        mock_create_job_sql.assert_called_once_with()

    @patch("src.adapters.storage.internal_reconciliation_rdbms."
           "InternalReconciliationStorageAdapterRDBMS.update_job_with_s3_inventory")
    @patch("src.adapters.storage.internal_reconciliation_rdbms."
           "InternalReconciliationStorageAdapterRDBMS.truncate_s3_partition")
    @patch("src.adapters.storage.internal_reconciliation_rdbms.create_engine")
    def test_pull_in_inventory_report_happy_path(
        self,
        mock_create_engine: MagicMock,
        mock_truncate_s3_partition: MagicMock,
        mock_update_job_with_s3_inventory: MagicMock,
    ):
        """
        Performs calls in sequence.
        """
        mock_user_connection_uri = Mock()
        mock_admin_connection_uri = Mock()
        mock_s3_access_key = Mock()
        mock_s3_secret_key = Mock()

        adapter = InternalReconciliationStorageAdapterRDBMS(
            mock_user_connection_uri,
            mock_admin_connection_uri,
            mock_s3_access_key,
            mock_s3_secret_key,
        )

        mock_create_engine.assert_has_calls([
            call(mock_user_connection_uri, future=True),
            call(mock_admin_connection_uri, future=True)
        ])
        self.assertEqual(2, mock_create_engine.call_count)

        mock_report_source = Mock()
        mock_report_cursor = Mock()
        mock_columns_in_csv = Mock()
        mock_csv_file_locations = Mock()
        mock_report_bucket_region = Mock()
        mock_logger = Mock()

        adapter.pull_in_inventory_report(
            mock_report_source,
            mock_report_cursor,
            mock_columns_in_csv,
            mock_csv_file_locations,
            mock_report_bucket_region,
            mock_logger,
        )

        mock_truncate_s3_partition.assert_called_once_with(mock_report_source, mock_logger)
        mock_update_job_with_s3_inventory.assert_called_once_with(
            mock_report_cursor,
            mock_columns_in_csv,
            mock_csv_file_locations,
            mock_report_bucket_region,
            mock_logger,
        )

    @patch("src.adapters.storage.internal_reconciliation_rdbms."
           "InternalReconciliationStorageAdapterRDBMS.truncate_s3_partition_sql")
    @patch("src.adapters.storage.internal_reconciliation_rdbms."
           "get_partition_name_from_bucket_name")
    @patch("src.adapters.storage.internal_reconciliation_rdbms.create_engine")
    def test_truncate_s3_partition_happy_path(
        self,
        mock_create_engine: MagicMock,
        mock_get_partition_name_from_bucket_name: MagicMock,
        mock_truncate_s3_partition_sql: MagicMock,
    ):
        """
        Happy path.
        """
        mock_logger = Mock()

        mock_user_connection_uri = Mock()
        mock_admin_connection_uri = Mock()
        mock_s3_access_key = Mock()
        mock_s3_secret_key = Mock()

        mock_orca_archive_location = Mock()
        mock_execute = Mock()
        mock_connection = Mock()
        mock_connection.execute = mock_execute
        mock_exit = Mock(return_value=False)
        mock_enter = Mock()
        mock_enter.__enter__ = Mock(return_value=mock_connection)
        mock_enter.__exit__ = mock_exit
        mock_engine = Mock()
        mock_engine.begin = Mock(return_value=mock_enter)
        mock_create_engine.side_effect = [Mock(), mock_engine]

        adapter = InternalReconciliationStorageAdapterRDBMS(
            mock_user_connection_uri,
            mock_admin_connection_uri,
            mock_s3_access_key,
            mock_s3_secret_key,
        )

        adapter.truncate_s3_partition(
            mock_orca_archive_location, mock_logger
        )

        mock_create_engine.assert_has_calls([
            call(mock_user_connection_uri, future=True),
            call(mock_admin_connection_uri, future=True)
        ])
        self.assertEqual(2, mock_create_engine.call_count)
        self.assertEqual(mock_engine, adapter.admin_engine)

        mock_get_partition_name_from_bucket_name \
            .assert_called_once_with(mock_orca_archive_location)
        mock_enter.__enter__.assert_called_once_with()
        mock_execute.assert_called_once_with(
            mock_truncate_s3_partition_sql.return_value,
            [
                {
                }
            ],
        )
        mock_exit.assert_called_once_with(None, None, None)
        mock_truncate_s3_partition_sql.assert_called_once_with(
            mock_get_partition_name_from_bucket_name.return_value)

    @patch("src.adapters.storage.internal_reconciliation_rdbms."
           "orca_shared.reconciliation.update_job")
    @patch("src.adapters.storage.internal_reconciliation_rdbms.create_engine")
    def test_update_job_happy_path(
        self,
        mock_create_engine: MagicMock,
        mock_update_job: MagicMock,
    ):
        mock_user_connection_uri = Mock()
        mock_admin_connection_uri = Mock()
        mock_s3_access_key = Mock()
        mock_s3_secret_key = Mock()

        adapter = InternalReconciliationStorageAdapterRDBMS(
            mock_user_connection_uri,
            mock_admin_connection_uri,
            mock_s3_access_key,
            mock_s3_secret_key,
        )

        job_id = random.randint(0, 9999999999)  # nosec
        report_cursor = InternalReconcileReportCursor(job_id=job_id)
        mock_status = Mock()
        mock_error_message = Mock()

        adapter.update_job(
            report_cursor,
            mock_status,
            mock_error_message,
        )

        mock_create_engine.assert_has_calls([
            call(mock_user_connection_uri, future=True),
            call(mock_admin_connection_uri, future=True)
        ])
        self.assertEqual(2, mock_create_engine.call_count)

        mock_update_job.assert_called_once_with(
            job_id,
            mock_status,
            mock_error_message,
            adapter.user_engine,
        )

    @patch("src.adapters.storage.internal_reconciliation_rdbms."
           "InternalReconciliationStorageAdapterRDBMS.update_job")
    @patch("src.adapters.storage.internal_reconciliation_rdbms."
           "InternalReconciliationStorageAdapterRDBMS.translate_s3_import_to_partitioned_data_sql")
    @patch("src.adapters.storage.internal_reconciliation_rdbms."
           "InternalReconciliationStorageAdapterRDBMS.trigger_csv_load_from_s3_sql")
    @patch("src.adapters.storage.internal_reconciliation_rdbms."
           "InternalReconciliationStorageAdapterRDBMS.create_temporary_table_sql")
    @patch("src.adapters.storage.internal_reconciliation_rdbms."
           "InternalReconciliationStorageAdapterRDBMS.generate_temporary_s3_column_list")
    @patch("src.adapters.storage.internal_reconciliation_rdbms.create_engine")
    def test_update_job_with_s3_inventory_happy_path(
        self,
        mock_create_engine: MagicMock,
        mock_generate_temporary_s3_column_list: MagicMock,
        mock_create_temporary_table_sql: MagicMock,
        mock_trigger_csv_load_from_s3_sql: MagicMock,
        mock_translate_s3_import_to_partitioned_data_sql: MagicMock,
        mock_update_job: MagicMock,
    ):
        """
        Happy path for pulling s3 inventory csv into postgres.
        Should perform each operation in a single transaction.
        """
        mock_logger = Mock()

        mock_user_connection_uri = Mock()
        mock_admin_connection_uri = Mock()
        mock_s3_access_key = Mock()
        mock_s3_secret_key = Mock()

        mock_report_bucket_name = uuid.uuid4().__str__()
        mock_report_bucket_region = Mock()
        csv_file_locations = [
            AWSS3FileLocation(
                bucket_name=mock_report_bucket_name,
                key=uuid.uuid4().__str__() + ".csv.gz",
            ),
            AWSS3FileLocation(
                bucket_name=mock_report_bucket_name,
                key=uuid.uuid4().__str__() + ".csv.gz",
            ),
        ]
        mock_job_id = random.randint(0, 999999999999)
        report_cursor = InternalReconcileReportCursor(mock_job_id)
        mock_columns_in_csv = Mock()
        mock_execute = Mock()
        mock_connection = Mock()
        mock_connection.execute = mock_execute
        mock_exit = Mock(return_value=False)
        mock_enter = Mock()
        mock_enter.__enter__ = Mock(return_value=mock_connection)
        mock_enter.__exit__ = mock_exit
        mock_engine = Mock()
        mock_engine.begin = Mock(return_value=mock_enter)
        mock_create_engine.side_effect = [Mock(), mock_engine]

        adapter = InternalReconciliationStorageAdapterRDBMS(
            mock_user_connection_uri,
            mock_admin_connection_uri,
            mock_s3_access_key,
            mock_s3_secret_key,
        )

        adapter.update_job_with_s3_inventory(
            report_cursor,
            mock_columns_in_csv,
            csv_file_locations,
            mock_report_bucket_region,
            mock_logger,
        )

        mock_create_engine.assert_has_calls([
            call(mock_user_connection_uri, future=True),
            call(mock_admin_connection_uri, future=True)
        ])
        self.assertEqual(2, mock_create_engine.call_count)
        self.assertEqual(mock_engine, adapter.admin_engine)

        mock_generate_temporary_s3_column_list.assert_called_once_with(
            mock_columns_in_csv
        )
        mock_enter.__enter__.assert_called_once_with()
        mock_trigger_csv_load_from_s3_sql.assert_has_calls(
            [call() for mock_csv_file_location in csv_file_locations]
        )
        self.assertEqual(
            len(csv_file_locations), mock_trigger_csv_load_from_s3_sql.call_count
        )
        mock_translate_s3_import_to_partitioned_data_sql.assert_called_once_with()
        mock_update_job.assert_called_once_with(
            report_cursor,
            OrcaStatus.STAGED,
            None,
        )
        mock_execute.assert_has_calls(
            [
                call(mock_create_temporary_table_sql.return_value, [{}]),
            ]
        )
        mock_execute.assert_has_calls(
            [
                call(
                    mock_trigger_csv_load_from_s3_sql.return_value,
                    [
                        {
                            "report_bucket_name": csv_file_location.bucket_name,
                            "csv_key_path": csv_file_location.key,
                            "report_bucket_region": mock_report_bucket_region,
                            "s3_access_key": mock_s3_access_key,
                            "s3_secret_key": mock_s3_secret_key,
                        }
                    ],
                )
                for csv_file_location in csv_file_locations
            ]
        )
        mock_execute.assert_has_calls(
            [
                call(
                    mock_translate_s3_import_to_partitioned_data_sql.return_value,
                    [{"job_id": mock_job_id}],
                )
            ]
        )
        self.assertEqual(len(csv_file_locations) + 2, mock_execute.call_count)
        mock_exit.assert_called_once_with(None, None, None)

    def test_generate_temporary_s3_column_list_happy_path(self):
        """
        Should properly translate columns to orca DB format.
        Must add extra columns for extra columns.
        """
        result = InternalReconciliationStorageAdapterRDBMS.generate_temporary_s3_column_list(
            ["IsDeleteMarker", "StorageClass", "blah", "Size", "Key",
             "IsLatest", "Extra", "Bucket", "LastModifiedDate", "ETag"]
        )
        self.assertEqual(
            "delete_marker bool, storage_class text, junk2 text, "
            "size_in_bytes bigint, key_path text, is_latest bool, "
            "junk6 text, orca_archive_location text, last_update timestamptz, etag text",
            result,
        )

    @patch("src.adapters.storage.internal_reconciliation_rdbms."
           "InternalReconciliationStorageAdapterRDBMS.generate_mismatch_reports_sql")
    @patch("src.adapters.storage.internal_reconciliation_rdbms."
           "InternalReconciliationStorageAdapterRDBMS.generate_orphan_reports_sql")
    @patch("src.adapters.storage.internal_reconciliation_rdbms."
           "InternalReconciliationStorageAdapterRDBMS.generate_phantom_reports_sql")
    @patch("src.adapters.storage.internal_reconciliation_rdbms.create_engine")
    def test_perform_orca_reconcile_happy_path(
        self,
        mock_create_engine: MagicMock,
        mock_generate_phantom_reports_sql: MagicMock,
        mock_generate_orphan_reports_sql: MagicMock,
        mock_generate_mismatch_reports_sql: MagicMock,
    ):
        """

        """
        mock_logger = Mock()

        mock_user_connection_uri = Mock()
        mock_admin_connection_uri = Mock()
        mock_s3_access_key = Mock()
        mock_s3_secret_key = Mock()

        mock_job_id = random.randint(0, 99999999)  # nosec
        mock_orca_archive_location = Mock()
        mock_execute = Mock()
        mock_connection = Mock()
        mock_connection.execute = mock_execute
        mock_exit = Mock(return_value=False)
        mock_enter = Mock()
        mock_enter.__enter__ = Mock(return_value=mock_connection)
        mock_enter.__exit__ = mock_exit
        mock_engine = Mock()
        mock_engine.begin = Mock(return_value=mock_enter)
        mock_create_engine.side_effect = [mock_engine, Mock()]

        adapter = InternalReconciliationStorageAdapterRDBMS(
            mock_user_connection_uri,
            mock_admin_connection_uri,
            mock_s3_access_key,
            mock_s3_secret_key,
        )
        adapter.perform_orca_reconcile(
            mock_orca_archive_location,
            InternalReconcileReportCursor(mock_job_id),
            mock_logger,
        )

        mock_enter.__enter__.assert_called_once_with()

        mock_generate_phantom_reports_sql.assert_called_once_with()
        mock_execute.assert_has_calls(
            [
                call(
                    mock_generate_phantom_reports_sql.return_value,
                    [
                        {
                            "job_id": mock_job_id,
                            "orca_archive_location": mock_orca_archive_location,
                        }
                    ],
                ),
                call(
                    mock_generate_orphan_reports_sql.return_value,
                    [
                        {
                            "job_id": mock_job_id,
                            "orca_archive_location": mock_orca_archive_location,
                        }
                    ],
                ),
                call(
                    mock_generate_mismatch_reports_sql.return_value,
                    [
                        {
                            "job_id": mock_job_id,
                            "orca_archive_location": mock_orca_archive_location,
                        }
                    ],
                ),
            ]
        )
        self.assertEqual(3, mock_execute.call_count)

        mock_generate_orphan_reports_sql.assert_called_once_with()

        mock_generate_mismatch_reports_sql.assert_called_once_with()

        mock_exit.assert_called_once_with(None, None, None)

    @patch("src.adapters.storage.internal_reconciliation_rdbms."
           "InternalReconciliationStorageAdapterRDBMS.get_phantom_page_sql")
    @patch("src.adapters.storage.internal_reconciliation_rdbms.create_engine")
    def test_get_phantom_page_next_page(
        self,
        mock_create_engine: MagicMock,
        mock_get_phantom_page_sql: MagicMock,
    ):
        """
        Happy path for getting the next or previous page of results.
        """
        for direction in [DirectionEnum.next, DirectionEnum.previous]:
            with self.subTest(direction=direction):
                mock_user_connection_uri = Mock()
                mock_admin_connection_uri = Mock()
                mock_s3_access_key = Mock()
                mock_s3_secret_key = Mock()

                mock_job_id = Mock()
                mock_cursor_collection_id = Mock()
                mock_cursor_granule_id = Mock()
                mock_cursor_key_path = Mock()
                mock_limit = Mock()
                mock_logger = Mock()

                phantoms = []
                rows = []
                for i in range(0, 3):
                    phantom = Phantom(
                        job_id=random.randint(0, 10000),  # nosec
                        collection_id=uuid.uuid4().__str__(),
                        granule_id=uuid.uuid4().__str__(),
                        filename=uuid.uuid4().__str__(),
                        key_path=uuid.uuid4().__str__(),
                        orca_etag=uuid.uuid4().__str__(),
                        orca_granule_last_update=random.randint(0, 10000),  # nosec
                        orca_size_in_bytes=random.randint(0, 10000),  # nosec
                        orca_storage_class=uuid.uuid4().__str__(),
                    )
                    phantoms.append(phantom)
                    rows.append(
                        {
                            "job_id": phantom.job_id,
                            "collection_id": phantom.collection_id,
                            "granule_id": phantom.granule_id,
                            "filename": phantom.filename,
                            "key_path": phantom.key_path,
                            "orca_etag": phantom.orca_etag,
                            "orca_last_update": phantom.orca_granule_last_update,
                            "orca_size_in_bytes": phantom.orca_size_in_bytes,
                            "orca_storage_class": phantom.orca_storage_class,
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
                mock_create_engine.side_effect = [mock_engine, Mock()]

                adapter = InternalReconciliationStorageAdapterRDBMS(
                    mock_user_connection_uri,
                    mock_admin_connection_uri,
                    mock_s3_access_key,
                    mock_s3_secret_key,
                )

                result = adapter.get_phantom_page(
                    mock_job_id, mock_cursor_collection_id, mock_cursor_granule_id,
                    mock_cursor_key_path,
                    direction, mock_limit, mock_logger
                )
                self.assertEqual(phantoms, result)

                mock_create_engine.assert_has_calls([
                    call(mock_user_connection_uri, future=True),
                    call(mock_admin_connection_uri, future=True)
                ])
                self.assertEqual(2, mock_create_engine.call_count)
                self.assertEqual(mock_engine, adapter.user_engine)
                mock_enter.__enter__.assert_called_once_with()
                mock_execute.assert_called_once_with(
                    mock_get_phantom_page_sql.return_value,
                    [{
                        "job_id": mock_job_id,
                        "cursor_collection_id": mock_cursor_collection_id,
                        "cursor_granule_id": mock_cursor_granule_id,
                        "cursor_key_path": mock_cursor_key_path,
                        "limit": mock_limit,
                    }],
                )
                mock_exit.assert_called_once_with(None, None, None)
                mock_get_phantom_page_sql.assert_called_once_with(direction)
            mock_create_engine.reset_mock()
            mock_get_phantom_page_sql.reset_mock()

    @patch("src.adapters.storage.internal_reconciliation_rdbms."
           "InternalReconciliationStorageAdapterRDBMS.get_mismatch_page_sql")
    @patch("src.adapters.storage.internal_reconciliation_rdbms.create_engine")
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
                mock_admin_connection_uri = Mock()
                mock_s3_access_key = Mock()
                mock_s3_secret_key = Mock()

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
                        job_id=random.randint(0, 10000),  # nosec
                        collection_id=uuid.uuid4().__str__(),
                        granule_id=uuid.uuid4().__str__(),
                        filename=uuid.uuid4().__str__(),
                        key_path=uuid.uuid4().__str__(),
                        cumulus_archive_location=uuid.uuid4().__str__(),
                        orca_etag=uuid.uuid4().__str__(),
                        s3_etag=uuid.uuid4().__str__(),
                        orca_granule_last_update=random.randint(0, 10000),  # nosec
                        s3_file_last_update=random.randint(0, 10000),  # nosec
                        orca_size_in_bytes=random.randint(0, 10000),  # nosec
                        s3_size_in_bytes=random.randint(0, 10000),  # nosec
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
                            "orca_last_update": mismatch.orca_granule_last_update,
                            "s3_last_update": mismatch.s3_file_last_update,
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
                mock_create_engine.side_effect = [mock_engine, Mock()]

                adapter = InternalReconciliationStorageAdapterRDBMS(
                    mock_user_connection_uri,
                    mock_admin_connection_uri,
                    mock_s3_access_key,
                    mock_s3_secret_key,
                )

                result = adapter.get_mismatch_page(
                    mock_job_id, mock_cursor_collection_id, mock_cursor_granule_id,
                    mock_cursor_key_path,
                    direction, mock_limit, mock_logger
                )
                self.assertEqual(mismatches, result)

                mock_create_engine.assert_has_calls([
                    call(mock_user_connection_uri, future=True),
                    call(mock_admin_connection_uri, future=True)
                ])
                self.assertEqual(2, mock_create_engine.call_count)
                self.assertEqual(mock_engine, adapter.user_engine)
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
