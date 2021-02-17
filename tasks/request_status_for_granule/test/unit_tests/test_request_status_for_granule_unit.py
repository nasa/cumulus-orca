"""
Name: test_request_status_for_granule_unit.py

Description:  Unit tests for request_status_for_granule.py.
"""
import unittest
import uuid
from unittest.mock import MagicMock, patch, Mock

import request_status_for_granule


class TestRequestStatusForGranuleUnit(unittest.TestCase):  # pylint: disable-msg=too-many-instance-attributes
    """
    TestRequestStatusForGranule.
    """

    # noinspection PyPep8Naming
    @patch('request_status_for_granule.task')
    @patch('cumulus_logger.CumulusLogger.setMetadata')
    def test_handler_happy_path(
            self,
            mock_setMetadata: MagicMock,
            mock_task: MagicMock
    ):
        granule_id = uuid.uuid4().__str__()
        async_operation_id = uuid.uuid4().__str__()

        event = {
            request_status_for_granule.GRANULE_ID_KEY: granule_id,
            request_status_for_granule.ASYNC_OPERATION_ID_KEY: async_operation_id
        }
        context = Mock()
        result = request_status_for_granule.handler(event, context)

        mock_setMetadata.assert_called_once_with(event, context)
        mock_task.assert_called_once_with(granule_id, async_operation_id)
        self.assertEqual(mock_task.return_value, result)

    @patch('request_status_for_granule.task')
    def test_handler_async_operation_id_defaults_to_none(
            self,
            mock_task: MagicMock
    ):
        """
        If asyncOperationId is missing, it should default to null.
        """
        granule_id = uuid.uuid4().__str__()

        event = {
            request_status_for_granule.GRANULE_ID_KEY: granule_id
        }
        context = Mock()
        result = request_status_for_granule.handler(event, context)

        mock_task.assert_called_once_with(granule_id, None)
        self.assertEqual(mock_task.return_value, result)

    @patch('request_status_for_granule.task')
    def test_handler_missing_granule_id_errors(
            self,
            mock_task: MagicMock
    ):
        async_operation_id = uuid.uuid4().__str__()

        event = {
            request_status_for_granule.ASYNC_OPERATION_ID_KEY: async_operation_id
        }
        context = Mock()

        try:
            request_status_for_granule.handler(event, context)
        except KeyError:
            mock_task.assert_not_called()
            return
        self.fail('Error not raised.')

    def test_task_granule_id_cannot_be_none(self):
        """
        Raises error if granule_id is None.
        """
        try:
            request_status_for_granule.task(None, uuid.uuid4().__str__())
        except ValueError:
            return
        self.fail('Error not raised.')
