import json

from orca_shared.database.entities import PostgresConnectionInfo
from orca_shared.database.use_cases import create_postgres_connection_uri
from orca_shared.database.use_cases.validation import validate_config

from src.adapters.api.fastapi import create_fastapi_app
from src.adapters.graphql.adapters import AdaptersStorage
from src.adapters.logger_provider.json import JsonLoggerProvider
from src.adapters.storage.internal_reconciliation_postgres import (
    InternalReconciliationStorageAdapterPostgres,
)
from src.adapters.storage.postgres import StorageAdapterPostgres
from src.adapters.webserver.uvicorn_settings import UvicornSettings
from src.adapters.word_generation.word_generation import UUIDWordGeneration

S3_ACCESS_CREDENTIALS_ACCESS_KEY_KEY = "s3_access_key"
S3_ACCESS_CREDENTIALS_SECRET_KEY_KEY = "s3_secret_key"  # nosec


def get_application(uvicorn_settings: UvicornSettings):
    """
    Sets up an application for use with uvicorn.

    Args:
        uvicorn_settings: Contains settings required by application components.
    """
    initialized_logger_provider = JsonLoggerProvider()
    logger = initialized_logger_provider.get_logger("Setup")

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
        db_connect_info, logger
    )
    admin_connection_uri = create_postgres_connection_uri.create_admin_uri(
        db_connect_info, logger, db_connect_info.user_database_name,
    )

    s3_credentials = json.loads(
        uvicorn_settings.S3_ACCESS_CREDENTIALS
    )
    s3_access_key = s3_credentials[S3_ACCESS_CREDENTIALS_ACCESS_KEY_KEY]
    s3_secret_key = s3_credentials[S3_ACCESS_CREDENTIALS_SECRET_KEY_KEY]

    adapters_storage = AdaptersStorage(
        UUIDWordGeneration(),
        StorageAdapterPostgres(user_connection_uri),
        InternalReconciliationStorageAdapterPostgres(
            user_connection_uri,
            admin_connection_uri,
            s3_access_key,
            s3_secret_key
        ),
        initialized_logger_provider
    )

    return create_fastapi_app(uvicorn_settings, adapters_storage)
