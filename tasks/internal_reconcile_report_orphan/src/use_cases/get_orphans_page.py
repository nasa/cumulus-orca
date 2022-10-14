from aws_lambda_powertools import Logger

from src.use_cases.adapter_interfaces.storage import OrphansPageStorageInterface
from src.entities.orphan import OrphanRecordPage, OrphanRecordFilter

# Set AWS powertools logger
Logger = Logger()


def task(
        orphan_record_filter: OrphanRecordFilter,
        orphans_page_storage: OrphansPageStorageInterface,
        logger: Logger
) -> OrphanRecordPage:
    """
    Args:
        orphan_record_filter: The filter designating which orphans to return.
        orphans_page_storage: The helper class for getting the page from the DB.
        logger: The logger to use.

    Returns:
        A list containing orphan records.
        A bool indicating if there are further pages to retrieve.
    """
    return orphans_page_storage.get_orphans_page(
        orphan_record_filter,
        logger
    )
