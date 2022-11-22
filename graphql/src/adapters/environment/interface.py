from orca_shared.database.entities import PostgresConnectionInfo

from src.use_cases.adapter_interfaces.logger_provider import LoggerProviderInterface


class EnvironmentInterface:
    """
    Generic class with methods that need to be implemented by adapter.
    """

    def get_db_connect_info(
        self, logger_provider: LoggerProviderInterface) -> PostgresConnectionInfo: ...
    """
    Args:
        logger_provider: The logger provider to use.
        
    Returns: A standardized object containing connection info.
    """
