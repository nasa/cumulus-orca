from orca_shared.database.adapters.api import get_configuration
from pydantic import BaseSettings

from src.adapters.logger_provider.basic import BasicLoggerProvider
from src.adapters.webserver.run import run


class AWSSettings(BaseSettings):
    """
    Settings specific to the AWS environment.
    """
    DB_CONNECT_INFO_SECRET_ARN: str  # Will raise error when not found/empty.


INSTANTIATED_AWS_SETTINGS = AWSSettings()

if __name__ == "__main__":
    logger_provider = BasicLoggerProvider()

    db_connect_info = get_configuration(INSTANTIATED_AWS_SETTINGS.DB_CONNECT_INFO_SECRET_ARN,
                                        logger_provider.get_logger())
    run(db_connect_info, logger_provider)
