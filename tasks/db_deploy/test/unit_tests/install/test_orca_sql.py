"""
Name: test_orca_sql.py

Description: Testing library for the orca_sql.py library.
"""
import random
import string
import unittest
import uuid
from inspect import getmembers, isfunction

from sqlalchemy.sql.elements import TextClause

from install import orca_sql


def generate_randoms_string(length=50):
    """
    Generates a random string consisting of a combination of A-Z,a-z,0-9, and _.
    """
    characters = string.ascii_letters + string.digits + "_"
    return "".join(random.choice(characters) for _ in range(length))  # nosec


class TestOrcaSqlLogic(unittest.TestCase):
    """
    Note that currently all the function calls in the orca_sql library
    return a SQL text string and have no logic except for the app_user_sql
    function that requires a string for the user password. The tests below
    validate the logic in the function.
    """

    def test_app_user_sql_happy_path(self) -> None:
        """
        Tests the happy path for the app_user_sql function and validates the
        user password is a part of the SQL.
        """
        user_name = uuid.uuid4().__str__()
        user_sql = orca_sql.app_user_sql(user_name)

        # Check that the username is in the SQL and the type is text
        self.assertIn(user_name, user_sql.text)
        self.assertEqual(type(user_sql), TextClause)

    def test_all_functions_return_text(self) -> None:
        """
        Validates that all functions return a type TextClause
        """

        for name, function in getmembers(orca_sql, isfunction):
            if name not in ["text"]:
                with self.subTest(function=function):
                    # These functions take in two string parameters.
                    if name in [
                        "app_database_sql",
                        "dbo_role_sql",
                    ]:
                        self.assertEqual(
                            type(
                                function(uuid.uuid4().__str__(), uuid.uuid4().__str__())
                            ),
                            TextClause,
                        )

                    # These functions take in a string parameter.
                    elif name in [
                        "app_database_comment_sql",
                        "app_role_sql",
                        "app_user_sql",
                        "drop_dr_role_sql",
                        "drop_dbo_user_sql",
                        "drop_drdbo_role_sql",
                        "reconcile_s3_object_partition_sql",
                    ]:
                        self.assertEqual(
                            type(function(generate_randoms_string())), TextClause
                        )

                    # All other functions have no parameters passed
                    else:
                        self.assertEqual(type(function()), TextClause)
