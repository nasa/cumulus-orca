"""
Name: test_migrate_sql_v4.py

Description: Testing library for the migrations/migrate_versions_3_to_4/migrate_sql_v4.py.
"""

import unittest
from inspect import getmembers, isfunction

from sqlalchemy.sql.elements import TextClause

import migrations.migrate_versions_3_to_4.migrate_sql_v4 as sql


class TestOrcaSqlLogic(unittest.TestCase):
    """
    Note that currently all of the function calls in the migrate_sql_v4.py
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
                    if name in ["providers_table_sql", "collections_table_sql", "granules_table_sql", "files_table_sql", "schema_versions_data_sql"]:
                        self.assertEqual(type(function()), TextClause)