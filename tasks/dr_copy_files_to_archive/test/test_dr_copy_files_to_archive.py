"""
Name: test_dr_copy_files_to_archive.py

Description:  Unit tests for dr_copy_files_to_archive.py.
"""
import unittest
from unittest.mock import Mock
import os
import json
import boto3
from botocore.exceptions import ClientError
import dr_copy_files_to_archive

class TestCopyFiles(unittest.TestCase):
    """
    TestCopyFiles.
    """
    def setUp(self):
        self.mock_boto3_client = boto3.client
        os.environ['COPY_RETRIES'] = '2'
        os.environ['COPY_RETRY_SLEEP_SECS'] = '1'
        self.exp_other_bucket = "unittest_protected_bucket"
        self.bucket_map = {".hdf": "unittest_hdf_bucket",
                           ".txt": "unittest_txt_bucket",
                           "other": self.exp_other_bucket}
        os.environ['BUCKET_MAP'] = json.dumps(self.bucket_map)

        self.exp_src_bucket = 'my-dr-fake-glacier-bucket'
        self.exp_target_bucket = 'unittest_txt_bucket'
        self.exp_file_key1 = 'dr-glacier/MOD09GQ.A0219114.N5aUCG.006.0656338553321.txt'
        self.exp_file_key2 = 'dr-glacier/MOD09GQ.A0219114.N5aUCG.006.0656338553321.xml'
        self.exp_file_key3 = 'dr-glacier/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf'
        self.exp_event = {"Records": [{"eventVersion": "2.1",
                                       "eventSource": "aws:s3",
                                       "awsRegion": "us-west-2",
                                       "eventTime": "2019-06-17T18:54:06.686Z",
                                       "eventName": "ObjectRestore:Post",
                                       "userIdentity": {"principalId": "AWS:AROXSO:request_files"},
                                       "requestParameters": {"sourceIPAddress": "34.217.126.178"},
                                       "responseElements": {"x-amz-request-id": "0364DD02830B32C0",
                                                            "x-amz-id-2": "4TpigLzkLqdD5F2RbnAnU="},
                                       "s3": {"s3SchemaVersion": "1.0",
                                              "configurationId": "dr_restore_complete",
                                              "bucket": {"name": self.exp_src_bucket,
                                                         "ownerIdentity": {"principalId": "A1BCJ9"},
                                                         "arn":
                                                             "arn:aws:s3::"
                                                             ":my-dr-fake-glacier-bucket"},
                                              "object": {"key": self.exp_file_key1,
                                                         "size": 645, "sequencer": "0054A126FB"}}}]}
        self.exp_rec_2 = {"eventVersion": "2.1",
                          "eventSource": "aws:s3",
                          "awsRegion": "us-west-2",
                          "eventTime": "2019-06-17T18:54:06.686Z",
                          "eventName": "ObjectRestore:Post",
                          "userIdentity": {"principalId": "AWS:AROAJXMHUPO:request_files"},
                          "requestParameters": {"sourceIPAddress": "34.217.126.178"},
                          "responseElements": {"x-amz-request-id": "0364DD02830B32C0",
                                               "x-amz-id-2": "4gzKLAPacP+xkLqdD5F2RbnAnU="},
                          "s3": {"s3SchemaVersion": "1.0",
                                 "configurationId": "dr_restore_complete",
                                 "bucket": {"name": self.exp_src_bucket,
                                            "ownerIdentity": {"principalId": "A1BC3XDGCJ9"},
                                            "arn": "arn:aws:s3:::my-dr-fake-glacier-bucket"},
                                 "object": {"key": self.exp_file_key3,
                                            "size": 645,
                                            "sequencer": "005CED5BF54A126FB"}}}
        self.exp_context = None

    def tearDown(self):
        boto3.client = self.mock_boto3_client
        try:
            del os.environ['BUCKET_MAP']
            del os.environ['COPY_RETRY_SLEEP_SECS']
            del os.environ['COPY_RETRIES']
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
        result = dr_copy_files_to_archive.handler(self.exp_event, None)
        os.environ['COPY_RETRIES'] = '2'
        os.environ['COPY_RETRY_SLEEP_SECS'] = '1'
        boto3.client.assert_called_with('s3')
        exp_result = json.dumps([{"success": True,
                                  "source_bucket": self.exp_src_bucket,
                                  "source_key": self.exp_file_key1,
                                  "target_bucket": self.exp_target_bucket,
                                  "err_msg": ""}])
        self.assertEqual(exp_result, result)
        s3_cli.copy_object.assert_called_with(Bucket=self.exp_target_bucket,
                                              CopySource={'Bucket': self.exp_src_bucket,
                                                          'Key': self.exp_file_key1},
                                              Key=self.exp_file_key1)

    def test_handler_two_records_success(self):
        """
        Test copy lambda with two files, expecting successful result.
        """
        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.copy_object = Mock(side_effect=[None, None])
        self.exp_event["Records"].append(self.exp_rec_2)
        result = dr_copy_files_to_archive.handler(self.exp_event, None)
        boto3.client.assert_called_with('s3')
        exp_result = json.dumps([{"success": True, "source_bucket": self.exp_src_bucket,
                                  "source_key": self.exp_file_key1,
                                  "target_bucket": self.exp_target_bucket,
                                  "err_msg": ""},
                                 {"success": True, "source_bucket": self.exp_src_bucket,
                                  "source_key": self.exp_file_key3,
                                  "target_bucket": "unittest_hdf_bucket",
                                  "err_msg": ""}])
        self.assertEqual(exp_result, result)
        s3_cli.copy_object.assert_any_call(Bucket=self.exp_target_bucket,
                                           CopySource={'Bucket': self.exp_src_bucket,
                                                       'Key': self.exp_file_key1},
                                           Key=self.exp_file_key1)
        s3_cli.copy_object.assert_any_call(Bucket='unittest_hdf_bucket',
                                           CopySource={'Bucket': self.exp_src_bucket,
                                                       'Key': self.exp_file_key3},
                                           Key=self.exp_file_key3)

    def test_handler_two_records_one_fail_one_success(self):
        """
        Test copy lambda with two files, one successful copy, one failed copy.
        """
        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.copy_object = Mock(side_effect=[ClientError({'Error': {'Code': 'AccessDenied'}},
                                                           'copy_object'),
                                               ClientError({'Error': {'Code': 'AccessDenied'}},
                                                           'copy_object'),
                                               ClientError({'Error': {'Code': 'AccessDenied'}},
                                                           'copy_object'),
                                               None])
        self.exp_event["Records"].append(self.exp_rec_2)
        exp_result = [{"success": False, "source_bucket": self.exp_src_bucket,
                       "source_key": self.exp_file_key1,
                       "target_bucket": self.exp_target_bucket,
                       "err_msg": "An error occurred (AccessDenied) when calling the copy_object "
                                  "operation: Unknown"},
                      {"success": True, "source_bucket": self.exp_src_bucket,
                       "source_key": self.exp_file_key3,
                       "target_bucket": "unittest_hdf_bucket",
                       "err_msg": ""}]
        exp_error = f'File copy failed. {exp_result}'
        try:
            dr_copy_files_to_archive.handler(self.exp_event, None)
            self.fail("expected CopyRequestError")
        except dr_copy_files_to_archive.CopyRequestError as ex:
            self.assertEqual(exp_error, str(ex))

        boto3.client.assert_called_with('s3')
        s3_cli.copy_object.assert_any_call(Bucket=self.exp_target_bucket,
                                           CopySource={'Bucket': self.exp_src_bucket,
                                                       'Key': self.exp_file_key1},
                                           Key=self.exp_file_key1)
        s3_cli.copy_object.assert_any_call(Bucket='unittest_hdf_bucket',
                                           CopySource={'Bucket': self.exp_src_bucket,
                                                       'Key': self.exp_file_key3},
                                           Key=self.exp_file_key3)

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
        exp_msg = 'An error occurred (AccessDenied) when calling the copy_object operation: Unknown'
        exp_result = [{'success': False, 'source_bucket': self.exp_src_bucket,
                       'source_key': self.exp_file_key1,
                       'target_bucket': self.exp_target_bucket,
                       'err_msg': exp_msg}]

        exp_error = f"File copy failed. {exp_result}"
        try:
            dr_copy_files_to_archive.handler(self.exp_event, None)
            self.fail("expected CopyRequestError")
        except dr_copy_files_to_archive.CopyRequestError as ex:
            self.assertEqual(exp_error, str(ex))
        boto3.client.assert_called_with('s3')
        s3_cli.copy_object.assert_called_with(Bucket=self.exp_target_bucket,
                                              CopySource={'Bucket': self.exp_src_bucket,
                                                          'Key': self.exp_file_key1},
                                              Key=self.exp_file_key1)

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
        result = dr_copy_files_to_archive.handler(self.exp_event, None)
        os.environ['COPY_RETRIES'] = '2'
        os.environ['COPY_RETRY_SLEEP_SECS'] = '1'
        boto3.client.assert_called_with('s3')
        exp_result = json.dumps([{"success": True, "source_bucket": self.exp_src_bucket,
                                  "source_key": self.exp_file_key1,
                                  "target_bucket": self.exp_target_bucket,
                                  "err_msg": ""}])
        self.assertEqual(exp_result, result)
        s3_cli.copy_object.assert_called_with(Bucket=self.exp_target_bucket,
                                              CopySource={'Bucket': self.exp_src_bucket,
                                                          'Key': self.exp_file_key1},
                                              Key=self.exp_file_key1)

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
            dr_copy_files_to_archive.handler(self.exp_event, None)
            self.fail("expected CopyRequestError")
        except dr_copy_files_to_archive.CopyRequestError as ex:
            self.assertEqual(exp_err, str(ex))
        os.environ['BUCKET_MAP'] = json.dumps(self.bucket_map)
        boto3.client.assert_called_with('s3')

    def test_handler_no_ext_in_bucket_map(self):
        """
        Test copy lambda with missing file extension in BUCKET_MAP.
        """
        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.copy_object = Mock(side_effect=[None])
        self.exp_event["Records"][0]["s3"]["object"]["key"] = self.exp_file_key2
        result = dr_copy_files_to_archive.handler(self.exp_event, None)
        boto3.client.assert_called_with('s3')
        exp_result = json.dumps([{"success": True, "source_bucket": self.exp_src_bucket,
                                  "source_key": self.exp_file_key2,
                                  "target_bucket": self.exp_other_bucket,
                                  "err_msg": ""}])
        self.assertEqual(exp_result, result)
        s3_cli.copy_object.assert_called_with(Bucket=self.exp_other_bucket,
                                              CopySource={'Bucket': self.exp_src_bucket,
                                                          'Key': self.exp_file_key2},
                                              Key=self.exp_file_key2)

    def test_handler_no_other_in_bucket_map(self):
        """
        Test copy lambda with missing "other" key in BUCKET_MAP.
        """
        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.copy_object = Mock(side_effect=[None])
        bucket_map = {".hdf": "unittest_hdf_bucket", ".txt": "unittest_txt_bucket"}
        os.environ['BUCKET_MAP'] = json.dumps(bucket_map)

        self.exp_event["Records"][0]["s3"]["object"]["key"] = self.exp_file_key2
        exp_err = f'BUCKET_MAP: {bucket_map} does not contain values for ".xml" or "other"'
        try:
            dr_copy_files_to_archive.handler(self.exp_event, None)
            self.fail("expected CopyRequestError")
        except dr_copy_files_to_archive.CopyRequestError as ex:
            self.assertEqual(exp_err, str(ex))

        boto3.client.assert_called_with('s3')

    def test_handler_no_object_key_in_event(self):
        """
        Test copy lambda with missing "object" key in input event.
        """
        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.copy_object = Mock(side_effect=[None])
        mydict = self.exp_event["Records"][0]["s3"]["object"]
        mydict.pop('key')
        exp_err = f'event record: "{self.exp_event["Records"][0]}" does not contain a ' \
                  f'value for Records["s3"]["object"]["key"]'
        try:
            dr_copy_files_to_archive.handler(self.exp_event, None)
            self.fail("expected CopyRequestError")
        except dr_copy_files_to_archive.CopyRequestError as ex:
            self.assertEqual(exp_err, str(ex))


if __name__ == '__main__':
    unittest.main(argv=['start'])
