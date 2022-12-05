import logging

from src.entities.orphan import OrphanRecordFilter, OrphanRecordPage


class OrphansPageStorageInterface:
    """
    Generic storage class with method that needs to be implemented by database adapter.
    """

    def get_orphans_page(self,
                         orphan_record_filter: OrphanRecordFilter,
                         LOGGER: logging.Logger
                         ) -> OrphanRecordPage: ...
