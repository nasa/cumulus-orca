import logging
from typing import Tuple, List

from adapter_database import AdapterDatabase, OrphanRecord

PAGE_SIZE = 100


def task(
        job_id: int,
        page_index: int,
        adapter_database: AdapterDatabase,
        logger: logging.Logger
) -> Tuple[List[OrphanRecord], bool]:
    """
    Args:
        job_id: The unique ID of job/report.
        page_index: The 0-based index of the results page to return.
        adapter_database: The helper class for interacting with the DB.
        logger: The logger to use.

    Returns:
        A list containing orphan records.
        A bool indicating if there are further pages to retrieve.
    """
    orphans, another_page = adapter_database.query_db(
        job_id,
        page_index,
        PAGE_SIZE,
        logger
    )
    return orphans, another_page
