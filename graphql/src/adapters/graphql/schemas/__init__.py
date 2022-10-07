# noinspection PyPackageRequirements
from strawberry import Schema
# noinspection PyPackageRequirements
from strawberry.extensions import AddValidationRules
# noinspection PyPackageRequirements
from graphql.validation import NoSchemaIntrospectionCustomRule

from src.adapters.graphql import graphql_settings
from src.adapters.graphql.schemas.queries import Query
# from server.adapters.api.graphql.schemas.mutations import Mutation
# from server.adapters.api.graphql.schemas.subscriptions import Subscription


def get_schema() -> Schema:
    """
    Returns a strawberry library Schema object used for exposing the API.
    """
    return Schema(
        Query,
        # mutation=Mutation,
        # subscription=Subscription,
        # config=
        # types=
        extensions=
        [AddValidationRules([NoSchemaIntrospectionCustomRule]), ]
        if graphql_settings.instantiated_settings.GRAPHIQL is False else
        []
        # scalar_overrides=
    )
