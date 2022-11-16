from src.adapters.graphql.dataTypes.common import InternalServerErrorStrawberryType
from src.adapters.graphql.dataTypes.storage_metadata import \
    GetStorageSchemaVersionStrawberryResponse
from src.adapters.graphql.initialized_adapters.adapters import storage
from src.adapters.storage.rdbms import StorageAdapterRDBMS
from src.use_cases.storage_metadata import StorageMetadata


def get_storage_migration_version() -> \
        GetStorageSchemaVersionStrawberryResponse:
    try:
        with storage.get_persistent_admin_connection_object(
                StorageAdapterRDBMS.AccessLevel.user
        ) as connection:
            return StorageMetadata(storage).get_schema_version(connection)
    except Exception as ex:
        return InternalServerErrorStrawberryType(ex)
