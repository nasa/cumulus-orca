from pydantic import BaseSettings


class UvicornSettings(BaseSettings):
    """
    Common settings used by the framework.
    """
    HOST: str = "0.0.0.0" # nosec
    PORT: int = 5000
    ORCA_ENV = "production"
    DB_CONNECT_INFO: str

    # noinspection PyPep8Naming
    def get_DEV(self) -> bool:
        return True if self.ORCA_ENV == "development" else False
    DEV = property(get_DEV)
