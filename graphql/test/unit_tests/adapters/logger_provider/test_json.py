import logging
import unittest
from unittest.mock import MagicMock, Mock, patch

from src.adapters.logger_provider.json import (
    JsonLoggerProvider,
    JsonRequestIdLoggerAdapter,
)


class TestJson(unittest.TestCase):

    @patch("src.adapters.logger_provider.json.logger")
    @patch("src.adapters.logger_provider.json.RequestIdLoggerAdapter")
    def test_JsonLoggerProvider_happy_path(
        self,
        mock_request_id_logger_adapter: MagicMock,
        mock_logger: MagicMock,
    ):
        """
        Should init the adapter properly.
        """
        mock_request_id = Mock()
        result = JsonLoggerProvider().get_logger(mock_request_id)

        self.assertEqual(mock_request_id_logger_adapter.return_value, result)
        mock_request_id_logger_adapter.assert_called_once_with(mock_logger, {
            "request_id": mock_request_id
        })

    def test_RequestIdLoggerAdapter_process_happy_path(
        self
    ):
        """
        Should attach the request_id to all logs.
        """
        mock_request_id = Mock()

        mock_logger = MagicMock()
        adapter = JsonRequestIdLoggerAdapter(mock_logger, {"request_id": mock_request_id})

        mock_message = Mock()
        adapter.error(mock_message)
        mock_logger.log.assert_called_once_with(
            logging.ERROR, f"{mock_request_id}: {mock_message}")
