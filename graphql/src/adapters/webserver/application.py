from src.adapters.environment.aws import AWSEnvironment
from src.adapters.environment.local import LocalEnvironment
from src.adapters.graphql import initialized_adapters
from src.adapters.graphql.initialized_adapters import logger_provider
from src.adapters.logger_provider.basic import BasicLoggerProvider
from src.adapters.webserver.uvicorn_settings import INSTANTIATED_WEBSERVER_SETTINGS
from src.use_cases.adapter_interfaces.logger_provider import LoggerProviderInterface


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
if INSTANTIATED_WEBSERVER_SETTINGS.RUNNING_LOCALLY:
    environment = LocalEnvironment()
else:
    environment = AWSEnvironment()

db_connect_info = environment.get_db_connect_info(
    initialized_adapters.logger_provider.static_logger_provider)

initialize_adapters()

# Don't start setting up fastapi/graphql app until adapters are ready to be referenced.
from src.adapters.api.fastapi import create_fastapi_app

# In a separate file to enable uvicorn.run to pull in statically-set properties such as adapters.
application = create_fastapi_app()
