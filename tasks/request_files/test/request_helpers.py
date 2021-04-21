"""
This module contains helper functions for the unit tests.
"""
import datetime
import json
import os
import time
import uuid
from unittest.mock import Mock
import boto3

# import restore_requests

REQUEST_ID1 = str(uuid.uuid4())
REQUEST_ID2 = str(uuid.uuid4())
REQUEST_ID3 = str(uuid.uuid4())
REQUEST_ID4 = str(uuid.uuid4())
REQUEST_ID5 = str(uuid.uuid4())
REQUEST_ID6 = str(uuid.uuid4())
REQUEST_ID7 = str(uuid.uuid4())
REQUEST_ID8 = str(uuid.uuid4())
REQUEST_ID9 = str(uuid.uuid4())
REQUEST_ID10 = str(uuid.uuid4())
REQUEST_ID11 = str(uuid.uuid4())
REQUEST_ID12 = str(uuid.uuid4())

UTC_NOW_EXP_1 = datetime.datetime.utcnow().isoformat()
time.sleep(1)
REQUEST_GROUP_ID_EXP_1 = str(uuid.uuid4())
UTC_NOW_EXP_2 = datetime.datetime.utcnow().isoformat()
time.sleep(1)
REQUEST_GROUP_ID_EXP_2 = str(uuid.uuid4())
UTC_NOW_EXP_3 = datetime.datetime.utcnow().isoformat()
time.sleep(1)
UTC_NOW_EXP_4 = datetime.datetime.utcnow().isoformat()
time.sleep(1)
REQUEST_GROUP_ID_EXP_3 = str(uuid.uuid4())
UTC_NOW_EXP_5 = datetime.datetime.utcnow().isoformat()
time.sleep(1)
UTC_NOW_EXP_6 = datetime.datetime.utcnow().isoformat()
time.sleep(1)
REQUEST_GROUP_ID_EXP_4 = str(uuid.uuid4())
UTC_NOW_EXP_7 = datetime.datetime.utcnow().isoformat()
time.sleep(1)
UTC_NOW_EXP_8 = datetime.datetime.utcnow().isoformat()
time.sleep(1)
REQUEST_GROUP_ID_EXP_5 = str(uuid.uuid4())
UTC_NOW_EXP_9 = datetime.datetime.utcnow().isoformat()
time.sleep(1)
REQUEST_GROUP_ID_EXP_6 = str(uuid.uuid4())
UTC_NOW_EXP_10 = datetime.datetime.utcnow().isoformat()
time.sleep(1)
UTC_NOW_EXP_11 = datetime.datetime.utcnow().isoformat()


def create_handler_event():
    """
    create a handler event for testing.
    """
    try:
        with open('test/testevents/request_files_fixture1.json') as fil:
            event = json.load(fil)
    except EnvironmentError:  # parent of IOError, OSError *and* WindowsError where available
        with open('testevents/request_files_fixture1.json') as fil:
            event = json.load(fil)
    return event


def create_copy_handler_event():
    """
    create a handler event for testing.
    """
    try:
        with open('test/testevents/copy_exp_event_1.json') as fil:
            event = json.load(fil)
    except EnvironmentError:  # parent of IOError, OSError *and* WindowsError where available
        with open('testevents/copy_exp_event_1.json') as fil:
            event = json.load(fil)
    return event


def create_copy_event2():
    """
    create a second handler event for testing.
    """
    try:
        with open('test/testevents/copy_exp_event_2.json') as fil:
            event = json.load(fil)
    except EnvironmentError:  # parent of IOError, OSError *and* WindowsError where available
        with open('testevents/copy_exp_event_2.json') as fil:
            event = json.load(fil)
    return event


def myconverter(obj):  # pylint: disable-msg=inconsistent-return-statements
    """
    Returns the current utc timestamp as a string in isoformat
    ex. '2019-07-17T17:36:38.494918'
    """
    if isinstance(obj, datetime.datetime):
        return obj.__str__()


class LambdaContextMock:  # pylint: disable-msg=too-few-public-methods
    """
    create a lambda context for testing.
    """

    def __init__(self):
        self.function_name = "request_files"
        self.function_version = 1
        self.invoked_function_arn = "arn:aws:lambda:us-west-2:065089468788:function:request_files:1"
