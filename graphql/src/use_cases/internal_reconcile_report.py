import logging

from src.entities.common import Page, PageParameters
from src.entities.internal_reconcile_report import Mismatch
from src.use_cases.adapter_interfaces.storage import StorageInternalReconcileReportInterface
from src.use_cases.helpers.edge_cursor import EdgeCursor

CURSOR_JOB_ID_KEY = "job_id"
CURSOR_COLLECTION_ID_KEY = "collection_id"
CURSOR_GRANULE_ID_KEY = "granule_id"
CURSOR_KEY_PATH_KEY = "key_path"

class InternalReconcileReport:
    def __init__(self, storage: StorageInternalReconcileReportInterface):
        self.storage = storage

    @staticmethod
    def _create_mismatch_cursor(mismatch: Mismatch) -> str:
        """
        Creates a cursor that points to the given element.

        Args:
            mismatch: The element to create a cursor for.

        Returns:
            A cursor that will always point to the given element.
        """
        return EdgeCursor.encode_cursor(**{
            CURSOR_JOB_ID_KEY: mismatch.job_id,
            CURSOR_COLLECTION_ID_KEY: mismatch.collection_id,
            CURSOR_GRANULE_ID_KEY: mismatch.granule_id,
            CURSOR_KEY_PATH_KEY: mismatch.key_path,
        })

    def get_mismatch_page(
        self,
        job_id: int,
        page_parameters: PageParameters,
        logger: logging.Logger
    ) -> Page[Mismatch]:
        """
        todo

        Args:
            job_id: The unique job ID of the reconciliation job.
            page_parameters: todo
            logger: todo

        Returns:
            The indicated page of mismatch reports.
        """
        # todo: cursor type instead of dict?
        cursor = EdgeCursor.decode_cursor(page_parameters.cursor, dict)

        mismatches = self.storage.get_mismatch_page(
            job_id,
            cursor[CURSOR_COLLECTION_ID_KEY],
            cursor[CURSOR_GRANULE_ID_KEY],
            cursor[CURSOR_KEY_PATH_KEY],
            page_parameters.direction,
            page_parameters.limit,
            logger
        )

        if len(mismatches) == 0:
            start_cursor = self._create_mismatch_cursor(mismatches[0])
            end_cursor = self._create_mismatch_cursor(mismatches[len(mismatches) - 1])
        else:
            start_cursor = None
            end_cursor = None

        return Page(items=mismatches,
                    start_cursor=start_cursor,
                    end_cursor=end_cursor)
