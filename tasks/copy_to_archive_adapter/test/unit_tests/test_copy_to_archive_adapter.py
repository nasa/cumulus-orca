import json
import random
import uuid
from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch

import fastjsonschema as fastjsonschema
from jsonschema.exceptions import ValidationError

import copy_to_archive_adapter

# Generating schema validators can take time, so do it once and reuse.
with open("schemas/output.json", "r") as raw_schema:
    _OUTPUT_VALIDATE = fastjsonschema.compile(json.loads(raw_schema.read()))


class TestCopyToArchiveAdapter(TestCase):
    """
    Test copy_to_archive_adapter functionality and business logic.
    """

    @patch("copy_to_archive_adapter.task")
    def test_handler_happy_path(self, mock_task: MagicMock):
        granules = [
            {
                "granuleId": uuid.uuid4().__str__(),
                "dataType": uuid.uuid4().__str__(),
                "version": uuid.uuid4().__str__(),
                "createdAt": random.randint(0, 628021800000),  # nosec
                "files": [
                    {
                        "bucket": uuid.uuid4().__str__(),
                        "key": uuid.uuid4().__str__(),
                        "checksum": uuid.uuid4().__str__(),
                        "checksumType": uuid.uuid4().__str__(),
                    }
                ],
            }
        ]

        config = {}  # Required by run_cumulus_task
        handler_input_event = {
            "payload": {"granules": granules},
            "task_config": config,
        }
        handler_input_context = Mock()

        expected_task_input = {
            "input": handler_input_event["payload"],
            "config": config,
        }
        mock_task.return_value = {
            "granules": [
                {
                    "granuleId": uuid.uuid4().__str__(),
                    "createdAt": random.randint(0, 999999999),  # nosec
                    "files": [
                        {
                            "bucket": uuid.uuid4().__str__(),
                            "key": uuid.uuid4().__str__(),
                            "checksum": uuid.uuid4().__str__(),
                            "checksumType": uuid.uuid4().__str__(),
                        }
                    ]
                },
            ],
            "copied_to_orca": [uuid.uuid4().__str__()],
        }

        result = copy_to_archive_adapter.handler(handler_input_event, handler_input_context)
        mock_task.assert_called_once_with(expected_task_input, handler_input_context)

        self.assertEqual(mock_task.return_value, result["payload"])

    @patch("copy_to_archive_adapter.task")
    def test_handler_rejects_bad_output(self, mock_task: MagicMock):
        granules = [
            {
                "granuleId": uuid.uuid4().__str__(),
                "dataType": uuid.uuid4().__str__(),
                "version": uuid.uuid4().__str__(),
                "createdAt": random.randint(0, 628021800000),  # nosec
                "files": [
                    {
                        "bucket": uuid.uuid4().__str__(),
                        "key": uuid.uuid4().__str__(),
                        "checksum": uuid.uuid4().__str__(),
                        "checksumType": uuid.uuid4().__str__(),
                    }
                ],
            }
        ]

        config = {}  # Required by run_cumulus_task
        handler_input_event = {
            "payload": {"granules": granules},
            "task_config": config,
        }
        handler_input_context = Mock()

        expected_task_input = {
            "input": handler_input_event["payload"],
            "config": config,
        }
        mock_task.return_value = {
            "granules": [
                {
                    "granuleId": uuid.uuid4().__str__(),
                    "createdAt": random.randint(0, 999999999),  # nosec
                },
            ],
            "copied_to_orca": [uuid.uuid4().__str__()],
        }

        with self.assertRaises(ValidationError) as cm:
            copy_to_archive_adapter.handler(handler_input_event, handler_input_context)
        self.assertTrue(
            str(cm.exception).startswith("output schema: 'files' is a required property"))
        mock_task.assert_called_once_with(expected_task_input, handler_input_context)

    def test_handler_integration(self):
        """
        Full run-through to make sure output is truly formatted input.
        """
        granules = [
            {
                "granuleId": uuid.uuid4().__str__(),
                "dataType": uuid.uuid4().__str__(),
                "version": uuid.uuid4().__str__(),
                "createdAt": random.randint(0, 628021800000),  # nosec
                "files": [
                    {
                        "bucket": uuid.uuid4().__str__(),
                        "key": uuid.uuid4().__str__(),
                        "checksum": uuid.uuid4().__str__(),
                        "checksumType": uuid.uuid4().__str__(),
                    }
                ],
            }
        ]

        config = {}  # Required by run_cumulus_task
        handler_input_event = {
            "payload": {"granules": granules},
            "task_config": config,
        }
        handler_input_context = Mock()

        result = copy_to_archive_adapter.handler(handler_input_event, handler_input_context)

        self.assertEqual({"granules": granules}, result["payload"])
