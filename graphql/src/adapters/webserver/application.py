import json
import logging

from orca_shared.database.entities import PostgresConnectionInfo
from orca_shared.database.use_cases.validation import validate_config

from src.adapters.graphql import initialized_adapters
from src.adapters.graphql.initialized_adapters import logger_provider
from src.adapters.logger_provider.basic import BasicLoggerProvider
from src.adapters.webserver.uvicorn_settings import INSTANTIATED_WEBSERVER_SETTINGS


def initialize_logger_provider():
    initialized_logger_provider = BasicLoggerProvider()
    initialized_adapters.logger_provider.static_logger_provider = initialized_logger_provider


def initialize_adapters():
    # Don't start setting up adapters until the static logger adapter is ready to be referenced.
    # todo: This feels substantially more gross to me than passing logger via parameters.
    from src.adapters.graphql.initialized_adapters import adapters
    from src.adapters.storage.postgres import StorageAdapterPostgres
    adapters.storage = StorageAdapterPostgres(db_connect_info)


initialize_logger_provider()

# todo: Make the loads and init a separate function in shared_db
db_connect_info = json.loads(
    INSTANTIATED_WEBSERVER_SETTINGS.DB_CONNECT_INFO
)
db_connect_info = PostgresConnectionInfo(
    admin_database_name=db_connect_info["admin_database"],
    admin_username=db_connect_info["admin_username"],
    admin_password=db_connect_info["admin_password"],
    user_username=db_connect_info["user_username"],
    user_password=db_connect_info["user_password"],
    user_database_name=db_connect_info["user_database"],
    host=db_connect_info["host"],
    port=db_connect_info["port"],
)
validate_config(
    db_connect_info,
    initialized_adapters.logger_provider.static_logger_provider.get_logger()
)

initialize_adapters()

# Don't start setting up fastapi/graphql app until adapters are ready to be referenced.
from src.adapters.api.fastapi import create_fastapi_app

application = create_fastapi_app()
