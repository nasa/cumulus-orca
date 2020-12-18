"""
Name: test_request_files.py

Description:  Unit tests for request_files.py.
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import os
import boto3
from botocore.exceptions import ClientError
from cumulus_logger import CumulusLogger
import requests_db
import db_config

from request_helpers import LambdaContextMock, create_handler_event
from request_helpers import (
    REQUEST_ID1, REQUEST_ID2, REQUEST_ID3, REQUEST_ID4,
    REQUEST_GROUP_ID_EXP_1, REQUEST_GROUP_ID_EXP_2,
    REQUEST_GROUP_ID_EXP_3, mock_ssm_get_parameter)
from request_helpers import print_rows

import request_files

UTC_NOW_EXP_1 = requests_db.get_utc_now_iso()
FILE1 = "MOD09GQ___006/2017/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.h5"
FILE2 = "MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.h5.met"
FILE3 = "MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321_ndvi.jpg"
FILE4 = "MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml"
PROTECTED_BUCKET = "sndbx-cumulus-protected"
PUBLIC_BUCKET = "sndbx-cumulus-public"
KEY1 = {"key": FILE1, "dest_bucket": PROTECTED_BUCKET}
KEY2 = {"key": FILE2, "dest_bucket": PROTECTED_BUCKET}
KEY3 = {"key": FILE3, "dest_bucket": None}
KEY4 = {"key": FILE4, "dest_bucket": PUBLIC_BUCKET}


class TestRequestFilesPostgres(unittest.TestCase):
    """
    TestRequestFiles.
    """

    def setUp(self):
        self.mock_boto3_client = boto3.client
        self.mock_info = CumulusLogger.info
        self.mock_error = CumulusLogger.error
        self.mock_generator = requests_db.request_id_generator
        db_config.set_env()
        os.environ['RESTORE_EXPIRE_DAYS'] = '5'
        os.environ['RESTORE_REQUEST_RETRIES'] = '3'
        os.environ['RESTORE_RETRIEVAL_TYPE'] = 'Standard'
        self.context = LambdaContextMock()

    def tearDown(self):
        boto3.client = Mock()
        mock_ssm_get_parameter(1)
        try:
            requests_db.delete_all_requests()
        except requests_db.NotFound:
            pass
        except requests_db.DatabaseError:
            pass
        requests_db.request_id_generator = self.mock_generator
        CumulusLogger.error = self.mock_error
        CumulusLogger.info = self.mock_info
        boto3.client = self.mock_boto3_client
        del os.environ['RESTORE_EXPIRE_DAYS']
        del os.environ['RESTORE_REQUEST_RETRIES']
        del os.environ["DATABASE_HOST"]
        del os.environ["DATABASE_NAME"]
        del os.environ["DATABASE_USER"]
        del os.environ["DATABASE_PW"]
        del os.environ["DATABASE_PORT"]
        del os.environ["RESTORE_RETRIEVAL_TYPE"]

    def test_handler(self):
        """
        Tests the handler
        """
        input_event = create_handler_event()
        task_input = {"input": input_event["payload"], "config": {}}
        exp_err = f'request: {task_input} does not contain a config value for glacier-bucket'
        CumulusLogger.error = Mock()
        try:
            request_files.handler(input_event, self.context)
        except request_files.RestoreRequestError as roe:
            self.assertEqual(exp_err, str(roe))

    def test_task_one_granule_4_files_success(self):
        """
        Test four files for one granule - successful
        """
        granule_id = "MOD09GQ.A0219114.N5aUCG.006.0656338553321"
        files = [KEY1, KEY2, KEY3, KEY4]
        input_event = {
            "input": {
                "granules": [
                    {
                        "granuleId": granule_id,
                        "keys": files
                    }
                ]
            },
            "config": {
                "glacier-bucket": "my-dr-fake-glacier-bucket"
            }
        }

        requests_db.request_id_generator = Mock(side_effect=[REQUEST_GROUP_ID_EXP_1,
                                                             REQUEST_ID1,
                                                             REQUEST_ID2,
                                                             REQUEST_ID3,
                                                             REQUEST_ID4])

        boto3.client = Mock()
        s3_cli = boto3.client('s3')

        s3_cli.restore_object = Mock(side_effect=[None,
                                                  None,
                                                  None,
                                                  None
                                                  ])
        s3_cli.head_object = Mock()
        CumulusLogger.info = Mock()
        mock_ssm_get_parameter(5)
        try:
            result = request_files.task(input_event, self.context)
        except requests_db.DatabaseError as err:
            self.fail(str(err))

        exp_gran = {
            'granuleId': granule_id,
            'recover_files': [
                {'key': FILE1, 'dest_bucket': PROTECTED_BUCKET, 'success': True, 'err_msg': ''},
                {'key': FILE2, 'dest_bucket': PROTECTED_BUCKET, 'success': True, 'err_msg': ''},
                {'key': FILE3, 'dest_bucket': None, 'success': True, 'err_msg': ''},
                {'key': FILE4, 'dest_bucket': PUBLIC_BUCKET, 'success': True, 'err_msg': ''}
            ],
            'keys': [
                {'key': FILE1, 'dest_bucket': PROTECTED_BUCKET},
                {'key': FILE2, 'dest_bucket': PROTECTED_BUCKET},
                {'key': FILE3, 'dest_bucket': None},
                {'key': FILE4, 'dest_bucket': PUBLIC_BUCKET}
            ]
        }
        exp_granules = {
            'granules': [exp_gran]
        }
        self.assertEqual(exp_granules, result)
        end_rows = requests_db.get_all_requests()
        self.assertEqual(4, len(end_rows))
        for row in end_rows:
            self.assertEqual("inprogress", row['job_status'])

    @patch('requests_db.request_id_generator')
    @patch('boto3.client')
    @patch('cumulus_logger.CumulusLogger.error')
    @patch('cumulus_logger.CumulusLogger.info')
    def test_task_client_error_one_file(self,
                                        mock_logger_info: MagicMock,
                                        mock_logger_error: MagicMock,
                                        mock_boto3_client: MagicMock,
                                        mock_request_id_generator: MagicMock):
        """
        Test retries for restore error for one file.
        """
        exp_event = {"config": {"glacier-bucket": "some_bucket"}, "input": {
            "granules": [{"granuleId": "MOD09GQ.A0219114.N5aUCG.006.0656338553321",
                          "keys": [KEY1]}]}}

        os.environ['RESTORE_RETRY_SLEEP_SECS'] = '.5'  # todo: This is not reset between tests
        mock_request_id_generator.side_effect = [REQUEST_GROUP_ID_EXP_1,
                                                 REQUEST_ID1,
                                                 REQUEST_ID2,
                                                 REQUEST_ID3]
        mock_s3_cli = mock_boto3_client('s3')
        mock_s3_cli.restore_object.side_effect = [ClientError({'Error': {'Code': 'NoSuchBucket'}}, 'restore_object'),
                                                  ClientError({'Error': {'Code': 'NoSuchBucket'}}, 'restore_object'),
                                                  ClientError({'Error': {'Code': 'NoSuchBucket'}}, 'restore_object')]
        mock_ssm_get_parameter(1)

        exp_gran = {
            'granuleId': 'MOD09GQ.A0219114.N5aUCG.006.0656338553321',
            'keys': [
                {
                    'key': FILE1,
                    'dest_bucket': PROTECTED_BUCKET
                }
            ],
            'recover_files': [
                {
                    'key': FILE1, 'dest_bucket': PROTECTED_BUCKET, 'success': False,
                    'err_msg': 'An error occurred (NoSuchBucket) when calling the restore_object operation: Unknown'
                }
            ]
        }
        exp_err = f"One or more files failed to be requested. {exp_gran}"
        try:
            request_files.task(exp_event, self.context)
            self.fail("RestoreRequestError expected")
        except request_files.RestoreRequestError as err:
            self.assertEqual(exp_err, str(err))
        del os.environ['RESTORE_RETRY_SLEEP_SECS']
        mock_boto3_client.assert_called_with('ssm')
        mock_s3_cli.head_object.assert_called_with(Bucket='some_bucket',
                                                   Key=FILE1)
        restore_req_exp = {'Days': 5, 'GlacierJobParameters': {'Tier': 'Standard'}}
        mock_s3_cli.restore_object.assert_called_with(
            Bucket='some_bucket',
            Key=FILE1,
            RestoreRequest=restore_req_exp)

    def test_task_client_error_3_times(self):
        """
        Test three files, two successful, one errors on all retries and fails.
        """
        exp_event = {"config": {"glacier-bucket": "some_bucket"}}
        granule_id = "MOD09GQ.A0219114.N5aUCG.006.0656338553321"
        gran = {"granuleId": granule_id, "keys": [KEY1, KEY3, KEY4]}
        exp_event["input"] = {
            "granules": [gran]}

        requests_db.request_id_generator = Mock(side_effect=[REQUEST_GROUP_ID_EXP_1,
                                                             REQUEST_ID1,
                                                             REQUEST_GROUP_ID_EXP_3,
                                                             REQUEST_ID2,
                                                             REQUEST_ID3,
                                                             REQUEST_ID4
                                                             ])
        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.head_object = Mock()
        s3_cli.restore_object = Mock(side_effect=[None,
                                                  ClientError({'Error': {'Code': 'NoSuchBucket'}},
                                                              'restore_object'),
                                                  None,
                                                  ClientError({'Error': {'Code': 'NoSuchBucket'}},
                                                              'restore_object'),
                                                  ClientError({'Error': {'Code': 'NoSuchKey'}},
                                                              'restore_object')
                                                  ])
        CumulusLogger.info = Mock()
        CumulusLogger.error = Mock()
        mock_ssm_get_parameter(3)
        exp_gran = {
            'granuleId': granule_id,
            'keys': [
                {'key': FILE1, 'dest_bucket': PROTECTED_BUCKET},
                {'key': FILE3, 'dest_bucket': None},
                {'key': FILE4, 'dest_bucket': PUBLIC_BUCKET}
            ],
            'recover_files': [
                {'key': FILE1, 'dest_bucket': PROTECTED_BUCKET, 'success': True, 'err_msg': ''},
                {'key': FILE3, 'dest_bucket': None, 'success': False,
                 'err_msg': 'An error occurred (NoSuchKey) when calling the restore_object '
                            'operation: Unknown'},
                {'key': FILE4, 'dest_bucket': PUBLIC_BUCKET, 'success': True, 'err_msg': ''}
            ]
        }
        exp_err = f"One or more files failed to be requested. {exp_gran}"

        print_rows("begin")
        try:
            request_files.task(exp_event, self.context)
            self.fail("RestoreRequestError expected")
        except request_files.RestoreRequestError as err:
            self.assertEqual(exp_err, str(err))
        print_rows("end")

    def test_task_client_error_2_times(self):
        """
        Test two files, first successful, second has two errors, then success.
        """
        granule_id = "MOD09GQ.A0219114.N5aUCG.006.0656338553321"
        file1 = {"key": FILE1,
                 "dest_bucket": "sndbx-cumulus-protected"}
        file2 = {"key": FILE2,
                 "dest_bucket": "sndbx-cumulus-protected"}
        exp_event = {
            "config": {"glacier-bucket": "some_bucket"},
            "input": {
                "granules": [{"granuleId": granule_id, "keys": [file1, file2]}]
            }
        }

        requests_db.request_id_generator = Mock(side_effect=[REQUEST_GROUP_ID_EXP_1,
                                                             REQUEST_ID1,
                                                             REQUEST_GROUP_ID_EXP_2,
                                                             REQUEST_ID2,
                                                             REQUEST_ID3])
        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.head_object = Mock()
        s3_cli.restore_object = Mock(side_effect=[None,
                                                  ClientError({'Error': {'Code': 'NoSuchBucket'}},
                                                              'restore_object'),
                                                  ClientError({'Error': {'Code': 'NoSuchBucket'}},
                                                              'restore_object'),
                                                  None
                                                  ])
        CumulusLogger.info = Mock()
        CumulusLogger.error = Mock()
        mock_ssm_get_parameter(2)
        exp_gran = {
            'granuleId': granule_id,
            'recover_files': [
                {'key': FILE1, 'dest_bucket': "sndbx-cumulus-protected", 'success': True, 'err_msg': ''},
                {'key': FILE2, 'dest_bucket': "sndbx-cumulus-protected", 'success': True, 'err_msg': ''}
            ],
            'keys': [
                {'key': FILE1, 'dest_bucket': "sndbx-cumulus-protected"},
                {'key': FILE2, 'dest_bucket': "sndbx-cumulus-protected"}
            ]
        }
        exp_granules = {
            'granules': [
                exp_gran
            ]
        }

        print_rows("begin")

        result = request_files.task(exp_event, self.context)
        self.assertEqual(exp_granules, result)

        print_rows("end")


if __name__ == '__main__':
    unittest.main(argv=['start'])
