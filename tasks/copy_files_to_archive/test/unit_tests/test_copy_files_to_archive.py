"""
Name: test_copy_files_to_archive.py

Description:  Unit tests for copy_files_to_archive.py.
"""
import os
import unittest
import uuid
from unittest.mock import Mock, call, patch, MagicMock

import requests_db
from botocore.exceptions import ClientError

import copy_files_to_archive
from test.request_helpers import (REQUEST_ID4, REQUEST_ID7,
                                  PROTECTED_BUCKET,
                                  create_copy_event2, mock_secretsmanager_get_parameter,
                                  create_copy_handler_event, create_select_requests)


class TestCopyFiles(unittest.TestCase):  # pylint: disable-msg=too-many-instance-attributes
    """
    TestCopyFiles.
    """

    def setUp(self):
        """
        Runs before each test. Sets up a series of default values for default cases.
        If you need these values for your test, set manually to a random/distinct value.
        TODO: Move these values into their respective tests and make sure they are 'assert'ed.
        """
        os.environ['COPY_RETRIES'] = '1'
        os.environ['DEVELOP_TESTS'] = 'False'
        os.environ['COPY_RETRY_SLEEP_SECS'] = '0'  # Makes tests run quickly if the unexpectedly hit sleep.
        os.environ["DATABASE_HOST"] = "my.db.host.gov"
        os.environ["DATABASE_PORT"] = "5400"
        os.environ["DATABASE_NAME"] = "sndbx"
        os.environ["DATABASE_USER"] = "unittestdbuser"
        os.environ["DATABASE_PW"] = "unittestdbpw"
        os.environ['PREFIX'] = uuid.uuid4().__str__()
        os.environ['DB_QUEUE_URL'] = f"db.queue.url"
        self.exp_src_bucket = 'my-dr-fake-glacier-bucket'
        self.exp_target_bucket = PROTECTED_BUCKET

        self.exp_file_key1 = 'dr-glacier/MOD09GQ.A0219114.N5aUCG.006.0656338553321.txt'
        self.handler_input_event = create_copy_handler_event()

    def tearDown(self):
        try:
            os.environ.pop('DB_QUEUE_URL')
            os.environ.pop('PREFIX')
            del os.environ['DEVELOP_TESTS']
            del os.environ['COPY_RETRIES']
            del os.environ['COPY_RETRY_SLEEP_SECS']
            del os.environ['DATABASE_HOST']
            del os.environ['DATABASE_NAME']
            del os.environ['DATABASE_USER']
            del os.environ['DATABASE_PW']
        except KeyError:
            pass

    @patch('database.single_query')
    @patch('boto3.client')
    @patch('time.sleep')
    def test_handler_one_file_success(self,
                                      mock_sleep: MagicMock,
                                      mock_boto3_client: MagicMock,
                                      mock_database_single_query: MagicMock):
        """
        Test copy lambda with one file, expecting successful result.
        """
        os.environ['COPY_RETRIES'] = '2'
        os.environ['COPY_RETRY_SLEEP_SECS'] = '0'
        exp_src_bucket = 'my-dr-fake-glacier-bucket'

        mock_s3_cli = mock_boto3_client('s3')
        mock_s3_cli.copy_object = Mock(side_effect=[None])
        exp_upd_result = []
        exp_request_ids = [REQUEST_ID7]
        _, exp_result = create_select_requests(exp_request_ids)
        mock_database_single_query.side_effect = [exp_result, exp_upd_result]
        mock_secretsmanager_get_parameter(2)
        result = copy_files_to_archive.handler(self.handler_input_event, None)
        mock_boto3_client.assert_has_calls([call('secretsmanager')])
        mock_s3_cli.copy_object.assert_called_with(Bucket=self.exp_target_bucket,
                                                   CopySource={'Bucket': exp_src_bucket,
                                                               'Key': self.exp_file_key1},
                                                   Key=self.exp_file_key1)
        exp_result = [{"success": True,
                       "source_bucket": self.exp_src_bucket,
                       "source_key": self.exp_file_key1,
                       "request_id": REQUEST_ID7,
                       "target_bucket": self.exp_target_bucket,
                       "err_msg": ""}]
        self.assertEqual(exp_result, result)
        self.assertEqual(mock_sleep.call_count, 0, "There should be no sleeps on happy path.")
        mock_database_single_query.assert_called()

    @patch('database.single_query')
    @patch('boto3.client')
    def test_handler_db_update_err(self,
                                   mock_boto3_client: MagicMock,
                                   mock_database_single_query: MagicMock):
        """
        Test copy lambda with error updating db.
        # todo: Expand on situation and expected behavior. My best attempt is below.
        Error when updating status in db. Should not retry, and should be considered completed.
        """
        s3_cli_mock = mock_boto3_client('s3')
        s3_cli_mock.copy_object = Mock(side_effect=[None])
        exp_request_ids = [REQUEST_ID7]
        _, exp_result = create_select_requests(exp_request_ids)
        exp_err = 'Database Error. Internal database error, please contact LP DAAC User Services'
        mock_database_single_query.side_effect = [exp_result, requests_db.DatabaseError(exp_err),
                                                  requests_db.DatabaseError(exp_err)]
        mock_secretsmanager_get_parameter(3)
        result = copy_files_to_archive.handler(self.handler_input_event, None)
        exp_result = [{'success': True, 'source_bucket': 'my-dr-fake-glacier-bucket',
                       'source_key': self.exp_file_key1,
                       'request_id': REQUEST_ID7,
                       'target_bucket': PROTECTED_BUCKET, 'err_msg': ''}]
        self.assertEqual(exp_result, result)

    @patch('database.single_query')
    @patch('boto3.client')
    @patch('time.sleep')
    def test_handler_db_read_err(self,
                                 mock_sleep: MagicMock,
                                 mock_boto3_client: MagicMock,
                                 mock_database_single_query):
        """
        Test copy lambda with error reading db.
        """
        os.environ['COPY_RETRIES'] = '1'
        os.environ['COPY_RETRY_SLEEP_SECS'] = '0'

        mock_s3_cli = mock_boto3_client('s3')
        mock_s3_cli.copy_object = Mock(side_effect=[None])
        exp_request_ids = [REQUEST_ID7]
        _, exp_result = create_select_requests(exp_request_ids)
        exp_err = 'Database Error. Internal database error, please contact LP DAAC User Services'
        mock_database_single_query.side_effect = [requests_db.DatabaseError(exp_err),
                                                  requests_db.DatabaseError(exp_err)]
        mock_secretsmanager_get_parameter(2)
        try:
            copy_files_to_archive.handler(self.handler_input_event, None)
        except copy_files_to_archive.CopyRequestError as err:
            exp_result = [{'success': False,
                           'source_bucket': 'my-dr-fake-glacier-bucket',
                           'source_key': self.exp_file_key1}]
            exp_err = f"File copy failed. {exp_result}"
            self.assertEqual(exp_err, str(err))

    @patch('database.single_query')
    @patch('boto3.client')
    @patch('time.sleep')
    def test_handler_db_read_not_found(self,
                                       mock_sleep: MagicMock,
                                       mock_boto3_client: MagicMock,
                                       mock_database_single_query: MagicMock):
        """
        Test copy lambda with no key found reading db.
        """
        os.environ['COPY_RETRIES'] = '1'
        os.environ['COPY_RETRY_SLEEP_SECS'] = '0'

        mock_s3_cli = mock_boto3_client('s3')
        mock_s3_cli.copy_object = Mock(side_effect=[None])
        exp_request_ids = [REQUEST_ID7]
        _, exp_result = create_select_requests(exp_request_ids)
        mock_database_single_query.side_effect = [[], []]
        mock_secretsmanager_get_parameter(2)
        try:
            copy_files_to_archive.handler(self.handler_input_event, None)
        except copy_files_to_archive.CopyRequestError as err:
            exp_result = [{'success': False,
                           'source_bucket': 'my-dr-fake-glacier-bucket',
                           'source_key': self.exp_file_key1}]
            exp_err = f"File copy failed. {exp_result}"
            self.assertEqual(exp_err, str(err))

    @patch('database.single_query')
    @patch('boto3.client')
    def test_handler_two_records_success(self,
                                         mock_boto3_client: MagicMock,
                                         mock_database_single_query: MagicMock):
        """
        Test copy lambda with two files, expecting successful result.
        """
        exp_file_key = 'dr-glacier/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf'
        mock_s3_cli = mock_boto3_client('s3')
        mock_s3_cli.copy_object = Mock(side_effect=[None, None])
        exp_upd_result = []
        exp_request_ids = [REQUEST_ID4, REQUEST_ID7]
        _, exp_result = create_select_requests(exp_request_ids)
        mock_database_single_query.side_effect = [exp_result, exp_upd_result,
                                                  exp_result, exp_upd_result]
        mock_secretsmanager_get_parameter(4)
        exp_rec_2 = create_copy_event2()
        self.handler_input_event["Records"].append(exp_rec_2)
        result = copy_files_to_archive.handler(self.handler_input_event, None)

        mock_boto3_client.assert_has_calls([call('secretsmanager')])
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

        mock_s3_cli.copy_object.assert_any_call(Bucket=self.exp_target_bucket,
                                                CopySource={'Bucket': self.exp_src_bucket,
                                                            'Key': self.exp_file_key1},
                                                Key=self.exp_file_key1)
        mock_s3_cli.copy_object.assert_any_call(Bucket=self.exp_target_bucket,
                                                CopySource={'Bucket': self.exp_src_bucket,
                                                            'Key': exp_file_key},
                                                Key=exp_file_key)

    @patch('database.single_query')
    @patch('boto3.client')
    @patch('time.sleep')
    def test_handler_one_file_fail_3x(self,
                                      mock_sleep: MagicMock,
                                      mock_boto3_client: MagicMock,
                                      mock_database_single_query: MagicMock):
        """
        Test copy lambda with one failed copy after 3 retries.
        """
        retry_sleep_seconds = 18
        os.environ['COPY_RETRY_SLEEP_SECS'] = str(retry_sleep_seconds)
        copy_retries = 2
        os.environ['COPY_RETRIES'] = str(copy_retries)
        mock_s3_cli = mock_boto3_client('s3')
        mock_s3_cli.copy_object = Mock(side_effect=[ClientError({'Error': {'Code': 'AccessDenied'}},
                                                                'copy_object'),
                                                    ClientError({'Error': {'Code': 'AccessDenied'}},
                                                                'copy_object'),
                                                    ClientError({'Error': {'Code': 'AccessDenied'}},
                                                                'copy_object')])
        mock_s3_cli.head_object = Mock()
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

        # todo: The file under test does not call single_query. Remove this and other references in test code.
        mock_database_single_query.side_effect = [exp_result,
                                                  exp_result,
                                                  exp_upd_result,
                                                  exp_result,
                                                  exp_upd_result]

        mock_secretsmanager_get_parameter(5)
        try:
            copy_files_to_archive.handler(self.handler_input_event, None)
            self.fail("expected CopyRequestError")
        except copy_files_to_archive.CopyRequestError as ex:
            self.assertEqual(exp_error, str(ex))
        mock_boto3_client.assert_has_calls([call('secretsmanager')])
        mock_s3_cli.copy_object.assert_called_with(Bucket=self.exp_target_bucket,
                                                   CopySource={'Bucket': self.exp_src_bucket,
                                                               'Key': self.exp_file_key1},
                                                   Key=self.exp_file_key1)
        self.assertEqual(copy_retries, mock_sleep.call_count, 'Should sleep once between each attempt.')
        mock_sleep.assert_has_calls([call(retry_sleep_seconds)] * copy_retries)
        mock_database_single_query.assert_called()

    @patch('database.single_query')
    @patch('boto3.client')
    @patch('time.sleep')
    def test_handler_one_file_retry_success(self,
                                            mock_sleep: MagicMock,
                                            mock_boto3_client: MagicMock,
                                            mock_database_single_query):
        """
        Test copy lambda with one failed copy attempts, second attempt successful.
        """
        retry_sleep_seconds = 13
        os.environ['COPY_RETRY_SLEEP_SECS'] = str(retry_sleep_seconds)
        copy_retries = 2
        os.environ['COPY_RETRIES'] = str(copy_retries)
        mock_s3_cli = mock_boto3_client('s3')
        mock_s3_cli.copy_object = Mock(side_effect=[ClientError({'Error': {'Code': 'AccessDenied'}}, 'copy_object'),
                                                    None])
        exp_request_ids = [REQUEST_ID7, REQUEST_ID4]
        _, exp_result = create_select_requests(exp_request_ids)
        exp_upd_result = []
        mock_database_single_query.side_effect = [exp_result,
                                                  exp_upd_result,
                                                  exp_result,
                                                  exp_upd_result]

        mock_secretsmanager_get_parameter(4)
        result = copy_files_to_archive.handler(self.handler_input_event, None)
        # todo: The file under test does not call boto3.client('secretsmanager'). Remove this and other references in test code.
        mock_boto3_client.assert_has_calls([call('secretsmanager')])
        exp_result = [{"success": True, "source_bucket": self.exp_src_bucket,
                       "source_key": self.exp_file_key1,
                       "request_id": REQUEST_ID7,
                       "target_bucket": self.exp_target_bucket,
                       "err_msg": ""}]
        self.assertEqual(exp_result, result)
        mock_s3_cli.copy_object.assert_called_with(Bucket=self.exp_target_bucket,
                                                   CopySource={'Bucket': self.exp_src_bucket,
                                                               'Key': self.exp_file_key1},
                                                   Key=self.exp_file_key1)
        self.assertEqual(1, mock_sleep.call_count, 'Should sleep once between each attempt.')
        mock_sleep.assert_has_calls([call(retry_sleep_seconds)])
        mock_database_single_query.assert_called()

    @patch('boto3.client')
    def test_handler_no_object_key_in_event(self,
                                            mock_boto3_client: MagicMock):
        """
        Test copy lambda with missing "object" key in input event.
        """
        mock_s3_cli = mock_boto3_client.client('s3')
        mock_s3_cli.copy_object = Mock(side_effect=[None])
        my_dict = self.handler_input_event["Records"][0]["s3"]["object"]
        my_dict.pop('key')
        exp_err = f'event record: "{self.handler_input_event["Records"][0]}" does not contain a ' \
                  f'value for Records["s3"]["object"]["key"]'
        try:
            copy_files_to_archive.handler(self.handler_input_event, None)
            self.fail("expected CopyRequestError")
        except copy_files_to_archive.CopyRequestError as ex:
            self.assertEqual(exp_err, str(ex))


if __name__ == '__main__':
    unittest.main(argv=['start'])
