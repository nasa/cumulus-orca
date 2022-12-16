from src.adapters.webserver.uvicorn_settings import UvicornSettings


class GraphQLSettings:
    """
    Settings used by the GraphQL adapter.

    In addition, the uvicorn_settings
    class sets additional GRAPHQL options for dev or production.
    """
    # URI: str = os.environ.get("ORCA_DB_USER_URI", "sqlite://")
    GRAPHIQL: bool
    DEBUG: bool
    ALLOW_GET: bool

    def __init__(self, webserver_settings: UvicornSettings):
        self.GRAPHIQL = webserver_settings.DEV
        self.DEBUG = webserver_settings.DEV
        self.ALLOW_GET = webserver_settings.DEV
