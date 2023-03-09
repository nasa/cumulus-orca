import logging
from datetime import datetime
from typing import List, Optional

from orca_shared.reconciliation import OrcaStatus

from src.entities.common import DirectionEnum
from src.entities.files import FileLocation
from src.entities.internal_reconcile_report import (
    InternalReconcileReportCursor,
    Mismatch,
    Phantom,
)


class StorageMetadataInterface:
    """
    Generic storage class with methods that need to be implemented by database adapter.
    """

    def get_schema_version(self, logger: logging.Logger) -> int:
        """
        Queries the database version table and returns the latest version.

        Args:
            logger: The logger to use.

        Returns:
            Version number of the currently installed ORCA schema.
        """
        ...


class InternalReconcileGenerationStorageInterface:
    """
    Generic storage class with methods that need to be implemented by database adapter.
    """

    def create_job(
        self,
        report_source: str,
        inventory_creation_time: datetime,
        logger: logging.Logger
    ) -> InternalReconcileReportCursor:
        """
        Creates the initial status entry for a job.

        Args:
            report_source: The region covered by the report.
            inventory_creation_time: The time the s3 Inventory report was created.
            logger: The logger to use.

        Returns: The auto-incremented job_id from the database.
        """
        ...

    def pull_in_inventory_report(
        self,
        report_source: str,
        report_cursor: InternalReconcileReportCursor,
        columns_in_csv: List[str],
        csv_file_locations: List[FileLocation],
        report_bucket_region: str,
        logger: logging.Logger,
    ):
        """
        Pulls the given inventory report into storage for the given report.

        Args:
            report_source: str,
            report_cursor: Cursor to the report to update.
            columns_in_csv: Columns in the csv files.
            csv_file_locations: Locations of the csv files in the report.
            report_bucket_region: Required by current Postgres driver.
            logger: The logger to use.
        """
        ...

    def update_job(
        self,
        report_cursor: InternalReconcileReportCursor,
        status: OrcaStatus,
        error_message: Optional[str],
    ) -> None:
        """
        Updates the status entry for a job.

        Args:
            report_cursor: Cursor to the report to update.
            status: The status to update the job with.
            error_message: The error to post to the job, if any.
        """
        ...

    def perform_orca_reconcile(
        self,
        report_source: str,
        report_cursor: InternalReconcileReportCursor,
        logger: logging.Logger,
    ) -> None:
        """
        Generates and posts phantom, orphan, and mismatch reports within the same transaction.

        Args:
            report_source: The region covered by the report.
            report_cursor: Cursor to the report to update.
            logger: The logger to use.
        """
        ...


class StorageInternalReconcileReportInterface:
    """
    Generic storage class with methods that need to be implemented by database adapter.
    """

    def get_phantom_page(
        self,
        job_id: int,
        cursor_collection_id: str,
        cursor_granule_id: str,
        cursor_key_path: str,
        direction: DirectionEnum,
        limit: int,
        logger: logging.Logger
    ) -> List[Phantom]:
        """
        Returns a page of phantoms,
        ordered by collection_id, granule_id, then key_path.

        Args:
            job_id: The job to return reports for.
            cursor_collection_id: Points to start/end of the page (non-inclusive).
            cursor_granule_id: Points to start/end of the page (non-inclusive).
            cursor_key_path: Points to start/end of the page (non-inclusive).
            direction: If `next`, cursor is the start of the page. Otherwise, end.
            limit: Limits the number of rows returned.
            logger: The logger to use.

        Returns:
            A list of phantoms.
        """
        ...

    def get_mismatch_page(
        self,
        job_id: int,
        cursor_collection_id: str,
        cursor_granule_id: str,
        cursor_key_path: str,
        direction: DirectionEnum,
        limit: int,
        logger: logging.Logger
    ) -> List[Mismatch]:
        """
        Returns a page of mismatches,
        ordered by collection_id, granule_id, then key_path.

        Args:
            job_id: The job to return reports for.
            cursor_collection_id: Points to start/end of the page (non-inclusive).
            cursor_granule_id: Points to start/end of the page (non-inclusive).
            cursor_key_path: Points to start/end of the page (non-inclusive).
            direction: If `next`, cursor is the start of the page. Otherwise, end.
            limit: Limits the number of rows returned.
            logger: The logger to use.

        Returns:
            A list of mismatches.
        """
        ...
