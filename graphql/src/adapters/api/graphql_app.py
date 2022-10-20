# noinspection PyPackageRequirements
from strawberry.fastapi import GraphQLRouter
from src.adapters.graphql import graphql_settings
from src.adapters.graphql.graphql_settings import INSTANTIATED_GRAPHQL_SETTINGS
from src.adapters.graphql.schemas import get_schema

schema = get_schema()
graphql_app = GraphQLRouter(
    schema,
    graphiql=INSTANTIATED_GRAPHQL_SETTINGS.GRAPHIQL,
    allow_queries_via_get=INSTANTIATED_GRAPHQL_SETTINGS.ALLOW_GET,
    debug=INSTANTIATED_GRAPHQL_SETTINGS.DEBUG
)
