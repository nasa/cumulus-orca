"""
Name: test_migrate_sql_v5.py

Description: Testing library for the migrations/migrate_versions_4_to_5/migrate_sql.py.
"""

import random
import string
import unittest
import uuid
from inspect import getmembers, isfunction

from sqlalchemy.sql.elements import TextClause

import migrations.migrate_versions_4_to_5.migrate_sql as sql


def generate_randoms_string(length=50):
    """
    Generates a random string consisting of a combination of A-Z,a-z,0-9, and _.
    """
    charachters = string.ascii_letters + string.digits + "_"
    return "".join(random.choice(charachters) for _ in range(length))  # nosec


class TestOrcaSqlLogic(unittest.TestCase):
    """
    Note that currently all of the function calls in the migrate_sql.py
    return a SQL text string. The tests below
    validate the logic in the function.
    """

    def test_all_functions_return_text(self) -> None:
        """
        Validates that all functions return a type TextClause
        """

        for name, function in getmembers(sql, isfunction):
            if name not in ["text"]:
                with self.subTest(function=function):
                    # These functions take in a string parameter:
                    if name in ["reconcile_s3_object_partition_sql"]:
                        self.assertEqual(
                            type(
                                function(uuid.uuid4().__str__())
                            ),
                            TextClause
                        )

                    # All other functions have no parameters passed
                    else:
                        self.assertEqual(type(function()), TextClause)

    def test_reconcile_s3_object_partition_sql_happy_path(self) -> None:
        """
        Tests the happy path and validates the partition_name is a part of the SQL.
        """
        partition_name = uuid.uuid4().__str__()
        partition_sql = sql.reconcile_s3_object_partition_sql(partition_name)

        # Check that the partition_name is in the SQL and the type is text
        self.assertIn(partition_name, partition_sql.text)
        self.assertEqual(type(partition_sql), TextClause)

