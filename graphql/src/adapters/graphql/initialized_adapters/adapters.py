from src.adapters.storage.rdbms import StorageAdapterRDBMS
from src.adapters.word_generation.word_generation import UUIDWordGeneration
from src.use_cases.adapter_interfaces.logger_provider import LoggerProviderInterface

word_generation = UUIDWordGeneration()

# Values below initialized in src/adapters/webserver/application.py
storage: StorageAdapterRDBMS
static_logger_provider: LoggerProviderInterface
