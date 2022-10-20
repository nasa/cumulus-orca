"""
Name: main.py
Description: Main entrypoint script for the application.
"""
import uvicorn

from src.adapters.api.fastapi import create_fastapi_app
from src.adapters.webserver.uvicorn_settings import INSTANTIATED_WEBSERVER_SETTINGS

application = create_fastapi_app()

if __name__ == "__main__":
    uvicorn.run("main:application",
                host=INSTANTIATED_WEBSERVER_SETTINGS.HOST,
                port=INSTANTIATED_WEBSERVER_SETTINGS.PORT,
                reload=INSTANTIATED_WEBSERVER_SETTINGS.DEV)
