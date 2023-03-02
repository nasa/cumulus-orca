import logging
from abc import abstractmethod

from orca_shared.database import shared_db
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.future import Engine

from src.use_cases.adapter_interfaces.storage import (
    StorageInternalReconcileReportInterface,
    StorageMetadataInterface, InternalReconcileGenerationStorageInterface,
)


class StorageAdapterRDBMS(
    StorageMetadataInterface,
    StorageInternalReconcileReportInterface,
    InternalReconcileGenerationStorageInterface,
):
    def __init__(
        self,
        user_connection_uri: str,
    ):
        self.user_engine: Engine = create_engine(user_connection_uri, future=True)

    @shared_db.retry_operational_error()
    def get_schema_version(
        self,
        logger: logging.Logger,
    ) -> int:
        # noinspection GrazieInspection
        """
        Queries the database version table and returns the latest version.

        Args:
            logger: The logger to use.

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

    @staticmethod
    @abstractmethod
    def get_schema_version_sql() -> text:
        # abstract to allow other sql formats
        raise NotImplementedError()
