"""
Name: test_request_files.py

Description:  Unit tests for request_files.py.
"""
import unittest
from unittest.mock import Mock
import os
import boto3
from botocore.exceptions import ClientError
from cumulus_logger import CumulusLogger
from helpers import LambdaContextMock, create_handler_event
import request_files

class TestRequestFiles(unittest.TestCase):
    """
    TestRequestFiles.
    """
    def setUp(self):
        self.mock_boto3_client = boto3.client
        self.mock_info = CumulusLogger.info
        self.mock_error = CumulusLogger.error
        os.environ["DATABASE_HOST"] = "elpdvx143.cr.usgs.gov"
        os.environ["DATABASE_NAME"] = "labsndbx"
        os.environ["DATABASE_USER"] = "druser"
        os.environ["DATABASE_PW"] = "July2019"
        os.environ['RESTORE_EXPIRE_DAYS'] = '5'
        os.environ['RESTORE_REQUEST_RETRIES'] = '3'
        self.context = LambdaContextMock()

    def tearDown(self):
        CumulusLogger.error = self.mock_error
        CumulusLogger.info = self.mock_info
        boto3.client = self.mock_boto3_client
        del os.environ['RESTORE_EXPIRE_DAYS']
        del os.environ['RESTORE_REQUEST_RETRIES']
        del os.environ["DATABASE_HOST"]
        del os.environ["DATABASE_NAME"]
        del os.environ["DATABASE_USER"]
        del os.environ["DATABASE_PW"]

    def test_handler(self):
        """
        Tests the handler
        """
        input_event = create_handler_event()
        task_input = {}
        task_input["input"] = input_event["payload"]
        task_input["config"] = {}
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
        file1 = "MOD09GQ___006/2017/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf"
        file2 = "MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf.met"
        file3 = "MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321_ndvi.jpg"
        file4 = "MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml"
        input_event = {
            "input": {
                "granules": [
                    {
                        "granuleId": "MOD09GQ.A0219114.N5aUCG.006.0656338553321",
                        "keys": [
                            file1,
                            file2,
                            file3,
                            file4
                        ]
                    }
                ]
            },
            "config": {
                "glacier-bucket": "my-dr-fake-glacier-bucket"
            }
        }
        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.restore_object = Mock(side_effect=[None,
                                                  None,
                                                  None,
                                                  None
                                                  ])
        s3_cli.head_object = Mock()
        CumulusLogger.info = Mock()
        result = request_files.task(input_event, self.context)
        boto3.client.assert_called_with('s3')
        s3_cli.head_object.assert_any_call(Bucket='my-dr-fake-glacier-bucket',
                                           Key=file1)
        s3_cli.head_object.assert_any_call(Bucket='my-dr-fake-glacier-bucket',
                                           Key=file2)
        s3_cli.head_object.assert_any_call(Bucket='my-dr-fake-glacier-bucket',
                                           Key=file3)
        s3_cli.head_object.assert_any_call(Bucket='my-dr-fake-glacier-bucket',
                                           Key=file4)
        s3_cli.restore_object.assert_any_call(
            Bucket='my-dr-fake-glacier-bucket',
            Key=file1,
            RestoreRequest={'Days': 5, 'GlacierJobParameters': {
                'Tier': 'Standard'}})
        s3_cli.restore_object.assert_any_call(
            Bucket='my-dr-fake-glacier-bucket',
            Key=file2,
            RestoreRequest={'Days': 5, 'GlacierJobParameters': {
                'Tier': 'Standard'}})
        s3_cli.restore_object.assert_any_call(
            Bucket='my-dr-fake-glacier-bucket',
            Key=file3,
            RestoreRequest={'Days': 5, 'GlacierJobParameters': {
                'Tier': 'Standard'}})
        s3_cli.restore_object.assert_any_call(
            Bucket='my-dr-fake-glacier-bucket',
            Key=file4,
            RestoreRequest={'Days': 5, 'GlacierJobParameters': {
                'Tier': 'Standard'}})

        exp_gran = {}
        exp_gran['granuleId'] = 'MOD09GQ.A0219114.N5aUCG.006.0656338553321'
        exp_files = []

        exp_file = {}
        exp_file['key'] = file1
        exp_file['success'] = True
        exp_file['err_msg'] = ''
        exp_files.append(exp_file)

        exp_file = {}
        exp_file['key'] = file2
        exp_file['success'] = True
        exp_file['err_msg'] = ''
        exp_files.append(exp_file)

        exp_file = {}
        exp_file['key'] = file3
        exp_file['success'] = True
        exp_file['err_msg'] = ''
        exp_files.append(exp_file)

        exp_file = {}
        exp_file['key'] = file4
        exp_file['success'] = True
        exp_file['err_msg'] = ''
        exp_files.append(exp_file)

        exp_gran['files'] = exp_files
        self.assertEqual(exp_gran, result)


    def test_task_two_granules(self):
        """
        Test two granules with one file each - successful.
        """
        file1 = "MOD09GQ___006/2017/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf"
        file2 = "MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf.met"
        exp_event = {}
        exp_event["input"] = {
            "granules": [{"granuleId": "MOD09GQ.A0219114.N5aUCG.006.0656338553321",
                          "keys": [file1]},
                         {"granuleId": "MOD09GQ.A0219115.N5aUCG.006.0656338553321",
                          "keys": [file2]}]}
        exp_event["config"] = {"glacier-bucket": "my-bucket"}

        exp_err = "request_files can only accept 1 granule in the list. This input contains 2"
        try:
            request_files.task(exp_event, self.context)
            self.fail("RestoreRequestError expected")
        except request_files.RestoreRequestError as roe:
            self.assertEqual(exp_err, str(roe))

    def test_task_file_not_in_glacier(self):
        """
        Test a file that is not in glacier.
        """
        file1 = "MOD09GQ___006/2017/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.xyz"
        exp_event = {}
        exp_event["input"] = {
            "granules": [{"granuleId": "MOD09GQ.A0219114.N5aUCG.006.0656338553321",
                          "keys": [file1]}]}
        exp_event["config"] = {"glacier-bucket": "my-bucket"}
        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.head_object = Mock(
            side_effect=[ClientError({'Error': {'Code': 'NotFound'}}, 'head_object')])
        CumulusLogger.info = Mock()
        result = request_files.task(exp_event, self.context)
        self.assertEqual({'files': [], 'granuleId': 'MOD09GQ.A0219114.N5aUCG.006.0656338553321'},
                         result)
        boto3.client.assert_called_with('s3')
        s3_cli.head_object.assert_called_with(Bucket='my-bucket', Key=file1)

    def test_task_no_retries_env_var(self):
        """
        Test environment var RESTORE_REQUEST_RETRIES not set - use default.
        """
        del os.environ['RESTORE_REQUEST_RETRIES']
        exp_event = {}
        file1 = "MOD09GQ___006/2017/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf"
        exp_event["input"] = {
            "granules": [{"granuleId": "MOD09GQ.A0219114.N5aUCG.006.0656338553321",
                          "keys": [file1]}]}
        exp_event["config"] = {"glacier-bucket": "some_bucket"}

        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.head_object = Mock()
        s3_cli.restore_object = Mock(side_effect=[None])
        CumulusLogger.info = Mock()

        exp_gran = {}
        exp_gran['granuleId'] = 'MOD09GQ.A0219114.N5aUCG.006.0656338553321'
        exp_files = []

        exp_file = {}
        exp_file['key'] = file1
        exp_file['success'] = True
        exp_file['err_msg'] = ''
        exp_files.append(exp_file)

        exp_gran['files'] = exp_files
        result = request_files.task(exp_event, self.context)
        self.assertEqual(exp_gran, result)
        os.environ['RESTORE_REQUEST_RETRIES'] = '3'

        boto3.client.assert_called_with('s3')
        s3_cli.head_object.assert_called_with(Bucket='some_bucket',
                                              Key=file1)

        s3_cli.restore_object.assert_called_with(
            Bucket='some_bucket',
            Key=file1,
            RestoreRequest={'Days': 5, 'GlacierJobParameters': {'Tier': 'Standard'}})

    def test_task_no_expire_days_env_var(self):
        """
        Test environment var RESTORE_EXPIRE_DAYS not set - use default.
        """
        del os.environ['RESTORE_EXPIRE_DAYS']
        exp_event = {}
        exp_event["config"] = {"glacier-bucket": "some_bucket"}
        file1 = "MOD09GQ___006/2017/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf"
        exp_event["input"] = {
            "granules": [{"granuleId": "MOD09GQ.A0219114.N5aUCG.006.0656338553321",
                          "keys": [file1]}]}

        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.head_object = Mock()
        s3_cli.restore_object = Mock(side_effect=[None])
        CumulusLogger.info = Mock()

        exp_gran = {}
        exp_gran['granuleId'] = 'MOD09GQ.A0219114.N5aUCG.006.0656338553321'
        exp_files = []

        exp_file = {}
        exp_file['key'] = file1
        exp_file['success'] = True
        exp_file['err_msg'] = ''
        exp_files.append(exp_file)

        exp_gran['files'] = exp_files
        result = request_files.task(exp_event, self.context)
        self.assertEqual(exp_gran, result)
        os.environ['RESTORE_EXPIRE_DAYS'] = '3'

        boto3.client.assert_called_with('s3')
        s3_cli.head_object.assert_called_with(Bucket='some_bucket',
                                              Key=file1)
        s3_cli.restore_object.assert_any_call(
            Bucket='some_bucket',
            Key=file1,
            RestoreRequest={'Days': 5, 'GlacierJobParameters': {'Tier': 'Standard'}})

    def test_task_no_glacier_bucket(self):
        """
        Test for missing glacier-bucket in config.
        """
        exp_event = {}
        file1 = "MOD09GQ___006/2017/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf"
        exp_event["input"] = {
            "granules": [{"granuleId": "MOD09GQ.A0219114.N5aUCG.006.0656338553321",
                          "keys": [file1]}]}

        exp_err = f"request: {exp_event} does not contain a config value for glacier-bucket"
        CumulusLogger.error = Mock()
        try:
            request_files.task(exp_event, self.context)
            self.fail("RestoreRequestError expected")
        except request_files.RestoreRequestError as err:
            self.assertEqual(exp_err, str(err))

    def test_task_client_error_one_file(self):
        """
        Test retries for restore error for one file.
        """
        exp_event = {}
        exp_event["config"] = {"glacier-bucket": "some_bucket"}
        file1 = "MOD09GQ___006/2017/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf"
        exp_event["input"] = {
            "granules": [{"granuleId": "MOD09GQ.A0219114.N5aUCG.006.0656338553321",
                          "keys": [file1]}]}

        os.environ['RESTORE_RETRY_SLEEP_SECS'] = '.5'
        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.head_object = Mock()
        s3_cli.restore_object = Mock(
            side_effect=[ClientError({'Error': {'Code': 'NoSuchBucket'}}, 'restore_object'),
                         ClientError({'Error': {'Code': 'NoSuchBucket'}}, 'restore_object'),
                         ClientError({'Error': {'Code': 'NoSuchBucket'}}, 'restore_object')])
        CumulusLogger.info = Mock()
        CumulusLogger.error = Mock()

        exp_gran = {}
        exp_gran['granuleId'] = 'MOD09GQ.A0219114.N5aUCG.006.0656338553321'
        exp_files = []

        exp_file = {}
        exp_file['key'] = file1
        exp_file['success'] = False
        exp_files.append(exp_file)

        exp_gran = {'granuleId': 'MOD09GQ.A0219114.N5aUCG.006.0656338553321', 'files': [
            {'key': file1,
             'success': False,
             'err_msg': 'An error occurred (NoSuchBucket) when calling the restore_object '
                        'operation: Unknown'}]}
        exp_err = f"One or more files failed to be requested. {exp_gran}"
        try:
            request_files.task(exp_event, self.context)
            self.fail("RestoreRequestError expected")
        except request_files.RestoreRequestError as err:
            self.assertEqual(exp_err, str(err))
        del os.environ['RESTORE_RETRY_SLEEP_SECS']
        boto3.client.assert_called_with('s3')
        s3_cli.head_object.assert_called_with(Bucket='some_bucket',
                                              Key=file1)
        s3_cli.restore_object.assert_any_call(
            Bucket='some_bucket',
            Key=file1,
            RestoreRequest={'Days': 5, 'GlacierJobParameters': {
                'Tier': 'Standard'}})

    def test_task_client_error_3_times(self):
        """
        Test four files, first 3 successful, fourth errors on all retries and fails.
        """
        file1 = "MOD09GQ___006/2017/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf"
        file3 = "MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321_ndvi.jpg"
        file4 = "MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml"
        exp_event = {}
        exp_event["config"] = {"glacier-bucket": "some_bucket"}
        gran = {}
        gran["granuleId"] = "MOD09GQ.A0219114.N5aUCG.006.0656338553321"
        keys = []
        keys.append(file1)
        keys.append(file3)
        keys.append(file4)
        gran["keys"] = keys
        exp_event["input"] = {
            "granules": [gran]}

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
        exp_gran = {}
        exp_gran['granuleId'] = 'MOD09GQ.A0219114.N5aUCG.006.0656338553321'
        exp_files = []

        exp_file = {}
        exp_file['key'] = file1
        exp_file['success'] = True
        exp_file['err_msg'] = ''
        exp_files.append(exp_file)

        exp_file = {}
        exp_file['key'] = file3
        exp_file['success'] = False
        exp_file['err_msg'] = 'An error occurred (NoSuchKey) when calling the restore_object ' \
                              'operation: Unknown'
        exp_files.append(exp_file)

        exp_file = {}
        exp_file['key'] = file4
        exp_file['success'] = True
        exp_file['err_msg'] = ''
        exp_files.append(exp_file)

        exp_gran['files'] = exp_files
        exp_err = f"One or more files failed to be requested. {exp_gran}"
        try:
            request_files.task(exp_event, self.context)
            self.fail("RestoreRequestError expected")
        except request_files.RestoreRequestError as err:
            self.assertEqual(exp_err, str(err))

        boto3.client.assert_called_with('s3')
        s3_cli.head_object.assert_any_call(Bucket='some_bucket',
                                           Key=file1)
        s3_cli.restore_object.assert_any_call(
            Bucket='some_bucket',
            Key=file1,
            RestoreRequest={'Days': 5, 'GlacierJobParameters': {'Tier': 'Standard'}})

    def test_task_client_error_2_times(self):
        """
        Test two files, first successful, second has two errors, then success.
        """
        file1 = "MOD09GQ___006/2017/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf"
        file2 = "MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf.met"
        exp_event = {}
        exp_event["config"] = {"glacier-bucket": "some_bucket"}
        gran = {}
        gran["granuleId"] = "MOD09GQ.A0219114.N5aUCG.006.0656338553321"
        keys = []
        keys.append(file1)
        keys.append(file2)
        gran["keys"] = keys
        exp_event["input"] = {
            "granules": [gran]}

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
        exp_gran = {}
        exp_gran['granuleId'] = 'MOD09GQ.A0219114.N5aUCG.006.0656338553321'
        exp_files = []

        exp_file = {}
        exp_file['key'] = file1
        exp_file['success'] = True
        exp_file['err_msg'] = ''
        exp_files.append(exp_file)

        exp_file = {}
        exp_file['key'] = file2
        exp_file['success'] = True
        exp_file['err_msg'] = ''
        exp_files.append(exp_file)

        exp_gran['files'] = exp_files
        result = request_files.task(exp_event, self.context)
        self.assertEqual(exp_gran, result)

        boto3.client.assert_called_with('s3')
        s3_cli.restore_object.assert_any_call(
            Bucket='some_bucket',
            Key=file1,
            RestoreRequest={'Days': 5, 'GlacierJobParameters': {'Tier': 'Standard'}})


if __name__ == '__main__':
    unittest.main(argv=['start'])
