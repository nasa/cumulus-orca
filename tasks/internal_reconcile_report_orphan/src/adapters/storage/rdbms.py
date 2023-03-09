from abc import abstractmethod

import logging
import sqlalchemy
from orca_shared.database import shared_db
from sqlalchemy import text, URL

from src.entities.orphan import OrphanRecordFilter, OrphanRecordPage, OrphanRecord
from src.use_cases.adapter_interfaces.storage import OrphansPageStorageInterface


class StorageAdapterRDBMS(OrphansPageStorageInterface):
    def __init__(self, connection_uri: URL):
        """
        Args:
            connection_uri: The DB connection URL.
        """
        self._engine = sqlalchemy.engine.create.create_engine(connection_uri, future=True)

    @shared_db.retry_operational_error()
    def get_orphans_page(
            self,
            orphan_record_filter: OrphanRecordFilter,
            # todo: @bhazuka has expressed a desire to not pass loggers via parameters
            LOGGER: logging.Logger
    ) -> OrphanRecordPage:
        # noinspection GrazieInspection
        """
            Gets orphans for the given job/page, up to PAGE_SIZE + 1 results.

            Args:
                orphan_record_filter: The filter designating which orphans to return.
                LOGGER: The logger to use.

            Returns:
                A list containing orphan records.
                A bool indicating if there are further pages to retrieve.
            """
        LOGGER.info(f"Retrieving page '{orphan_record_filter.page_index}' "
                    f"of reports for job '{orphan_record_filter.job_id}'")
        with self._engine.begin() as connection:
            sql_results = connection.execute(
                self.get_orphans_sql(),
                [
                    {
                        "job_id": orphan_record_filter.job_id,
                        "page_index": orphan_record_filter.page_index,
                        "page_size": orphan_record_filter.page_size,
                    }
                ],
            )

            orphans = []
            for sql_result in sql_results:
                orphans.append(
                    OrphanRecord(key_path=sql_result["key_path"],
                                 etag=sql_result["etag"],
                                 last_update=sql_result["last_update"],
                                 size_in_bytes=sql_result["size_in_bytes"],
                                 storage_class=sql_result["storage_class"], )
                )

            # we get one extra for anotherPage calculation.
            return OrphanRecordPage(
                orphans=orphans[0:orphan_record_filter.page_size],
                another_page=len(orphans) > orphan_record_filter.page_size
            )

    @staticmethod
    @abstractmethod
    def get_orphans_sql() -> text:
        # abstract to allow other sql formats
        raise NotImplementedError()


class StorageAdapterPostgres(StorageAdapterRDBMS):
    @staticmethod
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
        (EXTRACT(EPOCH FROM date_trunc('milliseconds', last_update)
         AT TIME ZONE 'UTC') * 1000)::bigint as last_update,
        size_in_bytes,
        storage_class
        FROM reconcile_orphan_report
        WHERE job_id = :job_id
        ORDER BY key_path, etag
        OFFSET :page_index*:page_size
        LIMIT :page_size+1"""
        )
