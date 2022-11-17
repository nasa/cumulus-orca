"""
Name: main.py
Description: Main entrypoint script for the application.
"""

import uvicorn
from orca_shared.database.entities import PostgresConnectionInfo

from src.adapters.graphql.initialized_adapters import logger_provider
from src.adapters.webserver.uvicorn_settings import INSTANTIATED_WEBSERVER_SETTINGS
from src.use_cases.adapter_interfaces.logger_provider import LoggerProviderInterface


def run(db_connect_info: PostgresConnectionInfo,
        initialized_logger_provider: LoggerProviderInterface):
    logger_provider.logger_provider = initialized_logger_provider

    # Don't start setting up adapters until the static logger adapter is ready to be referenced.
    # todo: This feels substantially more gross to me than passing logger via parameters.
    #  Need another solution.
    from src.adapters.graphql.initialized_adapters import adapters
    from src.adapters.storage.postgres import StorageAdapterPostgres
    adapters.storage = StorageAdapterPostgres(db_connect_info)

    # Don't start setting up fastapi/graphql app until adapters are ready to be referenced.
    from src.adapters.api.fastapi import create_fastapi_app

    uvicorn.run(
        # Many examples place the application init in the same file as `uvicorn.run`.
        # This actually leads to the init being run twice,
        # as uvicorn.run creates a new instance of the module/class containing `application`
        # before accessing the application property.
        # This also means that the application property cannot be set outside a static context,
        # as any changes will be not found when the new instance is created/accessed.
        # Additionally, this makes it impossible to set properties such as adapters,
        # as the new instance will not know about any changes.
        # Note that relative paths are not properly supported for this path.
        app=create_fastapi_app(),  # "src.adapters.webserver.application:application"
        host=INSTANTIATED_WEBSERVER_SETTINGS.HOST,
        port=INSTANTIATED_WEBSERVER_SETTINGS.PORT,
        # Can only enable 'reload' functionality by passing as an import string.
        # reload=INSTANTIATED_WEBSERVER_SETTINGS.DEV
    )
