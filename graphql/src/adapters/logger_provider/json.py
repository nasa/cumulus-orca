import json
import logging
from typing import Any, MutableMapping

from src.use_cases.adapter_interfaces.logger_provider import LoggerProviderInterface


class JsonFormatter(logging.Formatter):
    def formatMessage(self, record) -> dict:
        """
        Overwritten to return a dictionary of the relevant LogRecord attributes instead of a
        string.
        KeyError is raised if an unknown attribute is provided in the fmt_dict.
        """
        message_dict = json.loads(record.message)
        return {
            "request_id": message_dict["request_id"],
            "level": record.levelname,
            "message": message_dict["message"],
        }
        return {fmt_key: record.__dict__[fmt_val] for fmt_key, fmt_val in self.fmt_dict.items()}

    def format(self, record) -> str:
        """
        Mostly the same as the parent's class method, the difference being that a dict is
        manipulated and dumped as JSON
        instead of a string.
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


logger = logging.Logger("graphql")
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)
stream_handler.setFormatter(JsonFormatter())


class JsonLoggerProvider(LoggerProviderInterface):
    def get_logger(self, request_id: str) -> logging.Logger:
        """
        Args:
            request_id: A unique identifier to track requests.

        Returns: A logger for use in code.
        """

        # noinspection PyTypeChecker
        wrapped_logger = JsonRequestIdLoggerAdapter(logger, {"request_id": request_id})
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
