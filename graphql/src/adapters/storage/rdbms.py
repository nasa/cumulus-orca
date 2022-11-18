# todo: largely copy-paste. Rethink, considering previous prototypes.
from abc import abstractmethod
from enum import Enum

from orca_shared.database import shared_db
from sqlalchemy import text, create_engine
from sqlalchemy.future import Connection

from src.adapters.graphql.initialized_adapters.logger_provider import static_logger_provider
from src.use_cases.adapter_interfaces.storage import StorageMetadataInterface


class StorageAdapterRDBMS(StorageMetadataInterface):
    class AccessLevel(Enum):
        # Whenever this class changes, update WordTypeEnumStrawberryType
        admin = 1
        user = 2

    @abstractmethod
    def create_admin_uri(self,
                         database_level_override: AccessLevel = None):
        # abstract to allow other RDBMS technologies
        raise NotImplementedError()

    @abstractmethod
    def create_user_uri(self):
        # abstract to allow other RDBMS technologies
        raise NotImplementedError()

    @shared_db.retry_operational_error()
    def get_schema_version(
        self,
        connection: Connection
    ) -> int:
        # noinspection GrazieInspection
        """
        Queries the database version table and returns the latest version.

        Args:
            connection: Database connection object.

        Returns:
            Version number of the currently installed ORCA schema.
        """
        schema_version = 1

        # If table exists get the latest version from the table
        if self.app_version_table_exists(connection):
            static_logger_provider.get_logger().debug("Getting current schema version from table.")
            results = connection.execute(self.get_schema_version_sql())
            # todo: Remove this loop and raise error if more than one row is present.
            for row in results.fetchall():
                schema_version = row[0]

            return schema_version

    def app_version_table_exists(self, connection) -> bool:
        """
        Checks to see if the orca.schema_version table exists.

        Args:
            connection: Database connection object.

        Returns:
            True if ORCA schema_version table exists.
        """
        static_logger_provider.get_logger().debug("Checking for schema_versions table.")
        results = connection.execute(self.app_version_table_exists_sql())
        # todo: Remove this loop and raise error if more than one row is present.
        for row in results.fetchall():
            table_exists = row[0]

        static_logger_provider.get_logger().debug(f"schema_versions table exists {table_exists}")

        return table_exists

    def get_persistent_admin_connection_object(
        self,
        database_level_override: AccessLevel = None
    ):
        """
        Args:
            database_level_override:
                Use to override the target database. Defaults to the admin database.

        Returns:
            An object that can be used to maintain an open transaction with the database.
            Always use as
            with connection:
                {queries here}
        """
        uri = self.create_admin_uri(database_level_override)
        engine = create_engine(uri, future=True)
        return engine.begin()

    def get_persistent_user_connection_object(
        self
    ):
        """
        Returns:
            An object that can be used to maintain an open transaction with the database.
            Always use as
            with connection:
                {queries here}
        """
        uri = self.create_user_uri()
        engine = create_engine(uri)
        return engine.begin()

    @staticmethod
    @abstractmethod
    def get_schema_version_sql() -> text:
        # abstract to allow other sql formats
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def app_version_table_exists_sql() -> text:
        # abstract to allow other sql formats
        raise NotImplementedError()
