import logging

from use_cases.adapter_interfaces.database import DatabaseInterface
from entities.orphan import OrphanRecordPage, OrphanRecordFilter


def task(
        orphan_record_filter: OrphanRecordFilter,
        adapter_database: DatabaseInterface,
        logger: logging.Logger
) -> OrphanRecordPage:
    """
    Args:
        orphan_record_filter: The filter designating which orphans to return.
        adapter_database: The helper class for interacting with the DB.
        logger: The logger to use.

    Returns:
        A list containing orphan records.
        A bool indicating if there are further pages to retrieve.
    """
    return adapter_database.get_orphans_page(
        orphan_record_filter,
        logger
    )
