"""
Name: test_post_to_queue_and_trigger_step_function.py
Description:  Unit tests for test_post_to_queue_and_trigger_step_function.py.
"""
import copy
import json
import os
import random
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
    def test_process_records_happy_path(
        self, mock_process_record: MagicMock
    ):
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

    @patch(
        "post_to_queue_and_trigger_step_function.send_body_to_queue_and_trigger_workflow"
    )
    @patch("post_to_queue_and_trigger_step_function.translate_record_body")
    def test_process_record_happy_path(
        self,
        mock_translate_record_body: MagicMock,
        mock_send_body_to_queue_and_trigger_workflow: MagicMock,
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
        mock_send_body_to_queue_and_trigger_workflow.assert_called_once_with(
            mock_target_queue_url,
            mock_step_function_arn,
            mock_translate_record_body.return_value,
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
            f'{{'
            f'"{post_to_queue_and_trigger_step_function.OUTPUT_REPORT_BUCKET_REGION_KEY}": "{aws_region}", '
            f'"{post_to_queue_and_trigger_step_function.OUTPUT_REPORT_BUCKET_NAME_KEY}": "{bucket_name}", '
            f'"{post_to_queue_and_trigger_step_function.OUTPUT_MANIFEST_KEY_KEY}": "{object_key}"'
            f'}}',
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

    def test_send_body_to_queue_and_trigger_workflow_happy_path(self):
        pass

    def test_handler_happy_path(self):
        pass

    def test_handler_rejects_bad_input(self):
        pass

    def test_handler_rejects_multiple_records(self):
        pass

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
