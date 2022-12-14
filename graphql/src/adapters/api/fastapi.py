from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.adapters.api.graphql_app import get_graphql_app
from src.adapters.graphql.graphql_settings import GraphQLSettings
from src.adapters.webserver.uvicorn_settings import UvicornSettings


def create_fastapi_app(uvicorn_settings: UvicornSettings):
    app = FastAPI()

    # TODO: Need to lock down origins, methods and headers
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    # Create GraphQL routes
    app.include_router(
        router=get_graphql_app(GraphQLSettings(uvicorn_settings)),
        prefix="/graphql"
    )

    # Create health check
    @app.get("/healthz")
    def check_health():
        """
        Health check for server.
        """
        # TODO: Should figure out what is healthy to check for
        # .     here. Maybe a simple graphql call or a check to
        # .     see if external items are up?
        return {"Healthy": True}

    return app
