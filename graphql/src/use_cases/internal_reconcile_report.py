import dataclasses
import logging

from src.entities.common import Page, PageParameters
from src.entities.internal_reconcile_report import Mismatch
from src.use_cases.adapter_interfaces.storage import (
    StorageInternalReconcileReportInterface,
)
from src.use_cases.helpers.edge_cursor import EdgeCursor


class InternalReconcileReport:
    def __init__(self, storage: StorageInternalReconcileReportInterface):
        self.storage = storage

    def get_mismatch_page(
        self,
        job_id: int,
        page_parameters: PageParameters,
        logger: logging.Logger
    ) -> Page[Mismatch]:
        """
        Returns a page of mismatches,
        ordered by collection_id, granule_id, then key_path.

        Args:
            job_id: The unique job ID of the reconciliation job.
            page_parameters: The parameters to use for paging.
            logger: The logger to use.

        Returns:
            The indicated page of mismatch reports.
        """
        if page_parameters.cursor is None:
            cursor = Mismatch.Cursor()
        else:
            cursor = EdgeCursor.decode_cursor(page_parameters.cursor, Mismatch.Cursor)

        mismatches = self.storage.get_mismatch_page(
            job_id,
            cursor.collection_id,
            cursor.granule_id,
            cursor.key_path,
            page_parameters.direction,
            page_parameters.limit,
            logger
        )

        if len(mismatches) == 0:
            start_cursor = None
            end_cursor = None
        else:
            start_cursor = EdgeCursor.encode_cursor(
                **dataclasses.asdict(mismatches[0].get_cursor()))
            end_cursor = EdgeCursor.encode_cursor(
                **dataclasses.asdict(mismatches[len(mismatches) - 1].get_cursor()))

        return Page(items=mismatches,
                    start_cursor=start_cursor,
                    end_cursor=end_cursor)
