import logging
import unittest
import uuid
from unittest.mock import MagicMock, Mock, patch

from src.adapters.logger_provider.json import (
    JsonLoggerProvider,
    JsonRequestIdLoggerAdapter,
)


class TestJson(unittest.TestCase):

    def test_JsonFormatter_format_happy_path(self):
        """
        Checks format and formatMessage for json handling and output.
        Checking as one, due to the division only being due to logging library limitations.
        """

    @patch("src.adapters.logger_provider.json.JsonLoggerProvider._logger")
    @patch("src.adapters.logger_provider.json.JsonRequestIdLoggerAdapter")
    def test_JsonLoggerProvider_happy_path(
        self,
        mock_json_request_id_logger_adapter: MagicMock,
        mock_logger: MagicMock,
    ):
        """
        Should init the adapter properly.
        """
        mock_request_id = uuid.uuid4().__str__()

        result = JsonLoggerProvider().get_logger(mock_request_id)

        self.assertEqual(mock_json_request_id_logger_adapter.return_value, result)
        mock_json_request_id_logger_adapter.assert_called_once_with(mock_logger, {
            "request_id": mock_request_id
        })

    def test_JsonRequestIdLoggerAdapter_process_happy_path(
        self
    ):
        """
        Should attach the request_id to all logs.
        """
        mock_request_id = uuid.uuid4().__str__()

        mock_logger = MagicMock()
        adapter = JsonRequestIdLoggerAdapter(mock_logger, {"request_id": mock_request_id})

        mock_message = Mock()
        adapter.error(mock_message)
        mock_logger.log.assert_called_once_with(
            logging.ERROR, f"{{\"request_id\": \"{mock_request_id}\", "
                           f"\"message\": \"{mock_message}\"}}")
