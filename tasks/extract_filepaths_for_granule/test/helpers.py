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
        with open('test/unit_tests/testevents/fixture1.json') as fil:
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
        with open('test/unit_tests/testevents/task_event.json') as fil:
            event = json.load(fil)
    except EnvironmentError:  # parent of IOError, OSError *and* WindowsError where available
        with open('testevents/task_event.json') as fil:
            event = json.load(fil)
    return event
