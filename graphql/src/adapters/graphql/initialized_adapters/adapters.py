from src.adapters.storage.rdbms import StorageAdapterRDBMS
from src.adapters.word_generation.word_generation import UUIDWordGeneration

word_generation = UUIDWordGeneration()

storage: StorageAdapterRDBMS
