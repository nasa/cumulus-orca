"""
Name: test_migrate_sql_v6.py

Description: Testing library for the migrations/migrate_versions_5_to_6/migrate_sql.py.
"""

import unittest
from inspect import getmembers, isfunction

from sqlalchemy.sql.elements import TextClause

import migrations.migrate_versions_5_to_6.migrate_sql as sql


class TestOrcaSqlLogic(unittest.TestCase):
    """
    Note that currently all the function calls in the migrate_sql.py
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
                    self.assertEqual(type(function()), TextClause)
