from sqlalchemy import text
from src.adapters.storage.rdbms import StorageAdapterRDBMS


class StorageAdapterPostgres(StorageAdapterRDBMS):

    def __init__(self, user_connection_uri: str):
        super(StorageAdapterPostgres, self).__init__(user_connection_uri)

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
