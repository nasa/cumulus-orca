import unittest
from unittest.mock import Mock

from src.use_cases import get_orphans_page


class TestGetOrphansPage(unittest.TestCase):
    def test_happy_path(self):
        orphans_record_filter = Mock()
        orphans_page_storage = Mock()
        LOGGER = Mock()

        result = get_orphans_page.task(
            orphans_record_filter, orphans_page_storage, LOGGER
        )
        self.assertEqual(orphans_page_storage.get_orphans_page.return_value, result)
        orphans_page_storage.get_orphans_page.assert_called_once_with(
            orphans_record_filter, LOGGER
        )
