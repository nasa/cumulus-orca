"""
Name: test_request_status.py

Description:  Unit tests for request_status.py.
"""
import unittest
from unittest.mock import Mock
#from cumulus_logger import CumulusLogger
#from helpers import LambdaContextMock, create_handler_event, create_task_event
import os
import request_status
import requests
import test_requests

class TestRequestStatus(unittest.TestCase):
    """
    TestRequestStatus.
    """
    def setUp(self):
        #self.context = LambdaContextMock()
        #self.mock_error = CumulusLogger.error
        os.environ["DATABASE_HOST"] = "elpdvx143.cr.usgs.gov"
        os.environ["DATABASE_NAME"] = "labsndbx"
        os.environ["DATABASE_USER"] = "druser"
        os.environ["DATABASE_PW"] = "July2019"
        pass

    def tearDown(self):
        #CumulusLogger.error = self.mock_error
        del os.environ["DATABASE_HOST"]
        del os.environ["DATABASE_NAME"]
        del os.environ["DATABASE_USER"]
        del os.environ["DATABASE_PW"]
        

    def test_handler(self):
        """
        Test successful with four keys returned.
        """
        handler_input_event = {}
        granule_id = 'x'
        handler_input_event["granule_id"] = granule_id
        handler_input_event["function"] = "add"
        exp_result = {}
        try:
            result = request_status.handler(handler_input_event, None)
            print(result)
            self.assertEqual(exp_result, result)
        except requests.NotFound as err:
            self.assertEqual(f"Unknown granule_id: {granule_id}", str(err))
        
        self.assertEqual(exp_result, result)

    def test_task(self):
        """
        Test successful with four keys returned.
        """
        handler_input_event = {}
        granule_id = 'x'
        handler_input_event["granule_id"] = granule_id
        handler_input_event["function"] = "query"
        exp_result = {}
        try:
            result = request_status.task(handler_input_event, None)
            print(result)
            self.assertEqual(exp_result, result)
        except requests.NotFound as err:
            self.assertEqual(f"Unknown granule_id: {granule_id}", str(err))
        
        
if __name__ == '__main__':
    unittest.main(argv=['start'])
