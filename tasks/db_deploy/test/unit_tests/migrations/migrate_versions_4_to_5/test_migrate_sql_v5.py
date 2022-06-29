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
        except reconcile_s3_object_partition_sql which is tested in other tests
        """

        for name, function in getmembers(sql, isfunction):
            if name not in ["text", "reconcile_s3_object_partition_sql"]:
                with self.subTest(function=function):
                    self.assertEqual(type(function()), TextClause)
