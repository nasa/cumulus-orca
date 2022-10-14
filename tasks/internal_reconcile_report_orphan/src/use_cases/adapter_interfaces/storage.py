from aws_lambda_powertools import Logger

from src.entities.orphan import OrphanRecordFilter, OrphanRecordPage

# Set AWS powertools logger
Logger = Logger()


class OrphansPageStorageInterface:
    """
    Generic storage class with method that needs to be implemented by database adapter.
    """

    def get_orphans_page(self,
                         orphan_record_filter: OrphanRecordFilter,
                         logger: Logger
                         ) -> OrphanRecordPage: ...
