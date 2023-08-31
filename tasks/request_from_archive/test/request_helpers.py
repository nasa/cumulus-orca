"""
This module contains helper functions for the unit tests.
"""
import json


def create_handler_event():
    """
    create a handler event for testing.
    """
    try:
        with open("test/testevents/request_from_archive_fixture1.json") as fil:
            event = json.load(fil)
    except EnvironmentError:  # parent of IOError, OSError *and* WindowsError where available
        with open("testevents/request_from_archive_fixture1.json") as fil:
            event = json.load(fil)
    return event
