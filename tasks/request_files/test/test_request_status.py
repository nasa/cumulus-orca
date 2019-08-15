"""
Name: test_request_status.py

Description:  Unit tests for request_status.py.
"""
import unittest
#from unittest.mock import Mock
#from cumulus_logger import CumulusLogger
#from helpers import LambdaContextMock, create_handler_event, create_task_event
import os
import request_status
import requests
#import test_requests

class TestRequestStatus(unittest.TestCase):
    """
    TestRequestStatus.
    """
    def setUp(self):
        #self.context = LambdaContextMock()
        #self.mock_error = CumulusLogger.error
        os.environ["DATABASE_HOST"] = "elpdvx143.cr.usgs.gov"
        os.environ["DATABASE_NAME"] = "labsndbx"
        os.environ["DATABASE_USER"] = "postgres"
        os.environ["DATABASE_PW"] = "July2019"

    def tearDown(self):
        #CumulusLogger.error = self.mock_error
        del os.environ["DATABASE_HOST"]
        del os.environ["DATABASE_NAME"]
        del os.environ["DATABASE_USER"]
        del os.environ["DATABASE_PW"]


    def test_handler_add(self):
        """
        Test successful with four keys returned.
        """
        handler_input_event = {}
        granule_id = 'granule_new'
        request_id = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"
        status = "inprogress"
        handler_input_event["granule_id"] = granule_id
        handler_input_event["request_id"] = request_id
        handler_input_event["status"] = status
        handler_input_event["function"] = "add"
        exp_result = {}
        exp_result["granule_id"] = granule_id
        exp_result["request_id"] = request_id
        exp_result["job_status"] = status
        try:
            result = request_status.handler(handler_input_event, None)
            print(result)
            self.assertEqual(exp_result["granule_id"], result["granule_id"])
            self.assertEqual(exp_result["request_id"], result["request_id"])
            self.assertEqual(exp_result["job_status"], result["job_status"])
        except requests.NotFound as err:
            self.assertEqual(f"Unknown granule_id: {granule_id}", str(err))


    def test_task_query_granule_id(self):
        """
        Test query by granule_id.
        """
        handler_input_event = {}
        granule_id = 'granule_1'
        handler_input_event["granule_id"] = granule_id
        handler_input_event["function"] = "query"
        exp_result = []
        try:
            result = request_status.task(handler_input_event, None)
            print(result)
            self.assertEqual(exp_result, result)
        except requests.NotFound as err:
            self.assertEqual(f"Unknown granule_id: {granule_id}", str(err))

    def test_task_query_request_id(self):
        """
        Test query by request_id.
        """
        handler_input_event = {}
        request_id = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"
        handler_input_event["request_id"] = request_id
        handler_input_event["function"] = "query"
        exp_result = []
        try:
            result = request_status.task(handler_input_event, None)
            print(result)
            self.assertEqual(exp_result, result)
        except requests.NotFound as err:
            self.assertEqual(f"Unknown request_id: {request_id}", str(err))

    def test_task_query_job_id(self):
        """
        Test query by job_id.
        """
        handler_input_event = {}
        job_id = 1
        handler_input_event["job_id"] = job_id
        handler_input_event["function"] = "query"
        exp_result = []
        try:
            result = request_status.task(handler_input_event, None)
            print(result)
            self.assertEqual(exp_result, result)
        except requests.NotFound as err:
            self.assertEqual(f"Unknown job_id: {job_id}", str(err))

    def test_task_clear(self):
        """
        Test clearing the request_status table.
        """
        handler_input_event = {}
        handler_input_event["function"] = "clear"
        exp_result = []
        try:
            result = request_status.task(handler_input_event, None)
            print(result)
            self.assertEqual(exp_result, result)
        except requests.NotFound as err:
            self.assertEqual("No granules found", str(err))


if __name__ == '__main__':
    unittest.main(argv=['start'])
