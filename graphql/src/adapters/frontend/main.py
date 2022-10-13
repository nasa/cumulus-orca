"""
Name: main.py
Description: Main entrypoint script for the application.
"""
import uvicorn

from src import adapters
from src.adapters import api
from src.adapters.api.fastapi import create_fastapi_app
from src.adapters.frontend import uvicorn_settings

application = adapters.api.fastapi.create_fastapi_app()

if __name__ == "__main__":
    uvicorn.run("main:application",
                host=uvicorn_settings.instantiated_settings.HOST,
                port=uvicorn_settings.instantiated_settings.PORT,
                reload=uvicorn_settings.instantiated_settings.DEV)
