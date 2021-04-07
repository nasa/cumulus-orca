"""
Name: test_request_files.py

Description:  Unit tests for request_files.py.
"""
import os
import unittest
import uuid
from unittest.mock import Mock

import boto3
import requests_db
from cumulus_logger import CumulusLogger

import db_config
import request_files
from test.request_helpers import LambdaContextMock
from test.request_helpers import (
    REQUEST_ID1, REQUEST_ID2, REQUEST_ID3, REQUEST_ID4,
    REQUEST_GROUP_ID_EXP_1, mock_secretsmanager_get_parameter)

UTC_NOW_EXP_1 = requests_db.get_utc_now_iso()
FILE1 = 'MOD09GQ___006/2017/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.h5'
FILE2 = 'MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.h5.met'
FILE3 = 'MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321_ndvi.jpg'
FILE4 = 'MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml'
PROTECTED_BUCKET = 'sndbx-cumulus-protected'
PUBLIC_BUCKET = 'sndbx-cumulus-public'
KEY1 = {'key': FILE1, 'dest_bucket': PROTECTED_BUCKET}
KEY2 = {'key': FILE2, 'dest_bucket': PROTECTED_BUCKET}
KEY3 = {'key': FILE3, 'dest_bucket': None}
KEY4 = {'key': FILE4, 'dest_bucket': PUBLIC_BUCKET}


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
        os.environ['RESTORE_REQUEST_RETRIES'] = '2'
        os.environ['RESTORE_RETRIEVAL_TYPE'] = 'Standard'
        os.environ['PREFIX'] = uuid.uuid4().__str__()
        self.context = LambdaContextMock()

    def tearDown(self):
        boto3.client = Mock()  # todo: Why?
        mock_secretsmanager_get_parameter(1)
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
        os.environ.pop('PREFIX', None)
        del os.environ['RESTORE_EXPIRE_DAYS']
        del os.environ['RESTORE_REQUEST_RETRIES']
        db_config.del_env()
        del os.environ["RESTORE_RETRIEVAL_TYPE"]

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
        mock_secretsmanager_get_parameter(5)
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


if __name__ == '__main__':
    unittest.main(argv=['start'])
