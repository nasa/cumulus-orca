"""
Name: test_shared_reconciliation.py
Description: Unit tests for shared_reconciliation.py shared library.
"""
import unittest
from orca_shared.reconciliation import shared_reconciliation


class TestSharedReconciliationLibraries(unittest.TestCase):
    """
    Unit tests for the shared_reconciliation library used by ORCA Reconciliation Lambdas.
    """

    def test_get_partition_name_from_bucket_name_happy_path(self):
        """
        Should replace dashes with underscores.
        """
        result = shared_reconciliation.get_partition_name_from_bucket_name("apple-banana_-lemon")
        self.assertEqual("reconcile_s3_object_apple_banana__lemon", result)

    def test_get_partition_name_from_bucket_name_rejects_non_alphanumeric(self):
        """
        Should replace dashes with underscores.
        """
        for error_case in ["a a", "a!a"]:
            with self.subTest(error_case=error_case):
                with self.assertRaises(Exception) as cm:
                    shared_reconciliation.get_partition_name_from_bucket_name(error_case)
                self.assertEqual(f"'reconcile_s3_object_{error_case}' is not a valid partition name.", str(cm.exception))
