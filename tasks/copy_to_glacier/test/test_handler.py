import json
from os import path
from unittest import TestCase
from ..handler import *


class TestCopyToGlacierHandler(TestCase):
    """
    Test copy to glacier handler
    This will test if the function of test copy to glacier work as expected
    """
    excluded_file = 's3://test-bucket/this_file_should_be_exclude.example'
    not_excluded_file = 's3://test-bucket/prefix/this_file_should_not_be_exclude.txt'
    two_prefix_file = 's3://test-bucket/prefix1/prefix2/file.txt'
    path_to_this_file = os.path.abspath(os.path.dirname(__file__))
    event_path = os.path.join(path_to_this_file, "event.json")

    def test_1_exclude_file_types_excluded(self):
        """
        Testing exclude file types to be excluded
        """
        excluded_flag = should_exclude_files_type(self.excluded_file)
        self.assertEqual(excluded_flag, True)

    def test_2_excluded_file_types_not_excluded(self):
        """
        Testing exclude file types not to be excluded
        """

        not_excluded_flag = should_exclude_files_type(self.not_excluded_file)
        self.assertEqual(not_excluded_flag, False)

    def test_3_get_source_bucket_and_key(self):
        """
        Testing get source bucket and key
        """
        no_prefix_source = get_source_bucket_and_key(self.excluded_file)
        self.assertEqual(no_prefix_source[1], 'test-bucket')
        self.assertEqual(no_prefix_source[2], 'this_file_should_be_exclude.example')

        one_prefix_source = get_source_bucket_and_key(self.not_excluded_file)
        self.assertEqual(one_prefix_source[1], 'test-bucket')
        self.assertEqual(one_prefix_source[2], 'prefix/this_file_should_not_be_exclude.txt')

        two_prefix_source = get_source_bucket_and_key(self.two_prefix_file)
        self.assertEqual(two_prefix_source[1], 'test-bucket')
        self.assertEqual(two_prefix_source[2], 'prefix1/prefix2/file.txt')

    def test_4_get_bucket(self):
        """
        Testing get bucket
        """
        with open(self.event_path) as f:
            event = json.load(f)
            filename = path.basename(event.get('input', [])[0])
            files = event.get('config').get('collection').get('files', [])
            bucket = get_bucket(filename, files)
            self.assertEqual(bucket, 'protected')

    def test_5_task(self):
        """
        Testing task
        """
        context = []
        with open(self.event_path) as f:
            event = json.load(f)
            test_handler = task(event, context)
            print(test_handler)
