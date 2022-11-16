"""
Name: main.py
Description: Main entrypoint script for the application.
"""

import uvicorn
from orca_shared.database.entities import PostgresConnectionInfo

from src.adapters.api.fastapi import create_fastapi_app
from src.adapters.graphql.initialized_adapters import adapters
from src.adapters.storage.postgres import StorageAdapterPostgres
from src.adapters.webserver.uvicorn_settings import INSTANTIATED_WEBSERVER_SETTINGS

application = create_fastapi_app()


def run(db_connect_info: PostgresConnectionInfo):

    adapters.storage = StorageAdapterPostgres(db_connect_info)
    uvicorn.run("main:application",
                host=INSTANTIATED_WEBSERVER_SETTINGS.HOST,
                port=INSTANTIATED_WEBSERVER_SETTINGS.PORT,
                reload=INSTANTIATED_WEBSERVER_SETTINGS.DEV)
