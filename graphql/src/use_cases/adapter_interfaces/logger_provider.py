import logging


# todo: largely copy-paste. Rethink, considering previous prototypes.


class LoggerProviderInterface:
    """
    Generic class with methods that need to be implemented by adapter.
    """

    def get_logger(self) -> logging.Logger: ...
