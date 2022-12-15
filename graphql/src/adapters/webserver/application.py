import json

from orca_shared.database.entities import PostgresConnectionInfo
from orca_shared.database.use_cases import create_postgres_connection_uri
from orca_shared.database.use_cases.validation import validate_config

from src.adapters.api.fastapi import create_fastapi_app
from src.adapters.graphql.adapters import AdaptersStorage
from src.adapters.logger_provider.basic import BasicLoggerProvider
from src.adapters.storage.postgres import StorageAdapterPostgres
from src.adapters.webserver.uvicorn_settings import UvicornSettings
from src.adapters.word_generation.word_generation import UUIDWordGeneration

initialized_logger_provider = BasicLoggerProvider()
logger = initialized_logger_provider.get_logger("Setup")

uvicorn_settings = UvicornSettings()  # todo: pass in via parameter

# todo: Make the loads and init a separate function in shared_db
db_connect_info = json.loads(
    uvicorn_settings.DB_CONNECT_INFO
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
    logger
)

user_connection_uri = create_postgres_connection_uri.create_user_uri(
    db_connect_info, logger)
adapters_storage = AdaptersStorage(
    UUIDWordGeneration(),
    StorageAdapterPostgres(user_connection_uri),
    initialized_logger_provider
)

application = create_fastapi_app(uvicorn_settings, adapters_storage)
