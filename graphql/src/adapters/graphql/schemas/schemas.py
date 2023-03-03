# noinspection PyPackageRequirements
from graphql.validation import NoSchemaIntrospectionCustomRule

# noinspection PyPackageRequirements
from strawberry import Schema

# noinspection PyPackageRequirements
from strawberry.extensions import AddValidationRules

from src.adapters.graphql.adapters import AdaptersStorage
from src.adapters.graphql.graphql_settings import GraphQLSettings
from src.adapters.graphql.schemas.mutations import Mutations
from src.adapters.graphql.schemas.queries import Queries

# from server.adapters.api.graphql.schemas.mutations import Mutation
# from server.adapters.api.graphql.schemas.subscriptions import Subscription


def get_schema(graphql_settings: GraphQLSettings, adapters_storage: AdaptersStorage) -> Schema:
    """
    Returns a strawberry library Schema object used for exposing the API.
    """
    # can't use constructor due to Strawberry not accepting constructed classes
    Queries.adapters_storage = adapters_storage
    Mutations.adapters_storage = adapters_storage

    return Schema(
        query=Queries,
        mutation=Mutations,
        # subscription=Subscription,
        # config=
        # types=
        extensions=[AddValidationRules([NoSchemaIntrospectionCustomRule])]
        if graphql_settings.GRAPHIQL is False else
        []
        # scalar_overrides=
    )
