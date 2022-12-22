import logging
from typing import List

from src.entities.common import PageParameters, DirectionEnum
from src.entities.internal_reconcile_report import Mismatch


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
        todo
        """
        ...
