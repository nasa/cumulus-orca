import logging
from abc import abstractmethod
from typing import List

from orca_shared.database import shared_db
from sqlalchemy import create_engine, text
from sqlalchemy.future import Engine

from src.entities.common import DirectionEnum
from src.entities.internal_reconcile_report import Mismatch, Phantom
from src.use_cases.adapter_interfaces.storage import (
    StorageInternalReconcileReportInterface,
    StorageInternalReconcileGenerationInterface,
)


class StorageAdapterInternalReconciliationRDBMS(
    StorageInternalReconcileReportInterface,
    StorageInternalReconcileGenerationInterface,
):
    def __init__(
        self,
        user_connection_uri: str,
        s3_access_key: str,
        s3_secret_key: str,
    ):
        self.user_engine: Engine = create_engine(user_connection_uri, future=True)
        self.s3_access_key = s3_access_key
        self.s3_secret_key = s3_secret_key

    @shared_db.retry_operational_error()
    def get_phantom_page(
        self,
        job_id: int,
        cursor_collection_id: str,
        cursor_granule_id: str,
        cursor_key_path: str,
        direction: DirectionEnum,
        limit: int,
        logger: logging.Logger
    ) -> List[Phantom]:
        """
        Returns a page of phantoms,
        ordered by collection_id, granule_id, then key_path.

        Args:
            job_id: The job to return reports for.
            cursor_collection_id: Points to start/end of the page (non-inclusive).
            cursor_granule_id: Points to start/end of the page (non-inclusive).
            cursor_key_path: Points to start/end of the page (non-inclusive).
            direction: If `next`, cursor is the start of the page. Otherwise, end.
            limit: Limits the number of rows returned.
            logger: The logger to use.

        Returns:
            A list of phantoms.
        """
        with self.user_engine.begin() as connection:
            logger.info(f"Retrieving phantoms for job '{job_id}'.")
            results = connection.execute(
                self.get_phantom_page_sql(direction),
                [{
                    "job_id": job_id,
                    "cursor_collection_id": cursor_collection_id,
                    "cursor_granule_id": cursor_granule_id,
                    "cursor_key_path": cursor_key_path,
                    "limit": limit,
                }]
            )

            phantoms = []
            for result in results:
                phantoms.append(
                    Phantom(
                        job_id=result["job_id"],
                        collection_id=result["collection_id"],
                        granule_id=result["granule_id"],
                        filename=result["filename"],
                        key_path=result["key_path"],
                        orca_etag=result["orca_etag"],
                        orca_granule_last_update=result["orca_last_update"],
                        orca_size_in_bytes=result["orca_size_in_bytes"],
                        orca_storage_class=result["orca_storage_class"],
                    )
                )
            if direction == DirectionEnum.previous:
                # due to how previous pages are retrieved, order must be reversed to be consistent.
                phantoms.reverse()
            return phantoms

    @shared_db.retry_operational_error()
    def get_mismatch_page(
        self,
        job_id: int,
        cursor_collection_id: str,
        cursor_granule_id: str,
        cursor_key_path: str,
        direction: DirectionEnum,
        limit: int,
        logger: logging.Logger
    ) -> List[Mismatch]:
        """
        Returns a page of mismatches,
        ordered by collection_id, granule_id, then key_path.

        Args:
            job_id: The job to return mismatches for.
            cursor_collection_id: Points to start/end of the page (non-inclusive).
            cursor_granule_id: Points to start/end of the page (non-inclusive).
            cursor_key_path: Points to start/end of the page (non-inclusive).
            direction: If `next`, cursor is the start of the page. Otherwise, end.
            limit: Limits the number of rows returned.
            logger: The logger to use.

        Returns:
            A list of mismatches.
        """
        with self.user_engine.begin() as connection:
            logger.info(f"Retrieving mismatches for job '{job_id}'.")
            results = connection.execute(
                self.get_mismatch_page_sql(direction),
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
                        orca_granule_last_update=result["orca_last_update"],
                        s3_file_last_update=result["s3_last_update"],
                        orca_size_in_bytes=result["orca_size_in_bytes"],
                        s3_size_in_bytes=result["s3_size_in_bytes"],
                        orca_storage_class=result["orca_storage_class"],
                        s3_storage_class=result["s3_storage_class"],
                        discrepancy_type=result["discrepancy_type"],
                        comment=result["comment"]
                    )
                )
            if direction == DirectionEnum.previous:
                # due to how previous pages are retrieved, order must be reversed to be consistent.
                mismatches.reverse()
            return mismatches

    @staticmethod
    @abstractmethod
    def get_phantom_page_sql(direction: DirectionEnum) -> text:
        # abstract to allow other sql formats
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def get_mismatch_page_sql(direction: DirectionEnum) -> text:
        # abstract to allow other sql formats
        raise NotImplementedError()
