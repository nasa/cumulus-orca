"""
Name: test_internal_reconcile_report_phantom.py
Description:  Unit tests for internal_reconcile_report_phantom.py.
"""
import datetime
import json
import random
import unittest
import uuid
from unittest.mock import MagicMock, Mock, call, patch

from fastjsonschema import JsonSchemaValueException
from orca_shared.reconciliation import shared_reconciliation

import internal_reconcile_report_phantom


class TestInternalReconcileReportPhantom(
    unittest.TestCase
):  # pylint: disable-msg=too-many-instance-attributes
    """
    TestInternalReconcileReportPhantom.
    """

    def test_dummy():
        pass
