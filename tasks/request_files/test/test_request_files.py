"""
Name: test_request_files.py

Description:  Unit tests for request_files.py.
"""
import unittest
from unittest.mock import Mock
import os
import json
import boto3
from botocore.exceptions import ClientError
import request_files

class TestRequestFiles(unittest.TestCase):
    """
    TestRequestFiles.
    """
    def setUp(self):
        self.mock_boto3_client = boto3.client
        os.environ['RESTORE_EXPIRE_DAYS'] = '5'
        os.environ['RESTORE_REQUEST_RETRIES'] = '3'

    def tearDown(self):
        boto3.client = self.mock_boto3_client
        del os.environ['RESTORE_EXPIRE_DAYS']
        del os.environ['RESTORE_REQUEST_RETRIES']

    def test_handler_one_granule_4_files_success(self):
        """
        Test four files for one granule - successful
        """
        file1 = "MOD09GQ___006/2017/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf"
        file2 = "MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf.met"
        file3 = "MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321_ndvi.jpg"
        file4 = "MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml"
        exp_event = {}
        exp_event["glacierBucket"] = "my-dr-fake-glacier-bucket"
        exp_event["granules"] = [{"granuleId": "MOD09GQ.A0219114.N5aUCG.006.0656338553321",
                                  "filepaths": [file1,
                                                file2,
                                                file3,
                                                file4]}]

        exp_context = None
        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.restore_object = Mock(side_effect=[None,
                                                  None,
                                                  None,
                                                  None
                                                  ])
        print("exp_event1: ", exp_event)
        result = request_files.handler(exp_event, exp_context)
        print("result1: ", result)
        boto3.client.assert_called_with('s3')
        s3_cli.restore_object.assert_any_call(
            Bucket='my-dr-fake-glacier-bucket',
            Key='MOD09GQ___006/2017/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf',
            RestoreRequest={'Days': 5, 'GlacierJobParameters': {
                'Tier': 'Standard'}})
        s3_cli.restore_object.assert_any_call(
            Bucket='my-dr-fake-glacier-bucket',
            Key='MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf.met',
            RestoreRequest={'Days': 5, 'GlacierJobParameters': {
                'Tier': 'Standard'}})
        s3_cli.restore_object.assert_any_call(
            Bucket='my-dr-fake-glacier-bucket',
            Key='MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321_ndvi.jpg',
            RestoreRequest={'Days': 5, 'GlacierJobParameters': {
                'Tier': 'Standard'}})
        s3_cli.restore_object.assert_any_call(
            Bucket='my-dr-fake-glacier-bucket',
            Key='MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml',
            RestoreRequest={'Days': 5, 'GlacierJobParameters': {
                'Tier': 'Standard'}})

        exp_gran = {}
        exp_gran['granuleId'] = 'MOD09GQ.A0219114.N5aUCG.006.0656338553321'
        exp_files = []

        exp_file = {}
        exp_file['filepath'] = file1
        exp_file['success'] = True
        exp_file['err_msg'] = ''
        exp_files.append(exp_file)

        exp_file = {}
        exp_file['filepath'] = file2
        exp_file['success'] = True
        exp_file['err_msg'] = ''
        exp_files.append(exp_file)

        exp_file = {}
        exp_file['filepath'] = file3
        exp_file['success'] = True
        exp_file['err_msg'] = ''
        exp_files.append(exp_file)

        exp_file = {}
        exp_file['filepath'] = file4
        exp_file['success'] = True
        exp_file['err_msg'] = ''
        exp_files.append(exp_file)

        exp_gran['files'] = exp_files

        exp_result = json.dumps(exp_gran)
        self.assertEqual(exp_result, result)

    def test_handler_no_bucket(self):
        """
        Test no glacierBucket in input event.
        """
        file1 = "file1.hdf"
        exp_event = {}
        exp_event["granules"] = [{"granuleId": "xyz",
                                  "filepaths": [file1]}]

        exp_context = None

        print("exp_event1: ", exp_event)
        exp_err = "request: {'granules': [{'granuleId': 'xyz', " \
                 "'filepaths': ['file1.hdf']}]} does not contain a value for glacierBucket"
        try:
            request_files.handler(exp_event, exp_context)
            self.fail("RestoreRequestError expected")
        except request_files.RestoreRequestError as roe:
            self.assertEqual(exp_err, str(roe))

    def test_handler_two_granules(self):
        """
        Test two granules with one file each - successful.
        """
        file1 = "MOD09GQ___006/2017/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf"
        file2 = "MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf.met"
        exp_event = {}
        exp_event["glacierBucket"] = "my-dr-fake-glacier-bucket"
        exp_event["granules"] = [{"granuleId": "MOD09GQ.A0219114.N5aUCG.006.0656338553321",
                                  "filepaths": [file1]},
                                 {"granuleId": "MOD09GQ.A0219115.N5aUCG.006.0656338553321",
                                  "filepaths": [file2]}]

        exp_context = None

        print("exp_event1: ", exp_event)
        exp_err = "request_files can only accept 1 granule in the list. This input contains 2"
        try:
            request_files.handler(exp_event, exp_context)
            self.fail("RestoreRequestError expected")
        except request_files.RestoreRequestError as roe:
            self.assertEqual(exp_err, str(roe))


    def test_handler_no_retries_env_var(self):
        """
        Test environment var RESTORE_REQUEST_RETRIES not set - use default.
        """
        del os.environ['RESTORE_REQUEST_RETRIES']
        exp_event = {}
        exp_event["glacierBucket"] = "some_bucket"
        file1 = "MOD09GQ___006/2017/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf"
        exp_event["granules"] = [{"granuleId": "MOD09GQ.A0219114.N5aUCG.006.0656338553321",
                                  "filepaths": [file1]}]

        exp_context = None
        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.restore_object = Mock(side_effect=[None])

        exp_gran = {}
        exp_gran['granuleId'] = 'MOD09GQ.A0219114.N5aUCG.006.0656338553321'
        exp_files = []

        exp_file = {}
        exp_file['filepath'] = file1
        exp_file['success'] = True
        exp_file['err_msg'] = ''
        exp_files.append(exp_file)

        exp_gran['files'] = exp_files
        result = request_files.handler(exp_event, exp_context)
        exp_result = json.dumps(exp_gran)
        self.assertEqual(exp_result, result)
        os.environ['RESTORE_REQUEST_RETRIES'] = '3'

        boto3.client.assert_called_with('s3')
        s3_cli.restore_object.assert_any_call(
            Bucket='some_bucket',
            Key='MOD09GQ___006/2017/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf',
            RestoreRequest={'Days': 5, 'GlacierJobParameters': {'Tier': 'Standard'}})

    def test_handler_no_expire_days_env_var(self):
        """
        Test environment var RESTORE_EXPIRE_DAYS not set - use default.
        """
        del os.environ['RESTORE_EXPIRE_DAYS']
        exp_event = {}
        exp_event["glacierBucket"] = "some_bucket"
        file1 = "MOD09GQ___006/2017/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf"
        exp_event["granules"] = [{"granuleId": "MOD09GQ.A0219114.N5aUCG.006.0656338553321",
                                  "filepaths": [file1]}]

        exp_context = None
        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.restore_object = Mock(side_effect=[None])

        exp_gran = {}
        exp_gran['granuleId'] = 'MOD09GQ.A0219114.N5aUCG.006.0656338553321'
        exp_files = []

        exp_file = {}
        exp_file['filepath'] = file1
        exp_file['success'] = True
        exp_file['err_msg'] = ''
        exp_files.append(exp_file)

        exp_gran['files'] = exp_files
        result = request_files.handler(exp_event, exp_context)
        exp_result = json.dumps(exp_gran)
        self.assertEqual(exp_result, result)
        os.environ['RESTORE_EXPIRE_DAYS'] = '3'

        boto3.client.assert_called_with('s3')
        s3_cli.restore_object.assert_any_call(
            Bucket='some_bucket',
            Key='MOD09GQ___006/2017/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf',
            RestoreRequest={'Days': 5, 'GlacierJobParameters': {'Tier': 'Standard'}})

    def test_handler_client_error_one_file(self):
        """
        Test retries for restore error for one file.
        """
        exp_event = {}
        exp_event["glacierBucket"] = "some_bucket"
        file1 = "MOD09GQ___006/2017/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf"
        exp_event["granules"] = [{"granuleId": "MOD09GQ.A0219114.N5aUCG.006.0656338553321",
                                  "filepaths": [file1]}]

        exp_context = None
        os.environ['RESTORE_RETRY_SLEEP_SECS'] = '.5'
        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.restore_object = Mock(
            side_effect=[ClientError({'Error': {'Code': 'NoSuchBucket'}}, 'restore_object'),
                         ClientError({'Error': {'Code': 'NoSuchBucket'}}, 'restore_object'),
                         ClientError({'Error': {'Code': 'NoSuchBucket'}}, 'restore_object')])

        exp_gran = {}
        exp_gran['granuleId'] = 'MOD09GQ.A0219114.N5aUCG.006.0656338553321'
        exp_files = []

        exp_file = {}
        exp_file['filepath'] = file1
        exp_file['success'] = False
        exp_file['err_msg'] = 'An error occurred (NoSuchBucket) when calling the restore_object ' \
                             'operation: Unknown'
        exp_files.append(exp_file)

        exp_gran['files'] = exp_files
        exp_err = f"One or more files failed to be requested. {exp_gran}"
        print("exp_event2: ", exp_event)
        try:
            request_files.handler(exp_event, exp_context)
            self.fail("RestoreRequestError expected")
        except request_files.RestoreRequestError as err:
            self.assertEqual(exp_err, str(err))
        del os.environ['RESTORE_RETRY_SLEEP_SECS']
        boto3.client.assert_called_with('s3')
        s3_cli.restore_object.assert_any_call(
            Bucket='some_bucket',
            Key='MOD09GQ___006/2017/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf',
            RestoreRequest={'Days': 5, 'GlacierJobParameters': {
                'Tier': 'Standard'}})

    def test_handler_client_error_3_times(self):
        """
        Test four files, first 3 successful, fourth errors on all retries and fails.
        """
        file1 = "MOD09GQ___006/2017/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf"
        file3 = "MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321_ndvi.jpg"
        file4 = "MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml"
        exp_event = {}
        exp_event["glacierBucket"] = "some_bucket"
        gran = {}
        gran["granuleId"] = "MOD09GQ.A0219114.N5aUCG.006.0656338553321"
        filepaths = []
        filepaths.append(file1)
        filepaths.append(file3)
        filepaths.append(file4)
        gran["filepaths"] = filepaths
        exp_event['granules'] = [gran]

        exp_context = None
        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.restore_object = Mock(side_effect=[None,
                                                  ClientError({'Error': {'Code': 'NoSuchBucket'}},
                                                              'restore_object'),
                                                  None,
                                                  ClientError({'Error': {'Code': 'NoSuchBucket'}},
                                                              'restore_object'),
                                                  ClientError({'Error': {'Code': 'NoSuchKey'}},
                                                              'restore_object')
                                                  ])
        exp_gran = {}
        exp_gran['granuleId'] = 'MOD09GQ.A0219114.N5aUCG.006.0656338553321'
        exp_files = []

        exp_file = {}
        exp_file['filepath'] = file1
        exp_file['success'] = True
        exp_file['err_msg'] = ''
        exp_files.append(exp_file)

        exp_file = {}
        exp_file['filepath'] = file3
        exp_file['success'] = False
        exp_file['err_msg'] = 'An error occurred (NoSuchKey) when calling the restore_object ' \
                              'operation: Unknown'
        exp_files.append(exp_file)

        exp_file = {}
        exp_file['filepath'] = file4
        exp_file['success'] = True
        exp_file['err_msg'] = ''
        exp_files.append(exp_file)

        exp_gran['files'] = exp_files
        exp_err = f"One or more files failed to be requested. {exp_gran}"
        print("exp_event3: ", exp_event)
        try:
            request_files.handler(exp_event, exp_context)
            self.fail("RestoreRequestError expected")
        except request_files.RestoreRequestError as err:
            self.assertEqual(exp_err, str(err))

        boto3.client.assert_called_with('s3')
        s3_cli.restore_object.assert_any_call(
            Bucket='some_bucket',
            Key='MOD09GQ___006/2017/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf',
            RestoreRequest={'Days': 5, 'GlacierJobParameters': {'Tier': 'Standard'}})

    def test_handler_client_error_2_times(self):
        """
        Test two files, first successful, second has two errors, then success.
        """
        file1 = "MOD09GQ___006/2017/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf"
        file2 = "MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf.met"
        exp_event = {}
        exp_event["glacierBucket"] = "some_bucket"
        gran = {}
        gran["granuleId"] = "MOD09GQ.A0219114.N5aUCG.006.0656338553321"
        filepaths = []
        filepaths.append(file1)
        filepaths.append(file2)
        gran["filepaths"] = filepaths
        exp_event['granules'] = [gran]

        exp_context = None
        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.restore_object = Mock(side_effect=[None,
                                                  ClientError({'Error': {'Code': 'NoSuchBucket'}},
                                                              'restore_object'),
                                                  ClientError({'Error': {'Code': 'NoSuchBucket'}},
                                                              'restore_object'),
                                                  None
                                                  ])
        exp_gran = {}
        exp_gran['granuleId'] = 'MOD09GQ.A0219114.N5aUCG.006.0656338553321'
        exp_files = []

        exp_file = {}
        exp_file['filepath'] = file1
        exp_file['success'] = True
        exp_file['err_msg'] = ''
        exp_files.append(exp_file)

        exp_file = {}
        exp_file['filepath'] = file2
        exp_file['success'] = True
        exp_file['err_msg'] = ''
        exp_files.append(exp_file)

        exp_gran['files'] = exp_files
        print("exp_event4: ", exp_event)
        result = request_files.handler(exp_event, exp_context)
        exp_result = json.dumps(exp_gran)
        self.assertEqual(exp_result, result)

        boto3.client.assert_called_with('s3')
        s3_cli.restore_object.assert_any_call(
            Bucket='some_bucket',
            Key='MOD09GQ___006/2017/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf',
            RestoreRequest={'Days': 5, 'GlacierJobParameters': {'Tier': 'Standard'}})


if __name__ == '__main__':
    unittest.main(argv=['start'])
