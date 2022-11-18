"""
Name: main.py
Description: Main entrypoint script for the application.
"""

import uvicorn

from src.adapters.webserver.uvicorn_settings import INSTANTIATED_WEBSERVER_SETTINGS

if __name__ == "__main__":
    uvicorn.run(
        # uvicorn.run creates a fresh instance of the module/class containing `application`
        # before accessing the application property.
        #
        # Many examples place the application init as a property in this file, which
        # leads to the init being run twice,
        #
        # A fresh module instance means the application cannot be set outside a static context.
        # Note that relative paths are not properly supported for this path.
        app="application:application",
        # _create_application(),  # "src.adapters.webserver.application:application"
        host=INSTANTIATED_WEBSERVER_SETTINGS.HOST,
        port=INSTANTIATED_WEBSERVER_SETTINGS.PORT,
        # Can only enable 'reload' functionality by passing as an import string.
        reload=INSTANTIATED_WEBSERVER_SETTINGS.DEV
    )
