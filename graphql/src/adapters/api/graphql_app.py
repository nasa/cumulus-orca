# noinspection PyPackageRequirements
from strawberry.fastapi import GraphQLRouter

from src.adapters.graphql.adapters import AdaptersStorage
from src.adapters.graphql.graphql_settings import GraphQLSettings
from src.adapters.graphql.schemas.schemas import get_schema


def get_graphql_app(graphql_settings: GraphQLSettings, adapters_storage: AdaptersStorage)\
        -> GraphQLRouter:
    """
    Sets up a GraphQL router based on arguments.

    Args:
        graphql_settings: Contains settings required by application components.
        adapters_storage: Adapters required by application functionality.
    Returns:
        A router to be used by the webserver.
    """
    schema = get_schema(graphql_settings, adapters_storage)
    return GraphQLRouter(
        schema,
        graphiql=graphql_settings.GRAPHIQL,
        allow_queries_via_get=graphql_settings.ALLOW_GET,
        debug=graphql_settings.DEBUG
    )
