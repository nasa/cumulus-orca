"""
Name: test_copy_files_to_archive.py

Description:  Unit tests for copy_files_to_archive.py.
"""
import json
import os
import unittest
from unittest.mock import Mock

import boto3
from botocore.exceptions import ClientError

import copy_files_to_archive
import utils
import utils.database
from copy_helpers import create_event2, create_handler_event


class TestCopyFiles(unittest.TestCase):  #pylint: disable-msg=too-many-instance-attributes
    """
    TestCopyFiles.
    """
    def setUp(self):
        self.mock_boto3_client = boto3.client
        os.environ['COPY_RETRIES'] = '2'
        os.environ['COPY_RETRY_SLEEP_SECS'] = '1'
        os.environ["DATABASE_HOST"] = "my.db.host.gov"
        os.environ["DATABASE_NAME"] = "sndbx"
        os.environ["DATABASE_USER"] = "unittestdbuser"
        os.environ["DATABASE_PW"] = "unittestdbpw"
        self.exp_other_bucket = "unittest_protected_bucket"
        self.bucket_map = {".hdf": "unittest_hdf_bucket",
                           ".txt": "unittest_txt_bucket",
                           "other": self.exp_other_bucket}
        os.environ['BUCKET_MAP'] = json.dumps(self.bucket_map)

        self.exp_src_bucket = 'my-dr-fake-glacier-bucket'
        self.exp_target_bucket = 'unittest_txt_bucket'

        self.exp_file_key1 = 'dr-glacier/MOD09GQ.A0219114.N5aUCG.006.0656338553321.txt'
        self.handler_input_event = create_handler_event()
        self.mock_single_query = utils.database.single_query

    def tearDown(self):
        utils.database.single_query = self.mock_single_query
        boto3.client = self.mock_boto3_client
        try:
            del os.environ['BUCKET_MAP']
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
        utils.database.single_query = Mock(side_effect=[exp_upd_result])
        result = copy_files_to_archive.handler(self.handler_input_event, None)
        os.environ['COPY_RETRIES'] = '2'
        os.environ['COPY_RETRY_SLEEP_SECS'] = '1'
        boto3.client.assert_called_with('s3')
        exp_result = [{"success": True,
                       "source_bucket": self.exp_src_bucket,
                       "source_key": self.exp_file_key1,
                       "target_bucket": self.exp_target_bucket,
                       "err_msg": ""}]
        self.assertEqual(exp_result, result)
        s3_cli.copy_object.assert_called_with(Bucket=self.exp_target_bucket,
                                              CopySource={'Bucket': self.exp_src_bucket,
                                                          'Key': self.exp_file_key1},
                                              Key=self.exp_file_key1)
        utils.database.single_query.assert_called_once()

    def test_handler_two_records_success(self):
        """
        Test copy lambda with two files, expecting successful result.
        """
        exp_file_key = 'dr-glacier/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf'
        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.copy_object = Mock(side_effect=[None, None])
        exp_rec_2 = create_event2()
        self.handler_input_event["Records"].append(exp_rec_2)
        result = copy_files_to_archive.handler(self.handler_input_event, None)

        boto3.client.assert_called_with('s3')
        exp_result = [{"success": True, "source_bucket": self.exp_src_bucket,
                       "source_key": self.exp_file_key1,
                       "target_bucket": self.exp_target_bucket,
                       "err_msg": ""},
                      {"success": True, "source_bucket": self.exp_src_bucket,
                       "source_key": exp_file_key,
                       "target_bucket": "unittest_hdf_bucket",
                       "err_msg": ""}]
        self.assertEqual(exp_result, result)

        s3_cli.copy_object.assert_any_call(Bucket=self.exp_target_bucket,
                                           CopySource={'Bucket': self.exp_src_bucket,
                                                       'Key': self.exp_file_key1},
                                           Key=self.exp_file_key1)
        s3_cli.copy_object.assert_any_call(Bucket='unittest_hdf_bucket',
                                           CopySource={'Bucket': self.exp_src_bucket,
                                                       'Key': exp_file_key},
                                           Key=exp_file_key)

    def test_handler_two_records_one_fail_one_success(self):
        """
        Test copy lambda with two files, one successful copy, one failed copy.
        """
        exp_file_key = 'dr-glacier/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf'
        exp_file2_key = 'dr-glacier/MOD09GQ.A0219114.N5aUCG.006.0656338553321.txt'
        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.copy_object = Mock(side_effect=[ClientError({'Error': {'Code': 'AccessDenied'}},
                                                           'copy_object'),
                                               ClientError({'Error': {'Code': 'AccessDenied'}},
                                                           'copy_object'),
                                               ClientError({'Error': {'Code': 'AccessDenied'}},
                                                           'copy_object'),
                                               None])
        exp_rec_2 = create_event2()
        self.handler_input_event["Records"].append(exp_rec_2)

        exp_error = "File copy failed. " \
                    "[{'success': False, " \
                    f"'source_bucket': '{self.exp_src_bucket}', " \
                    f"'source_key': '{exp_file2_key}', " \
                    f"'target_bucket': '{self.exp_target_bucket}', " \
                    "'err_msg': 'An error occurred (AccessDenied) when calling " \
                    "the copy_object operation: Unknown'}, {'success': True, " \
                    f"'source_bucket': '{self.exp_src_bucket}', " \
                    f"'source_key': '{exp_file_key}', " \
                    "'target_bucket': 'unittest_hdf_bucket', 'err_msg': ''}]"
        try:
            copy_files_to_archive.handler(self.handler_input_event, None)
            self.fail("expected CopyRequestError")
        except copy_files_to_archive.CopyRequestError as ex:
            self.assertEqual(exp_error, str(ex))

        boto3.client.assert_called_with('s3')
        s3_cli.copy_object.assert_any_call(Bucket=self.exp_target_bucket,
                                           CopySource={'Bucket': self.exp_src_bucket,
                                                       'Key': self.exp_file_key1},
                                           Key=self.exp_file_key1)
        s3_cli.copy_object.assert_any_call(Bucket='unittest_hdf_bucket',
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
                    f"'target_bucket': '{self.exp_target_bucket}', " \
                    "'err_msg': 'An error occurred (AccessDenied) when calling " \
                    "the copy_object operation: Unknown'}]"
        exp_result = []
        utils.database.single_query = Mock(side_effect=[exp_result, exp_result])
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
        utils.database.single_query.assert_called()

    def test_handler_one_file_retry2_success(self):
        """
        Test copy lambda with two failed copy attempts, third attempt successful.
        """
        del os.environ['COPY_RETRY_SLEEP_SECS']
        del os.environ['COPY_RETRIES']
        import time
        time.sleep(1)
        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.copy_object = Mock(side_effect=[ClientError({'Error': {'Code': 'AccessDenied'}},
                                                           'copy_object'),
                                               None])
        exp_upd_result = []
        utils.database.single_query = Mock(side_effect=[exp_upd_result, exp_upd_result])
        result = copy_files_to_archive.handler(self.handler_input_event, None)
        os.environ['COPY_RETRIES'] = '2'
        os.environ['COPY_RETRY_SLEEP_SECS'] = '1'
        boto3.client.assert_called_with('s3')
        exp_result = [{"success": True, "source_bucket": self.exp_src_bucket,
                       "source_key": self.exp_file_key1,
                       "target_bucket": self.exp_target_bucket,
                       "err_msg": ""}]
        self.assertEqual(exp_result, result)
        s3_cli.copy_object.assert_called_with(Bucket=self.exp_target_bucket,
                                              CopySource={'Bucket': self.exp_src_bucket,
                                                          'Key': self.exp_file_key1},
                                              Key=self.exp_file_key1)
        utils.database.single_query.assert_called()

    def test_handler_no_bucket_map(self):
        """
        Test copy lambda with no BUCKET_MAP environment variable.
        """
        del os.environ['BUCKET_MAP']
        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.copy_object = Mock(side_effect=[None])
        exp_err = 'BUCKET_MAP: {} does not contain values for ".txt" or "other"'
        try:
            copy_files_to_archive.handler(self.handler_input_event, None)
            self.fail("expected CopyRequestError")
        except copy_files_to_archive.CopyRequestError as ex:
            self.assertEqual(exp_err, str(ex))
        os.environ['BUCKET_MAP'] = json.dumps(self.bucket_map)
        boto3.client.assert_called_with('s3')

    def test_handler_no_ext_in_bucket_map(self):
        """
        Test copy lambda with missing file extension in BUCKET_MAP.
        """
        exp_file_key = 'dr-glacier/MOD09GQ.A0219114.N5aUCG.006.0656338553321.xml'
        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.copy_object = Mock(side_effect=[None])
        self.handler_input_event["Records"][0]["s3"]["object"]["key"] = exp_file_key
        exp_upd_result = []
        utils.database.single_query = Mock(side_effect=[exp_upd_result])
        result = copy_files_to_archive.handler(self.handler_input_event, None)
        boto3.client.assert_called_with('s3')
        exp_result = [{"success": True, "source_bucket": self.exp_src_bucket,
                       "source_key": exp_file_key,
                       "target_bucket": self.exp_other_bucket,
                       "err_msg": ""}]
        self.assertEqual(exp_result, result)
        s3_cli.copy_object.assert_called_with(Bucket=self.exp_other_bucket,
                                              CopySource={'Bucket': self.exp_src_bucket,
                                                          'Key': exp_file_key},
                                              Key=exp_file_key)
        utils.database.single_query.assert_called_once()


    def test_handler_no_other_in_bucket_map(self):
        """
        Test copy lambda with missing "other" key in BUCKET_MAP.
        """
        exp_file_key = 'dr-glacier/MOD09GQ.A0219114.N5aUCG.006.0656338553321.xml'
        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.copy_object = Mock(side_effect=[None])
        bucket_map = {".hdf": "unittest_hdf_bucket", ".txt": "unittest_txt_bucket"}
        os.environ['BUCKET_MAP'] = json.dumps(bucket_map)

        self.handler_input_event["Records"][0]["s3"]["object"]["key"] = exp_file_key
        exp_err = f'BUCKET_MAP: {bucket_map} does not contain values for ".xml" or "other"'
        try:
            copy_files_to_archive.handler(self.handler_input_event, None)
            self.fail("expected CopyRequestError")
        except copy_files_to_archive.CopyRequestError as ex:
            self.assertEqual(exp_err, str(ex))

        boto3.client.assert_called_with('s3')

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
