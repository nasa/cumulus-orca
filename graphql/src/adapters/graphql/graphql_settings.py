from src.adapters.uvicorn import uvicorn_settings


class GraphQLSettings:
    """
    Settings used by the GraphQL adapter.

    In addition, the uvicorn_settings
    class sets additional GRAPHQL options for dev or production.
    """
    # URI: str = os.environ.get("ORCA_DB_USER_URI", "sqlite://")
    GRAPHIQL: bool = uvicorn_settings.instantiated_settings.DEV
    DEBUG: bool = uvicorn_settings.instantiated_settings.DEV
    ALLOW_GET: bool = uvicorn_settings.instantiated_settings.DEV


instantiated_settings = GraphQLSettings()
