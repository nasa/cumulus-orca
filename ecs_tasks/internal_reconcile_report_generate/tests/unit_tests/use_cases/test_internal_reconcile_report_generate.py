import unittest
from unittest.mock import Mock, call

from src.entities.aws import S3InventoryManifestMetadata, S3InventoryManifest, AWSS3FileLocation, \
    AWSSQSInventoryReportMessage
from src.use_cases.internal_reconcile_report_generate import InternalReconcileReportGenerate


class MyTestCase(unittest.TestCase):
    def test_internal_reconcile_report_generate_happy_path(
        self,
    ):
        """
        Happy path for generating report.
        """
        mock_report_bucket_region0 = Mock()
        mock_report_bucket_name0 = Mock()
        mock_manifest_key0 = Mock()
        mock_report_bucket_region1 = Mock()
        mock_report_bucket_name1 = Mock()
        mock_manifest_key1 = Mock()
        manifest_metadata0 = S3InventoryManifestMetadata(
            report_bucket_region=mock_report_bucket_region0,
            report_bucket_name=mock_report_bucket_name0,
            manifest_key=mock_manifest_key0,
        )
        manifest_metadata1 = S3InventoryManifestMetadata(
            report_bucket_region=mock_report_bucket_region1,
            report_bucket_name=mock_report_bucket_name1,
            manifest_key=mock_manifest_key1,
        )
        file_bucket_name0 = Mock()
        file_key0 = Mock()
        csv_file0 = AWSS3FileLocation(bucket_name=file_bucket_name0, key=file_key0)
        file_bucket_name1 = Mock()
        file_key1 = Mock()
        csv_file1 = AWSS3FileLocation(bucket_name=file_bucket_name1, key=file_key1)
        file_bucket_name2 = Mock()
        file_key2 = Mock()
        csv_file2 = AWSS3FileLocation(bucket_name=file_bucket_name2, key=file_key2)
        file_bucket_name3 = Mock()
        file_key3 = Mock()
        csv_file3 = AWSS3FileLocation(bucket_name=file_bucket_name3, key=file_key3)
        source_bucket_name0 = Mock()
        manifest_creation_datetime_0 = Mock()
        source_bucket_name1 = Mock()
        manifest_creation_datetime_1 = Mock()
        manifest0 = S3InventoryManifest(
            source_bucket_name=source_bucket_name0,
            manifest_creation_datetime=manifest_creation_datetime_0,
            manifest_files=[csv_file0, csv_file1],
            manifest_files_columns=Mock(),
        )
        manifest1 = S3InventoryManifest(
            source_bucket_name=source_bucket_name1,
            manifest_creation_datetime=manifest_creation_datetime_1,
            manifest_files=[csv_file2, csv_file3],
            manifest_files_columns=Mock(),
        )
        message_receipt = Mock()
        sqs_message = AWSSQSInventoryReportMessage(
            manifest_metadatas=[manifest_metadata0, manifest_metadata1],
            message_receipt=message_receipt,
        )

        mock_aws_adapter = Mock()
        mock_aws_adapter.get_s3_manifest_event_from_sqs = Mock(return_value=sqs_message)
        mock_aws_adapter.get_manifest = Mock(side_effect=[manifest0, manifest1])
        mock_aws_adapter.add_metadata_to_gzip = Mock()

        mock_storage_adapter = Mock()
        mock_report_cursor0 = Mock()
        mock_report_cursor1 = Mock()
        mock_storage_adapter.create_job = Mock(
            side_effect=[mock_report_cursor0, mock_report_cursor1]
        )
        mock_storage_adapter.import_current_archive_list_for_reconciliation_job = Mock()
        mock_storage_adapter.perform_orca_reconcile_for_reconciliation_job = Mock()
        mock_aws_adapter.remove_job_from_queue = Mock()

        mock_logger = Mock()

        result = InternalReconcileReportGenerate(mock_aws_adapter, mock_storage_adapter)\
            .internal_reconcile_report_generate(mock_logger)

        mock_aws_adapter.get_s3_manifest_event_from_sqs.assert_called_once_with()
        mock_aws_adapter.get_manifest.assert_has_calls([
            call(mock_manifest_key0, mock_report_bucket_name0, mock_report_bucket_region0,
                 mock_logger),
            call(mock_manifest_key1, mock_report_bucket_name1, mock_report_bucket_region1,
                 mock_logger)
        ])
        self.assertEqual(2, mock_aws_adapter.get_manifest.call_count)
        mock_aws_adapter.add_metadata_to_gzip.assert_has_calls([
            call(csv_file0), call(csv_file1), call(csv_file2), call(csv_file3),
        ])
        self.assertEqual(4, mock_aws_adapter.add_metadata_to_gzip.call_count)
        mock_storage_adapter.import_current_archive_list_for_reconciliation_job.assert_has_calls([
            call(manifest0, manifest_metadata0, mock_report_cursor0),
            call(manifest1, manifest_metadata1, mock_report_cursor1),
        ])
        self.assertEqual(2, mock_storage_adapter.
                         import_current_archive_list_for_reconciliation_job.call_count)
        mock_storage_adapter.perform_orca_reconcile_for_reconciliation_job.assert_has_calls([
            call(source_bucket_name0, mock_report_cursor0),
            call(source_bucket_name1, mock_report_cursor1),
        ])
        self.assertEqual(2, mock_storage_adapter.
                         perform_orca_reconcile_for_reconciliation_job.call_count)
        mock_aws_adapter.remove_job_from_queue.assert_called_once_with(
            message_receipt, mock_logger)

        self.assertTrue(result)

    def test_internal_reconcile_report_generate_no_manifest_returns_false(
        self,
    ):
        """
        If no manifest is found, return False to indicate that reconciliation was not performed.
        """
        mock_aws_adapter = Mock()
        mock_aws_adapter.get_s3_manifest_event_from_sqs = Mock(return_value=None)
        mock_storage_adapter = Mock()
        mock_logger = Mock()

        result = InternalReconcileReportGenerate(mock_aws_adapter, mock_storage_adapter)\
            .internal_reconcile_report_generate(mock_logger)

        mock_aws_adapter.get_s3_manifest_event_from_sqs.assert_called_once_with()
        mock_storage_adapter.assert_not_called()

        self.assertFalse(result)
