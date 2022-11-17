from orca_shared.database.adapters.api import get_configuration
from orca_shared.database.entities import PostgresConnectionInfo
from pydantic import BaseSettings

from src.adapters.environment.interface import EnvironmentInterface
from src.use_cases.adapter_interfaces.logger_provider import LoggerProviderInterface


class AWSSettings(BaseSettings):
    """
    Settings specific to the AWS environment.
    """
    DB_CONNECT_INFO_SECRET_ARN: str  # Will raise error when not found/empty.


class AWSEnvironment(EnvironmentInterface):

    def __init__(self):
        self.INSTANTIATED_AWS_SETTINGS = AWSSettings()

    def get_db_connect_info(self, logger_provider: LoggerProviderInterface) \
            -> PostgresConnectionInfo:
        db_connect_info = get_configuration(
            self.INSTANTIATED_AWS_SETTINGS.DB_CONNECT_INFO_SECRET_ARN,
            logger_provider.get_logger())
        return db_connect_info
