import datetime
import json
import os
import random
import uuid
from unittest import TestCase
from unittest.mock import MagicMock, Mock, call, patch

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

    @patch("orca_recovery_adapter.get_state_machine_execution_results")
    @patch("orca_recovery_adapter.Config")
    @patch("boto3.client")
    def test_task_happy_path(
        self,
        mock_boto3_client: MagicMock,
        mock_boto3_config: MagicMock,
        mock_get_state_machine_execution_results: MagicMock,
    ):
        """
        Basic happy-path test for invoking the target lambda and receiving a 200 response.
        """
        orca_recovery_step_function_arn = uuid.uuid4().__str__()

        payload = {
            uuid.uuid4().__str__(): uuid.uuid4().__str__(),
            uuid.uuid4().__str__(): uuid.uuid4().__str__(),
        }
        response = {
            "status": "SUCCEEDED",
            "output": json.dumps(payload)
        }
        mock_get_state_machine_execution_results.return_value = response

        mock_execution_arn = Mock()
        mock_start_execution = Mock(return_value={"executionArn": mock_execution_arn})
        mock_stepfunctions_client = Mock()
        mock_stepfunctions_client.start_execution = mock_start_execution
        mock_boto3_client.return_value = mock_stepfunctions_client

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
                            orca_recovery_adapter.OS_ENVIRON_ORCA_RECOVERY_STEP_FUNCTION_ARN_KEY:
                                orca_recovery_step_function_arn
                        }):
            result = orca_recovery_adapter.task(event, None)

        mock_boto3_config.assert_called_once_with(
            read_timeout=600, retries={'total_max_attempts': 1}
        )
        mock_boto3_client.assert_called_once_with(
            "stepfunctions",
            config=mock_boto3_config.return_value
        )
        mock_start_execution.assert_called_once_with(
            stateMachineArn=orca_recovery_step_function_arn,
            input=json.dumps({
                orca_recovery_adapter.ORCA_INPUT_KEY: mock_input,
                orca_recovery_adapter.ORCA_CONFIG_KEY: mock_config
            }, indent=4)
        )
        mock_get_state_machine_execution_results.assert_called_once_with(
            mock_stepfunctions_client,
            mock_execution_arn
        )
        self.assertEqual(payload, result)

    @patch("orca_recovery_adapter.get_state_machine_execution_results")
    @patch("orca_recovery_adapter.Config")
    @patch("boto3.client")
    def test_task_status_code_not_succeeded_raises_exception(
        self,
        mock_boto3_client: MagicMock,
        mock_boto3_config: MagicMock,
        mock_get_state_machine_execution_results: MagicMock,
    ):
        """
        If a non-SUCCEEDED status code is returned, raise an error with the attached error message.
        """
        orca_recovery_step_function_arn = uuid.uuid4().__str__()

        payload = {
            uuid.uuid4().__str__(): uuid.uuid4().__str__(),
            uuid.uuid4().__str__(): uuid.uuid4().__str__(),
        }
        response = {
            "status": "NOPE",
            "output": json.dumps(payload)
        }
        mock_get_state_machine_execution_results.return_value = response

        mock_execution_arn = Mock()
        mock_start_execution = Mock(return_value={"executionArn": mock_execution_arn})
        mock_stepfunctions_client = Mock()
        mock_stepfunctions_client.start_execution = mock_start_execution
        mock_boto3_client.return_value = mock_stepfunctions_client

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
                            orca_recovery_adapter.OS_ENVIRON_ORCA_RECOVERY_STEP_FUNCTION_ARN_KEY:
                                orca_recovery_step_function_arn
                        }):
            with self.assertRaises(Exception) as cm:
                orca_recovery_adapter.task(event, None)

        mock_boto3_config.assert_called_once_with(
            read_timeout=600, retries={'total_max_attempts': 1}
        )
        mock_boto3_client.assert_called_once_with(
            "stepfunctions",
            config=mock_boto3_config.return_value
        )
        mock_start_execution.assert_called_once_with(
            stateMachineArn=orca_recovery_step_function_arn,
            input=json.dumps({
                orca_recovery_adapter.ORCA_INPUT_KEY: mock_input,
                orca_recovery_adapter.ORCA_CONFIG_KEY: mock_config
            }, indent=4)
        )
        mock_get_state_machine_execution_results.assert_called_once_with(
            mock_stepfunctions_client,
            mock_execution_arn,
        )
        self.assertEqual(f"Step function did not succeed: "
                         f"{str(response).replace('{', '{{').replace('}', '}}')}",
                         str(cm.exception))

    @patch("time.sleep")
    def test_get_state_machine_execution_results_retries_until_not_running(
        self,
        mock_sleep: MagicMock,
    ):
        mock_client = Mock()
        final_execution_state = {
            "status": "BLAH",
            uuid.uuid4().__str__(): uuid.uuid4().__str__(),
        }
        mock_client.describe_execution = Mock(side_effect=[
            {
                "status": "RUNNING",
            },
            final_execution_state,
        ])
        mock_execution_arn = Mock()
        mock_retry_interval_seconds = random.randint(0, 5)  # nosec

        result = orca_recovery_adapter.get_state_machine_execution_results(
            mock_client,
            mock_execution_arn,
            mock_retry_interval_seconds,
            20,
        )

        mock_sleep.assert_called_once_with(mock_retry_interval_seconds)
        mock_client.describe_execution.assert_has_calls([
            call(executionArn=mock_execution_arn),
            call(executionArn=mock_execution_arn),
        ])
        self.assertEqual(2, mock_client.describe_execution.call_count)

        self.assertEqual(final_execution_state, result)

    @patch("time.sleep")
    def test_get_state_machine_execution_results_retries_until_timeout(
        self,
        mock_sleep: MagicMock,
    ):
        mock_client = Mock()
        final_execution_state = {
            "status": "RUNNING",
        }
        mock_client.describe_execution = Mock(return_value=final_execution_state)
        mock_execution_arn = Mock()
        mock_retry_interval_seconds = 1

        start = datetime.datetime.utcnow()
        result = orca_recovery_adapter.get_state_machine_execution_results(
            mock_client,
            mock_execution_arn,
            mock_retry_interval_seconds,
            4,
        )
        end = datetime.datetime.utcnow()

        mock_sleep.assert_called_with(mock_retry_interval_seconds)
        mock_client.describe_execution.assert_called_with(
            executionArn=mock_execution_arn,
        )
        self.assertLess(100, mock_client.describe_execution.call_count)

        duration_seconds = (end - start).total_seconds()
        self.assertLess(2, duration_seconds)
        self.assertGreater(4, duration_seconds)

        self.assertEqual(final_execution_state, result)

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
