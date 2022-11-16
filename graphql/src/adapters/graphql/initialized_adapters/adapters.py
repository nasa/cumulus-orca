from src.adapters.storage.rdbms import StorageAdapterRDBMS
from src.adapters.word_generation.word_generation import UUIDWordGeneration

word_generation = UUIDWordGeneration()

OS_ENVIRON_DB_CONNECT_INFO_SECRET_ARN_KEY = "DB_CONNECT_INFO_SECRET_ARN"  # nosec

storage: StorageAdapterRDBMS
