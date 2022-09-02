import logging

from entities.orphan import OrphanRecordFilter, OrphanRecordPage


class DatabaseInterface:
    """
    Generic storage class with method that needs to be implemented by database adapter.
    """

    def get_orphans_page(self,
                         orphan_record_filter: OrphanRecordFilter,
                         logger: logging.Logger
                         ) -> OrphanRecordPage: ...
