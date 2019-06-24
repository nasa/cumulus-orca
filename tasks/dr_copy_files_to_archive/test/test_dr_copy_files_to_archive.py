import unittest
import os
import json
import boto3
import dr_copy_files_to_archive
from unittest.mock import Mock
from botocore.exceptions import ClientError

class TestCopyFiles(unittest.TestCase):

    def setUp(self):
        self.mock_boto3_client = boto3.client
        os.environ['COPY_RETRIES'] = '2'
        os.environ['COPY_RETRY_SLEEP_SECS'] = '1'
        self.exp_other_bucket = "unittest_protected_bucket"
        self.bucket_map = {".hdf": "unittest_hdf_bucket", ".txt": "unittest_txt_bucket", "other": self.exp_other_bucket}
        os.environ['BUCKET_MAP'] = json.dumps(self.bucket_map)

        self.exp_src_bucket = 'my-dr-fake-glacier-bucket'
        self.exp_target_bucket = 'unittest_txt_bucket'

        self.exp_file_key1 = 'dr-glacier/MOD09GQ.A0219114.N5aUCG.006.0656338553321.txt'
        with open('testevents/exp_event_1.json') as f:
            self.exp_event = json.load(f)

        self.exp_context = None

    def tearDown(self):
        boto3.client = self.mock_boto3_client
        try:
            del os.environ['BUCKET_MAP']
            del os.environ['COPY_RETRY_SLEEP_SECS']
            del os.environ['COPY_RETRIES']
        except KeyError as ke:
            pass

    def test_handler_one_file_success(self):
        del os.environ['COPY_RETRY_SLEEP_SECS']
        del os.environ['COPY_RETRIES']
        boto3.client = Mock()
        s3 = boto3.client('s3')
        s3.copy_object = Mock(side_effect=[None])
        result = dr_copy_files_to_archive.handler(self.exp_event, self.exp_context)
        os.environ['COPY_RETRIES'] = '2'
        os.environ['COPY_RETRY_SLEEP_SECS'] = '1'
        boto3.client.assert_called_with('s3')
        exp_result = json.dumps([{"success": True, "source_bucket": self.exp_src_bucket, "source_key": self.exp_file_key1, "target_bucket": self.exp_target_bucket, "err_msg": ""}])
        self.assertEqual(exp_result, result)
        s3.copy_object.assert_called_with(Bucket=self.exp_target_bucket,
                                          CopySource={'Bucket': self.exp_src_bucket,
                                                      'Key': self.exp_file_key1},
                                          Key=self.exp_file_key1)

    def test_handler_two_records_success(self):
        #TODO I don't know if this is even a valid input event...
        exp_file_key = 'dr-glacier/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf'
        boto3.client = Mock()
        s3 = boto3.client('s3')
        s3.copy_object = Mock(side_effect=[None, None])
        with open('testevents/exp_event_2.json') as f:
            exp_rec_2 = json.load(f)
        self.exp_event["Records"].append(exp_rec_2)
        result = dr_copy_files_to_archive.handler(self.exp_event, self.exp_context)
        boto3.client.assert_called_with('s3')
        exp_result = json.dumps([{"success": True, "source_bucket": self.exp_src_bucket,
                                  "source_key": self.exp_file_key1,
                                  "target_bucket": self.exp_target_bucket,
                                  "err_msg": ""},
                                 {"success": True, "source_bucket": self.exp_src_bucket,
                                  "source_key": exp_file_key,
                                  "target_bucket": "unittest_hdf_bucket",
                                  "err_msg": ""}])
        self.assertEqual(exp_result, result)
        s3.copy_object.assert_any_call(Bucket=self.exp_target_bucket,
                                          CopySource={'Bucket': self.exp_src_bucket,
                                                      'Key': self.exp_file_key1},
                                          Key=self.exp_file_key1)
        s3.copy_object.assert_any_call(Bucket='unittest_hdf_bucket',
                                       CopySource={'Bucket': self.exp_src_bucket,
                                                   'Key': exp_file_key},
                                       Key=exp_file_key)

    def test_handler_two_records_one_fail_one_success(self):
        #TODO I don't know if this is even a valid input event...
        exp_file_key = 'dr-glacier/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf'
        boto3.client = Mock()
        s3 = boto3.client('s3')
        s3.copy_object = Mock(side_effect=[ClientError({'Error': {'Code': 'AccessDenied'}}, 'copy_object'),
                                           ClientError({'Error': {'Code': 'AccessDenied'}}, 'copy_object'),
                                           ClientError({'Error': {'Code': 'AccessDenied'}}, 'copy_object'),
                                           None])
        with open('testevents/exp_event_2.json') as f:
            exp_rec_2 = json.load(f)
        self.exp_event["Records"].append(exp_rec_2)
        exp_result = [{"success": False, "source_bucket": self.exp_src_bucket,
                     "source_key": self.exp_file_key1,
                     "target_bucket": self.exp_target_bucket,
                     "err_msg": "An error occurred (AccessDenied) when calling the copy_object operation: Unknown"},
                     {"success": True, "source_bucket": self.exp_src_bucket,
                     "source_key": exp_file_key,
                     "target_bucket": "unittest_hdf_bucket",
                     "err_msg": ""}]
        exp_error =  f'File copy failed. {exp_result}'
        try:
            dr_copy_files_to_archive.handler(self.exp_event, self.exp_context)
            self.fail("expected CopyRequestError")
        except dr_copy_files_to_archive.CopyRequestError as ex:
            self.assertEqual(exp_error, str(ex))

        boto3.client.assert_called_with('s3')
        s3.copy_object.assert_any_call(Bucket=self.exp_target_bucket,
                                          CopySource={'Bucket': self.exp_src_bucket,
                                                      'Key': self.exp_file_key1},
                                          Key=self.exp_file_key1)
        s3.copy_object.assert_any_call(Bucket='unittest_hdf_bucket',
                                       CopySource={'Bucket': self.exp_src_bucket,
                                                   'Key': exp_file_key},
                                       Key=exp_file_key)

    def test_handler_one_file_fail_3x(self):
        boto3.client = Mock()
        s3 = boto3.client('s3')
        s3.copy_object = Mock(side_effect=[ClientError({'Error': {'Code': 'AccessDenied'}}, 'copy_object'),
                                              ClientError({'Error': {'Code': 'AccessDenied'}}, 'copy_object'),
                                              ClientError({'Error': {'Code': 'AccessDenied'}}, 'copy_object')])
        exp_msg = 'An error occurred (AccessDenied) when calling the copy_object operation: Unknown'
        exp_result = [{'success': False, 'source_bucket': self.exp_src_bucket, 'source_key': self.exp_file_key1, 'target_bucket': self.exp_target_bucket, 'err_msg': exp_msg}]

        exp_error = f"File copy failed. {exp_result}"
        try:
            dr_copy_files_to_archive.handler(self.exp_event, self.exp_context)
            self.fail("expected CopyRequestError")
        except dr_copy_files_to_archive.CopyRequestError as ex:
            self.assertEqual(exp_error, str(ex))
        boto3.client.assert_called_with('s3')
        s3.copy_object.assert_called_with(Bucket=self.exp_target_bucket,
                                          CopySource={'Bucket': self.exp_src_bucket,
                                                      'Key': self.exp_file_key1},
                                          Key=self.exp_file_key1)

    def test_handler_one_file_retry2_success(self):
        del os.environ['COPY_RETRY_SLEEP_SECS']
        del os.environ['COPY_RETRIES']
        import time
        time.sleep(1)
        boto3.client = Mock()
        s3 = boto3.client('s3')
        s3.copy_object = Mock(side_effect=[ClientError({'Error': {'Code': 'AccessDenied'}}, 'copy_object'),
                                           None])
        result = dr_copy_files_to_archive.handler(self.exp_event, self.exp_context)
        os.environ['COPY_RETRIES'] = '2'
        os.environ['COPY_RETRY_SLEEP_SECS'] = '1'
        boto3.client.assert_called_with('s3')
        exp_result = json.dumps([{"success": True, "source_bucket": self.exp_src_bucket, "source_key": self.exp_file_key1, "target_bucket": self.exp_target_bucket, "err_msg": ""}])
        self.assertEqual(exp_result, result)
        s3.copy_object.assert_called_with(Bucket=self.exp_target_bucket,
                                          CopySource={'Bucket': self.exp_src_bucket,
                                                      'Key': self.exp_file_key1},
                                          Key=self.exp_file_key1)

    def test_handler_no_bucket_map(self):
        del os.environ['BUCKET_MAP']
        boto3.client = Mock()
        s3 = boto3.client('s3')
        s3.copy_object = Mock(side_effect=[None])
        exp_err = 'BUCKET_MAP: {} does not contain values for ".txt" or "other"'
        try:
            dr_copy_files_to_archive.handler(self.exp_event, self.exp_context)
            self.fail("expected CopyRequestError")
        except dr_copy_files_to_archive.CopyRequestError as ex:
            self.assertEqual(exp_err, str(ex))
        os.environ['BUCKET_MAP'] = json.dumps(self.bucket_map)
        boto3.client.assert_called_with('s3')

    def test_handler_no_ext_in_bucket_map(self):
        exp_file_key = 'dr-glacier/MOD09GQ.A0219114.N5aUCG.006.0656338553321.xml'
        boto3.client = Mock()
        s3 = boto3.client('s3')
        s3.copy_object = Mock(side_effect=[None])
        self.exp_event["Records"][0]["s3"]["object"]["key"] = exp_file_key
        result = dr_copy_files_to_archive.handler(self.exp_event, self.exp_context)
        boto3.client.assert_called_with('s3')
        exp_result = json.dumps([{"success": True, "source_bucket": self.exp_src_bucket, "source_key": exp_file_key, "target_bucket": self.exp_other_bucket, "err_msg": ""}])
        self.assertEqual(exp_result, result)
        s3.copy_object.assert_called_with(Bucket=self.exp_other_bucket,
                                          CopySource={'Bucket': self.exp_src_bucket,
                                                      'Key': exp_file_key},
                                          Key=exp_file_key)

    def test_handler_no_other_in_bucket_map(self):
        exp_file_key = 'dr-glacier/MOD09GQ.A0219114.N5aUCG.006.0656338553321.xml'
        boto3.client = Mock()
        s3 = boto3.client('s3')
        s3.copy_object = Mock(side_effect=[None])
        bucket_map = {".hdf": "unittest_hdf_bucket", ".txt": "unittest_txt_bucket"}
        os.environ['BUCKET_MAP'] = json.dumps(bucket_map)

        self.exp_event["Records"][0]["s3"]["object"]["key"] = exp_file_key
        exp_err = f'BUCKET_MAP: {bucket_map} does not contain values for ".xml" or "other"'
        try:
            dr_copy_files_to_archive.handler(self.exp_event, self.exp_context)
            self.fail("expected CopyRequestError")
        except dr_copy_files_to_archive.CopyRequestError as ex:
            self.assertEqual(exp_err, str(ex))

        boto3.client.assert_called_with('s3')

    def test_handler_no_object_key_in_event(self):
        boto3.client = Mock()
        s3 = boto3.client('s3')
        s3.copy_object = Mock(side_effect=[None])
        mydict = self.exp_event["Records"][0]["s3"]["object"]
        mydict.pop('key')
        exp_err = f'event record: "{self.exp_event["Records"][0]}" does not contain a value for Records["s3"]["object"]["key"]'
        try:
            dr_copy_files_to_archive.handler(self.exp_event, self.exp_context)
            self.fail("expected CopyRequestError")
        except dr_copy_files_to_archive.CopyRequestError as ex:
            self.assertEqual(exp_err, str(ex))


if __name__ == '__main__':
    unittest.main(argv=['start'])
