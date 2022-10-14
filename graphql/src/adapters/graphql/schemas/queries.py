import typing
from typing import Annotated

# noinspection PyPackageRequirements
from strawberry import type, field, argument

from src.adapters import graphql
from src.adapters.graphql import resolvers
from src.adapters.graphql.dataTypes.echo import GetEchoStrawberryResponse
from src.adapters.graphql.resolvers.echo import get_echo


@type
class Queries:

    @field(
        description="""Echos the given word back as a check of basic GraphQL functionality.""")
    def get_echo(
        self,
        word: Annotated[typing.Optional[str],  # `Optional` marks it as 'optional'...
                        argument(
                            description="""The word to echo back."""
                        )
                        ] = None,  # Default value actually MAKES it optional
    ) -> GetEchoStrawberryResponse:
        return graphql.resolvers.echo.get_echo(word)
