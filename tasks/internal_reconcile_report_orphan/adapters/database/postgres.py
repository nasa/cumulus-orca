import dataclasses
import logging

from orca_shared.database import shared_db
from sqlalchemy import text
from sqlalchemy.future import Engine

from entities.orphan import OrphanRecordFilter, OrphanRecordPage, OrphanRecord
from use_cases.adapter_interfaces.database import DatabaseInterface


@dataclasses.dataclass  # todo: Replace the loosely-defined dictionary in orca_shared.database with this.
class PostgresConnectionInfo:
    admin_database_name: str
    admin_username: str
    admin_password: str
    user_username: str
    user_password: str
    user_database_name: str
    host: str
    port: str


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


class AdapterDatabase(DatabaseInterface):
    _engine: Engine = None

    def __init__(self, db_connect_info: PostgresConnectionInfo):
        """
        Args:
            db_connect_info: See shared_db.py's get_configuration for further details.
        """
        engine = shared_db.get_user_connection({
            "admin_database": db_connect_info.admin_database_name,
            "admin_username": db_connect_info.admin_username,
            "admin_password": db_connect_info.admin_password,
            "user_username": db_connect_info.user_username,
            "user_password": db_connect_info.user_password,
            "user_database": db_connect_info.user_database_name,
            "host": db_connect_info.host,
            "port": db_connect_info.port,
        })
        self._engine = engine

    @shared_db.retry_operational_error()
    def get_orphans_page(
            self,
            orphan_record_filter: OrphanRecordFilter,
            logger: logging.Logger
    ) -> OrphanRecordPage:
        # noinspection GrazieInspection
        """
            Gets orphans for the given job/page, up to PAGE_SIZE + 1 results.

            Args:
                orphan_record_filter: The filter designating which orphans to return.
                logger: The logger to use.

            Returns:
                A list containing orphan records.
                A bool indicating if there are further pages to retrieve.
            """
        logger.info(f"Retrieving page '{orphan_record_filter.page_index}' "
                    f"of reports for job '{orphan_record_filter.job_id}'")
        with self._engine.begin() as connection:
            sql_results = connection.execute(
                get_orphans_sql(),
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
                    OrphanRecord(sql_result["key_path"],
                                 sql_result["etag"],
                                 sql_result["last_update"],
                                 sql_result["size_in_bytes"],
                                 sql_result["storage_class"], )
                )

            # we get one extra for anotherPage calculation.
            return OrphanRecordPage(orphans[0:orphan_record_filter.page_size], len(orphans) > orphan_record_filter.page_size)
