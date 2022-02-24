"""
Name: test_internal_reconcile_report_phantom.py
Description:  Unit tests for internal_reconcile_report_phantom.py.
"""
import datetime
import json
import random
import unittest
import uuid
from unittest.mock import Mock, call, patch, MagicMock

from fastjsonschema import JsonSchemaValueException

import internal_reconcile_report_phantom
from orca_shared.reconciliation import shared_reconciliation


class TestInternalReconcileReportPhantom(
    unittest.TestCase
):  # pylint: disable-msg=too-many-instance-attributes
    """
    TestInternalReconcileReportPhantom.
    """
def test_dummy():
    pass