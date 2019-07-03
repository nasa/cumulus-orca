from os import path
import json

def create_event():
    try:
        with open('test/testevents/fixture1.json') as f:
            event = json.load(f)
    except EnvironmentError:  # parent of IOError, OSError *and* WindowsError where available
        with open('testevents/fixture1.json') as f:
            event = json.load(f)
    return event


def create_handler_config():
    return {
        "task": {
            "root": path.join(path.dirname(path.realpath(__file__)), "fixtures"),
            "schemas": {
                "input": "schemas/input.json",
                "config": "schemas/config.json",
                "output": "schemas/output.json"
            }
        }
    }


class LambdaContextMock:
    def __init__(self):
        self.function_name = "extract_filepaths_for_granule"
        self.function_version = 1
        self.invoked_function_arn = "arn:aws:lambda:us-west-2:065089468788:function:extract_filepaths_for_granule:1"
