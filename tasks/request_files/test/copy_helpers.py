"""
This module contains helper functions for the unit tests.
"""
import json
import time

import requests

UTC_NOW_EXP_1 = requests.get_utc_now_iso()
time.sleep(1)
REQUEST_GROUP_ID_EXP_1 = requests.request_id_generator()
UTC_NOW_EXP_2 = requests.get_utc_now_iso()
time.sleep(1)
REQUEST_GROUP_ID_EXP_2 = requests.request_id_generator()
UTC_NOW_EXP_3 = requests.get_utc_now_iso()
time.sleep(1)
UTC_NOW_EXP_4 = requests.get_utc_now_iso()
time.sleep(1)
REQUEST_GROUP_ID_EXP_3 = requests.request_id_generator()
UTC_NOW_EXP_5 = requests.get_utc_now_iso()
time.sleep(1)
UTC_NOW_EXP_6 = requests.get_utc_now_iso()
time.sleep(1)
REQUEST_GROUP_ID_EXP_4 = requests.request_id_generator()
UTC_NOW_EXP_7 = requests.get_utc_now_iso()
time.sleep(1)
UTC_NOW_EXP_8 = requests.get_utc_now_iso()
time.sleep(1)
REQUEST_GROUP_ID_EXP_5 = requests.request_id_generator()
REQUEST_GROUP_ID_EXP_6 = requests.request_id_generator()

def create_handler_event():
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

def create_event2():
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


class LambdaContextMock:   #pylint: disable-msg=too-few-public-methods
    """
    create a lambda context for testing.
    """
    def __init__(self):
        self.function_name = "copy_files_to_archive"
        self.function_version = 1
        self.invoked_function_arn = (
            "arn:aws:lambda:us-west-2:065089468788:function:copy_files_to_archive:1")
