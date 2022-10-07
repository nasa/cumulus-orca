from src.adapters.uvicorn import uvicorn_settings


class GraphQLSettings:
    """
    GraphQL Settings used by the GraphQL adapter.
    The settings are set by the environment and
    specifically the following variables:
       ORCA_DB_USER_URI

    In addition, the server.adapters.api.framework.settings DEV
    attribute sets additional GRAPHQL options for dev or production.
    """
    # URI: str = os.environ.get("ORCA_DB_USER_URI", "sqlite://")
    GRAPHIQL: bool = uvicorn_settings.instantiated_settings.DEV
    DEBUG: bool = uvicorn_settings.instantiated_settings.DEV
    ALLOW_GET: bool = uvicorn_settings.instantiated_settings.DEV


instantiated_settings = GraphQLSettings()
