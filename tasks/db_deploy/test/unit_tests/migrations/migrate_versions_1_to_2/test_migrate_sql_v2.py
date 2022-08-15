"""
Name: test_migrate_sql_v2.py

Description: Unit tests for the migrations/migrate_versions_1_to_2/migrate_sql.py.
"""

import unittest
import uuid
from inspect import getmembers, isfunction

from sqlalchemy.sql.elements import TextClause

import migrations.migrate_versions_1_to_2.migrate_sql as sql


class TestOrcaSqlLogic(unittest.TestCase):
    """
    Note that currently all of the function calls in the migrate_sql_v2.py
    return a SQL text string and have no logic except for the app_user_sql
    function that requires a string for the user password. The tests below
    validate the logic in the function.
    """

    def test_all_functions_return_text(self) -> None:
        """
        Validates that all functions return a type TextClause
        """

        for name, function in getmembers(sql, isfunction):
            if name not in ["text"]:
                with self.subTest(function=function):
                    if name in ["app_database_sql", "dbo_role_sql"]:
                        # These functions take in two string parameters.
                        self.assertEqual(
                            type(
                                function(uuid.uuid4().__str__(), uuid.uuid4().__str__())
                            ),
                            TextClause,
                        )
                    elif name in [
                        "app_database_comment_sql",
                        "app_role_sql",
                        "app_user_sql",
                        "drop_dr_role_sql",
                        "drop_dbo_user_sql",
                        "drop_drdbo_role_sql",
                    ]:
                        # These functions take in a string parameter.
                        self.assertEqual(
                            type(function(uuid.uuid4().__str__())), TextClause
                        )
                    else:
                        self.assertEqual(type(function()), TextClause)
