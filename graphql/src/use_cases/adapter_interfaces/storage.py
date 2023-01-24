import logging
from typing import List

from src.entities.common import DirectionEnum
from src.entities.internal_reconcile_report import Mismatch, Phantom


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
