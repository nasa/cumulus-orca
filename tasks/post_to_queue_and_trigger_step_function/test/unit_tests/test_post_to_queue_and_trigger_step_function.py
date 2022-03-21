"""
Name: test_post_to_queue_and_trigger_step_function.py
Description:  Unit tests for test_post_to_queue_and_trigger_step_function.py.
"""
import json
import os
import unittest
import uuid
from unittest.mock import MagicMock, Mock, call, patch

from fastjsonschema import JsonSchemaValueException

import post_to_queue_and_trigger_step_function
import sqs_library


class TestPostToQueueAndTriggerStepFunction(
    unittest.TestCase
):  # pylint: disable-msg=too-many-instance-attributes
    """
    TestPostToQueueAndTriggerStepFunction.
    """

    @patch("post_to_queue_and_trigger_step_function.process_record")
    def test_process_records_happy_path(self, mock_process_record: MagicMock):
        """
        process_records should iterate over records and call appropriate functions.
        """
        mock_record0 = Mock()
        mock_record1 = Mock()
        mock_target_queue_url = Mock()
        mock_step_function_arn = Mock()

        post_to_queue_and_trigger_step_function.process_records(
            [mock_record0, mock_record1],
            mock_target_queue_url,
            mock_step_function_arn,
        )

        mock_process_record.assert_has_calls(
            [
                call(
                    mock_record0,
                    mock_target_queue_url,
                    mock_step_function_arn,
                ),
                call(
                    mock_record1,
                    mock_target_queue_url,
                    mock_step_function_arn,
                ),
            ]
        )

    @patch("post_to_queue_and_trigger_step_function.process_record")
    def test_process_records_error_does_not_halt_loop(
        self, mock_process_record: MagicMock
    ):
        """
        If we process multiple records, then an exception should not cause a halt.
        """
        mock_process_record.side_effect = [Exception(), None]

        mock_record0 = Mock()
        mock_record1 = Mock()
        mock_target_queue_url = Mock()
        mock_step_function_arn = Mock()

        post_to_queue_and_trigger_step_function.process_records(
            [mock_record0, mock_record1],
            mock_target_queue_url,
            mock_step_function_arn,
        )

        mock_process_record.assert_has_calls(
            [
                call(
                    mock_record0,
                    mock_target_queue_url,
                    mock_step_function_arn,
                ),
                call(
                    mock_record1,
                    mock_target_queue_url,
                    mock_step_function_arn,
                ),
            ]
        )

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
        record = {
            "body": uuid.uuid4().__str__()
        }

        with patch.dict(
            os.environ,
            {
                post_to_queue_and_trigger_step_function.OS_ENVIRON_TARGET_QUEUE_URL_KEY: target_queue_url,
                post_to_queue_and_trigger_step_function.OS_ENVIRON_STEP_FUNCTION_ARN_KEY: step_function_arn,
            },
        ):
            post_to_queue_and_trigger_step_function.handler({
                "Records": [record]
            }, Mock())

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
        record = {
            "body": 1
        }

        with self.assertRaises(JsonSchemaValueException) as cm:
            with patch.dict(
                os.environ,
                {
                    post_to_queue_and_trigger_step_function.OS_ENVIRON_TARGET_QUEUE_URL_KEY: target_queue_url,
                    post_to_queue_and_trigger_step_function.OS_ENVIRON_STEP_FUNCTION_ARN_KEY: step_function_arn,
                },
            ):
                post_to_queue_and_trigger_step_function.handler({
                    "Records": [record]
                }, Mock())
        self.assertEqual("data.Records[0].body must be string", str(cm.exception))

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
                post_to_queue_and_trigger_step_function.handler({
                    "Records": [{"body": uuid.uuid4().__str__()}, {"body": uuid.uuid4().__str__()}]
                }, Mock())
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
