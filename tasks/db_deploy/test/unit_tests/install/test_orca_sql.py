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
    charachters = string.ascii_letters + string.digits + "_"
    return "".join(random.choice(charachters) for _ in range(length))  # nosec


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
        user_pass = "MySup3rL0ngPassForAUser"  # nosec
        user_name = uuid.uuid4().__str__()
        user_sql = orca_sql.app_user_sql(user_pass, user_name)

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
                    orca_sql.app_user_sql("orcauser", bad_password)
                self.assertEqual(str(cm.exception), message)

        bad_user_names = [None, ""]
        message = "Username must be non-empty."
        for bad_user_name in bad_user_names:
            with self.subTest(bad_user_name=bad_user_name):
                with self.assertRaises(Exception) as cm:
                    orca_sql.app_user_sql(bad_user_name, "AbCdEfG12345")
                self.assertEqual(str(cm.exception), message)

        message = "Username must be less than 64 characters."
        bad_user_name = "".join("a" * 64)
        with self.subTest(bad_user_name=bad_user_name) as cm:
            with self.assertRaises(Exception) as cm:
                orca_sql.app_user_sql(bad_user_name, "AbCdEfG12345")
            self.assertEqual(str(cm.exception), message)

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
                        "app_user_sql",
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
                        "dbo_role_sql",
                        "app_role_sql",
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

    def test_reconcile_s3_object_partition_sql_happy_path(self) -> None:
        """
        Tests that a well formed table name passes checks. The name must be made up of the
        characters A-Z, a-z, 0-9, or _
        """
        partition_name = generate_randoms_string()
        sql_text = orca_sql.reconcile_s3_object_partition_sql(partition_name)
        self.assertEqual(type(sql_text), TextClause)

    def test_reconcile_s3_object_partition_sql_exception(self) -> None:
        """
        Tests that an exception is thrown if the table name is not made up of the following
        characters A-Z, a-z, 0-9, and _. Also the table name cannot be None.
        """
        # Test for None
        partition_name = None
        with self.assertRaises(ValueError) as ve:
            orca_sql.reconcile_s3_object_partition_sql(partition_name)
        self.assertEqual(
            "Table name must be a string and cannot be None.", str(ve.exception)
        )

        partition_names = ["", uuid.uuid4().__str__(), "$!ABadName2"]
        for partition_name in partition_names:
            with self.subTest(partition_name=partition_name):
                with self.assertRaises(ValueError) as ve:
                    orca_sql.reconcile_s3_object_partition_sql(partition_name)
                self.assertEqual(
                    f"Table name {partition_name} is invalid.", str(ve.exception)
                )
