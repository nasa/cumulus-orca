"""
Name: test_get_current_archive_list.py

Description:  Unit tests for test_get_current_archive_list.py.
"""
import datetime
import json
import random
import unittest
import uuid
from unittest.mock import Mock, call, patch, MagicMock

from fastjsonschema import JsonSchemaValueException

import get_current_archive_list
from orca_shared.recovery.shared_recovery import OrcaStatus
from orca_shared.recovery import shared_recovery


class TestGetCurrentArchiveList(
    unittest.TestCase
):  # pylint: disable-msg=too-many-instance-attributes
    """
    TestGetCurrentArchiveList.
    """
