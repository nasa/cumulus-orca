import json
import os
from http import HTTPStatus
from unittest import TestCase
from unittest.mock import MagicMock, patch

from src.simple_input.adapter import lambda_handler


def load_sample_event_from_file(test_event_file_name: str) -> dict:
    """
    Loads test events from the file system
    """
    event_file_name = f"tests/events/{test_event_file_name}.json"
    with open(event_file_name, "r", encoding="UTF-8") as file_handle:
        event = json.load(file_handle)
        return event


class TestLambdaHandler(TestCase):
    """
    Loads an event and tests the lambda handler and
    routing.
    """

    @patch.dict(
        os.environ,
        {
            "DEFAULT_STORAGE_CLASS": "GLACIER",
            "DEFAULT_ORCA_BUCKET": "orca_primary_archive",
            "DEFAULT_MULTIPART_CHUNKSIZE_MB": "256",
        },
        clear=True,
    )
    def test_lambda_handler_success(self):
        """ """
        return_value_success = {
            "statusCode": HTTPStatus.OK,
            "body": "{\"message\":\"this is a test with a config of {'storage_class': 'GLACIER', 'orca_bucket': 'orca_primary_archive', 'multipart_chunksize': 256, 'excluded_files_regex': None}\",\"errorCode\":null}",  # noqa: E501
            "isBase64Encoded": False,
            "multiValueHeaders": {
                "Content-Type": [
                    "application/json"
                ]
            }
        }
        test_event = load_sample_event_from_file("test_event_success")
        test_context = MagicMock(
            function_name="simple_task",
            memory_limit_in_mb=2048,
            invoked_function_arn="arn:Lambda:123456789:test_simple_task",
            aws_request_id="A123456789",
        )
        return_value = lambda_handler(event=test_event, context=test_context)

        # Checks
        self.assertEqual(return_value, return_value_success)
