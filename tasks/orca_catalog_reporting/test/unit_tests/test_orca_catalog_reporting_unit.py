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

import orca_catalog_reporting


class TestRequestStatusForGranuleUnit(
    unittest.TestCase
):  # pylint: disable-msg=too-many-instance-attributes
    """
    TestOrcaCatalogReporting.
    """
    def test_task_output_json_schema(self):
        """
        Checks a realistic output against the output.json.
        """
        result = orca_catalog_reporting.handler(
            {
                "pageIndex": 0,
                "endTimestamp": "2021-10-08T19:24:07.605323Z"
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
        result = orca_catalog_reporting.handler(
            {
                "pageIndex": 0,
                "providerId": [uuid.uuid4().__str__(), uuid.uuid4().__str__()],
                "collectionId": [uuid.uuid4().__str__(), uuid.uuid4().__str__()],
                "granuleId": [uuid.uuid4().__str__(), uuid.uuid4().__str__()],
                "startTimestamp": "2021-10-08T16:24:07.605323Z",
                "endTimestamp": "2021-10-08T19:24:07.605323Z"
            }, Mock()
        )

        with open("schemas/output.json", "r") as raw_schema:
            schema = json.loads(raw_schema.read())

        validate = fastjsonschema.compile(schema)
        validate(result)

