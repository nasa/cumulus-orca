import logging
from typing import Any, MutableMapping

from src.use_cases.adapter_interfaces.logger_provider import LoggerProviderInterface

logger = logging.Logger("graphql")


class BasicLoggerProvider(LoggerProviderInterface):
    def get_logger(self, request_id: str) -> logging.Logger:
        """
        Args:
            request_id: A unique identifier to track requests.

        Returns: A logger for use in code.
        """

        # noinspection PyTypeChecker
        return GuidLoggerAdapter(logger, {'request_id': request_id})


class GuidLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg: Any, kwargs: MutableMapping[str, Any]) ->\
            tuple[Any, MutableMapping[str, Any]]:
        return f"{self.extra['request_id']}: {msg}", kwargs
