"""
Name: test_orca_sql.py

Description: Testing library for the orca_sql.py library.
"""

import unittest
from inspect import getmembers, isfunction
import orca_sql
from sqlalchemy import text
from sqlalchemy.sql.elements import TextClause


class TestOrcaSqlLogic(unittest.TestCase):
    """
    Note that currently all of the function calls in the orca_sql library
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
        user_sql = orca_sql.app_user_sql(user_pass)

        # Check that the password is in the SQL and the typw is text
        self.assertIn(user_pass, user_sql.text)
        self.assertEqual(type(user_sql), TextClause)

    def test_app_user_sql_exceptions(self) -> None:
        """
        Tests that an exception is thrown if the password is not set or is not
        a minimum of 12 characters.
        """
        bad_passwords = [None, "", "abc123", "1234567890", "AbCdEfG1234"]
        message = "Password not long enough."

        for bad_password in bad_passwords:
            with self.subTest(bad_password=bad_password):
                with self.assertRaises(Exception) as cm:
                    orca_sql.app_user_sql(bad_password)
                self.assertEquals(str(cm.exception), message)

    def test_all_functions_return_text(self) -> None:
        """
        Validates that all functions return a type TextClause
        """

        for name, function in getmembers(orca_sql, isfunction):
            if name not in ["text", "app_user_sql"]:
                with self.subTest(function=function):
                    self.assertEqual(type(function()), TextClause)
