import logging

from src.adapters.graphql.dataTypes.common import InternalServerErrorGraphqlType
from src.adapters.graphql.dataTypes.storage_metadata import \
    GetStorageSchemaVersionStrawberryResponse
from src.adapters.graphql.adapters import initialized_adapters
from src.use_cases.storage_metadata import StorageMetadata


def get_storage_migration_version(logger: logging.Logger) -> \
        GetStorageSchemaVersionStrawberryResponse:
    try:
        return StorageMetadata(initialized_adapters.storage).get_schema_version(logger)
    except Exception as ex:
        return InternalServerErrorGraphqlType(ex)
