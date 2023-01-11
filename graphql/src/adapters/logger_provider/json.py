import json
import logging
from typing import Any, MutableMapping

from src.use_cases.adapter_interfaces.logger_provider import LoggerProviderInterface


class JsonFormatter(logging.Formatter):
    """
    Formats messages to a json format. Must be used with JsonRequestIdLoggerAdapter.

    Partially taken from
    https://stackoverflow.com/questions/50144628/python-logging-into-file-as-a-dictionary-or-json
    """
    def formatMessage(self, record) -> dict:
        """
        Overwritten to return a dictionary of the relevant attributes instead of a string.
        """
        # Convert the message from JsonRequestIdLoggerAdapter to get properties.
        try:
            message_dict = json.loads(record.message)
        except json.JSONDecodeError:
            message_dict = {"message": record.message}
        return {
            "request_id": message_dict.get("request_id", "ERROR"),
            "level": record.levelname,
            "message": message_dict.get("message", "ERROR"),
        }

    def format(self, record) -> str:
        """
        Mostly the same as the parent's class method, the difference being that a dict is
        manipulated and dumped as JSON instead of a string.
        """
        record.message = record.getMessage()

        message_dict = self.formatMessage(record)

        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)

        if record.exc_text:
            message_dict["exc_info"] = record.exc_text

        if record.stack_info:
            message_dict["stack_info"] = self.formatStack(record.stack_info)

        return json.dumps(message_dict, default=str)


class JsonLoggerProvider(LoggerProviderInterface):
    _logger = logging.Logger("graphql")
    _stream_handler = logging.StreamHandler()
    _stream_handler.setFormatter(JsonFormatter())
    _logger.addHandler(_stream_handler)

    def get_logger(self, request_id: str) -> logging.Logger:
        """
        Args:
            request_id: A unique identifier to track requests.

        Returns: A logger for use in code.
        """

        # noinspection PyTypeChecker
        wrapped_logger = JsonRequestIdLoggerAdapter(self._logger, {"request_id": request_id})
        # Technically not a logging.Logger, but implements much of the same interface.
        # https://docs.python.org/3/library/logging.html#loggeradapter-objects
        # Sadly, the logging library doesn't have great inheritance.
        return wrapped_logger


class JsonRequestIdLoggerAdapter(logging.LoggerAdapter):
    """
    An adapter that adds per-request specific information for use in JsonFormatter.
    Must output a string due to logger limitations.
    """
    def process(self, msg: Any, kwargs: MutableMapping[str, Any]) -> \
            tuple[Any, MutableMapping[str, Any]]:
        return json.dumps({
            "request_id": self.extra['request_id'],
            "message": str(msg),
        }), kwargs
