from orca_shared.database.entities import PostgresConnectionInfo
from orca_shared.database.use_cases import create_postgres_connection_uri
from sqlalchemy import text

from src.adapters.graphql.initialized_adapters.logger_provider import static_logger_provider
from src.adapters.storage.rdbms import StorageAdapterRDBMS


class StorageAdapterPostgres(StorageAdapterRDBMS):
    def __init__(self, db_connect_info: PostgresConnectionInfo):
        self.db_connect_info = db_connect_info
        super(StorageAdapterPostgres, self).__init__()

    def create_admin_uri(self,
                         database_level_override: StorageAdapterRDBMS.AccessLevel = None) -> str:
        """
        Creates a URI that can be used to connect to the database as the admin user.

        Args:
            database_level_override:
                Default `admin`. If `user`, sets up URI for user database instead of admin.

        Returns: The URI for use in sqlalchemy connections.
        """
        if database_level_override is None:
            database_name_override = None
        elif database_level_override == StorageAdapterRDBMS.AccessLevel.admin:
            database_name_override = self.db_connect_info.admin_database_name
        elif database_level_override == StorageAdapterRDBMS.AccessLevel.user:
            database_name_override = self.db_connect_info.user_database_name
        else:
            raise NotImplementedError(f"Access level '{database_level_override}' not supported.")

        return create_postgres_connection_uri.create_admin_uri(
            self.db_connect_info, static_logger_provider.get_logger(), database_name_override)

    def create_user_uri(self) -> str:
        """
        Creates a URI that can be used to connect to the database as the application user.

        Returns: The URI for use in sqlalchemy connections.
        """
        return create_postgres_connection_uri.create_user_uri(
            self.db_connect_info, static_logger_provider.get_logger())

    @staticmethod
    def get_schema_version_sql() -> text:  # pragma: no cover
        """
        SQL for getting the version number of the most up-to-date version of the DB structure
        deployed.
        """
        return text("""
SELECT
    version_id
FROM
    orca.schema_versions
WHERE
    is_latest = True"""
                    )

    @staticmethod
    def app_version_table_exists_sql() -> text:  # pragma: no cover
        """
        SQL for getting the version number of the most up-to-date version of the DB structure
        deployed.
        """
        return text("""
SELECT EXISTS (
    SELECT
        table_name
    FROM
        information_schema.tables
    WHERE
        table_schema = 'orca'
    AND
        table_name = 'schema_versions'
)"""
                    )
