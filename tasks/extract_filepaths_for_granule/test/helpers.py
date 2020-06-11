"""
Name: helpers.py

Description:  helper functions for testing.
"""
import json

def create_handler_event():
    """
    create a handler event for testing.
    """
    try:
        with open('test/testevents/fixture1.json') as fil:
            event = json.load(fil)
    except EnvironmentError:  # parent of IOError, OSError *and* WindowsError where available
        with open('testevents/fixture1.json') as fil:
            event = json.load(fil)
    return event

def create_task_event():
    """
    create a task event for testing.
    """
    try:
        with open('test/testevents/task_event.json') as fil:
            event = json.load(fil)
    except EnvironmentError:  # parent of IOError, OSError *and* WindowsError where available
        with open('testevents/task_event.json') as fil:
            event = json.load(fil)
    return event

class LambdaContextMock:      #pylint: disable-msg=too-few-public-methods
    """
    create a lambda context for testing.
    """
    def __init__(self):
        self.function_name = "extract_filepaths_for_granule"
        self.function_version = 1
        self.invoked_function_arn = ("arn:aws:lambda:us-west-2:065089468788:"
                                     "function:extract_filepaths_for_granule:1")
