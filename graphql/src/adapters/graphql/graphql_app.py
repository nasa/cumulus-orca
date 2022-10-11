# noinspection PyPackageRequirements
from strawberry.fastapi import GraphQLRouter  # todo: pull out like https://git.earthdata.nasa.gov/projects/ORCA/repos/orca-prototype-graphql/browse/src/server/adapters/api/graphql/adapter_interfaces/fastapi.py?at=refs%2Fheads%2Ffeature%2Ffastapi-strawberry-clean

from src.adapters.graphql import graphql_settings
from src.adapters.graphql.schemas import get_schema

schema = get_schema()
graphql_app = GraphQLRouter(
    schema,
    graphiql=graphql_settings.instantiated_settings.GRAPHIQL,
    allow_queries_via_get=graphql_settings.instantiated_settings.ALLOW_GET,
    debug=graphql_settings.instantiated_settings.DEBUG
)
