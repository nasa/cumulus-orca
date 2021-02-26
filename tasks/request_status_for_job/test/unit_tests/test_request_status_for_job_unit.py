"""
Name: test_request_status_for_job_unit.py

Description:  Unit tests for request_status_for_granule.py.
"""
import unittest
import uuid
from unittest.mock import patch, MagicMock, Mock

import request_status_for_job


class TestRequestStatusForJobUnit(unittest.TestCase):  # pylint: disable-msg=too-many-instance-attributes
    """
    TestRequestStatusForJob.
    """

    # noinspection PyPep8Naming
    @patch('request_status_for_job.task')
    @patch('cumulus_logger.CumulusLogger.setMetadata')
    def test_handler_happy_path(
            self,
            mock_setMetadata: MagicMock,
            mock_task: MagicMock
    ):
        async_operation_id = uuid.uuid4().__str__()

        event = {
            request_status_for_job.INPUT_JOB_ID_KEY: async_operation_id
        }
        context = Mock()
        result = request_status_for_job.handler(event, context)

        mock_setMetadata.assert_called_once_with(event, context)
        mock_task.assert_called_once_with(async_operation_id)
        self.assertEqual(mock_task.return_value, result)

    def test_task_async_operation_id_cannot_be_none(self):
        """
        Raises error if async_operation_id is None.
        """
        try:
            request_status_for_job.task(None)
        except ValueError:
            return
        self.fail('Error not raised.')
