import logging
from abc import abstractmethod
from typing import List

from orca_shared.database import shared_db
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.future import Engine

from src.entities.common import DirectionEnum
from src.entities.internal_reconcile_report import Mismatch
from src.use_cases.adapter_interfaces.storage import StorageMetadataInterface, \
    StorageInternalReconcileReportInterface


class StorageAdapterRDBMS(
    StorageMetadataInterface,
    StorageInternalReconcileReportInterface
):
    def __init__(self, user_connection_uri: str):
        self.user_engine: Engine = create_engine(user_connection_uri, future=True)

    @shared_db.retry_operational_error()
    def get_schema_version(
        self,
        logger: logging.Logger,
    ) -> int:
        # noinspection GrazieInspection
        """
        Queries the database version table and returns the latest version.

        Returns:
            Version number of the currently installed ORCA schema.
        """
        try:
            with self.user_engine.begin() as connection:
                # If table exists get the latest version from the table
                logger.info("Getting current schema version from table.")
                results = connection.execute(self.get_schema_version_sql())
                row = results.fetchone()
                schema_version = row[0]

                return schema_version
        except ProgrammingError as ex:
            if ex.code == "f405":  # UndefinedTable
                return 1
            raise

    @shared_db.retry_operational_error()
    def get_mismatch_page(
        self,
        job_id: int,
        cursor_collection_id: str,
        cursor_granule_id: str,
        cursor_key_path: str,
        direction: DirectionEnum,  # todo: use
        limit: int,
        logger: logging.Logger
    ) -> List[Mismatch]:
        """
        todo
        """
        with self.user_engine.begin() as connection:
            logger.info("todo")
            results = connection.execute(
                self.get_mismatch_page_sql(),
                [{
                    "job_id": job_id,
                    "cursor_collection_id": cursor_collection_id,
                    "cursor_granule_id": cursor_granule_id,
                    "cursor_key_path": cursor_key_path,
                    "limit": limit,
                }]
            )

            mismatches = []
            for result in results:
                mismatches.append(
                    Mismatch(
                        job_id=result["job_id"],
                        collection_id=result["collection_id"],
                        granule_id=result["granule_id"],
                        filename=result["filename"],
                        key_path=result["key_path"],
                        cumulus_archive_location=result["cumulus_archive_location"],
                        orca_etag=result["orca_etag"],
                        s3_etag=result["s3_etag"],
                        orca_last_update=result["orca_last_update"],
                        s3_last_update=result["s3_last_update"],
                        orca_size_in_bytes=result["orca_size_in_bytes"],
                        s3_size_in_bytes=result["s3_size_in_bytes"],
                        orca_storage_class=result["orca_storage_class"],
                        s3_storage_class=result["s3_storage_class"],
                        discrepancy_type=result["discrepancy_type"],
                        comment=result["comment"]
                    )
                )
            return mismatches

    @staticmethod
    @abstractmethod
    def get_schema_version_sql() -> text:
        # abstract to allow other sql formats
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def get_mismatch_page_sql() -> text:
        # abstract to allow other sql formats
        raise NotImplementedError()