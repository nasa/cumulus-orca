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
from request_helpers import LambdaContextMock, create_handler_event
from request_helpers import create_insert_request
from request_helpers import (
    REQUEST_ID1, REQUEST_ID2, REQUEST_ID3, REQUEST_GROUP_ID_EXP_1,
    REQUEST_GROUP_ID_EXP_2,
    REQUEST_GROUP_ID_EXP_3)
import requests
import request_files
import utils
import utils.database

UTC_NOW_EXP_1 = requests.get_utc_now_iso()

class TestRequestFiles(unittest.TestCase):
    """
    TestRequestFiles.
    """
    def setUp(self):
        self.mock_boto3_client = boto3.client
        self.mock_info = CumulusLogger.info
        self.mock_error = CumulusLogger.error
        self.mock_single_query = utils.database.single_query
        self.mock_generator = requests.request_id_generator
        os.environ["DATABASE_HOST"] = "my.db.host.gov"
        os.environ["DATABASE_PORT"] = "54"
        os.environ["DATABASE_NAME"] = "sndbx"
        os.environ["DATABASE_USER"] = "unittestdbuser"
        os.environ["DATABASE_PW"] = "unittestdbpw"
        os.environ['RESTORE_EXPIRE_DAYS'] = '5'
        os.environ['RESTORE_REQUEST_RETRIES'] = '3'
        self.context = LambdaContextMock()

    def tearDown(self):
        requests.request_id_generator = self.mock_generator
        utils.database.single_query = self.mock_single_query
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
        granule_id = "MOD09GQ.A0219114.N5aUCG.006.0656338553321"
        files = ["MOD09GQ___006/2017/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf",
                 "MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf.met",
                 "MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321_ndvi.jpg",
                 "MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml"]
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
        response1 = {'ResponseMetadata': {'RequestId': 'A1BC2345DE67F8A1', 'RetryAttempts': 0}}
        response2 = {'ResponseMetadata': {'RequestId': 'A2BC2345DE67F8A1', 'RetryAttempts': 0}}
        response3 = {'ResponseMetadata': {'RequestId': 'A3BC2345DE67F8A1', 'RetryAttempts': 0}}
        response4 = {'ResponseMetadata': {'RequestId': 'A4BC2345DE67F8A1', 'RetryAttempts': 0}}
        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.restore_object = Mock(side_effect=[response1,
                                                  response2,
                                                  response3,
                                                  response4
                                                  ])
        s3_cli.head_object = Mock()
        CumulusLogger.info = Mock()
        qresult_1_inprogress, _ = create_insert_request(
            REQUEST_ID1, REQUEST_GROUP_ID_EXP_1, granule_id, files[0],
            "restore", "some_bucket", "inprogress",
            UTC_NOW_EXP_1, None, None)
        qresult_3_inprogress, _ = create_insert_request(
            REQUEST_ID1, REQUEST_GROUP_ID_EXP_1, granule_id, files[2],
            "restore", "some_bucket", "inprogress",
            UTC_NOW_EXP_1, None, None)
        qresult_4_inprogress, _ = create_insert_request(
            REQUEST_ID1, REQUEST_GROUP_ID_EXP_1, granule_id, files[3],
            "restore", "some_bucket", "inprogress",
            UTC_NOW_EXP_1, None, None)

        requests.request_id_generator = Mock(side_effect=[REQUEST_GROUP_ID_EXP_1,
                                                          REQUEST_GROUP_ID_EXP_1,
                                                          REQUEST_GROUP_ID_EXP_1,
                                                          REQUEST_GROUP_ID_EXP_1])
        utils.database.single_query = Mock(
            side_effect=[qresult_1_inprogress, qresult_1_inprogress,
                         qresult_3_inprogress, qresult_4_inprogress])

        try:
            result = request_files.task(input_event, self.context)
        except requests.DatabaseError as err:
            self.fail(str(err))

        boto3.client.assert_called_with('s3')
        s3_cli.head_object.assert_any_call(Bucket='my-dr-fake-glacier-bucket',
                                           Key=files[0])
        s3_cli.head_object.assert_any_call(Bucket='my-dr-fake-glacier-bucket',
                                           Key=files[1])
        s3_cli.head_object.assert_any_call(Bucket='my-dr-fake-glacier-bucket',
                                           Key=files[2])
        s3_cli.head_object.assert_any_call(Bucket='my-dr-fake-glacier-bucket',
                                           Key=files[3])
        s3_cli.restore_object.assert_any_call(
            Bucket='my-dr-fake-glacier-bucket',
            Key=files[0],
            RestoreRequest={'Days': 5, 'GlacierJobParameters': {
                'Tier': 'Standard'}})
        s3_cli.restore_object.assert_any_call(
            Bucket='my-dr-fake-glacier-bucket',
            Key=files[1],
            RestoreRequest={'Days': 5, 'GlacierJobParameters': {
                'Tier': 'Standard'}})
        s3_cli.restore_object.assert_any_call(
            Bucket='my-dr-fake-glacier-bucket',
            Key=files[2],
            RestoreRequest={'Days': 5, 'GlacierJobParameters': {
                'Tier': 'Standard'}})
        s3_cli.restore_object.assert_any_call(
            Bucket='my-dr-fake-glacier-bucket',
            Key=files[3],
            RestoreRequest={'Days': 5, 'GlacierJobParameters': {
                'Tier': 'Standard'}})

        exp_gran = {}
        exp_gran['granuleId'] = granule_id

        exp_files = self.get_expected_files(files[0], files[1], files[2], files[3])
        exp_gran['files'] = exp_files
        self.assertEqual(exp_gran, result)
        utils.database.single_query.assert_called()  #called 4 times

    @staticmethod
    def get_expected_files(file1, file2, file3, file4):
        """
        builds a list of expected files
        """
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
        return exp_files

    def test_task_one_granule_1_file_db_error(self):
        """
        Test one file for one granule - db error inserting status
        """
        granule_id = "MOD09GQ.A0219114.N5aUCG.006.0656338553321"
        file1 = "MOD09GQ___006/2017/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf"

        input_event = {
            "input": {
                "granules": [
                    {
                        "granuleId": granule_id,
                        "keys": [
                            file1
                        ]
                    }
                ]
            },
            "config": {
                "glacier-bucket": "my-dr-fake-glacier-bucket"
            }
        }
        response1 = {'ResponseMetadata': {'RequestId': 'A1BC2345DE67F8A1', 'RetryAttempts': 0}}
        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.restore_object = Mock(side_effect=[response1
                                                  ])
        s3_cli.head_object = Mock()
        CumulusLogger.info = Mock()
        CumulusLogger.error = Mock()
        requests.request_id_generator = Mock(side_effect=[REQUEST_GROUP_ID_EXP_1])
        utils.database.single_query = Mock(
            side_effect=[utils.database.DbError("mock insert failed error")])
        exp_result = {'granuleId': granule_id, 'files': [{'key': file1,
                                                          'success': True,
                                                          'err_msg': ''}]}
        try:
            result = request_files.task(input_event, self.context)
            self.assertEqual(exp_result, result)
        except requests.DatabaseError as err:
            self.fail(f"failed insert does not throw exception. {str(err)}")

        boto3.client.assert_called_with('s3')
        s3_cli.head_object.assert_any_call(Bucket='my-dr-fake-glacier-bucket',
                                           Key=file1)
        s3_cli.restore_object.assert_any_call(
            Bucket='my-dr-fake-glacier-bucket',
            Key=file1,
            RestoreRequest={'Days': 5, 'GlacierJobParameters': {
                'Tier': 'Standard'}})

        exp_gran = {}
        exp_gran['granuleId'] = granule_id
        exp_files = []

        exp_file = {}
        exp_file['key'] = file1
        exp_file['success'] = True
        exp_file['err_msg'] = ''
        exp_files.append(exp_file)

        exp_gran['files'] = exp_files
        self.assertEqual(exp_gran, result)
        utils.database.single_query.assert_called()  #called 1 times

    def test_task_two_granules(self):
        """
        Test two granules with one file each - successful.
        """
        granule_id = "MOD09GQ.A0219114.N5aUCG.006.0656338553321"
        file1 = "MOD09GQ___006/2017/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf"
        file2 = "MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf.met"
        exp_event = {}
        exp_event["input"] = {
            "granules": [{"granuleId": granule_id,
                          "keys": [file1]},
                         {"granuleId": granule_id,
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
        granule_id = "MOD09GQ.A0219114.N5aUCG.006.0656338553321"
        exp_event["input"] = {
            "granules": [{"granuleId": granule_id,
                          "keys": [file1]}]}
        exp_event["config"] = {"glacier-bucket": "my-bucket"}
        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.head_object = Mock(
            side_effect=[ClientError({'Error': {'Code': 'NotFound'}}, 'head_object')])
        CumulusLogger.info = Mock()
        requests.request_id_generator = Mock(return_value=REQUEST_GROUP_ID_EXP_1)
        try:
            result = request_files.task(exp_event, self.context)

            self.assertEqual({'files': [], 'granuleId': granule_id}, result)
            boto3.client.assert_called_with('s3')
            s3_cli.head_object.assert_called_with(Bucket='my-bucket', Key=file1)
        except requests.DatabaseError as err:
            self.fail(str(err))


    def test_task_no_retries_env_var(self):
        """
        Test environment var RESTORE_REQUEST_RETRIES not set - use default.
        """
        del os.environ['RESTORE_REQUEST_RETRIES']
        exp_event = {}
        granule_id = "MOD09GQ.A0219114.N5aUCG.006.0656338553321"
        file1 = "MOD09GQ___006/2017/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf"
        exp_event["input"] = {
            "granules": [{"granuleId": granule_id,
                          "keys": [file1]}]}
        exp_event["config"] = {"glacier-bucket": "some_bucket"}
        response1 = {'ResponseMetadata': {'RequestId': 'A1BC2345DE67F8A1', 'RetryAttempts': 0}}
        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.head_object = Mock()
        s3_cli.restore_object = Mock(side_effect=[response1])
        CumulusLogger.info = Mock()
        requests.request_id_generator = Mock(return_value=REQUEST_GROUP_ID_EXP_1)
        exp_gran = {}
        exp_gran['granuleId'] = granule_id
        exp_files = []

        exp_file = {}
        exp_file['key'] = file1
        exp_file['success'] = True
        exp_file['err_msg'] = ''
        exp_files.append(exp_file)

        exp_gran['files'] = exp_files
        qresult_1_inprogress, _ = create_insert_request(
            REQUEST_ID1, REQUEST_GROUP_ID_EXP_1, granule_id, file1, "restore", "some_bucket",
            "inprogress", UTC_NOW_EXP_1, None, None)
        utils.database.single_query = Mock(side_effect=[qresult_1_inprogress])
        try:
            result = request_files.task(exp_event, self.context)
            os.environ['RESTORE_REQUEST_RETRIES'] = '3'
            self.assertEqual(exp_gran, result)

            boto3.client.assert_called_with('s3')
            s3_cli.head_object.assert_called_with(Bucket='some_bucket',
                                                  Key=file1)

            s3_cli.restore_object.assert_called_with(
                Bucket='some_bucket',
                Key=file1,
                RestoreRequest={'Days': 5, 'GlacierJobParameters': {'Tier': 'Standard'}})
            utils.database.single_query.assert_called_once()
        except request_files.RestoreRequestError as err:
            os.environ['RESTORE_REQUEST_RETRIES'] = '3'
            self.fail(str(err))


    def test_task_no_expire_days_env_var(self):
        """
        Test environment var RESTORE_EXPIRE_DAYS not set - use default.
        """
        del os.environ['RESTORE_EXPIRE_DAYS']
        exp_event = {}
        granule_id = "MOD09GQ.A0219114.N5aUCG.006.0656338553321"
        exp_event["config"] = {"glacier-bucket": "some_bucket"}
        file1 = "MOD09GQ___006/2017/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf"
        exp_event["input"] = {
            "granules": [{"granuleId": granule_id,
                          "keys": [file1]}]}
        response1 = {'ResponseMetadata': {'RequestId': 'A1BC2345DE67F8A1', 'RetryAttempts': 0}}
        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.head_object = Mock()
        s3_cli.restore_object = Mock(side_effect=[response1])
        CumulusLogger.info = Mock()
        requests.request_id_generator = Mock(return_value=REQUEST_GROUP_ID_EXP_1)
        exp_gran = {}
        exp_gran['granuleId'] = granule_id
        exp_files = []

        exp_file = {}
        exp_file['key'] = file1
        exp_file['success'] = True
        exp_file['err_msg'] = ''
        exp_files.append(exp_file)

        exp_gran['files'] = exp_files

        qresult_1_inprogress, _ = create_insert_request(
            REQUEST_ID1, REQUEST_GROUP_ID_EXP_1, granule_id, file1, "restore", "some_bucket",
            "inprogress", UTC_NOW_EXP_1, None, None)
        utils.database.single_query = Mock(side_effect=[qresult_1_inprogress])

        try:
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
        except request_files.RestoreRequestError as err:
            self.fail(str(err))
        utils.database.single_query.assert_called_once()

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
        requests.request_id_generator = Mock(side_effect=[REQUEST_GROUP_ID_EXP_1,
                                                          REQUEST_GROUP_ID_EXP_2])
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
        Test three files, two successful, one errors on all retries and fails.
        """
        keys = ["MOD09GQ___006/2017/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf",
                "MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321_ndvi.jpg",
                "MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml"]

        exp_event = {}
        exp_event["config"] = {"glacier-bucket": "some_bucket"}
        gran = {}
        gran["granuleId"] = "MOD09GQ.A0219114.N5aUCG.006.0656338553321"

        gran["keys"] = keys
        exp_event["input"] = {
            "granules": [gran]}
        response1 = {'ResponseMetadata': {'RequestId': 'A1BC2345DE67F8A1', 'RetryAttempts': 0}}
        response3 = {'ResponseMetadata': {'RequestId': 'A3BC2345DE67F8A1', 'RetryAttempts': 0}}
        requests.request_id_generator = Mock(side_effect=[REQUEST_GROUP_ID_EXP_1,
                                                          REQUEST_GROUP_ID_EXP_3])
        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.head_object = Mock()
        s3_cli.restore_object = Mock(side_effect=[response1,
                                                  ClientError({'Error': {'Code': 'NoSuchBucket'}},
                                                              'restore_object'),
                                                  response3,
                                                  ClientError({'Error': {'Code': 'NoSuchBucket'}},
                                                              'restore_object'),
                                                  ClientError({'Error': {'Code': 'NoSuchKey'}},
                                                              'restore_object')
                                                  ])
        CumulusLogger.info = Mock()
        CumulusLogger.error = Mock()
        exp_gran = {}
        exp_gran['granuleId'] = gran["granuleId"]

        exp_files = self.get_exp_files_3_errs(keys)

        exp_gran['files'] = exp_files
        exp_err = f"One or more files failed to be requested. {exp_gran}"
        qresult_1_inprogress, _ = create_insert_request(
            REQUEST_ID1, REQUEST_GROUP_ID_EXP_1, gran["granuleId"], keys[0],
            "restore", "some_bucket",
            "inprogress", UTC_NOW_EXP_1, None, None)
        qresult_1_error, _ = create_insert_request(
            REQUEST_ID1, REQUEST_GROUP_ID_EXP_1, gran["granuleId"], keys[0],
            "restore", "some_bucket",
            "error", UTC_NOW_EXP_1, None, "'Code': 'NoSuchBucket'")
        qresult_3_inprogress, _ = create_insert_request(
            REQUEST_ID1, REQUEST_GROUP_ID_EXP_3, gran["granuleId"], keys[1],
            "restore", "some_bucket",
            "inprogress", UTC_NOW_EXP_1, None, None)
        qresult_3_error, _ = create_insert_request(
            REQUEST_ID1, REQUEST_GROUP_ID_EXP_3, gran["granuleId"], keys[1],
            "restore", "some_bucket",
            "error", UTC_NOW_EXP_1, None, "'Code': 'NoSuchBucket'")
        utils.database.single_query = Mock(side_effect=[qresult_1_inprogress,
                                                        qresult_1_error,
                                                        qresult_3_inprogress,
                                                        qresult_1_error,
                                                        qresult_3_error])
        try:
            request_files.task(exp_event, self.context)
            self.fail("RestoreRequestError expected")
        except request_files.RestoreRequestError as err:
            self.assertEqual(exp_err, str(err))

        boto3.client.assert_called_with('s3')
        s3_cli.head_object.assert_any_call(Bucket='some_bucket',
                                           Key=keys[0])
        s3_cli.restore_object.assert_any_call(
            Bucket='some_bucket',
            Key=keys[0],
            RestoreRequest={'Days': 5, 'GlacierJobParameters': {'Tier': 'Standard'}})
        utils.database.single_query.assert_called()  # 5 times

    @staticmethod
    def get_exp_files_3_errs(keys):
        """
        builds list of expected files for test case
        """
        exp_files = []

        exp_file = {}
        exp_file['key'] = keys[0]
        exp_file['success'] = True
        exp_file['err_msg'] = ''
        exp_files.append(exp_file)

        exp_file = {}
        exp_file['key'] = keys[1]
        exp_file['success'] = False
        exp_file['err_msg'] = 'An error occurred (NoSuchKey) when calling the restore_object ' \
                              'operation: Unknown'
        exp_files.append(exp_file)

        exp_file = {}
        exp_file['key'] = keys[2]
        exp_file['success'] = True
        exp_file['err_msg'] = ''
        exp_files.append(exp_file)
        return exp_files

    def test_task_client_error_2_times(self):
        """
        Test two files, first successful, second has two errors, then success.
        """
        exp_event = {}
        exp_event["config"] = {"glacier-bucket": "some_bucket"}
        gran = {}
        granule_id = "MOD09GQ.A0219114.N5aUCG.006.0656338553321"
        gran["granuleId"] = granule_id
        keys = ["MOD09GQ___006/2017/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf",
                "MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf.met"]
        gran["keys"] = keys
        exp_event["input"] = {
            "granules": [gran]}
        requests.request_id_generator = Mock(side_effect=[REQUEST_GROUP_ID_EXP_1])
        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.head_object = Mock()
        response1 = {'ResponseMetadata': {'RequestId': 'A1BC2345DE67F8A1', 'RetryAttempts': 0}}
        response2 = {'ResponseMetadata': {'RequestId': 'A2BC2345DE67F8A1', 'RetryAttempts': 0}}
        s3_cli.restore_object = Mock(side_effect=[response1,
                                                  ClientError({'Error': {'Code': 'NoSuchBucket'}},
                                                              'restore_object'),
                                                  ClientError({'Error': {'Code': 'NoSuchBucket'}},
                                                              'restore_object'),
                                                  response2
                                                  ])
        CumulusLogger.info = Mock()
        CumulusLogger.error = Mock()
        exp_gran = {}
        exp_gran['granuleId'] = granule_id
        exp_files = []

        exp_file = {}
        exp_file['key'] = keys[0]
        exp_file['success'] = True
        exp_file['err_msg'] = ''
        exp_files.append(exp_file)

        exp_file = {}
        exp_file['key'] = keys[1]
        exp_file['success'] = True
        exp_file['err_msg'] = ''
        exp_files.append(exp_file)

        exp_gran['files'] = exp_files

        qresult1, _ = create_insert_request(
            REQUEST_ID1, REQUEST_GROUP_ID_EXP_1, granule_id, keys[0], "restore", "some_bucket",
            "inprogress", UTC_NOW_EXP_1, None, None)
        qresult2, _ = create_insert_request(
            REQUEST_ID2, REQUEST_GROUP_ID_EXP_1, granule_id, keys[0], "restore", "some_bucket",
            "error", UTC_NOW_EXP_1, None, "'Code': 'NoSuchBucket'")
        qresult3, _ = create_insert_request(
            REQUEST_ID3, REQUEST_GROUP_ID_EXP_1, granule_id, keys[1], "restore", "some_bucket",
            "inprogress", UTC_NOW_EXP_1, None, None)
        utils.database.single_query = Mock(side_effect=[qresult1, qresult2, qresult2, qresult3])

        result = request_files.task(exp_event, self.context)
        self.assertEqual(exp_gran, result)

        boto3.client.assert_called_with('s3')
        s3_cli.restore_object.assert_any_call(
            Bucket='some_bucket',
            Key=keys[0],
            RestoreRequest={'Days': 5, 'GlacierJobParameters': {'Tier': 'Standard'}})
        utils.database.single_query.assert_called()  # 4 times

if __name__ == '__main__':
    unittest.main(argv=['start'])
