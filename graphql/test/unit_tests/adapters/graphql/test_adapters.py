import unittest
from unittest.mock import Mock

from src.adapters.graphql.adapters import AdaptersStorage
from src.adapters.storage.rdbms import StorageAdapterRDBMS
from src.use_cases.adapter_interfaces.logger_provider import LoggerProviderInterface
from src.use_cases.adapter_interfaces.word_generation import WordGenerationInterface


class TestAdapters(unittest.TestCase):

    def test_AdaptersStorage_init(
        self,
    ):
        """
        Parameters should properly map to properties.
        """
        mock_word_generation = Mock(spec=WordGenerationInterface)
        mock_storage = Mock(spec=StorageAdapterRDBMS)
        mock_storage_internal_reconciliation = Mock(spec=StorageAdapterRDBMS)
        mock_logger_provider = Mock(spec=LoggerProviderInterface)

        result = AdaptersStorage(
            mock_word_generation,
            mock_storage,
            mock_storage_internal_reconciliation,
            mock_logger_provider
        )

        self.assertEqual(mock_word_generation, result.word_generation)
        self.assertEqual(mock_storage, result.storage)
        self.assertEqual(
            mock_storage_internal_reconciliation, result.storage_internal_reconciliation
        )
        self.assertEqual(mock_logger_provider, result.logger_provider)
