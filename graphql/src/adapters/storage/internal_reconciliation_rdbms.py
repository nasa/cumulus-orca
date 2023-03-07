import logging
from abc import abstractmethod
from typing import List, Optional

import orca_shared
from orca_shared.database import shared_db
from orca_shared.reconciliation import OrcaStatus, get_partition_name_from_bucket_name
from sqlalchemy import create_engine, text
from sqlalchemy.future import Engine
from datetime import datetime, timezone

from src.adapters.storage.internal_reconciliation_s3 import AWSS3FileLocation
from src.entities.common import DirectionEnum
from src.entities.internal_reconcile_report import Mismatch, Phantom, InternalReconcileReportCursor
from src.use_cases.adapter_interfaces.storage import (
    StorageInternalReconcileReportInterface,
    InternalReconcileGenerationStorageInterface,
)


class InternalReconciliationStorageAdapterRDBMS(
    StorageInternalReconcileReportInterface,
    InternalReconcileGenerationStorageInterface,
):
    def __init__(
        self,
        user_connection_uri: str,
        admin_connection_uri: str,
        s3_access_key: str,
        s3_secret_key: str,
    ):
        self.user_engine: Engine = create_engine(user_connection_uri, future=True)
        self.admin_engine: Engine = create_engine(admin_connection_uri, future=True)
        self.s3_access_key = s3_access_key
        self.s3_secret_key = s3_secret_key

    def create_job(
        self,
        orca_archive_location: str,
        inventory_creation_time: datetime,
        logger: logging.Logger,
    ) -> InternalReconcileReportCursor:
        """
        Creates the initial status entry for a job.

        Args:
            orca_archive_location: The name of the bucket to generate the reports for.
            inventory_creation_time: The time the s3 Inventory report was created.
            logger: The logger to use.

        Returns: The auto-incremented job_id from the database.
        """
        logger.debug("Creating status for job.")
        try:
            with self.user_engine.begin() as connection:
                # Within this transaction import the csv and update the job status
                now = datetime.now(timezone.utc)
                rows = connection.execute(
                    self.create_job_sql(),
                    [
                        {
                            "orca_archive_location": orca_archive_location,
                            "inventory_creation_time": inventory_creation_time,
                            "status_id": OrcaStatus.GETTING_S3_LIST.value,
                            "start_time": now,
                            "last_update": now,
                            "end_time": None,
                            "error_message": None,
                        }
                    ],
                )
        except Exception as sql_ex:
            logger.error(f"Error while creating job: {sql_ex}")
            raise

        return InternalReconcileReportCursor(rows.fetchone()["id"])

    def pull_in_inventory_report(
        self,
        report_source: str,
        report_cursor: InternalReconcileReportCursor,
        columns_in_csv: List[str],
        csv_file_locations: List[AWSS3FileLocation],
        report_bucket_region: str,
        logger: logging.Logger,
    ):
        """
        Pulls the given inventory report into storage for the given report.

        Args:
            report_source: The region covered by the report.
            report_cursor: Cursor to the report to update.
            columns_in_csv: Columns in the csv files.
            csv_file_locations: Locations of the csv files in the report.
            report_bucket_region: Required by current Postgres driver.
            logger: The logger to use.
        """
        self.truncate_s3_partition(
            report_source,
            logger,
        )

        self.update_job_with_s3_inventory(
            report_cursor,
            columns_in_csv,
            csv_file_locations,
            report_bucket_region,
            logger,
        )

    def truncate_s3_partition(
        self,
        report_source: str,
        logger: logging.Logger,
    ):
        """
        Truncates the partition for the given orca_archive_location, removing its data.

        Args:
            report_source: The region covered by the report.
            logger: The logger to use.
        """
        try:
            logger.debug(f"Truncating old s3 data blocking report {report_source}.")
            partition_name = get_partition_name_from_bucket_name(report_source)
            with self.admin_engine.begin() as connection:
                connection.execute(
                    self.truncate_s3_partition_sql(partition_name),
                    [{}],
                )
        except Exception as sql_ex:
            logger.error(
                f"Error while truncating bucket '{report_source}': {sql_ex}"
            )
            raise

    def update_job(
        self,
        report_cursor: InternalReconcileReportCursor,
        status: OrcaStatus,
        error_message: Optional[str],
    ) -> None:
        """
        Updates the status entry for a job.

        Args:
            report_cursor: Cursor to the report to update.
            status: The status to update the job with.
            error_message: The error to post to the job, if any.
        """
        orca_shared.reconciliation.update_job(
            int(report_cursor.job_id),
            status,
            error_message,
            self.user_engine
        )

    def update_job_with_s3_inventory(
        self,
        report_cursor: InternalReconcileReportCursor,
        columns_in_csv: List[str],
        csv_file_locations: List[AWSS3FileLocation],
        report_bucket_region: str,
        logger: logging.Logger,
    ):
        """
        Constructs a temporary table capable of holding full data from s3 inventory report,
        triggers load into that table, then moves that data into the proper partition.

        Args:
            report_cursor: Cursor to the report to update.
            columns_in_csv: Columns in the csv files.
            csv_file_locations: Locations of the csv files in the report.
            report_bucket_region: Required by current Postgres driver.
            logger: The logger to use.
        """
        try:
            logger.debug(f"Pulling in s3 inventory records for job {report_cursor.job_id}.")
            temporary_s3_column_list = self.generate_temporary_s3_column_list(
                columns_in_csv
            )
            with self.admin_engine.begin() as connection:
                # Within this transaction import the csv and update the job status
                connection.execute(
                    self.create_temporary_table_sql(temporary_s3_column_list),
                    [{}],
                )
                for csv_file_location in csv_file_locations:
                    # Have postgres load the csv
                    logger.debug(
                        f"Loading CSV {csv_file_location.key} for job {report_cursor.job_id}.")
                    connection.execute(
                        self.trigger_csv_load_from_s3_sql(),
                        [
                            {
                                "report_bucket_name": csv_file_location.bucket_name,
                                "csv_key_path": csv_file_location.key,
                                "report_bucket_region": report_bucket_region,
                                "s3_access_key": self.s3_access_key,
                                "s3_secret_key": self.s3_secret_key,
                            }
                        ],
                    )
                # Now that all csvs are loaded, pull them into main db from temporary table
                logger.debug(f"Translating data to Orca format for job {report_cursor.job_id}.")
                connection.execute(
                    self.translate_s3_import_to_partitioned_data_sql(),
                    [
                        {
                            "job_id": report_cursor.job_id,
                        }
                    ],
                )
                # Update job status
                logger.debug(f"Posting successful status for job {report_cursor.job_id}.")
                orca_shared.reconciliation.shared_reconciliation.update_job(
                    int(report_cursor.job_id),
                    OrcaStatus.STAGED,
                    None,
                    self.user_engine,
                )
        except Exception as sql_ex:
            logger.error(f"Error while processing job '{report_cursor.job_id}': {sql_ex}")
            raise

    @staticmethod
    def generate_temporary_s3_column_list(columns_in_csv: List[str]) -> str:
        """
        Creates a list of columns that matches the order of columns in the manifest.
        Columns used by our database are given standardized names.
        Args:
            columns_in_csv: Columns in the csv files.

        Returns: A string representing SQL columns to create.
            Columns required for import but unused by orca will be filled in with `junk` values.
            For example, 'orca_archive_location text, key_path text, size_in_bytes bigint,
            last_update timestamptz, etag text,storage_class text, junk7 text, junk8 text,
            junk9 text, junk10 text, junk11 text, junk12 text, junk13 text'

        """
        # Keys indicate columns in the s3 inventory csv.
        # Values indicate the corresponding column in orca.reconcile_s3_object
        column_mappings = {
            "Bucket": "orca_archive_location text",
            "Key": "key_path text",
            "Size": "size_in_bytes bigint",
            "LastModifiedDate": "last_update timestamptz",
            "ETag": "etag text",
            "StorageClass": "storage_class text",
            "IsDeleteMarker": "delete_marker bool",
            "IsLatest": "is_latest bool",
        }
        columns_in_postgres = []
        for column_index, column_in_csv in enumerate(columns_in_csv):
            postgres_column_name = column_mappings.get(
                column_in_csv, "junk" + str(column_index) + " text"
            )
            columns_in_postgres.append(postgres_column_name)
        return ", ".join(columns_in_postgres)

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
    def create_job_sql() -> text:  # pragma: no cover
        # abstract to allow other sql formats
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def truncate_s3_partition_sql(partition_name: str) -> text:  # pragma: no cover
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def create_temporary_table_sql(temporary_s3_column_list: str) -> text:  # pragma: no cover
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def trigger_csv_load_from_s3_sql() -> text:  # pragma: no cover
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def translate_s3_import_to_partitioned_data_sql() -> text:  # pragma: no cover
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def get_phantom_page_sql(direction: DirectionEnum) -> text:  # pragma: no cover
        # abstract to allow other sql formats
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def get_mismatch_page_sql(direction: DirectionEnum) -> text:  # pragma: no cover
        # abstract to allow other sql formats
        raise NotImplementedError()
