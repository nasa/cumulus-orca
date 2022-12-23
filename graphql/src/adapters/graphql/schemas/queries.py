import typing
import uuid
from typing import Annotated

# noinspection PyPackageRequirements
import strawberry
from strawberry import argument, field, type

from src.adapters.graphql.adapters import AdaptersStorage
from src.adapters.graphql.dataTypes.sample import GetEchoStrawberryResponse
from src.adapters.graphql.dataTypes.storage_metadata import (
    GetStorageSchemaVersionStrawberryResponse,
)
from src.adapters.graphql.resolvers.sample import get_echo
from src.adapters.graphql.resolvers.storage_metadata import (
    get_storage_migration_version,
)


@type
class Queries:
    # Set in schemas.py,
    # can't use constructor due to Strawberry not accepting constructed classes.
    adapters_storage: strawberry.Private[AdaptersStorage]

    @field(
        description="""Echos the given word back as a check of basic GraphQL functionality.""")
    def get_echo(
        self,
        word: Annotated[
            typing.Optional[str],  # `Optional` marks it as 'optional'...
            argument(
                description="""The word to echo back."""
            )
        ] = None,  # Default value actually MAKES it optional
    ) -> GetEchoStrawberryResponse:
        return get_echo(word,
                        Queries.adapters_storage.word_generation,
                        Queries.adapters_storage.logger_provider.get_logger(
                            uuid.uuid4().__str__()
                        )
                        )

    @field(
        description="""Gets all phantom reports for the given filter.""")
    def get_storage_schema_version(
        self,

    ) -> GetStorageSchemaVersionStrawberryResponse:
        return get_storage_migration_version(
            self.adapters_storage.storage,
            self.adapters_storage.logger_provider.get_logger(
                uuid.uuid4().__str__()
            )
        )
