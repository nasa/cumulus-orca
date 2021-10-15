"""
Name: manual_test.py

Description: Runs the db_deploy Lambda code to perform manual tests.
"""
import os
import sys


def set_search_path():
    """
    Some silliness we have to do to import the modules.
    """
    our_base = os.path.abspath(os.path.join(os.getcwd(), "../.."))
    if our_base not in sys.path:
        sys.path.insert(0, our_base)


def get_configuration():
    """
    Sets a static configuration so testing is easy. Only HOST and PASSWORDS
    are variable per user.
    """
    my_host = os.getenv("DATABASE_HOST")
    my_admin_pass = os.getenv("ADMIN_PASSWORD")
    my_app_pass = os.getenv("APPLICATION_PASSWORD")

    return {
        "admin_database": "postgres",
        "admin_password": my_admin_pass,
        "admin_username": "postgres",
        "host": my_host,
        "port": "5433",
        "user_database": "disaster_recovery",
        "user_password": my_app_pass,
        "user_username": "orcauser",  
    }


if __name__ == "__main__":
    set_search_path()
    from db_deploy import task
    from orca_shared.database.shared_db import logger

    logger.info("Beginning manual test.")
    # We skip handle since we do not want to create the secretmanager objects
    # and logging setup so we do not have to pass an event and context. This is
    # for pure functionality testing of the SQL and the call order.
    task(get_configuration())
    logger.info("Manual test complete.")
