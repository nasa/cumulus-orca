"""
Name: test_orca_reconcile_sql.py

Description: Testing library for the orca_reconcile_sql.py.
"""

import unittest
from inspect import getmembers, isfunction

from sqlalchemy.sql.elements import TextClause

from install import orca_reconcile_sql


class TestOrcaSqlLogic(unittest.TestCase):
    """
    Note that currently all of the function calls in the orca_reconcile_sql.py
    return a SQL text string. The tests below
    validate the logic in the function.
    """

    def test_all_functions_return_text(self) -> None:
        """
        Validates that all functions return a type TextClause
        """

        for name, function in getmembers(orca_reconcile_sql, isfunction):
            if name not in ["text"]:
                with self.subTest(function=function):
                    if name in ["reconcile_status_table_sql", "reconcile_job_table_sql", "reconcile_s3_object_table_sql", "reconcile_catalog_mismatch_report_table_sql",
                                  "reconcile_orphan_report_table_sql", "reconcile_phantom_report_table_sql", "drop_extension", "create_extension"]:
                        self.assertEqual(type(function()), TextClause)