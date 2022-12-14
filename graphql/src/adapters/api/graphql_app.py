# noinspection PyPackageRequirements
from strawberry.fastapi import GraphQLRouter

from src.adapters.graphql.graphql_settings import GraphQLSettings
from src.adapters.graphql.schemas.schemas import get_schema


def get_graphql_app(graphql_settings: GraphQLSettings):
    # todo: Add docstrings here and elsewhere
    schema = get_schema(graphql_settings)
    return GraphQLRouter(
        schema,
        graphiql=graphql_settings.GRAPHIQL,
        allow_queries_via_get=graphql_settings.ALLOW_GET,
        debug=graphql_settings.DEBUG
    )
