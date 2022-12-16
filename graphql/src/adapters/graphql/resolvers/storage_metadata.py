import logging

from src.adapters.graphql.dataTypes.common import InternalServerErrorGraphqlType
from src.adapters.graphql.dataTypes.storage_metadata import (
    GetStorageSchemaVersionStrawberryResponse,
)
from src.use_cases.adapter_interfaces.storage import StorageMetadataInterface
from src.use_cases.storage_metadata import StorageMetadata


def get_storage_migration_version(storage_metadata: StorageMetadataInterface, logger: logging.Logger) -> \
        GetStorageSchemaVersionStrawberryResponse:
    try:
        return StorageMetadata(storage_metadata).get_schema_version(logger)
    except Exception as ex:
        return InternalServerErrorGraphqlType(ex)
