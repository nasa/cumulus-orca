import logging


class LoggerProviderInterface:
    """
    Generic class with methods that need to be implemented by adapter.
    """

    def get_logger(self, request_id: str) -> logging.Logger:
        """
        Args:
            request_id: A unique identifier to track requests.

        Returns: A logger for use in code.
        """
        ...
