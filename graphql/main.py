from pydantic import BaseSettings

from src.adapters.environment.aws import AWSEnvironment
from src.adapters.environment.local import LocalEnvironment
from src.adapters.logger_provider.basic import BasicLoggerProvider
from src.adapters.webserver.run import run


class BasicSettings(BaseSettings):
    """
    Settings specific to the AWS environment.
    """
    RUNNING_LOCALLY: bool = False


if __name__ == "__main__":
    instantiated_basic_settings = BasicSettings()
    logger_provider = BasicLoggerProvider()
    if instantiated_basic_settings.RUNNING_LOCALLY:
        # Importing a class in Python auto-magically instantiates it,
        # which will make Pydantic auto-magically check settings.
        # This is dangerous, as many environment variables are not set in the other environment.
        environment = LocalEnvironment()
    else:
        environment = AWSEnvironment()

    db_connect_info = environment.get_db_connect_info(logger_provider)

    run(db_connect_info, logger_provider)
