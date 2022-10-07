import os
from pydantic import BaseSettings


# todo: Can we just pass these into main.py?
class UvicornSettings(BaseSettings):
    """Common settings used by the framework."""
    HOST: str = os.environ.get("HOST", "0.0.0.0")
    PORT: int = int(os.environ.get("PORT", "5000"))
    # todo: change key
    DEV: bool = True if os.environ.get("ORCA_ENV", "development") == "development" else False


instantiated_settings = UvicornSettings()
