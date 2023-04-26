import json
import os
import random
import uuid
from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch

# noinspection PyPackageRequirements
import fastjsonschema as fastjsonschema

# noinspection PyPackageRequirements
from jsonschema.exceptions import ValidationError

import orca_recovery_adapter

# noinspection PyPackageRequirements

# Generating schema validators can take time, so do it once and reuse.
with open("schemas/output.json", "r") as raw_schema:
    _OUTPUT_VALIDATE = fastjsonschema.compile(json.loads(raw_schema.read()))


class TestOrcaRecoveryAdapter(TestCase):
    """
    Test orca_recovery_adapter functionality and business logic.
    """

    @patch("orca_recovery_adapter.Config")
    @patch("boto3.client")
    def test_task_happy_path(
        self,
        mock_boto3_client: MagicMock,
        mock_boto3_config: MagicMock,
    ):
        """
        Basic happy-path test for invoking the target lambda and receiving a 200 response.
        """
        copy_to_archive_arn = uuid.uuid4().__str__()

        payload = {
            uuid.uuid4().__str__(): uuid.uuid4().__str__(),
            uuid.uuid4().__str__(): uuid.uuid4().__str__(),
        }
        mock_payload = Mock()
        mock_payload.read = Mock(return_value=json.dumps(payload))
        response = {
            "StatusCode": 200,
            "Payload": mock_payload
        }

        mock_invoke = Mock(return_value=response)
        mock_lambda_client = Mock()
        mock_lambda_client.invoke = mock_invoke
        mock_boto3_client.return_value = mock_lambda_client

        mock_input = {
            uuid.uuid4().__str__(): uuid.uuid4().__str__(),
            uuid.uuid4().__str__(): uuid.uuid4().__str__(),
        }
        mock_config = {
            uuid.uuid4().__str__(): uuid.uuid4().__str__(),
            uuid.uuid4().__str__(): uuid.uuid4().__str__(),
        }

        event = {
            "input": mock_input,
            "config": mock_config,
        }

        with patch.dict(os.environ,
                        {
                            orca_recovery_adapter.OS_ENVIRON_COPY_TO_ARCHIVE_ARN_KEY:
                                copy_to_archive_arn
                        }):
            result = orca_recovery_adapter.task(event, None)

        mock_boto3_config.assert_called_once_with(
            read_timeout=600, retries={'total_max_attempts': 1}
        )
        mock_boto3_client.assert_called_once_with(
            "lambda",
            config=mock_boto3_config.return_value
        )
        mock_invoke.assert_called_once_with(
            FunctionName=copy_to_archive_arn,
            InvocationType="RequestResponse",  # Synchronous
            Payload=json.dumps({
                orca_recovery_adapter.ORCA_INPUT_KEY: mock_input,
                orca_recovery_adapter.ORCA_CONFIG_KEY: mock_config
            }, indent=4).encode("utf-8")
        )
        mock_payload.read.assert_called_once_with()
        self.assertEqual(payload, result)

    @patch("orca_recovery_adapter.Config")
    @patch("boto3.client")
    def test_task_status_code_not_200_raises_exception(
        self,
        mock_boto3_client: MagicMock,
        mock_boto3_config: MagicMock,
    ):
        """
        If a non-200 status code is returned, raise an error with the attached error message.
        """
        copy_to_archive_arn = uuid.uuid4().__str__()

        error_message = uuid.uuid4().__str__()
        response = {
            "StatusCode": 201,  # We only expect 200, so even 201 should fail.
            "FunctionError": error_message
        }

        mock_invoke = Mock(return_value=response)
        mock_lambda_client = Mock()
        mock_lambda_client.invoke = mock_invoke
        mock_boto3_client.return_value = mock_lambda_client

        mock_input = {
            uuid.uuid4().__str__(): uuid.uuid4().__str__(),
            uuid.uuid4().__str__(): uuid.uuid4().__str__(),
        }
        mock_config = {
            uuid.uuid4().__str__(): uuid.uuid4().__str__(),
            uuid.uuid4().__str__(): uuid.uuid4().__str__(),
        }

        event = {
            "input": mock_input,
            "config": mock_config,
        }

        with patch.dict(os.environ,
                        {
                            orca_recovery_adapter.OS_ENVIRON_COPY_TO_ARCHIVE_ARN_KEY:
                                copy_to_archive_arn
                        }):
            with self.assertRaises(Exception) as cm:
                orca_recovery_adapter.task(event, None)

        mock_boto3_config.assert_called_once_with(
            read_timeout=600, retries={'total_max_attempts': 1}
        )
        mock_boto3_client.assert_called_once_with(
            "lambda",
            config=mock_boto3_config.return_value
        )
        mock_invoke.assert_called_once_with(
            FunctionName=copy_to_archive_arn,
            InvocationType="RequestResponse",  # Synchronous
            Payload=json.dumps({
                orca_recovery_adapter.ORCA_INPUT_KEY: mock_input,
                orca_recovery_adapter.ORCA_CONFIG_KEY: mock_config
            }, indent=4).encode("utf-8")
        )
        self.assertEqual(str(cm.exception), error_message)

    @patch("orca_recovery_adapter.task")
    def test_handler_happy_path(self, mock_task: MagicMock):
        granules = [
            {
                "recoveryBucketOverride": uuid.uuid4().__str__(),
                "granuleId": uuid.uuid4().__str__(),
                "files": [
                    {
                        "fileName": uuid.uuid4().__str__(),
                        "key": uuid.uuid4().__str__()
                    }
                ],
            }
        ]

        config = {
            "buckets": {
                uuid.uuid4().__str__():
                    {"name": uuid.uuid4().__str__(), "type": uuid.uuid4().__str__()},
            },
            "fileBucketMaps": [
                {
                    "regex": uuid.uuid4().__str__(),
                    "sampleFileName": uuid.uuid4().__str__(),
                    "bucket": uuid.uuid4().__str__(),
                }
            ],
            "excludedFileExtensions": ["." + uuid.uuid4().__str__()],
            "asyncOperationId": uuid.uuid4().__str__(),
            "s3MultipartChunksizeMb": random.randint(0, 5000),  # nosec
            "defaultBucketOverride": uuid.uuid4().__str__(),
            "defaultRecoveryTypeOverride": uuid.uuid4().__str__(),
        }
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
                    "recoverFiles": [
                        {
                            "errorMessage": uuid.uuid4().__str__(),
                            "completionTime": "2023-04-26T19:12:44.213614+00:00",
                            "filename": uuid.uuid4().__str__(),
                            "keyPath": uuid.uuid4().__str__(),
                            "lastUpdate": "2023-04-26T19:12:44.213614+00:00",
                            "restoreDestination": uuid.uuid4().__str__(),
                            "requestTime": "2023-04-26T19:12:44.213614+00:00",
                            "statusId": random.randint(1, 3),  # nosec
                            "success": True,
                            "s3MultipartChunksizeMb": random.randint(0, 5000),  # nosec
                        }
                    ]
                },
            ],
            "asyncOperationId": uuid.uuid4().__str__(),
        }

        result = orca_recovery_adapter.handler(handler_input_event, handler_input_context)
        mock_task.assert_called_once_with(expected_task_input, handler_input_context)

        self.assertEqual(mock_task.return_value, result["payload"])

    @patch("orca_recovery_adapter.task")
    def test_handler_rejects_bad_output(self, mock_task: MagicMock):
        granules = [
            {
                "granuleId": uuid.uuid4().__str__(),
                "files": [
                    {
                        "fileName": uuid.uuid4().__str__(),
                        "key": uuid.uuid4().__str__()
                    }
                ],
            }
        ]

        config = {
            "buckets": {
                uuid.uuid4().__str__():
                    {"name": uuid.uuid4().__str__(), "type": uuid.uuid4().__str__()},
            },
            "fileBucketMaps": [
                {
                    "regex": uuid.uuid4().__str__(),
                    "bucket": uuid.uuid4().__str__(),
                }
            ],
        }
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
                    "recoverFiles": [
                        {
                            "filename": uuid.uuid4().__str__(),
                            "keyPath": uuid.uuid4().__str__(),
                            "lastUpdate": "2023-04-26T19:12:44.213614+00:00",
                            "restoreDestination": uuid.uuid4().__str__(),
                            "requestTime": "2023-04-26T19:12:44.213614+00:00",
                            "statusId": random.randint(1, 3),  # nosec
                            "success": True,
                        }
                    ]
                },
            ],
            "asyncOperationId": uuid.uuid4().__str__(),
        }

        with self.assertRaises(ValidationError) as cm:
            orca_recovery_adapter.handler(handler_input_event, handler_input_context)
        self.assertTrue(
            str(cm.exception).startswith("output schema: 'granuleId' is a required property"))
        mock_task.assert_called_once_with(expected_task_input, handler_input_context)
