"""
Name: test_post_to_queue_and_trigger_step_function.py
Description:  Unit tests for test_post_to_queue_and_trigger_step_function.py.
"""
import copy
import os
import random
import unittest
import uuid
from unittest.mock import MagicMock, Mock, call, patch

import post_to_queue_and_trigger_step_function


class TestPostToQueueAndTriggerStepFunction(
    unittest.TestCase
):  # pylint: disable-msg=too-many-instance-attributes
    """
    TestPostToQueueAndTriggerStepFunction.
    """

    def test_task_happy_path(self):
        pass

    def test_task_error_does_not_halt_loop(self):
        pass

    # todo: more tests

    # copied from shared_db.py
    @patch("time.sleep")
    def test_retry_operational_error_happy_path(self, mock_sleep: MagicMock):
        expected_result = Mock()

        @post_to_queue_and_trigger_step_function.retry_error(3)
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

        @post_to_queue_and_trigger_step_function.retry_error(max_retries)
        def dummy_call():
            raise expected_error

        try:
            dummy_call()
        except Exception as caught_error:
            self.assertEqual(expected_error, caught_error)
            self.assertEqual(max_retries, mock_sleep.call_count)
            return
        self.fail("Error not raised.")
