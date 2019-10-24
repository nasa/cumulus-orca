"""
Name: test_copy_files_to_archive.py

Description:  Unit tests for copy_files_to_archive.py.
"""
import os
import time
import unittest
from unittest.mock import Mock

import boto3
import database
import requests_db
from botocore.exceptions import ClientError

import copy_files_to_archive
from request_helpers import (REQUEST_ID4, REQUEST_ID7, 
                             PROTECTED_BUCKET,
                             create_copy_event2,
                             create_copy_handler_event, create_select_requests)

class TestCopyFiles(unittest.TestCase):  #pylint: disable-msg=too-many-instance-attributes
    """
    TestCopyFiles.
    """
    def setUp(self):
        self.mock_boto3_client = boto3.client
        os.environ['COPY_RETRIES'] = '2'
        os.environ['COPY_RETRY_SLEEP_SECS'] = '1'
        os.environ["DATABASE_HOST"] = "my.db.host.gov"
        os.environ["DATABASE_PORT"] = "5400"
        os.environ["DATABASE_NAME"] = "sndbx"
        os.environ["DATABASE_USER"] = "unittestdbuser"
        os.environ["DATABASE_PW"] = "unittestdbpw"
        self.exp_other_bucket = "unittest_protected_bucket"
        self.exp_src_bucket = 'my-dr-fake-glacier-bucket'
        self.exp_target_bucket = PROTECTED_BUCKET

        self.exp_file_key1 = 'dr-glacier/MOD09GQ.A0219114.N5aUCG.006.0656338553321.txt'
        self.handler_input_event = create_copy_handler_event()
        self.mock_single_query = database.single_query
        self.mock_time_sleep = time.sleep

    def tearDown(self):
        time.sleep = self.mock_time_sleep
        database.single_query = self.mock_single_query
        boto3.client = self.mock_boto3_client
        try:
            del os.environ['COPY_RETRY_SLEEP_SECS']
            del os.environ['COPY_RETRIES']
            del os.environ["DATABASE_HOST"]
            del os.environ["DATABASE_NAME"]
            del os.environ["DATABASE_USER"]
            del os.environ["DATABASE_PW"]
        except KeyError:
            pass

    def test_handler_one_file_success(self):
        """
        Test copy lambda with one file, expecting successful result.
        """
        del os.environ['COPY_RETRY_SLEEP_SECS']
        del os.environ['COPY_RETRIES']
        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.copy_object = Mock(side_effect=[None])
        exp_upd_result = []
        exp_request_ids = [REQUEST_ID7]
        _, exp_result = create_select_requests(exp_request_ids)
        database.single_query = Mock(side_effect=[exp_result, exp_upd_result])
        result = copy_files_to_archive.handler(self.handler_input_event, None)
        os.environ['COPY_RETRIES'] = '2'
        os.environ['COPY_RETRY_SLEEP_SECS'] = '1'
        boto3.client.assert_called_with('s3')
        s3_cli.copy_object.assert_called_with(Bucket=self.exp_target_bucket,
                                              CopySource={'Bucket': self.exp_src_bucket,
                                                          'Key': self.exp_file_key1},
                                              Key=self.exp_file_key1)
        exp_result = [{"success": True,
                       "source_bucket": self.exp_src_bucket,
                       "source_key": self.exp_file_key1,
                       "request_id": REQUEST_ID7,
                       "target_bucket": self.exp_target_bucket,
                       "err_msg": ""}]
        self.assertEqual(exp_result, result)
        database.single_query.assert_called()

    def test_handler_db_update_err(self):
        """
        Test copy lambda with error updating db.
        """
        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.copy_object = Mock(side_effect=[None])
        exp_request_ids = [REQUEST_ID7]
        _, exp_result = create_select_requests(exp_request_ids)
        time.sleep = Mock(side_effect=None)
        exp_err = 'Database Error. Internal database error, please contact LP DAAC User Services'
        database.single_query = Mock(
            side_effect=[exp_result, requests_db.DatabaseError(exp_err),
                         requests_db.DatabaseError(exp_err)])
        result = copy_files_to_archive.handler(self.handler_input_event, None)
        exp_result = [{'success': True, 'source_bucket': 'my-dr-fake-glacier-bucket',
                       'source_key': self.exp_file_key1,
                       'request_id': REQUEST_ID7,
                       'target_bucket': PROTECTED_BUCKET, 'err_msg': ''}]
        self.assertEqual(exp_result, result)

    def test_handler_db_read_err(self):
        """
        Test copy lambda with error reading db.
        """
        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.copy_object = Mock(side_effect=[None])
        exp_request_ids = [REQUEST_ID7]
        _, exp_result = create_select_requests(exp_request_ids)
        time.sleep = Mock(side_effect=None)
        exp_err = 'Database Error. Internal database error, please contact LP DAAC User Services'
        database.single_query = Mock(
            side_effect=[requests_db.DatabaseError(exp_err),
                         requests_db.DatabaseError(exp_err)])
        try:
            copy_files_to_archive.handler(self.handler_input_event, None)
        except copy_files_to_archive.CopyRequestError as err:
            exp_result = [{'success': False,
                           'source_bucket': 'my-dr-fake-glacier-bucket',
                           'source_key': self.exp_file_key1}]
            exp_err = f"File copy failed. {exp_result}"
            self.assertEqual(exp_err, str(err))

    def test_handler_db_read_notfound(self):
        """
        Test copy lambda with no key found reading db.
        """
        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.copy_object = Mock(side_effect=[None])
        exp_request_ids = [REQUEST_ID7]
        _, exp_result = create_select_requests(exp_request_ids)
        time.sleep = Mock(side_effect=None)
        database.single_query = Mock(side_effect=[[], []])
        try:
            copy_files_to_archive.handler(self.handler_input_event, None)
        except copy_files_to_archive.CopyRequestError as err:
            exp_result = [{'success': False,
                           'source_bucket': 'my-dr-fake-glacier-bucket',
                           'source_key': self.exp_file_key1}]
            exp_err = f"File copy failed. {exp_result}"
            self.assertEqual(exp_err, str(err))

    def test_handler_two_records_success(self):
        """
        Test copy lambda with two files, expecting successful result.
        """
        os.environ['DEVELOP_TESTS'] = "False"
        exp_file_key = 'dr-glacier/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf'
        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.copy_object = Mock(side_effect=[None, None])
        exp_upd_result = []
        exp_request_ids = [REQUEST_ID4, REQUEST_ID7]
        _, exp_result = create_select_requests(exp_request_ids)
        database.single_query = Mock(side_effect=[exp_result, exp_upd_result,
                                                  exp_result, exp_upd_result])

        exp_rec_2 = create_copy_event2()
        self.handler_input_event["Records"].append(exp_rec_2)
        result = copy_files_to_archive.handler(self.handler_input_event, None)

        boto3.client.assert_called_with('s3')
        exp_result = [{"success": True, "source_bucket": self.exp_src_bucket,
                       "source_key": self.exp_file_key1,
                       "request_id": REQUEST_ID7,
                       "target_bucket": self.exp_target_bucket,
                       "err_msg": ""},
                      {"success": True, "source_bucket": self.exp_src_bucket,
                       "source_key": exp_file_key,
                       "request_id": REQUEST_ID7,
                       "target_bucket": self.exp_target_bucket,
                       "err_msg": ""}]
        self.assertEqual(exp_result, result)

        s3_cli.copy_object.assert_any_call(Bucket=self.exp_target_bucket,
                                           CopySource={'Bucket': self.exp_src_bucket,
                                                       'Key': self.exp_file_key1},
                                           Key=self.exp_file_key1)
        s3_cli.copy_object.assert_any_call(Bucket=self.exp_target_bucket,
                                           CopySource={'Bucket': self.exp_src_bucket,
                                                       'Key': exp_file_key},
                                           Key=exp_file_key)

    def test_handler_one_file_fail_3x(self):
        """
        Test copy lambda with one failed copy after 3 retries.
        """
        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.copy_object = Mock(side_effect=[ClientError({'Error': {'Code': 'AccessDenied'}},
                                                           'copy_object'),
                                               ClientError({'Error': {'Code': 'AccessDenied'}},
                                                           'copy_object'),
                                               ClientError({'Error': {'Code': 'AccessDenied'}},
                                                           'copy_object')])
        s3_cli.head_object = Mock()
        exp_error = "File copy failed. [{'success': False, " \
                    f"'source_bucket': '{self.exp_src_bucket}', " \
                    f"'source_key': '{self.exp_file_key1}', " \
                    f"'request_id': '{REQUEST_ID7}', " \
                    f"'target_bucket': '{self.exp_target_bucket}', " \
                    "'err_msg': 'An error occurred (AccessDenied) when calling " \
                    "the copy_object operation: Unknown'}]"
        exp_upd_result = []

        exp_request_ids = [REQUEST_ID7, REQUEST_ID4]
        _, exp_result = create_select_requests(exp_request_ids)

        database.single_query = Mock(side_effect=[exp_result,
                                                  exp_result,
                                                  exp_upd_result,
                                                  exp_result,
                                                  exp_upd_result])
        try:
            copy_files_to_archive.handler(self.handler_input_event, None)
            self.fail("expected CopyRequestError")
        except copy_files_to_archive.CopyRequestError as ex:
            self.assertEqual(exp_error, str(ex))
        boto3.client.assert_called_with('s3')
        s3_cli.copy_object.assert_called_with(Bucket=self.exp_target_bucket,
                                              CopySource={'Bucket': self.exp_src_bucket,
                                                          'Key': self.exp_file_key1},
                                              Key=self.exp_file_key1)
        database.single_query.assert_called()

    def test_handler_one_file_retry2_success(self):
        """
        Test copy lambda with two failed copy attempts, third attempt successful.
        """
        del os.environ['COPY_RETRY_SLEEP_SECS']
        del os.environ['COPY_RETRIES']
        time.sleep(1)
        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.copy_object = Mock(side_effect=[ClientError({'Error': {'Code': 'AccessDenied'}},
                                                           'copy_object'),
                                               None])
        exp_request_ids = [REQUEST_ID7, REQUEST_ID4]
        _, exp_result = create_select_requests(exp_request_ids)
        exp_upd_result = []
        database.single_query = Mock(side_effect=[exp_result,
                                                  exp_upd_result,
                                                  exp_result,
                                                  exp_upd_result])
        result = copy_files_to_archive.handler(self.handler_input_event, None)
        os.environ['COPY_RETRIES'] = '2'
        os.environ['COPY_RETRY_SLEEP_SECS'] = '1'
        boto3.client.assert_called_with('s3')
        exp_result = [{"success": True, "source_bucket": self.exp_src_bucket,
                       "source_key": self.exp_file_key1,
                       "request_id": REQUEST_ID7,
                       "target_bucket": self.exp_target_bucket,
                       "err_msg": ""}]
        self.assertEqual(exp_result, result)
        s3_cli.copy_object.assert_called_with(Bucket=self.exp_target_bucket,
                                              CopySource={'Bucket': self.exp_src_bucket,
                                                          'Key': self.exp_file_key1},
                                              Key=self.exp_file_key1)
        database.single_query.assert_called()

    def test_handler_no_object_key_in_event(self):
        """
        Test copy lambda with missing "object" key in input event.
        """
        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.copy_object = Mock(side_effect=[None])
        mydict = self.handler_input_event["Records"][0]["s3"]["object"]
        mydict.pop('key')
        exp_err = f'event record: "{self.handler_input_event["Records"][0]}" does not contain a ' \
                  f'value for Records["s3"]["object"]["key"]'
        try:
            copy_files_to_archive.handler(self.handler_input_event, None)
            self.fail("expected CopyRequestError")
        except copy_files_to_archive.CopyRequestError as ex:
            self.assertEqual(exp_err, str(ex))


if __name__ == '__main__':
    unittest.main(argv=['start'])
