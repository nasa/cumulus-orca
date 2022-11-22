import logging

from src.use_cases.adapter_interfaces.logger_provider import LoggerProviderInterface

logger = logging.Logger("graphql")


class BasicLoggerProvider(LoggerProviderInterface):
    def get_logger(self) -> logging.Logger:
        """
        Returns: A logger for use in code.
        """
        return logger
