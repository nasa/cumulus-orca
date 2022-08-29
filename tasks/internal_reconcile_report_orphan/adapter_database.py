import logging
from typing import List, Tuple

from orca_shared.database.shared_db import retry_operational_error
from sqlalchemy import text
from sqlalchemy.future import Engine

from internal_reconcile_report_orphan import OrphanRecord


def get_orphans_sql() -> text:  # pragma: no cover
    """
    SQL for getting orphan report entries for a given job_id, page_size, and page_index.
    Formats datetimes in milliseconds since 1 January 1970 UTC.
    """
    return text(
        """
SELECT
    key_path,
    etag,
    (EXTRACT(EPOCH FROM date_trunc('milliseconds', last_update) AT TIME ZONE 'UTC') * 1000)::bigint as last_update,
    size_in_bytes,
    storage_class
    FROM reconcile_orphan_report
    WHERE job_id = :job_id
    ORDER BY key_path, etag
    OFFSET :page_index*:page_size
    LIMIT :page_size+1"""
    )


class AdapterDatabase:
    engine = None

    def __init__(self, engine: Engine):
        self.engine = engine

    @retry_operational_error()
    def query_db(
            self,
            job_id: str,
            page_index: int,
            page_size: int,
            logger: logging.Logger
    ) -> Tuple[List[OrphanRecord], bool]:
        # noinspection GrazieInspection
        """
            Gets orphans for the given job/page, up to PAGE_SIZE + 1 results.

            Args:
                job_id: The unique ID of job/report.
                page_index: The 0-based index of the results page to return.
                page_size: The maximum number of results to return.
                logger: The logger to use.

            Returns:
                A list containing orphan records.
                A bool indicating if there are further pages to retrieve.
            """
        logger.info(f"Retrieving page '{page_index}' of reports for job '{job_id}'")
        with self.engine.begin() as connection:
            sql_results = connection.execute(
                get_orphans_sql(),
                [
                    {
                        "job_id": job_id,
                        "page_index": page_index,
                        "page_size": page_size,
                    }
                ],
            )

            orphans = []
            for sql_result in sql_results:
                orphans.append(
                    OrphanRecord(sql_result["key_path"],
                                 sql_result["etag"],
                                 sql_result["last_update"],
                                 sql_result["size_in_bytes"],
                                 sql_result["storage_class"], )
                )

            # we get one extra for anotherPage calculation.
            return orphans[0:page_size], \
                   len(orphans) > page_size
