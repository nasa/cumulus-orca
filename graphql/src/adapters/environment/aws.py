import logging

from orca_shared.database.adapters.api import get_configuration
from pydantic import BaseSettings

from src.adapters.webserver.main import run


class AWSSettings(BaseSettings):
    """
    Settings specific to the AWS environment.
    """
    DB_CONNECT_INFO_SECRET_ARN: str  # Will raise error when not found/empty.


INSTANTIATED_AWS_SETTINGS = AWSSettings()

if __name__ == "__main__":
    db_connect_info = get_configuration(INSTANTIATED_AWS_SETTINGS.DB_CONNECT_INFO_SECRET_ARN,
                                        logging.Logger())  # todo: pass in logger
    run(db_connect_info)
