import logging

from src.entities.storage_metadata import StorageSchemaVersion
from src.use_cases.adapter_interfaces.storage import StorageMetadataInterface


# todo: largely copy-paste. Rethink, considering previous prototypes.


class StorageMetadata:
    def __init__(self, storage: StorageMetadataInterface):
        self.storage = storage

    def get_schema_version(self, connection) -> StorageSchemaVersion:
        result = self.storage.get_schema_version(connection)
        return StorageSchemaVersion(result)
