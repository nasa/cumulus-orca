from src.adapters.webserver.uvicorn_settings import INSTANTIATED_WEBSERVER_SETTINGS


class GraphQLSettings:
    """
    Settings used by the GraphQL adapter.

    In addition, the uvicorn_settings
    class sets additional GRAPHQL options for dev or production.
    """
    # URI: str = os.environ.get("ORCA_DB_USER_URI", "sqlite://")
    GRAPHIQL: bool = INSTANTIATED_WEBSERVER_SETTINGS.DEV
    DEBUG: bool = INSTANTIATED_WEBSERVER_SETTINGS.DEV
    ALLOW_GET: bool = INSTANTIATED_WEBSERVER_SETTINGS.DEV


INSTANTIATED_GRAPHQL_SETTINGS = GraphQLSettings()
