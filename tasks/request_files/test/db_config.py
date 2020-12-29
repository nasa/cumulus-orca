"""
This module contains helper functions for making the database donnection.
"""
import json
import os


def set_env():
    """
    Reads the values for database environment variables from a file and writes them to current environment.
    """
    with open("private_config.json") as private_file:
        private_config = json.load(private_file)

    os.environ["DATABASE_HOST"] = private_config["DATABASE_HOST"]
    os.environ["DATABASE_PORT"] = private_config["DATABASE_PORT"]
    os.environ["DATABASE_NAME"] = private_config["DATABASE_NAME"]
    os.environ["DATABASE_USER"] = private_config["DATABASE_USER"]
    os.environ["DATABASE_PW"] = private_config["DATABASE_PW"]

def del_env():
    """
    Removes the values for database environment variables from the environment.
    """
    os.environ.pop("DATABASE_HOST")
    os.environ.pop("DATABASE_PORT")
    os.environ.pop("DATABASE_NAME")
    os.environ.pop("DATABASE_USER")
    os.environ.pop("DATABASE_PW")
