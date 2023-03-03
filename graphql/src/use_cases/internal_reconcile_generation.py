import logging
from datetime import datetime, timezone
from typing import List, Optional

from orca_shared.reconciliation import OrcaStatus

from src.entities.files import FileLocation
from src.entities.internal_reconcile_report import InternalReconcileReportCursor
from src.use_cases.adapter_interfaces.storage import InternalReconcileGenerationStorageInterface


class InternalReconcileGeneration:
    def __init__(
        self,
        storage: InternalReconcileGenerationStorageInterface,
    ):
        self.storage = storage

    def create_job(
        self,
        report_source: str,
        creation_timestamp: int,
        logger: logging.Logger,
    ) -> InternalReconcileReportCursor:
        """

        Args:
            report_source: The region covered by the report.
            creation_timestamp: Seconds since UTC origin that the report was created.
            logger: The logger to use.

        Returns:

        """
        job_id = self.storage.create_job(
            report_source,
            datetime.utcfromtimestamp(
                creation_timestamp
            ).replace(tzinfo=timezone.utc),
            logger,
        )
        return InternalReconcileReportCursor(
            job_id=job_id
        )

    def update_job(
        self,
        report_cursor: InternalReconcileReportCursor,
        status: OrcaStatus,
        error_message: Optional[str],
    ):
        """
        Updates the status entry for a job.

        Args:
            report_cursor: Cursor to the report to update.
            status: The status to update the job with.
            error_message: The error to post to the job, if any.
        """
        self.storage.update_job(
            report_cursor,
            status,
            error_message,
        )

    def get_current_archive_list(
        self,
        report_source: str,
        report_cursor: InternalReconcileReportCursor,
        columns_in_csv: List[str],
        csv_file_locations: List[FileLocation],
        report_bucket_region: str,
        logger: logging.Logger,
    ) -> None:
        """
        Pulls the given inventory report into storage for the given report.

        Args:
            report_source: The region covered by the report.
            report_cursor: Cursor to the report to update.
            columns_in_csv: Columns in the csv files.
            csv_file_locations: Locations of the csv files in the report.
            report_bucket_region: Required by current Postgres driver.
            logger: The logger to use.
        """
        self.storage.pull_in_inventory_report(
            report_source,
            report_cursor,
            columns_in_csv,
            csv_file_locations,
            report_bucket_region,
            logger
        )
