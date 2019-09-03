"""
Name: test_request_status.py

Description:  Unit tests for request_status.py.
"""
import os
import unittest
from unittest.mock import Mock

import request_status
import requests
from requests import result_to_json
from request_helpers import (
    JOB_ID_1, JOB_ID_2, JOB_ID_3, JOB_ID_4, JOB_ID_5, JOB_ID_6, JOB_ID_7,
    JOB_ID_8, JOB_ID_9, JOB_ID_10, JOB_ID_11, REQUEST_ID_EXP_1,
    create_insert_request, create_select_requests)
import utils
import utils.database

UTC_NOW_EXP_1 = requests.get_utc_now_iso()

class TestRequestStatus(unittest.TestCase):
    """
    TestRequestStatus.
    """
    def setUp(self):
        os.environ["DATABASE_HOST"] = "my.db.host.gov"
        os.environ["DATABASE_NAME"] = "sndbx"
        os.environ["DATABASE_USER"] = "unittestdbuser"
        os.environ["DATABASE_PW"] = "unittestdbpw"
        self.mock_utcnow = requests.get_utc_now_iso
        self.mock_request_id = requests.request_id_generator
        self.mock_single_query = utils.database.single_query

    def tearDown(self):
        utils.database.single_query = self.mock_single_query
        requests.request_id_generator = self.mock_request_id
        requests.get_utc_now_iso = self.mock_utcnow
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
        request_id_exp = REQUEST_ID_EXP_1
        requests.get_utc_now_iso = Mock(return_value=utc_now_exp)
        requests.request_id_generator = Mock(return_value=request_id_exp)
        granule_id = 'granule_1'
        request_id = REQUEST_ID_EXP_1
        status = "error"
        req_err = "error submitting restore request"
        handler_input_event["function"] = "add"
        handler_input_event["error"] = req_err
        qresult, ins_result = create_insert_request(JOB_ID_1, request_id, granule_id, "object_key",
                                                    "restore", "my_s3_bucket", status,
                                                    utc_now_exp, None, req_err)
        utils.database.single_query = Mock(side_effect=[qresult, ins_result])
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
            self.assertEqual("Missing 'request_id' in input data", str(err))
        handler_input_event["request_id"] = request_id
        try:
            result = request_status.handler(handler_input_event, None)
            expected = result_to_json(ins_result)
            self.assertEqual(expected, result)
            utils.database.single_query.assert_called()
        except request_status.BadRequestError as err:
            self.fail(err)
        except requests.DbError as err:
            self.fail(err)


    def test_task_query_all(self):
        """
        Test query by granule_id.
        """
        exp_job_ids = [JOB_ID_1, JOB_ID_2, JOB_ID_3, JOB_ID_4, JOB_ID_5,
                       JOB_ID_6, JOB_ID_7, JOB_ID_8, JOB_ID_9, JOB_ID_10,
                       JOB_ID_11]
        qresult, exp_result = create_select_requests(exp_job_ids)
        handler_input_event = {}
        handler_input_event["function"] = "query"
        expected = result_to_json(exp_result)
        utils.database.single_query = Mock(side_effect=[qresult])
        try:
            result = request_status.task(handler_input_event, None)
            self.assertEqual(expected, result)
            utils.database.single_query.assert_called()
        except requests.NotFound as err:
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
        exp_job_ids = [JOB_ID_1]
        _, exp_result = create_select_requests(exp_job_ids)
        expected = result_to_json(exp_result)
        utils.database.single_query = Mock(side_effect=[exp_result])
        try:
            result = request_status.task(handler_input_event, None)
            self.assertEqual(expected, result)
        except requests.NotFound as err:
            self.assertEqual(f"Unknown granule_id: {granule_id}", str(err))


    def test_task_query_request_id(self):
        """
        Test query by request_id.
        """
        handler_input_event = {}
        request_id = REQUEST_ID_EXP_1
        handler_input_event["request_id"] = request_id
        handler_input_event["function"] = "query"
        exp_result = []
        exp_job_ids = [JOB_ID_1]
        _, exp_result = create_select_requests(exp_job_ids)
        expected = result_to_json(exp_result)
        utils.database.single_query = Mock(side_effect=[exp_result])
        try:
            result = request_status.task(handler_input_event, None)
            self.assertEqual(expected, result)
            utils.database.single_query.assert_called_once()
        except requests.NotFound as err:
            self.assertEqual(f"Unknown request_id: {request_id}", str(err))

    def test_task_query_request_id_dberror(self):
        """
        Test query by request_id.
        """
        handler_input_event = {}
        request_id = REQUEST_ID_EXP_1
        handler_input_event["request_id"] = request_id
        handler_input_event["function"] = "query"
        utils.database.single_query = Mock(side_effect=[requests.DbError("Db call failed")])
        try:
            request_status.task(handler_input_event, None)
            self.fail("expected DbError")
        except requests.DatabaseError as err:
            self.assertEqual("Db call failed", str(err))
            utils.database.single_query.assert_called_once()

    def test_task_query_request_id_notfound(self):
        """
        Test query by request_id.
        """
        handler_input_event = {}
        request_id = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"

        handler_input_event["request_id"] = request_id
        handler_input_event["function"] = "query"
        exp_result = []
        utils.database.single_query = Mock(side_effect=[exp_result])
        try:
            result = request_status.task(handler_input_event, None)
            self.assertEqual(exp_result, result)
            utils.database.single_query.assert_called_once()
        except requests.NotFound as err:
            self.fail(str(err))


    def test_task_query_job_id(self):
        """
        Test query by job_id.
        """
        handler_input_event = {}
        job_id = 1
        handler_input_event["job_id"] = job_id
        handler_input_event["function"] = "query"
        exp_result = []
        exp_job_ids = [JOB_ID_1]
        _, exp_result = create_select_requests(exp_job_ids)
        expected = result_to_json(exp_result)
        utils.database.single_query = Mock(side_effect=[exp_result])
        try:
            result = request_status.task(handler_input_event, None)
            self.assertEqual(expected, result)
        except requests.NotFound as err:
            self.assertEqual(f"Unknown job_id: {job_id}", str(err))

    def test_task_clear(self):
        """
        Test clearing the request_status table.
        """
        handler_input_event = {}
        handler_input_event["function"] = "clear"
        exp_result = []
        exp_job_ids = [JOB_ID_1, JOB_ID_2, JOB_ID_3, JOB_ID_4, JOB_ID_5,
                       JOB_ID_6, JOB_ID_7, JOB_ID_8, JOB_ID_9, JOB_ID_10,
                       JOB_ID_11]
        try:
            qresult = create_select_requests(exp_job_ids)
            empty_result = []
            utils.database.single_query = Mock(
                side_effect=[qresult, empty_result, empty_result,
                             empty_result, empty_result, empty_result,
                             empty_result, empty_result, empty_result,
                             empty_result, empty_result, empty_result,
                             empty_result])
            result = request_status.task(handler_input_event, None)
            self.assertEqual(exp_result, result)
        except requests.NotFound as err:
            self.assertEqual("No granules found", str(err))


if __name__ == '__main__':
    unittest.main(argv=['start'])
