import logging

from src.adapters.api.aws import AWS
from src.use_cases.adapter_interfaces.storage import StorageInterface


class InternalReconcileReportGenerate:
    def __init__(
        self,
        aws_adapter: AWS,
        storage_adapter: StorageInterface,
    ):
        self.aws_adapter = aws_adapter
        self.storage_adapter = storage_adapter

    def internal_reconcile_report_generate(
        self,
        logger: logging.Logger
    ) -> bool:
        """
        Orchestrates Internal Reconciliation Report generation.

        Args:
            logger: The logger to use.

        Returns: False if there were no reports to generate. True otherwise.
        """
        sqs_message = self.aws_adapter.get_s3_manifest_event_from_sqs()
        if sqs_message is None:
            logger.info("No messages in queue.")
            return False

        for manifest_metadata in sqs_message.manifest_metadatas:
            manifest = self.aws_adapter.get_manifest(
                manifest_metadata.manifest_key,
                manifest_metadata.report_bucket_name,
                manifest_metadata.report_bucket_region,
                logger,
            )
            report_cursor = self.storage_adapter.create_job(
                manifest.manifest_creation_datetime,
                manifest.source_bucket_name,
            )

            # set gzip metadata
            for csv_file in manifest.manifest_files:
                if not csv_file.key.endswith(".csv.gz"):
                    raise Exception(f"Cannot handle file extension on '{csv_file.key}'")
                # Set the required metadata
                self.aws_adapter.add_metadata_to_gzip(csv_file.bucket_name, csv_file.key)

            self.storage_adapter.import_current_archive_list_for_reconciliation_job(
                manifest,
                manifest_metadata,
                report_cursor,
            )
            self.storage_adapter.perform_orca_reconcile_for_reconciliation_job(
                manifest.source_bucket_name,
                report_cursor,
            )
            self.aws_adapter.remove_job_from_queue(sqs_message.message_receipt, logger)
            return True
