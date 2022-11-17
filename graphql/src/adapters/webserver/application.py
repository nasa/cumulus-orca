# todo: This file only exists as a trial for getting relative uvicorn imports working.
#  Either fix, or delete.

# Don't start setting up fastapi/graphql app until storage adapter is ready to be referenced.
from src.adapters.api.fastapi import create_fastapi_app

# In a separate file to enable uvicorn.run to pull in statically-set application property.
application = create_fastapi_app()
