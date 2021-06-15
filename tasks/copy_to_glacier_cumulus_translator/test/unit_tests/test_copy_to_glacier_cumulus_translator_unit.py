"""
Name: test_copy_to_glacier_cumulus_translator_unit.py

Description:  Unit tests for copy_to_glacier_cumulus_translator.py.
"""
import unittest
from unittest.mock import MagicMock, patch, Mock

import copy_to_glacier_cumulus_translator


class TestCopyToGlacierCumulusTranslatorUnit(
    unittest.TestCase
):  # pylint: disable-msg=too-many-instance-attributes
    """
    TestCopyToGlacierCumulusTranslator.
    """

    # noinspection PyPep8Naming
    @patch("run_cumulus_task.run_cumulus_task")
    @patch("cumulus_logger.CumulusLogger.setMetadata")
    def test_handler_happy_path(
            self,
            mock_setMetadata: MagicMock,
            mock_run_cumulus_task: MagicMock
    ):
        """
        Basic path with all information present.
        """
        event = Mock()
        context = Mock()
        result = copy_to_glacier_cumulus_translator.handler(event, context)

        mock_setMetadata.assert_called_once_with(event, context)
        mock_run_cumulus_task.assert_called_once_with(
            copy_to_glacier_cumulus_translator.task, event, context
        )
        self.assertEqual(mock_run_cumulus_task.return_value, result)

    @patch("copy_to_glacier_cumulus_translator.task")
    @patch("cumulus_logger.CumulusLogger.setMetadata")
    def test_task_passthrough(self,
                              mock_setMetadata: MagicMock,
                              mock_task: MagicMock):
        # event = {
        #     "task_config": {
        #         "file_mapping": {
        #             "name": "some_name",
        #             "filepath": "some/path",
        #             "filename": "some/filename"
        #         }
        #     },
        #     "payload": {
        #         "granules": []
        #     }
        # }
        expected_input = {"granules": []}
        expected_config = {
            "file_mapping": {
                "name": "some_name",
                "filepath": "some/path",
                "bucket": "someBucket",
                "filename": "some/filename"
            }
        }
        event = {
            "task_config": expected_config,
            "payload": expected_input
        }
        context = Mock()

        mock_task.return_value = {"granules": [{"granule_id": "some_granule_id", "files": []}]}

        result = copy_to_glacier_cumulus_translator.handler(event, context)
        self.assertEqual(mock_task.return_value, result['payload'])
        mock_task.assert_called_once_with({"input": expected_input, "config": expected_config}, context)
