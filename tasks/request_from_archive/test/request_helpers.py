"""
This module contains helper functions for the unit tests.
"""
import json


def create_handler_event():
    """
    create a handler event for testing.
    """
    try:
        with open('test/testevents/request_from_archive_fixture1.json') as fil:
            event = json.load(fil)
    except EnvironmentError:  # parent of IOError, OSError *and* WindowsError where available
        with open('testevents/request_from_archive_fixture1.json') as fil:
            event = json.load(fil)
    return event


class LambdaContextMock:  # pylint: disable-msg=too-few-public-methods
    """
    create a lambda context for testing.
    """

    def __init__(self):
        self.function_name = "request_from_archive"
        self.function_version = 1
        self.invoked_function_arn = "arn:aws:lambda:us-west-2:065089468788:\
            function:request_from_archive:1"
