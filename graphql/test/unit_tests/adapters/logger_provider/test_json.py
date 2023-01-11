import json
import logging
import unittest
import uuid
from unittest.mock import MagicMock, Mock, patch

from src.adapters.logger_provider.json import (
    JsonLoggerProvider,
    JsonRequestIdLoggerAdapter, JsonFormatter,
)


class TestJson(unittest.TestCase):

    def test_JsonFormatter_formatMessage_happy_path(self):
        """
        formatMessage should pull properties from a json string.
        """
        request_id = uuid.uuid4().__str__()
        message = uuid.uuid4().__str__()
        level = uuid.uuid4().__str__()

        mock_record = Mock()
        mock_record.message = json.dumps({
            "request_id": request_id,
            "message": message,
        })
        # noinspection SpellCheckingInspection
        mock_record.levelname = level

        formatter = JsonFormatter()
        result = formatter.formatMessage(mock_record)
        self.assertEqual({
            "request_id": request_id,
            "level": level,
            "message": message,
        }, result)

    def test_JsonFormatter_formatMessage_default_values(self):
        """
        If properties are missing, use defaults.
        """
        level = uuid.uuid4().__str__()

        mock_record = Mock()
        mock_record.message = json.dumps({
        })
        # noinspection SpellCheckingInspection
        mock_record.levelname = level

        formatter = JsonFormatter()
        result = formatter.formatMessage(mock_record)
        self.assertEqual({
            "request_id": "ERROR",
            "level": level,
            "message": "ERROR",
        }, result)

    def test_JsonFormatter_formatMessage_not_json(self):
        """
        If message is not json, still log.
        """
        message = uuid.uuid4().__str__()
        level = uuid.uuid4().__str__()

        mock_record = Mock()
        mock_record.message = message
        # noinspection SpellCheckingInspection
        mock_record.levelname = level

        formatter = JsonFormatter()
        result = formatter.formatMessage(mock_record)
        self.assertEqual({
            "request_id": "ERROR",
            "level": level,
            "message": message,
        }, result)

    @patch("src.adapters.logger_provider.json.JsonFormatter.formatStack")
    @patch("src.adapters.logger_provider.json.JsonFormatter.formatException")
    @patch("src.adapters.logger_provider.json.JsonFormatter.formatMessage")
    def test_JsonFormatter_format_happy_path(
        self,
        mock_format_message: MagicMock,
        mock_format_exception: MagicMock,
        mock_format_stack: MagicMock,
    ):
        """
        Should call formatMessage, and construct a logging string based on results.
        """
        mock_exc_info = Mock()
        mock_stack_info = Mock()
        mock_record = Mock()
        mock_record.exc_info = mock_exc_info
        mock_record.stack_info = mock_stack_info
        mock_message = Mock()
        mock_record.getMessage = Mock(return_value=mock_message)
        message_key = uuid.uuid4().__str__()
        message_value = uuid.uuid4().__str__()
        mock_format_message.return_value = {message_key: message_value}

        formatter = JsonFormatter()

        mock_record.exc_text = None
        result = formatter.format(mock_record)

        mock_record.getMessage.assert_called_once_with()
        mock_format_message.assert_called_once_with(
            mock_record)
        mock_format_exception.assert_called_once_with(mock_exc_info)
        mock_format_stack.assert_called_once_with(mock_stack_info)

        self.assertEqual(
            f"{{\"{message_key}\": \"{message_value}\", "
            f"\"exc_info\": \"{mock_format_exception.return_value}\","
            f" \"stack_info\": \"{mock_format_stack.return_value}\"}}",
            result)

    @patch("src.adapters.logger_provider.json.JsonFormatter.formatStack")
    @patch("src.adapters.logger_provider.json.JsonFormatter.formatException")
    @patch("src.adapters.logger_provider.json.JsonFormatter.formatMessage")
    def test_JsonFormatter_format_default_values(
        self,
        mock_format_message: MagicMock,
        mock_format_exception: MagicMock,
        mock_format_stack: MagicMock,
    ):
        """
        If properties are missing, use defaults.
        """
        mock_record = Mock()
        mock_record.exc_info = None
        mock_record.stack_info = None
        mock_message = Mock()
        mock_record.getMessage = Mock(return_value=mock_message)
        message_key = uuid.uuid4().__str__()
        message_value = uuid.uuid4().__str__()
        mock_format_message.return_value = {message_key: message_value}

        formatter = JsonFormatter()

        mock_record.exc_text = None
        result = formatter.format(mock_record)

        mock_record.getMessage.assert_called_once_with()
        mock_format_message.assert_called_once_with(
            mock_record)
        mock_format_exception.assert_not_called()
        mock_format_stack.assert_not_called()

        self.assertEqual(
            f"{{\"{message_key}\": \"{message_value}\"}}",
            result)

    @patch("src.adapters.logger_provider.json.JsonFormatter")
    @patch("src.adapters.logger_provider.json.logging")
    def test_JsonLoggerProvider_init_happy_path(
        self,
        mock_logging: MagicMock,
        mock_json_formatter: MagicMock,
    ):
        """
        Should set up the logger properly.
        """
        result = JsonLoggerProvider()

        mock_logging.Logger.assert_called_once_with("graphql")
        mock_logging.StreamHandler.assert_called_once_with()
        mock_json_formatter.assert_called_once_with()
        mock_logging.StreamHandler.return_value.setFormatter.assert_called_once_with(
            mock_json_formatter.return_value)
        mock_logging.Logger.return_value.addHandler.assert_called_once_with(
            mock_logging.StreamHandler.return_value
        )
        self.assertEqual(mock_logging.Logger.return_value, result._logger)

    @patch("src.adapters.logger_provider.json.JsonRequestIdLoggerAdapter")
    def test_JsonLoggerProvider_happy_path(
        self,
        mock_json_request_id_logger_adapter: MagicMock,
    ):
        """
        Should init the adapter properly.
        """
        mock_request_id = uuid.uuid4().__str__()

        provider = JsonLoggerProvider()
        result = provider.get_logger(mock_request_id)

        self.assertEqual(mock_json_request_id_logger_adapter.return_value, result)
        mock_json_request_id_logger_adapter.assert_called_once_with(provider._logger, {
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
