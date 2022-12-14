# noinspection PyPackageRequirements
from strawberry import Schema
# noinspection PyPackageRequirements
from strawberry.extensions import AddValidationRules
# noinspection PyPackageRequirements
from graphql.validation import NoSchemaIntrospectionCustomRule

from src.adapters.graphql.graphql_settings import GraphQLSettings
# from src.adapters.graphql.schemas.queries import Queries
# from server.adapters.api.graphql.schemas.mutations import Mutation
# from server.adapters.api.graphql.schemas.subscriptions import Subscription


def get_schema(graphql_settings: GraphQLSettings) -> Schema:
    """
    Returns a strawberry library Schema object used for exposing the API.
    """
    return Schema(
        query=None,
        # Queries,  # todo: Reintroduce once dependencies are better handled in queries.py
        # mutation=Mutation,
        # subscription=Subscription,
        # config=
        # types=
        extensions=
        [AddValidationRules([NoSchemaIntrospectionCustomRule]), ]
        if graphql_settings.GRAPHIQL is False else
        []
        # scalar_overrides=
    )
