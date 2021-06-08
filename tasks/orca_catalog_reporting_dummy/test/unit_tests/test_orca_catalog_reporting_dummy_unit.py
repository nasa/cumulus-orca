"""
Name: test_request_status_for_granule_unit.py

Description:  Unit tests for request_status_for_granule.py.
"""
from datetime import datetime, timezone
import json
import unittest
import uuid
from unittest.mock import Mock

import fastjsonschema

import orca_catalog_reporting_dummy


class TestRequestStatusForGranuleUnit(
    unittest.TestCase
):  # pylint: disable-msg=too-many-instance-attributes
    """
    TestOrcaCatalogReportingDummy.
    """
    def test_task_output_json_schema(self):
        """
        Checks a realistic output against the output.json.
        """
        result = orca_catalog_reporting_dummy.handler(
            {
            }, Mock()
        )

        with open("schemas/output.json", "r") as raw_schema:
            schema = json.loads(raw_schema.read())

        validate = fastjsonschema.compile(schema)
        validate(result)

    def test_task_input_json_schema(self):
        """
        Checks a realistic input against the input.json.
        """
        result = orca_catalog_reporting_dummy.handler(
            {
                "providerId": [uuid.uuid4().__str__(), uuid.uuid4().__str__()],
                "collectionId": [uuid.uuid4().__str__(), uuid.uuid4().__str__()],
                "granuleId": [uuid.uuid4().__str__(), uuid.uuid4().__str__()],
                "startTimestamp": datetime.now(timezone.utc).isoformat(),
                "endTimestamp": datetime.now(timezone.utc).isoformat()
            }, Mock()
        )

        with open("schemas/output.json", "r") as raw_schema:
            schema = json.loads(raw_schema.read())

        validate = fastjsonschema.compile(schema)
        validate(result)

