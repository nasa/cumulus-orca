# noinspection PyPackageRequirements
import strawberry

from src.adapters.graphql.dataTypes.common import InternalServerErrorGraphqlType
from src.entities.storage_metadata import StorageSchemaVersion

GetStorageSchemaVersionStrawberryResponse = strawberry.union(
    "GetStorageSchemaVersionStrawberryResponse",
    [StorageSchemaVersion, InternalServerErrorGraphqlType]
)
