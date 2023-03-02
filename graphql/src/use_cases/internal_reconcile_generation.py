import json
import logging
import os
from datetime import datetime, timezone

from orca_shared.reconciliation import OrcaStatus

from src.adapters.storage.internal_reconciliation_s3 import AWSS3FileLocation
from src.entities.internal_reconcile_report import InternalReconcileReportCursor
from src.use_cases.adapter_interfaces.files import InternalReconciliationFilesInterface
from src.use_cases.adapter_interfaces.storage import InternalReconcileGenerationStorageInterface

MANIFEST_SOURCE_BUCKET_KEY = "sourceBucket"
MANIFEST_FILE_SCHEMA_KEY = "fileSchema"
MANIFEST_CREATION_TIMESTAMP_KEY = "creationTimestamp"


# todo: This process is heavily coupled to AWS and postgres.
#  Decoupling will be required for clean architecture.
class InternalReconcileGeneration:
    def __init__(
        self,
        storage: InternalReconcileGenerationStorageInterface,
        files: InternalReconciliationFilesInterface,
    ):
        self.storage = storage
        self.files = files

    def get_current_archive_list(
        self,
        manifest_location: AWSS3FileLocation,
        report_bucket_region: str,
        logger: logging.Logger,
    ) -> InternalReconcileReportCursor:
        """

        Args:
            manifest_location:
            report_bucket_region:
            logger:

        Returns:

        """
        filename = os.path.basename(manifest_location.key)
        if filename != "manifest.json":
            logger.error(f"Illegal file '{filename}'. Must be 'manifest.json'")
            raise Exception(f"Illegal file '{filename}'. Must be 'manifest.json'")

        file_str = self.files.get_file_body(
            manifest_location,
            report_bucket_region,
        )
        manifest = json.loads(file_str)

        job_id = self.storage.create_job(
            manifest[MANIFEST_SOURCE_BUCKET_KEY],
            datetime.utcfromtimestamp(
                int(manifest[MANIFEST_CREATION_TIMESTAMP_KEY]) / 1000
            ).replace(tzinfo=timezone.utc),
            logger,
        )

        try:
            self.storage.truncate_s3_partition(
                manifest[MANIFEST_SOURCE_BUCKET_KEY],
                logger,
            )

            csv_key_paths = self.files.setup_inventory_report_from_manifest(manifest, logger)

            self.storage.update_job_with_s3_inventory(
                manifest_location.bucket_name,
                report_bucket_region,
                csv_key_paths,
                manifest[MANIFEST_FILE_SCHEMA_KEY],
                job_id,
                logger,
            )
        except Exception as fatal_exception:
            # On error, set job status to failure.
            logger.error(f"Encountered a fatal error: {fatal_exception}")
            # noinspection PyArgumentList
            self.storage.update_job(
                job_id,
                OrcaStatus.ERROR,
                str(fatal_exception),
            )
            raise

        return InternalReconcileReportCursor(
            job_id=job_id, orca_archive_location=manifest[MANIFEST_SOURCE_BUCKET_KEY]
        )
