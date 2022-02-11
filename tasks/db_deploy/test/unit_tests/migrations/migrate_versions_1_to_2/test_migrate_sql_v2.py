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

    def test_app_user_sql_happy_path(self) -> None:
        """
        Tests the happy path for the app_user_sql function and validates the
        user password is a part of the SQL.
        """
        user_pass = "MySup3rL0ngPassForAUser"
        user_name = uuid.uuid4().__str__()
        user_sql = sql.app_user_sql(user_pass, user_name)

        # Check that the username and password are in the SQL and the type is text
        self.assertIn(user_pass, user_sql.text)
        self.assertIn(user_name, user_sql.text)
        self.assertEqual(type(user_sql), TextClause)

    def test_app_user_sql_exceptions(self) -> None:
        """
        Tests that an exception is thrown if the password is not set or is not
        a minimum of 12 characters,
        or if user_name is not set or is over 64 characters.
        """
        bad_passwords = [None, "", "abc123", "1234567890", "AbCdEfG1234"]
        message = "User password must be at least 12 characters long."

        for bad_password in bad_passwords:
            with self.subTest(bad_password=bad_password):
                with self.assertRaises(Exception) as cm:
                    sql.app_user_sql("orcauser", bad_password)
                self.assertEqual(str(cm.exception), message)

        bad_user_names = [None, ""]
        message = "Username must be non-empty."
        for bad_user_name in bad_user_names:
            with self.subTest(bad_user_name=bad_user_name):
                with self.assertRaises(Exception) as cm:
                    sql.app_user_sql(bad_user_name, "AbCdEfG12345")
                self.assertEqual(str(cm.exception), message)

        message = "Username must be less than 64 characters."
        bad_user_name = "".join("a" * 64)
        with self.subTest(bad_user_name=bad_user_name) as cm:
            with self.assertRaises(Exception) as cm:
                sql.app_user_sql(bad_user_name, "AbCdEfG12345")
            self.assertEqual(str(cm.exception), message)

    def test_all_functions_return_text(self) -> None:
        """
        Validates that all functions return a type TextClause
        """

        for name, function in getmembers(sql, isfunction):
            if name not in ["text"]:
                with self.subTest(function=function):
                    if name in ["app_user_sql"]:
                        self.assertEqual(type(function(uuid.uuid4().__str__(), uuid.uuid4().__str__())), TextClause)
                        # These functions take in two string parameters.
                    elif name in ["app_database_sql", "app_database_comment_sql", "dbo_role_sql", "app_role_sql",
                                  "drop_dr_role_sql", "drop_dbo_user_sql", "drop_drdbo_role_sql"]:
                        # These functions take in a string parameter.
                        self.assertEqual(type(function(uuid.uuid4().__str__())), TextClause)
                    else:
                        self.assertEqual(type(function()), TextClause)
