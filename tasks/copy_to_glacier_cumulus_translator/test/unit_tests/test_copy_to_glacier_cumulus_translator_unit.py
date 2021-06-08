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
    @patch("copy_to_glacier_cumulus_translator.task")
    @patch("cumulus_logger.CumulusLogger.setMetadata")
    def test_handler_happy_path(
        self,
        mock_setMetadata: MagicMock,
        mock_task: MagicMock
    ):
        """
        Basic path with all information present.
        """
        event = Mock()
        context = Mock()
        result = copy_to_glacier_cumulus_translator.handler(event, context)

        mock_setMetadata.assert_called_once_with(event, context)
        mock_task.assert_called_once_with(
            event
        )
        self.assertEqual(mock_task.return_value, result)
