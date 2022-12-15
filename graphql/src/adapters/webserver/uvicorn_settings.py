import os
from pydantic import BaseSettings


# todo: Give this a proper constructor to make it testable. As-is, it will auto-eval defaults on IMPORT.
class UvicornSettings(BaseSettings):
    """
    Common settings used by the framework.
    """
    HOST: str = "0.0.0.0"
    PORT: int = 5000
    DEV: bool = True if os.environ.get("ORCA_ENV", "production") == "development" else False
    DB_CONNECT_INFO: str
