"""
Name: test_request_status.py

Description:  Unit tests for request_status.py.
"""
import os
import unittest
from unittest.mock import Mock
import database
import requests_db
from requests_db import result_to_json
import request_status
from request_helpers import (REQUEST_GROUP_ID_EXP_1, REQUEST_ID1, REQUEST_ID2,
                             REQUEST_ID3, REQUEST_ID4, REQUEST_ID5,
                             REQUEST_ID6, REQUEST_ID7, REQUEST_ID8,
                             REQUEST_ID9, REQUEST_ID10, REQUEST_ID11,
                             create_insert_request, create_select_requests)


UTC_NOW_EXP_1 = requests_db.get_utc_now_iso()

class TestRequestStatus(unittest.TestCase):
    """
    TestRequestStatus.
    """
    def setUp(self):
        os.environ["DATABASE_HOST"] = "my.db.host.gov"
        os.environ["DATABASE_NAME"] = "sndbx"
        os.environ["DATABASE_USER"] = "unittestdbuser"
        os.environ["DATABASE_PW"] = "unittestdbpw"
        self.mock_utcnow = requests_db.get_utc_now_iso
        self.mock_request_group_id = requests_db.request_id_generator
        self.mock_single_query = database.single_query

    def tearDown(self):
        database.single_query = self.mock_single_query
        requests_db.request_id_generator = self.mock_request_group_id
        requests_db.get_utc_now_iso = self.mock_utcnow
        del os.environ["DATABASE_HOST"]
        del os.environ["DATABASE_NAME"]
        del os.environ["DATABASE_USER"]
        del os.environ["DATABASE_PW"]


    def test_handler_add(self):
        """
        Test successful with four keys returned.
        """
        handler_input_event = {}
        utc_now_exp = UTC_NOW_EXP_1
        requests_db.get_utc_now_iso = Mock(return_value=utc_now_exp)
        requests_db.request_id_generator = Mock(return_value=REQUEST_ID1)
        granule_id = 'granule_1'
        status = "error"
        req_err = "error submitting restore request"
        handler_input_event["function"] = "add"
        handler_input_event["error"] = req_err

        qresult, ins_result = create_insert_request(REQUEST_ID1, REQUEST_GROUP_ID_EXP_1,
                                                    granule_id, "object_key",
                                                    "restore", "my_s3_bucket", status,
                                                    utc_now_exp, None, req_err)
        database.single_query = Mock(side_effect=[qresult, ins_result])
        try:
            result = request_status.handler(handler_input_event, None)
            self.fail("expected BadRequestError")
        except request_status.BadRequestError as err:
            self.assertEqual("Missing 'granule_id' in input data", str(err))
        handler_input_event["granule_id"] = granule_id
        try:
            result = request_status.handler(handler_input_event, None)
            self.fail("expected BadRequestError")
        except request_status.BadRequestError as err:
            self.assertEqual("Missing 'request_group_id' in input data", str(err))
        handler_input_event["request_group_id"] = REQUEST_GROUP_ID_EXP_1
        try:
            result = request_status.handler(handler_input_event, None)
            expected = result_to_json(ins_result)
            self.assertEqual(expected, result)
            database.single_query.assert_called()
        except request_status.BadRequestError as err:
            self.fail(err)
        except requests_db.DbError as err:
            self.fail(err)


    def test_task_query_all(self):
        """
        Test query all.
        """
        exp_request_ids = [REQUEST_ID1, REQUEST_ID2, REQUEST_ID3, REQUEST_ID4, REQUEST_ID5,
                           REQUEST_ID6, REQUEST_ID7, REQUEST_ID8, REQUEST_ID9, REQUEST_ID10,
                           REQUEST_ID11]
        qresult, exp_result = create_select_requests(exp_request_ids)
        handler_input_event = {}
        handler_input_event["function"] = "query"
        expected = result_to_json(exp_result)
        database.single_query = Mock(side_effect=[qresult])
        try:
            result = request_status.task(handler_input_event, None)
            self.assertEqual(expected, result)
            database.single_query.assert_called()
        except requests_db.NotFound as err:
            self.fail(str(err))


    def test_task_query_granule_id(self):
        """
        Test query by granule_id.
        """
        handler_input_event = {}
        granule_id = 'granule_1'
        handler_input_event["granule_id"] = granule_id
        handler_input_event["function"] = "query"
        exp_result = []
        exp_request_ids = [REQUEST_ID1]
        _, exp_result = create_select_requests(exp_request_ids)
        expected = result_to_json(exp_result)
        database.single_query = Mock(side_effect=[exp_result])
        try:
            result = request_status.task(handler_input_event, None)
            self.assertEqual(expected, result)
        except requests_db.NotFound as err:
            self.assertEqual(f"Unknown granule_id: {granule_id}", str(err))


    def test_task_query_request_group_id(self):
        """
        Test query by request_group_id.
        """
        handler_input_event = {}
        request_group_id = REQUEST_GROUP_ID_EXP_1
        handler_input_event["request_group_id"] = request_group_id
        handler_input_event["function"] = "query"
        exp_request_ids = [REQUEST_ID1]
        _, exp_result = create_select_requests(exp_request_ids)
        expected = result_to_json(exp_result)
        database.single_query = Mock(side_effect=[exp_result])
        try:
            result = request_status.task(handler_input_event, None)
            self.assertEqual(expected, result)
            database.single_query.assert_called_once()
        except requests_db.NotFound as err:
            self.assertEqual(f"Unknown request_group_id: {request_group_id}", str(err))

    def test_task_query_request_group_id_dberror(self):
        """
        Test dberror running query by request_group_id.
        """
        handler_input_event = {}
        request_group_id = REQUEST_GROUP_ID_EXP_1
        handler_input_event["request_group_id"] = request_group_id
        handler_input_event["function"] = "query"
        database.single_query = Mock(side_effect=[requests_db.DbError("Db call failed")])
        try:
            request_status.task(handler_input_event, None)
            self.fail("expected DbError")
        except requests_db.DatabaseError as err:
            self.assertEqual("Db call failed", str(err))
            database.single_query.assert_called_once()

    def test_task_no_function(self):
        """
        Test no function given.
        """
        handler_input_event = {}
        try:
            request_status.task(handler_input_event, None)
            self.fail("expected BadRequestError")
        except request_status.BadRequestError as err:
            self.assertEqual("Missing 'function' in input data", str(err))


    def test_task_query_request_group_id_notfound(self):
        """
        Test query by request_group_id.
        """
        handler_input_event = {}
        request_group_id = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"

        handler_input_event["request_group_id"] = request_group_id
        handler_input_event["function"] = "query"
        exp_result = []
        database.single_query = Mock(side_effect=[exp_result])
        try:
            result = request_status.task(handler_input_event, None)
            self.assertEqual(exp_result, result)
            database.single_query.assert_called_once()
        except requests_db.NotFound as err:
            self.fail(str(err))


    def test_task_query_request_id(self):
        """
        Test query by request_id.
        """
        handler_input_event = {}
        request_id = 1
        handler_input_event["request_id"] = request_id
        handler_input_event["function"] = "query"
        exp_request_ids = [REQUEST_ID1]
        _, exp_result = create_select_requests(exp_request_ids)
        expected = result_to_json(exp_result)
        database.single_query = Mock(side_effect=[exp_result])
        try:
            result = request_status.task(handler_input_event, None)
            self.assertEqual(expected, result)
        except requests_db.NotFound as err:
            self.assertEqual(f"Unknown request_id: {request_id}", str(err))

    def test_task_query_object_key(self):
        """
        Test query by object_key.
        """
        handler_input_event = {}
        object_key = "objectkey_2"
        handler_input_event["object_key"] = object_key
        handler_input_event["function"] = "query"
        exp_request_ids = [REQUEST_ID4, REQUEST_ID7]
        _, exp_result = create_select_requests(exp_request_ids)
        expected = result_to_json(exp_result)
        database.single_query = Mock(side_effect=[exp_result])
        try:
            result = request_status.task(handler_input_event, None)
            self.assertEqual(expected, result)
        except requests_db.NotFound as err:
            self.assertEqual(f"Unknown object_key: {object_key}", str(err))

    def test_task_clear(self):
        """
        Test clearing the request_status table.
        """
        handler_input_event = {}
        handler_input_event["function"] = "clear"
        exp_result = []
        exp_request_ids = [REQUEST_ID1, REQUEST_ID2, REQUEST_ID3, REQUEST_ID4, REQUEST_ID5,
                           REQUEST_ID6, REQUEST_ID7, REQUEST_ID8, REQUEST_ID9, REQUEST_ID10,
                           REQUEST_ID11]
        try:
            qresult, _ = create_select_requests(exp_request_ids)
            empty_result = []
            database.single_query = Mock(
                side_effect=[qresult, empty_result, empty_result,
                             empty_result, empty_result, empty_result,
                             empty_result, empty_result, empty_result,
                             empty_result, empty_result, empty_result,
                             empty_result])
            result = request_status.task(handler_input_event, None)
            self.assertEqual(exp_result, result)
        except requests_db.NotFound as err:
            self.assertEqual("No granules found", str(err))


if __name__ == '__main__':
    unittest.main(argv=['start'])
