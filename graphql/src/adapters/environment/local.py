from orca_shared.database.entities import PostgresConnectionInfo
from pydantic import BaseSettings

from src.adapters.environment.interface import EnvironmentInterface
from src.use_cases.adapter_interfaces.logger_provider import LoggerProviderInterface


class LocalSettings(BaseSettings):
    """
    Settings specific to the AWS environment.
    """
    ADMIN_DATABASE_NAME: str = "postgres"
    ADMIN_PASSWORD: str
    ADMIN_USERNAME: str = "postgres"
    DATABASE_HOST: str
    DATABASE_PORT: str = "5433"
    USER_DATABASE_NAME: str = "orca"
    APPLICATION_PASSWORD: str  # naming holdover from db_deploy
    USER_USERNAME: str = "orcauser"


class LocalEnvironment(EnvironmentInterface):

    def __init__(self):
        self.INSTANTIATED_LOCAL_SETTINGS = LocalSettings()

    def get_db_connect_info(self, logger_provider: LoggerProviderInterface) \
            -> PostgresConnectionInfo:
        """
        Args:
            logger_provider: The logger provider to use.

        Returns: A standardized object containing connection info.
        """
        db_connect_info = PostgresConnectionInfo(
            admin_database_name=self.INSTANTIATED_LOCAL_SETTINGS.ADMIN_DATABASE_NAME,
            admin_password=self.INSTANTIATED_LOCAL_SETTINGS.ADMIN_PASSWORD,
            admin_username=self.INSTANTIATED_LOCAL_SETTINGS.ADMIN_USERNAME,
            host=self.INSTANTIATED_LOCAL_SETTINGS.DATABASE_HOST,
            port=self.INSTANTIATED_LOCAL_SETTINGS.DATABASE_PORT,
            user_database_name=self.INSTANTIATED_LOCAL_SETTINGS.USER_DATABASE_NAME,
            user_password=self.INSTANTIATED_LOCAL_SETTINGS.APPLICATION_PASSWORD,
            user_username=self.INSTANTIATED_LOCAL_SETTINGS.USER_USERNAME,
        )
        return db_connect_info
