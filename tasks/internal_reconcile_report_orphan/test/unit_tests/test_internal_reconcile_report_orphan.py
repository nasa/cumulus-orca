"""
Name: test_internal_reconcile_report_orphan.py
Description:  Unit tests for internal_reconcile_report_orphan.py.
"""
import datetime
import json
import random
import unittest
import uuid
from unittest.mock import MagicMock, Mock, call, patch

from fastjsonschema import JsonSchemaValueException
from orca_shared.reconciliation import shared_reconciliation
 
import internal_reconcile_report_orphan


class TestInternalReconcileReportOrphan(
    unittest.TestCase
):  # pylint: disable-msg=too-many-instance-attributes
    """
    TestInternalReconcileReportOrphan.
    """

    def test_dummy():
        pass
