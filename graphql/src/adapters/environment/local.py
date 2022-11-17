from orca_shared.database.entities import PostgresConnectionInfo
from pydantic import BaseSettings

from src.adapters.webserver.run import run


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


INSTANTIATED_LOCAL_SETTINGS = LocalSettings()

if __name__ == "__main__":
    db_connect_info = PostgresConnectionInfo(
        admin_database_name=INSTANTIATED_LOCAL_SETTINGS.ADMIN_DATABASE_NAME,
        admin_password=INSTANTIATED_LOCAL_SETTINGS.ADMIN_PASSWORD,
        admin_username=INSTANTIATED_LOCAL_SETTINGS.ADMIN_USERNAME,
        host=INSTANTIATED_LOCAL_SETTINGS.DATABASE_HOST,
        port=INSTANTIATED_LOCAL_SETTINGS.DATABASE_PORT,
        user_database_name=INSTANTIATED_LOCAL_SETTINGS.USER_DATABASE_NAME,
        user_password=INSTANTIATED_LOCAL_SETTINGS.APPLICATION_PASSWORD,
        user_username=INSTANTIATED_LOCAL_SETTINGS.USER_USERNAME,
    )
    run(db_connect_info)
