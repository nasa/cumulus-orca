"""
Name: test_post_to_queue_and_trigger_step_function.py
Description:  Unit tests for test_post_to_queue_and_trigger_step_function.py.
"""
import json
import os
import unittest
import uuid
from unittest.mock import MagicMock, Mock, patch

import boto3
from fastjsonschema import JsonSchemaValueException
from moto import mock_sqs

import post_to_queue_and_trigger_step_function
import sqs_library


class TestPostToQueueAndTriggerStepFunction(
    unittest.TestCase
):  # pylint: disable-msg=too-many-instance-attributes
    """
    TestPostToQueueAndTriggerStepFunction.
    """

    # Create the mock for SQS unit tests
    mock_sqs = mock_sqs()

    def setUp(self):
        """
        Perform initial setup for the tests.
        """
        self.mock_sqs.start()
        self.test_sqs = boto3.resource("sqs", region_name="us-east-2")
        self.queue = self.test_sqs.create_queue(QueueName="test-queue")
        self.queue_url = self.queue.url

    def tearDown(self):
        """
        Perform teardown for the tests
        """
        self.mock_sqs.stop()

    @patch("post_to_queue_and_trigger_step_function.trigger_step_function")
    @patch("sqs_library.post_to_fifo_queue")
    @patch("post_to_queue_and_trigger_step_function.translate_record_body")
    def test_process_record_happy_path(
        self,
        mock_translate_record_body: MagicMock,
        mock_post_to_fifo_queue: MagicMock,
        mock_trigger_step_function: MagicMock,
    ):
        mock_target_queue_url = Mock()
        mock_step_function_arn = Mock()
        mock_record_body = Mock()

        post_to_queue_and_trigger_step_function.process_record(
            {"body": mock_record_body},
            mock_target_queue_url,
            mock_step_function_arn,
        )

        mock_translate_record_body.assert_called_once_with(mock_record_body)
        mock_post_to_fifo_queue.assert_called_once_with(
            mock_target_queue_url, mock_translate_record_body.return_value
        )
        mock_trigger_step_function.assert_called_once_with(
            mock_step_function_arn,
        )

    def test_translate_record_body_happy_path(self):
        aws_region = uuid.uuid4().__str__()
        bucket_name = uuid.uuid4().__str__()
        object_key = uuid.uuid4().__str__()

        result = post_to_queue_and_trigger_step_function.translate_record_body(
            json.dumps(
                {
                    "awsRegion": aws_region,
                    "s3": {
                        "bucket": {"name": bucket_name},
                        "object": {"key": object_key},
                    },
                }
            )
        )

        self.assertEqual(
            {
                post_to_queue_and_trigger_step_function.OUTPUT_REPORT_BUCKET_REGION_KEY: aws_region,
                post_to_queue_and_trigger_step_function.OUTPUT_REPORT_BUCKET_NAME_KEY: bucket_name,
                post_to_queue_and_trigger_step_function.OUTPUT_MANIFEST_KEY_KEY: object_key,
            },
            result,
        )

    def test_translate_record_body_rejects_bad_input(self):
        aws_region = uuid.uuid4().__str__()
        object_key = uuid.uuid4().__str__()

        with self.assertRaises(JsonSchemaValueException) as cm:
            post_to_queue_and_trigger_step_function.translate_record_body(
                json.dumps(
                    {
                        "awsRegion": aws_region,
                        "s3": {
                            "object": {"key": object_key},
                        },
                    }
                )
            )
        self.assertEqual(
            f"data.s3 must contain ['bucket', 'object'] properties", str(cm.exception)
        )

    @patch("boto3.client")
    def test_trigger_step_function_happy_path(
        self,
        mock_client: MagicMock,
    ):
        mock_step_function_arn = Mock()

        post_to_queue_and_trigger_step_function.trigger_step_function(
            mock_step_function_arn
        )

        mock_client.assert_called_once_with("stepfunctions")
        mock_client.return_value.start_execution.assert_called_once_with(
            stateMachineArn=mock_step_function_arn
        )

    @patch("post_to_queue_and_trigger_step_function.process_record")
    def test_handler_happy_path(
        self,
        mock_process_record: MagicMock,
    ):
        target_queue_url = uuid.uuid4().__str__()
        step_function_arn = uuid.uuid4().__str__()
        record = {"body": uuid.uuid4().__str__()}

        with patch.dict(
            os.environ,
            {
                post_to_queue_and_trigger_step_function.OS_ENVIRON_TARGET_QUEUE_URL_KEY: target_queue_url,
                post_to_queue_and_trigger_step_function.OS_ENVIRON_STEP_FUNCTION_ARN_KEY: step_function_arn,
            },
        ):
            post_to_queue_and_trigger_step_function.handler(
                {"Records": [record]}, Mock()
            )

        mock_process_record.assert_called_once_with(
            record, target_queue_url, step_function_arn
        )

    @patch("post_to_queue_and_trigger_step_function.process_record")
    def test_handler_rejects_bad_input(
        self,
        mock_process_record: MagicMock,
    ):
        target_queue_url = uuid.uuid4().__str__()
        step_function_arn = uuid.uuid4().__str__()
        record = {"body": 1}

        with self.assertRaises(JsonSchemaValueException) as cm:
            with patch.dict(
                os.environ,
                {
                    post_to_queue_and_trigger_step_function.OS_ENVIRON_TARGET_QUEUE_URL_KEY: target_queue_url,
                    post_to_queue_and_trigger_step_function.OS_ENVIRON_STEP_FUNCTION_ARN_KEY: step_function_arn,
                },
            ):
                post_to_queue_and_trigger_step_function.handler(
                    {"Records": [record]}, Mock()
                )
        self.assertEqual("data.Records[0].body must be string", str(cm.exception))

        mock_process_record.assert_not_called()

    @patch("post_to_queue_and_trigger_step_function.LOGGER")
    @patch("post_to_queue_and_trigger_step_function.process_record")
    def test_handler_missing_env_variables_raises_error(
        self,
        mock_process_record: MagicMock,
        mock_logger: MagicMock,
    ):
        """
        If environment variables are missing, raise error and halt.
        """
        target_queue_url = uuid.uuid4().__str__()
        step_function_arn = uuid.uuid4().__str__()
        record = {"body": uuid.uuid4().__str__()}

        for key in [
            post_to_queue_and_trigger_step_function.OS_ENVIRON_TARGET_QUEUE_URL_KEY,
            post_to_queue_and_trigger_step_function.OS_ENVIRON_STEP_FUNCTION_ARN_KEY,
        ]:
            with patch.dict(
                os.environ,
                {
                    post_to_queue_and_trigger_step_function.OS_ENVIRON_TARGET_QUEUE_URL_KEY: target_queue_url,
                    post_to_queue_and_trigger_step_function.OS_ENVIRON_STEP_FUNCTION_ARN_KEY: step_function_arn,
                },
            ):
                with self.subTest(key):
                    os.environ.pop(key)
                    with self.assertRaises(KeyError) as cm:
                        post_to_queue_and_trigger_step_function.handler(
                            {"Records": [record]}, Mock()
                        )
                    self.assertEqual(f"'{key}'", str(cm.exception))
                    mock_process_record.assert_not_called()

    @patch("post_to_queue_and_trigger_step_function.process_record")
    def test_handler_rejects_multiple_records(
        self,
        mock_process_record: MagicMock,
    ):
        target_queue_url = uuid.uuid4().__str__()
        step_function_arn = uuid.uuid4().__str__()

        with self.assertRaises(ValueError) as cm:
            with patch.dict(
                os.environ,
                {
                    post_to_queue_and_trigger_step_function.OS_ENVIRON_TARGET_QUEUE_URL_KEY: target_queue_url,
                    post_to_queue_and_trigger_step_function.OS_ENVIRON_STEP_FUNCTION_ARN_KEY: step_function_arn,
                },
            ):
                post_to_queue_and_trigger_step_function.handler(
                    {
                        "Records": [
                            {"body": uuid.uuid4().__str__()},
                            {"body": uuid.uuid4().__str__()},
                        ]
                    },
                    Mock(),
                )
        self.assertEqual("Must be passed a single record. Was 2", str(cm.exception))

        mock_process_record.assert_not_called()

    # copied from shared_db.py
    @patch("time.sleep")
    def test_retry_operational_error_happy_path(self, mock_sleep: MagicMock):
        expected_result = Mock()

        @sqs_library.retry_error(3)
        def dummy_call():
            return expected_result

        result = dummy_call()

        self.assertEqual(expected_result, result)
        mock_sleep.assert_not_called()

    # copied from shared_db.py
    @patch("time.sleep")
    def test_retry_error_error_retries_and_raises(self, mock_sleep: MagicMock):
        """
        If the error raised is an OperationalError, it should retry up to the maximum allowed.
        """
        max_retries = 16
        # I have not tested that the below is a perfect recreation of an AdminShutdown error.
        expected_error = Exception()

        @sqs_library.retry_error(max_retries)
        def dummy_call():
            raise expected_error

        try:
            dummy_call()
        except Exception as caught_error:
            self.assertEqual(expected_error, caught_error)
            self.assertEqual(max_retries, mock_sleep.call_count)
            return
        self.fail("Error not raised.")

    @patch("time.sleep")
    @patch.dict(os.environ, {"AWS_DEFAULT_REGION": "us-east-2"}, clear=True)
    def test_post_to_fifo_queue_happy_path(self, mock_sleep: MagicMock):
        """
        SQS library happy path. Checks that the message sent to SQS is same as the message received from SQS.
        """
        sqs_body = {
            post_to_queue_and_trigger_step_function.OUTPUT_REPORT_BUCKET_REGION_KEY: uuid.uuid4().__str__(),
            post_to_queue_and_trigger_step_function.OUTPUT_MANIFEST_KEY_KEY: uuid.uuid4().__str__(),
            post_to_queue_and_trigger_step_function.OUTPUT_REPORT_BUCKET_NAME_KEY: uuid.uuid4().__str__(),
        }
        # Send values to the function
        sqs_library.post_to_fifo_queue(
            self.queue_url,
            sqs_body,
        )
        # grabbing queue contents after the message is sent
        queue_contents = self.queue.receive_messages()
        queue_output_body = json.loads(queue_contents[0].body)

        # Testing required fields
        self.assertEqual(queue_output_body, sqs_body)

    # todo: since sleep is not called in function under test, this violates good unit test practices.
    @patch("time.sleep")
    @patch.dict(os.environ, {"AWS_DEFAULT_REGION": "us-east-2"}, clear=True)
    def test_post_to_fifo_queue_retry_failures(self, mock_sleep: MagicMock):
        """
        Produces a failure and checks if retries are performed in the SQS library.
        """
        sqs_body = {
            post_to_queue_and_trigger_step_function.OUTPUT_REPORT_BUCKET_REGION_KEY: uuid.uuid4().__str__(),
            post_to_queue_and_trigger_step_function.OUTPUT_MANIFEST_KEY_KEY: uuid.uuid4().__str__(),
            post_to_queue_and_trigger_step_function.OUTPUT_REPORT_BUCKET_NAME_KEY: uuid.uuid4().__str__(),
        }
        # url is intentionally set wrong so send_message will fail.
        # Send values to the function
        with self.assertRaises(Exception) as cm:
            sqs_library.post_to_fifo_queue(
                "dummy",
                sqs_body,
            )
        self.assertEqual(
            "An error occurred (AWS.SimpleQueueService.NonExistentQueue) when calling the SendMessage operation: The "
            "specified queue does not exist for this wsdl version.",
            str(cm.exception),
        )
        self.assertEqual(3, mock_sleep.call_count)
