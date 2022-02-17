"""
Name: test_migrate_db.py

Description: Runs unit tests for the migrations/migrate_db.py library.
"""

import unittest
from unittest.mock import MagicMock, patch

from migrations import migrate_db


class TestMigrateDatabaseLibraries(unittest.TestCase):
    """
    Runs unit tests on the migrate_db functions.
    """

    def setUp(self):
        """
        Set up test.
        """
        self.config = {
            "admin_database": "admin_db",
            "admin_password": "admin123",
            "admin_username": "admin",
            "host": "aws.postgresrds.host",
            "port": 5432,
            "user_database": "user_db",
            "user_password": "user123456789",
            "user_username": "user",
        }
        self.orca_buckets = ["orca_worm", "orca_versioned", "orca_special"]

    def tearDown(self):
        """
        Tear down test
        """
        self.config = None
        self.orca_buckets = None

    @patch("migrations.migrate_db.migrate_versions_1_to_2")
    @patch("migrations.migrate_db.migrate_versions_2_to_3")
    @patch("migrations.migrate_db.migrate_versions_3_to_4")
    @patch("migrations.migrate_db.migrate_versions_4_to_5")
    def test_perform_migration_happy_path(
        self,
        mock_migrate_v4_to_v5: MagicMock,
        mock_migrate_v3_to_v4: MagicMock,
        mock_migrate_v2_to_v3: MagicMock,
        mock_migrate_v1_to_v2: MagicMock,
    ):
        """
        Tests the perform_migration function happy paths
        """
        for version in [1, 2, 3, 4, 5, 6]:
            with self.subTest(version=version):
                migrate_db.perform_migration(version, self.config, self.orca_buckets)

                # Make sure the proper migrations happens.
                # Note that for version 2 and 3 the function is not called so
                # overall through all the tests it is only called once.
                if version < 2:
                    mock_migrate_v1_to_v2.assert_called_once_with(self.config, False)
                else:
                    mock_migrate_v1_to_v2.assert_not_called()

                if version < 3:
                    mock_migrate_v2_to_v3.assert_called_once_with(self.config, False)
                else:
                    mock_migrate_v2_to_v3.assert_not_called()

                if version < 4:
                    mock_migrate_v3_to_v4.assert_called_once_with(self.config, False)
                else:
                    mock_migrate_v3_to_v4.assert_not_called()

                if version < 5:
                    mock_migrate_v4_to_v5.assert_called_once_with(
                        self.config, True, self.orca_buckets
                    )
                else:
                    mock_migrate_v4_to_v5.assert_not_called()

                # Reset for next loop
                mock_migrate_v1_to_v2.reset_mock()
                mock_migrate_v2_to_v3.reset_mock()
                mock_migrate_v3_to_v4.reset_mock()
                mock_migrate_v4_to_v5.reset_mock()
